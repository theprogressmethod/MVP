#!/usr/bin/env python3
"""
Import only commitments from scoreboards data - users already exist
"""

import json
import requests
import time
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://apfiwfkpdhslfavnncsl.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwZml3ZmtwZGhzbGZhdm5uY3NsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTIwNDI2MSwiZXhwIjoyMDcwNzgwMjYxfQ.JLhxI_CsO4RHRT0gfO8l8o3Sp36SNq1jyPwjZ3l5kLk"

headers = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def get_user_mapping():
    """Get mapping of imported users"""
    print("Getting user mapping...")
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?status=eq.imported_scoreboards&select=id,first_name,last_name",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get users: {response.status_code}")
        return {}
    
    users = response.json()
    user_mapping = {}
    
    for user in users:
        # Reconstruct the name format from scoreboards
        last_name = user['last_name'] or ""
        if last_name:
            full_name = f"{user['first_name']} {last_name}"
        else:
            full_name = user['first_name']
        user_mapping[full_name] = user['id']
        print(f"  Found user: {full_name} -> {user['id']}")
    
    return user_mapping

def import_commitments(scoreboards_data, user_mapping):
    """Import all historical commitments"""
    print("Importing historical commitments...")
    
    total_commitments = 0
    successful_imports = 0
    
    for full_name, user_data in scoreboards_data.items():
        if full_name not in user_mapping:
            print(f"  ⚠️  Skipping {full_name} - no user ID found")
            continue
        
        user_id = user_mapping[full_name]
        print(f"  Processing {full_name}...")
        
        for date_str, date_data in user_data.items():
            commitments = date_data.get('commitments', [])
            
            for commitment in commitments:
                total_commitments += 1
                
                # Skip empty commitments
                if not commitment['text'] or commitment['text'].strip() in ['-', '']:
                    continue
                
                commitment_data = {
                    "user_id": user_id,
                    "commitment": commitment['text'],
                    "status": "completed" if commitment['fulfilled'] == "true" else "failed" if commitment['fulfilled'] == "false" else "pending"
                }
                
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/commitments",
                    headers=headers,
                    json=commitment_data
                )
                
                if response.status_code == 201:
                    successful_imports += 1
                    if successful_imports % 10 == 0:
                        print(f"    Imported {successful_imports} commitments...")
                else:
                    print(f"    ❌ Failed to import commitment for {full_name} on {date_str}: {response.status_code}")
                
                time.sleep(0.05)  # Rate limiting
    
    print(f"✅ Imported {successful_imports}/{total_commitments} commitments")
    return successful_imports

def main():
    """Main import function"""
    print("🚀 Starting Commitments Import to Supabase")
    print("=" * 50)
    
    # Load scoreboards data
    try:
        with open('tpm_scoreboards_data.json', 'r') as f:
            scoreboards_data = json.load(f)
        print(f"📊 Loaded data for {len(scoreboards_data)} users")
    except FileNotFoundError:
        print("❌ tpm_scoreboards_data.json not found.")
        return
    
    try:
        # Get user mapping
        user_mapping = get_user_mapping()
        if not user_mapping:
            print("❌ No imported users found. Run full import first.")
            return
        
        # Import commitments
        imported_count = import_commitments(scoreboards_data, user_mapping)
        
        print(f"\n🎉 Import completed!")
        print(f"✅ Imported {imported_count} commitments")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()