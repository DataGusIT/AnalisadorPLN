# config/storages.py
from django.conf import settings
from django.core.files.storage import Storage
from supabase import create_client, Client
import io

class SupabaseStorage(Storage):
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.bucket_name = settings.SUPABASE_BUCKET

    def _save(self, name, content):
        content.seek(0)
        self.client.storage.from_(self.bucket_name).upload(name, content.read())
        return name

    def _open(self, name, mode='rb'):
        response = self.client.storage.from_(self.bucket_name).download(name)
        return io.BytesIO(response)

    def delete(self, name):
        self.client.storage.from_(self.bucket_name).remove(name)

    def url(self, name):
        return self.client.storage.from_(self.bucket_name).get_public_url(name)

    def exists(self, name):
        # Esta verificação pode ser lenta. Em um app maior, considere otimizar.
        try:
            self.client.storage.from_(self.bucket_name).download(name)
            return True
        except Exception:
            return False