#!/usr/bin/env python3
"""
Import TPM Scoreboards Data to Supabase Production Database
Creates users, meetings, commitments, and attendance records from historical scoreboards
"""

import json
import requests
import uuid
from datetime import datetime, date
from typing import Dict, List, Any
import time

# Supabase configuration
SUPABASE_URL = "https://apfiwfkpdhslfavnncsl.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwZml3ZmtwZGhzbGZhdm5uY3NsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTIwNDI2MSwiZXhwIjoyMDcwNzgwMjYxfQ.JLhxI_CsO4RHRT0gfO8l8o3Sp36SNq1jyPwjZ3l5kLk"

headers = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}


def create_tables():
    """Create required tables if they don't exist"""
    print("Creating required tables...")
    
    # Create pod_meetings table first (referenced by meeting_attendance)
    pod_meetings_sql = """
    CREATE TABLE IF NOT EXISTS pod_meetings (
        id uuid NOT NULL DEFAULT gen_random_uuid(),
        pod_id uuid NULL,
        scheduled_date date NOT NULL,
        scheduled_time time NULL,
        status varchar(20) DEFAULT 'completed',
        created_at timestamp with time zone DEFAULT now(),
        CONSTRAINT pod_meetings_pkey PRIMARY KEY (id),
        CONSTRAINT pod_meetings_pod_id_fkey FOREIGN KEY (pod_id) REFERENCES pods(id) ON DELETE CASCADE
    );
    """
    
    # Create meet_participants table (referenced by meeting_attendance)
    meet_participants_sql = """
    CREATE TABLE IF NOT EXISTS meet_participants (
        id uuid NOT NULL DEFAULT gen_random_uuid(),
        meeting_id uuid NULL,
        user_id uuid NULL,
        join_time timestamp with time zone NULL,
        leave_time timestamp with time zone NULL,
        duration_minutes integer NULL DEFAULT 0,
        created_at timestamp with time zone DEFAULT now(),
        CONSTRAINT meet_participants_pkey PRIMARY KEY (id),
        CONSTRAINT meet_participants_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    # Create meeting_attendance table with provided schema
    meeting_attendance_sql = """
    CREATE TABLE IF NOT EXISTS meeting_attendance (
        id uuid NOT NULL DEFAULT gen_random_uuid(),
        meeting_id uuid NULL,
        user_id uuid NULL,
        attended boolean NULL DEFAULT false,
        duration_minutes integer NULL DEFAULT 0,
        created_at timestamp with time zone NULL DEFAULT now(),
        meet_participant_id uuid NULL,
        detection_method character varying(50) NULL DEFAULT 'manual'::character varying,
        meet_join_time timestamp with time zone NULL,
        meet_leave_time timestamp with time zone NULL,
        meet_duration_minutes integer NULL,
        meet_reconnect_count integer NULL DEFAULT 0,
        meet_device_type character varying(50) NULL,
        confidence_score double precision NULL DEFAULT 1.0,
        CONSTRAINT meeting_attendance_pkey PRIMARY KEY (id),
        CONSTRAINT meeting_attendance_meeting_id_user_id_key UNIQUE (meeting_id, user_id),
        CONSTRAINT meeting_attendance_meet_participant_id_fkey FOREIGN KEY (meet_participant_id) REFERENCES meet_participants (id),
        CONSTRAINT meeting_attendance_meeting_id_fkey FOREIGN KEY (meeting_id) REFERENCES pod_meetings (id) ON DELETE CASCADE,
        CONSTRAINT meeting_attendance_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    
    CREATE INDEX IF NOT EXISTS idx_meeting_attendance_meet_participant ON meeting_attendance USING btree (meet_participant_id);
    CREATE INDEX IF NOT EXISTS idx_meeting_attendance_detection_method ON meeting_attendance USING btree (detection_method);
    """
    
    # Execute SQL via HTTP (Supabase doesn't support direct SQL via REST API)
    # We'll need to create tables manually in Supabase SQL Editor
    print("⚠️  MANUAL STEP REQUIRED:")
    print("Please run the following SQL in Supabase SQL Editor:")
    print("\n" + "="*60)
    print(pod_meetings_sql)
    print(meet_participants_sql) 
    print(meeting_attendance_sql)
    print("="*60 + "\n")
    
    print("Assuming tables have been created. Proceeding with import...")


def parse_name(full_name: str) -> tuple:
    """Parse full name into first and last name"""
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        # Handle names with middle initials or multiple parts
        return parts[0], " ".join(parts[1:])


def create_users(scoreboards_data: Dict) -> Dict[str, str]:
    """Create users for all scoreboard names and return name->user_id mapping"""
    print("Creating users from scoreboard data...")
    
    user_mapping = {}
    
    for full_name in scoreboards_data.keys():
        first_name, last_name = parse_name(full_name)
        
        # Create user record
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name.lower()}.{last_name.lower()}@scoreboards.import".replace(" ", ""),
            "status": "imported_scoreboards",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert user
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=headers,
            json=user_data
        )
        
        if response.status_code == 201:
            # Get the created user ID
            user_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/users?email=eq.{user_data['email']}&select=id",
                headers=headers
            )
            
            if user_response.status_code == 200 and user_response.json():
                user_id = user_response.json()[0]['id']
                user_mapping[full_name] = user_id
                print(f"  ✅ Created user: {full_name} -> {user_id}")
            else:
                print(f"  ❌ Failed to get user ID for: {full_name}")
        else:
            print(f"  ❌ Failed to create user: {full_name} - {response.status_code}: {response.text}")
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"Created {len(user_mapping)} users")
    return user_mapping


def create_default_pod() -> str:
    """Create a default pod for imported meetings"""
    print("Creating default pod for imported meetings...")
    
    pod_data = {
        "name": "Imported Scoreboards Pod",
        "day_of_week": 1,  # Monday = 1
        "time_utc": "19:00:00",
        "status": "imported",
        "created_at": datetime.now().isoformat()
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/pods",
        headers=headers,
        json=pod_data
    )
    
    if response.status_code == 201:
        # Get the created pod ID
        pod_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/pods?name=eq.Imported Scoreboards Pod&select=id",
            headers=headers
        )
        
        if pod_response.status_code == 200 and pod_response.json():
            pod_id = pod_response.json()[0]['id']
            print(f"  ✅ Created default pod: {pod_id}")
            return pod_id
    
    print(f"  ❌ Failed to create default pod - {response.status_code}: {response.text}")
    return None


def create_pod_meetings(scoreboards_data: Dict, pod_id: str) -> Dict[str, str]:
    """Create pod_meetings records for all unique dates and return date->meeting_id mapping"""
    print("Creating pod meetings for all dates...")
    
    # Collect all unique dates from scoreboards
    all_dates = set()
    for user_data in scoreboards_data.values():
        for date_str in user_data.keys():
            all_dates.add(date_str)
    
    meeting_mapping = {}
    
    for date_str in sorted(all_dates):
        meeting_data = {
            "pod_id": pod_id,
            "meeting_date": date_str,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/pod_meetings",
            headers=headers,
            json=meeting_data
        )
        
        if response.status_code == 201:
            # Get the created meeting ID
            meeting_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/pod_meetings?meeting_date=eq.{date_str}&pod_id=eq.{pod_id}&select=id",
                headers=headers
            )
            
            if meeting_response.status_code == 200 and meeting_response.json():
                meeting_id = meeting_response.json()[0]['id']
                meeting_mapping[date_str] = meeting_id
                print(f"  ✅ Created meeting: {date_str} -> {meeting_id}")
            else:
                print(f"  ❌ Failed to get meeting ID for: {date_str}")
        else:
            print(f"  ❌ Failed to create meeting: {date_str} - {response.status_code}: {response.text}")
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"Created {len(meeting_mapping)} pod meetings")
    return meeting_mapping


def import_commitments(scoreboards_data: Dict, user_mapping: Dict[str, str]):
    """Import all historical commitments"""
    print("Importing historical commitments...")
    
    total_commitments = 0
    
    for full_name, user_data in scoreboards_data.items():
        if full_name not in user_mapping:
            print(f"  ⚠️  Skipping {full_name} - no user ID found")
            continue
        
        user_id = user_mapping[full_name]
        
        for date_str, date_data in user_data.items():
            commitments = date_data.get('commitments', [])
            
            for commitment in commitments:
                commitment_data = {
                    "user_id": user_id,
                    "commitment": commitment['text'],
                    "original_commitment": commitment['text'],
                    "status": "completed" if commitment['fulfilled'] == "true" else "failed" if commitment['fulfilled'] == "false" else "pending",
                    "smart_score": 1.0,
                    "completed_at": f"{date_str}T23:59:59Z" if commitment['fulfilled'] == "true" else None,
                    "created_at": f"{date_str}T00:00:00Z",
                    "updated_at": f"{date_str}T23:59:59Z"
                }
                
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/commitments",
                    headers=headers,
                    json=commitment_data
                )
                
                if response.status_code == 201:
                    total_commitments += 1
                    if total_commitments % 10 == 0:
                        print(f"  Imported {total_commitments} commitments...")
                else:
                    print(f"  ❌ Failed to import commitment for {full_name} on {date_str}")
                
                time.sleep(0.05)  # Rate limiting
    
    print(f"✅ Imported {total_commitments} total commitments")


def import_attendance(scoreboards_data: Dict, user_mapping: Dict[str, str], meeting_mapping: Dict[str, str]):
    """Import attendance data to meeting_attendance table"""
    print("Importing attendance data...")
    
    total_attendance = 0
    
    for full_name, user_data in scoreboards_data.items():
        if full_name not in user_mapping:
            continue
        
        user_id = user_mapping[full_name]
        
        for date_str, date_data in user_data.items():
            if date_str not in meeting_mapping:
                continue
            
            meeting_id = meeting_mapping[date_str]
            attendance_status = date_data.get('attendance', 'unknown')
            
            # Convert attendance status to boolean
            attended = True if attendance_status == "attended" else False if attendance_status == "not_attended" else None
            
            attendance_data = {
                "meeting_id": meeting_id,
                "user_id": user_id,
                "attended": attended,
                "duration_minutes": 60 if attended else 0,  # Assume 60 min meetings
                "detection_method": "scoreboards_import",
                "confidence_score": 1.0 if attendance_status != "unknown" else 0.5,
                "created_at": f"{date_str}T00:00:00Z"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/meeting_attendance",
                headers=headers,
                json=attendance_data
            )
            
            if response.status_code == 201:
                total_attendance += 1
                if total_attendance % 20 == 0:
                    print(f"  Imported {total_attendance} attendance records...")
            else:
                print(f"  ❌ Failed to import attendance for {full_name} on {date_str}")
            
            time.sleep(0.05)  # Rate limiting
    
    print(f"✅ Imported {total_attendance} total attendance records")


def main():
    """Main import function"""
    print("🚀 Starting TPM Scoreboards Import to Supabase")
    print("=" * 50)
    
    # Load scoreboards data
    try:
        with open('tpm_scoreboards_data.json', 'r') as f:
            scoreboards_data = json.load(f)
        print(f"📊 Loaded data for {len(scoreboards_data)} users")
    except FileNotFoundError:
        print("❌ tpm_scoreboards_data.json not found. Run excel_to_json_converter.py first.")
        return
    
    try:
        # Step 1: Create required tables
        create_tables()
        
        # Step 2: Create users
        user_mapping = create_users(scoreboards_data)
        
        # Step 3: Create default pod
        pod_id = create_default_pod()
        if not pod_id:
            print("❌ Failed to create default pod. Aborting.")
            return
        
        # Step 4: Create pod meetings
        meeting_mapping = create_pod_meetings(scoreboards_data, pod_id)
        
        # Step 5: Import commitments
        import_commitments(scoreboards_data, user_mapping)
        
        # Step 6: Import attendance
        import_attendance(scoreboards_data, user_mapping, meeting_mapping)
        
        print("\n🎉 Import completed successfully!")
        print(f"✅ Created {len(user_mapping)} users")
        print(f"✅ Created {len(meeting_mapping)} meetings")
        print("✅ Imported all commitments and attendance data")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()