"""
Setup Script: Initialize Database with Lawyer Data
Run with: conda activate verma && python setup_database.py
"""

import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime

# Database path
DB_PATH = r"D:\legal\data\legalbuddy.db"

print("\n" + "="*70)
print("LEGAL SYSTEM - DATABASE INITIALIZATION")
print("="*70)

try:
    print("\n1. Creating database tables...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            phone TEXT UNIQUE,
            email TEXT UNIQUE,
            age INTEGER NOT NULL,
            profession TEXT NOT NULL,
            language TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Chat sessions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Chat messages
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Lawyers profile table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lawyers_profile (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            gender TEXT,
            type_of_lawyer TEXT,
            specialization TEXT,
            court_level TEXT,
            state TEXT,
            city TEXT,
            email TEXT,
            mobile TEXT,
            cases_fought INTEGER,
            cases_won INTEGER,
            cases_lost INTEGER,
            experience_years INTEGER,
            fee_range TEXT,
            language TEXT,
            availability TEXT,
            online_consultation TEXT,
            rating REAL,
            ranking_score REAL,
            win_rate REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Bookings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lawyer_id INTEGER NOT NULL,
            case_description TEXT NOT NULL,
            preferred_date TEXT,
            preferred_time TEXT,
            consultation_type TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lawyer_id) REFERENCES lawyers_profile (id)
        )
    """)
    
    # Appointments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            status TEXT DEFAULT 'scheduled',
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            meeting_link TEXT,
            FOREIGN KEY (booking_id) REFERENCES bookings (id)
        )
    """)
    
    # Lawyer ratings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lawyer_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            lawyer_id INTEGER NOT NULL,
            user_id INTEGER,
            rating REAL,
            review TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings (id),
            FOREIGN KEY (lawyer_id) REFERENCES lawyers_profile (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # User-lawyer interactions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_lawyer_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lawyer_id INTEGER,
            interaction_type TEXT,
            details TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lawyer_id) REFERENCES lawyers_profile (id)
        )
    """)
    
    # Create indices
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_lawyer_id ON bookings(lawyer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_appointments_booking_id ON appointments(booking_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ratings_lawyer_id ON lawyer_ratings(lawyer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user ON user_lawyer_interactions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lawyers_state_city ON lawyers_profile(state, city)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lawyers_type ON lawyers_profile(type_of_lawyer)")
    
    conn.commit()
    print("   SUCCESS - Tables created")
    
    # Load lawyer data
    print("\n2. Loading lawyer data from CSV...")
    df = pd.read_csv(r"D:\legal\models\lawyers_processed.csv")
    
    for idx, row in df.iterrows():
        cur.execute("""
            INSERT OR REPLACE INTO lawyers_profile (
                id, name, gender, type_of_lawyer, specialization, court_level,
                state, city, email, mobile, cases_fought, cases_won, cases_lost,
                experience_years, fee_range, language, availability, online_consultation,
                rating, ranking_score, win_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(row['id']),
            row['name'],
            row['gender'],
            row['type_of_lawyer'],
            row['specialization'],
            row['court_level'],
            row['state'],
            row['city'],
            row['email'],
            row['mobile'],
            int(row['cases_fought']),
            int(row['cases_won']),
            int(row['cases_lost']),
            int(row['experience_years']),
            row['fee_range'],
            row['language'],
            row['availability'],
            row['online_consultation'],
            float(row['rating']),
            float(row['ranking_score']),
            float(row['win_rate'])
        ))
        
        if (idx + 1) % 10000 == 0:
            print(f"   Loaded {idx + 1}/{len(df)} lawyers...")
    
    conn.commit()
    print(f"   SUCCESS - {len(df)} lawyers loaded")
    
    # Verify data
    print("\n3. Verifying data...")
    cur.execute("SELECT COUNT(*) as count FROM lawyers_profile")
    lawyer_count = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(DISTINCT state) as count FROM lawyers_profile")
    state_count = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(DISTINCT city) as count FROM lawyers_profile")
    city_count = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(DISTINCT type_of_lawyer) as count FROM lawyers_profile")
    type_count = cur.fetchone()['count']
    
    conn.close()
    
    print(f"   Total lawyers: {lawyer_count:,}")
    print(f"   States: {state_count}")
    print(f"   Cities: {city_count}")
    print(f"   Lawyer types: {type_count}")
    
    print("\n" + "="*70)
    print("DATABASE INITIALIZATION COMPLETE - SUCCESS!")
    print("="*70)
    print("\nDatabase location: ", DB_PATH)
    print("\nNext steps:")
    print("1. Update main.py with new endpoints (see main_py_new_endpoints.py)")
    print("2. Start backend:  python main.py")
    print("3. Test endpoints at: http://localhost:8000/docs")
    print("4. Update Streamlit UI with new pages")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
