import httpx
from supabase import create_client, Client
from app.core.config import settings
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    if 'proxy' in kwargs:
        kwargs['proxies'] = kwargs.pop('proxy')
    original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init
url: str = settings.SUPABASE_URL.strip()
key: str = settings.SUPABASE_KEY.strip()

supabase: Client = create_client(url, key)

print("DEBUG: Supabase Client initialized successfully with Monkey Patch!")