from database.supabase import supabase

print("✅ Connected")

response = supabase.auth.get_user()

print(response)