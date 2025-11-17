import os
import requests

supabase_url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

print(f"URL: {supabase_url}/rest/v1")
print(f"Key length: {len(service_key)} chars")

response = requests.get(
    f"{supabase_url}/rest/v1/doc_files?limit=3",
    headers={
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}"
    }
)

print(f"\nResponse status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ SUCCESS! Got {len(data)} records")
else:
    print(f"❌ ERROR: {response.text[:300]}")
