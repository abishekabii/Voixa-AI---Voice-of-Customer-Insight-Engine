import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase=create_client(url,key)

# Insert a sample test row
response = supabase.table("feedback").insert({
    "text": "Test connection from Voixa AI",
    "sentiment": "POSITIVE",
    "confidence": 0.99
}).execute()

print(response)