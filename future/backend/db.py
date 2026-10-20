import os
import sqlite3
import hashlib
import secrets
from datetime import datetime

from rag import get_history_db

DB_PATH = r"D:\legal\data\legalbuddy.db"


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
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
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cur.execute(
        """
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
        """
    )

    # NEW TABLES FOR LAWYER RECOMMENDATION SYSTEM
    
    # Lawyers Profile Table
    cur.execute(
        """
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
        """
    )
    
    # Bookings Table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lawyer_id INTEGER NOT NULL,
            case_description TEXT NOT NULL,
            preferred_date TEXT,
            preferred_time TEXT,
            consultation_type TEXT CHECK(consultation_type IN ('online', 'offline')),
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'completed', 'cancelled')),
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lawyer_id) REFERENCES lawyers_profile (id)
        )
        """
    )
    
    # Appointments Table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled', 'rescheduled')),
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            meeting_link TEXT,
            FOREIGN KEY (booking_id) REFERENCES bookings (id)
        )
        """
    )
    
    # Lawyer Ratings Table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS lawyer_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            lawyer_id INTEGER NOT NULL,
            user_id INTEGER,
            rating REAL CHECK(rating >= 1 AND rating <= 5),
            review TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings (id),
            FOREIGN KEY (lawyer_id) REFERENCES lawyers_profile (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    
    # User-Lawyer Interactions Table (for analytics)
    cur.execute(
        """
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
        """
    )
    
    # Create indices for performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_lawyer_id ON bookings(lawyer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)")
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_appointments_booking_id ON appointments(booking_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date)")
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ratings_lawyer_id ON lawyer_ratings(lawyer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON lawyer_ratings(user_id)")
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user ON user_lawyer_interactions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interactions_lawyer ON user_lawyer_interactions(lawyer_id)")
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lawyers_state_city ON lawyers_profile(state, city)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lawyers_type ON lawyers_profile(type_of_lawyer)")

    conn.commit()
    conn.close()


def _timestamp():
    return datetime.utcnow().isoformat()


def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return f"{salt}${digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    salt, _ = stored_hash.split("$", 1)
    return _hash_password(password, salt) == stored_hash


def _user_from_row(row):
    if not row:
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "city": row["city"],
        "state": row["state"],
        "phone": row["phone"],
        "email": row["email"],
        "age": row["age"],
        "profession": row["profession"],
        "language": row["language"],
        "created_at": row["created_at"],
    }


def register_user(user_info: dict, password: str):
    if not user_info.get("phone") and not user_info.get("email"):
        raise ValueError("Phone or email is required.")

    conn = get_connection()
    cur = conn.cursor()

    if user_info.get("phone"):
        cur.execute("SELECT id FROM users WHERE phone = ?", (user_info["phone"],))
        if cur.fetchone():
            conn.close()
            raise ValueError("Phone is already registered.")

    if user_info.get("email"):
        cur.execute("SELECT id FROM users WHERE email = ?", (user_info["email"],))
        if cur.fetchone():
            conn.close()
            raise ValueError("Email is already registered.")

    created_at = _timestamp()
    password_hash = _hash_password(password)

    cur.execute(
        """
        INSERT INTO users (
            name, city, state, phone, email, age, profession, language,
            password_hash, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_info["name"],
            user_info["city"],
            user_info["state"],
            user_info.get("phone"),
            user_info.get("email"),
            user_info["age"],
            user_info["profession"],
            user_info["language"],
            password_hash,
            created_at,
        ),
    )

    user_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = _user_from_row(cur.fetchone())
    conn.close()
    return user


def login_user(identifier: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE phone = ? OR email = ?",
        (identifier, identifier),
    )
    row = cur.fetchone()
    conn.close()

    if not row or not _verify_password(password, row["password_hash"]):
        return None

    return _user_from_row(row)


def create_chat_session(user_id: int, first_query: str | None = None):
    now = _timestamp()
    title_source = (first_query or "New Chat").strip()
    title = title_source[:60] or "New Chat"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, title, now, now),
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_user_sessions(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, created_at, updated_at
        FROM chat_sessions
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,),
    )
    sessions = [dict(row) for row in cur.fetchall()]
    conn.close()
    return sessions


def get_session_messages(session_id: int, user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, role, content, created_at
        FROM chat_messages
        WHERE session_id = ? AND user_id = ?
        ORDER BY id ASC
        """,
        (session_id, user_id),
    )
    messages = [dict(row) for row in cur.fetchall()]
    conn.close()
    return messages


def save_message(session_id: int, user_id: int, role: str, content: str):
    now = _timestamp()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_messages (session_id, user_id, role, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session_id, user_id, role, content, now),
    )
    message_id = cur.lastrowid
    cur.execute(
        "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
        (now, session_id),
    )
    conn.commit()
    conn.close()
    return message_id


def save_exchange_to_history_vectorstore(
    user_id: int,
    session_id: int,
    query: str,
    answer: str,
):
    history_db = get_history_db()
    doc_text = f"User question: {query}\nAssistant answer: {answer}"
    doc_id = f"user-{user_id}-session-{session_id}-{secrets.token_hex(8)}"

    history_db.add_texts(
        texts=[doc_text],
        metadatas=[
            {
                "user_id": user_id,
                "session_id": session_id,
                "query": query[:500],
            }
        ],
        ids=[doc_id],
    )


def get_semantic_history(user_id: int, query: str, limit: int = 2):
    history_db = get_history_db()
    results = history_db.similarity_search(
        query,
        k=limit,
        filter={"user_id": user_id},
    )
    return [doc.page_content for doc in results]


# ═════════════════════════════════════════════════════════════════════════════
# LAWYER RECOMMENDATION & BOOKING SYSTEM HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════


def load_lawyers_to_db():
    """Load lawyers from processed CSV to database"""
    import pandas as pd
    
    df = pd.read_csv(r"D:\legal\models\lawyers_processed.csv")
    
    conn = get_connection()
    cur = conn.cursor()
    
    for _, row in df.iterrows():
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
    
    conn.commit()
    print(f"Loaded {len(df)} lawyers to database")


def get_booking_details(booking_id: int):
    """Get complete booking details with lawyer and user info"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            b.*,
            u.name as user_name,
            u.email as user_email,
            u.phone as user_phone,
            l.name as lawyer_name,
            l.type_of_lawyer,
            l.city as lawyer_city,
            l.email as lawyer_email,
            l.mobile as lawyer_mobile
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN lawyers_profile l ON b.lawyer_id = l.id
        WHERE b.id = ?
    """, (booking_id,))
    
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_booking_status(booking_id: int, status: str):
    """Update booking status"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE bookings 
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, booking_id))
    
    conn.commit()
    conn.close()
    return True


def get_lawyer_average_rating(lawyer_id: int):
    """Get average rating of a lawyer"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
        FROM lawyer_ratings
        WHERE lawyer_id = ?
    """, (lawyer_id,))
    
    result = cur.fetchone()
    conn.close()
    
    return {
        'average_rating': result['avg_rating'] or 0,
        'total_ratings': result['total_ratings'] or 0
    }


def get_user_booking_history(user_id: int, limit: int = 10):
    """Get user's booking history"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            b.*,
            l.name as lawyer_name,
            l.type_of_lawyer,
            r.rating,
            r.review
        FROM bookings b
        LEFT JOIN lawyers_profile l ON b.lawyer_id = l.id
        LEFT JOIN lawyer_ratings r ON b.id = r.booking_id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
        LIMIT ?
    """, (user_id, limit))
    
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
