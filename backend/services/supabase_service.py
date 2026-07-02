import os
from supabase import create_client, Client
import uuid


class SupabaseDB:
    def __init__(self):
        self.url: str = os.environ.get("SUPABASE_URL")
        self.key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(self.url, self.key)

    def upload_pdf(self, user_id: str, file_bytes: bytes, filename: str) -> str:
        storage_path = f"{user_id}/{uuid.uuid4()}_{filename}"
        try:
            self.supabase.storage.from_("pdf-store").upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": "application/pdf"}
            )
        except Exception as e:
            raise e
        return storage_path

    def get_pdf_url(self, storage_path: str) -> str:
        response = self.supabase.storage.from_("pdf-store").create_signed_url(
            path=storage_path,
            expires_in=3600
        )
        return response["signedURL"]

    def insert_record(self, user_id: str, filename: str, storage_url: str) -> str:
        response = self.supabase.table("documents").insert({
            "user_id": user_id,
            "filename": filename,
            "storage_url": storage_url,
            "status": "uploaded"
        }).execute()
        return response.data[0]['id']

    def update_document_status(self, document_id: str, status: str):
        self.supabase.table("documents").update(
            {"status": status}
        ).eq("id", document_id).execute()

    def get_user_document(self, user_id: str) -> list:
        response = self.supabase.table("documents").select("*").eq(
            "user_id", user_id
        ).order("timestamp", desc=True).execute()
        return response.data
    
    def upsert_user(self, clerk_user_id: str, stripe_customer_id: str):
        self.supabase.table("users").upsert({
            "clerk_user_id": clerk_user_id,
            "stripe_customer_id": stripe_customer_id,
            "plan": "pro"
        }, on_conflict="clerk_user_id").execute()
        
    def get_user_plan(self, clerk_user_id: str) -> str:
        response = self.supabase.table("users").select("plan").eq(
            "clerk_user_id", clerk_user_id
        ).execute()
        
        if response.data:
            return response.data[0]["plan"]
        return "free"