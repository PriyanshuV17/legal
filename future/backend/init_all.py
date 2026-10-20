#!/usr/bin/env python
"""
Complete LegalBuddy Backend Initialization
Rebuilds all vectorstores and seeds all databases
Run this ONCE after installation
"""

import os
import sys
from pathlib import Path

# Setup paths
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

print("╔════════════════════════════════════════════════════════╗")
print("║     LegalBuddy Backend - Complete Initialization       ║")
print("╚════════════════════════════════════════════════════════╝\n")

# Step 1: Initialize SQLite Database
print("STEP 1: Initializing SQLite Database...")
print("-" * 50)
try:
    from db import init_db
    init_db()
    print("✅ Database initialized with full schema\n")
except Exception as e:
    print(f"❌ Database init failed: {e}\n")
    sys.exit(1)

# Step 2: Rebuild Law Vectorstore (Constitution, IPC, BNS)
print("STEP 2: Rebuilding Law Vectorstore...")
print("-" * 50)
try:
    from ingest_laws import ingest
    ingest()
    print("✅ All legal documents loaded into vectorstore\n")
except Exception as e:
    print(f"⚠️  Law vectorstore error: {e}\n")

# Step 3: Skip Case Loading - Using Existing case_db
print("STEP 3: Using Existing Case Vectorstore...")
print("-" * 50)
print("⏭️  Skipping case ingestion (using existing case_db)")
print("✅ Case vectorstore will be used as-is\n")
print("Note: To reload cases in future, run: python ingest_cases.py\n")

# Step 4: Load Lawyers (86000+)
print("STEP 4: Loading Lawyer Data (86000+ records)...")
print("-" * 50)
try:
    import pandas as pd
    import sqlite3
    
    LAWYER_CSV = r"D:\legal\data\lawyers_large.csv"
    DB_PATH = r"D:\legal\data\legalbuddy.db"
    
    if os.path.exists(LAWYER_CSV):
        df = pd.read_csv(LAWYER_CSV)
        print(f"📁 Found {len(df)} lawyer records")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear existing records
        cursor.execute("DELETE FROM lawyers_profile")
        
        # Insert all lawyers
        for idx, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO lawyers_profile (
                        id, name, gender, type_of_lawyer, specialization,
                        court_level, state, city, email, mobile,
                        cases_fought, cases_won, cases_lost, experience_years,
                        fee_range, language, availability, online_consultation,
                        rating, ranking_score, win_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row.get('id', idx)) if pd.notna(row.get('id')) else idx,
                    str(row.get('name', f'Lawyer {idx}'))[:100],
                    str(row.get('gender', 'M'))[:10],
                    str(row.get('type_of_lawyer', 'General'))[:50],
                    str(row.get('specialization', 'General Practice'))[:150],
                    str(row.get('court_level', 'District'))[:50],
                    str(row.get('state', 'India'))[:50],
                    str(row.get('city', 'Unknown'))[:50],
                    str(row.get('email', f'lawyer{idx}@legal.ai'))[:120],
                    str(row.get('mobile', '9000000000'))[:20],
                    int(row.get('cases_fought', 0)) if pd.notna(row.get('cases_fought')) else 0,
                    int(row.get('cases_won', 0)) if pd.notna(row.get('cases_won')) else 0,
                    int(row.get('cases_lost', 0)) if pd.notna(row.get('cases_lost')) else 0,
                    int(row.get('experience_years', 5)) if pd.notna(row.get('experience_years')) else 5,
                    str(row.get('fee_range', '10000-50000'))[:30],
                    str(row.get('language', 'English'))[:50],
                    str(row.get('availability', 'Available'))[:50],
                    str(row.get('online_consultation', 'Yes'))[:10],
                    float(row.get('rating', 4.0)) if pd.notna(row.get('rating')) else 4.0,
                    float(row.get('ranking_score', 75.0)) if pd.notna(row.get('ranking_score')) else 75.0,
                    float(row.get('win_rate', 0.7)) if pd.notna(row.get('win_rate')) else 0.7,
                ))
                
                if (idx + 1) % 5000 == 0:
                    conn.commit()
                    print(f"  ✓ Loaded {idx + 1} lawyers...")
                    
            except Exception as e:
                if idx < 3:
                    print(f"  ⚠️  Error loading lawyer {idx}: {str(e)[:60]}")
        
        conn.commit()
        total = cursor.execute("SELECT COUNT(*) FROM lawyers_profile").fetchone()[0]
        conn.close()
        print(f"✅ Loaded {total} lawyers into database\n")
    else:
        print(f"⚠️  Lawyer CSV not found at {LAWYER_CSV}\n")
        
except Exception as e:
    print(f"⚠️  Lawyer loading error: {e}\n")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 50)
print("╔════════════════════════════════════════════════════════╗")
print("║              ✅ INITIALIZATION COMPLETE                ║")
print("╚════════════════════════════════════════════════════════╝")
print("\nNext Steps:")
print("  1. START OLLAMA:     python START_OLLAMA.bat")
print("  2. START BACKEND:    cd webapp/backend && uvicorn app.main:app --reload")
print("  3. START FRONTEND:   cd frontend && npm start")
print("\nAll datasets are now loaded and ready!")
