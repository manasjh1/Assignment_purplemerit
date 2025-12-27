import os
import asyncio
import json
import redis.asyncio as redis
from dotenv import load_dotenv
from app.services.db import supabase

load_dotenv()

# Configuration
MAX_RETRIES = 3
REDIS_URL = f"redis://{os.getenv('REDIS_USER', 'default')}:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"

async def process_jobs():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    print("Worker connected with Reliability Logic (Retries enabled)...")
    
    while True:
        try:
            # 1. Fetch Job
            result = await r.blpop("job_queue", timeout=2)
            if not result:
                continue
                
            job_json = result[1]
            job_data = json.loads(job_json)
            job_id = job_data.get("id")
            retries = job_data.get("retry_count", 0)

            print(f"Processing Job: {job_id} (Attempt {retries + 1})")

            # 2. Update DB to 'Processing' [cite: 69]
            supabase.table("jobs").update({"status": "processing"}).eq("id", job_id).execute()

            # 3. TRY Executing (Simulating work)
            try:
                # Simulate a failure for demonstration if 'task_name' is 'fail_test'
                if job_data.get("task_name") == "fail_test":
                    raise Exception("Simulated Failure")
                
                await asyncio.sleep(2) # The "Work"
                
                # Success!
                supabase.table("jobs").update({
                    "status": "completed", 
                    "result": "Success"
                }).eq("id", job_id).execute()
                print(f"✅ Finished Job: {job_id}")

            except Exception as e:
                # 4. FAILURE HANDLING & RETRY LOGIC [cite: 71, 72]
                print(f"❌ Job Failed: {str(e)}")
                
                if retries < MAX_RETRIES:
                    # Increment retry count and push back to queue
                    job_data["retry_count"] = retries + 1
                    await r.rpush("job_queue", json.dumps(job_data))
                    print(f"🔄 Retrying job {job_id} (Re-queued)")
                    
                    # Update DB status to warn user
                    supabase.table("jobs").update({
                        "status": "retrying", 
                        "result": f"Attempt {retries+1} failed"
                    }).eq("id", job_id).execute()
                else:
                    # Max retries reached - Mark as FAILED
                    supabase.table("jobs").update({
                        "status": "failed", 
                        "result": f"Max retries reached. Error: {str(e)}"
                    }).eq("id", job_id).execute()
                    print(f"💀 Job {job_id} permanently failed.")

        except Exception as main_e:
            print(f"CRITICAL WORKER ERROR: {str(main_e)}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(process_jobs())