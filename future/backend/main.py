import os
from datetime import datetime
import json
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from db import (
    create_chat_session,
    get_connection,
    get_semantic_history,
    get_session_messages,
    get_user_sessions,
    init_db,
    login_user,
    register_user,
    save_exchange_to_history_vectorstore,
    save_message,
)
from llm import get_llm
from rag import get_case_db, get_law_db
from recommender import classify_case, recommend_lawyer

# Import lawyer recommendation system
try:
    from lawyer_recommender import get_recommender
    LAWYER_SYSTEM_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Lawyer recommendation system not available: {e}")
    LAWYER_SYSTEM_AVAILABLE = False

app = FastAPI()

BASE_PATH = r"D:\legal\data\supreme_court_judgments"
init_db()


class RegisterRequest(BaseModel):
    name: str
    city: str
    state: str
    phone: str | None = None
    email: str | None = None
    age: int
    profession: str
    language: str
    password: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class ChatRequest(BaseModel):
    query: str
    user_id: int
    session_id: int | None = None


# Lawyer Recommendation System Models
class LawyerRecommendationRequest(BaseModel):
    case_type: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    language: Optional[str] = None
    court_level: Optional[str] = None
    top_n: int = 10
    user_id: int


class LawyerSearchRequest(BaseModel):
    query: str
    type_of_lawyer: Optional[str] = None
    state: Optional[str] = None
    language: Optional[str] = None
    min_rating: Optional[float] = None
    court_level: Optional[str] = None
    top_n: int = 10


class BookingRequest(BaseModel):
    user_id: int
    lawyer_id: int
    case_description: str
    preferred_date: str
    preferred_time: str
    consultation_type: str
    notes: Optional[str] = None


class AppointmentCreateRequest(BaseModel):
    booking_id: int
    appointment_date: str
    appointment_time: str
    duration_minutes: int = 60
    notes: Optional[str] = None


class RatingRequest(BaseModel):
    booking_id: int
    lawyer_id: int
    rating: float
    review: str


def get_user_profile(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(row)


def build_prompt(user: dict, query: str, law_context: str, case_context: str, history_context: str):
    profession = user.get("profession", "")
    user_state = user.get("state", "")
    user_city = user.get("city", "")
    user_language = user.get("language", "English")
    user_age = user.get("age", 0)

    if profession == "Student / Learner":
        style_block = f"""
You are a legal teacher helping students learn Indian law.
User: {user_language} language, Age: {user_age}

Explain the concept in simple, student-friendly terms.

Give:
- Easy explanation
- Relevant law sections (Constitution, IPC, BNS)
- Real example from case law
- Key takeaways
"""
    elif profession == "Lawyer":
        style_block = f"""
You are a legal research assistant helping lawyer from {user_state}.

Provide:
- Relevant law sections with citations
- Court interpretation trends
- Similar case precedents
- Argument direction
- Applicable judgment references

Be professional, precise, and jurisdiction-aware for {user_state} courts.
"""
    else:  # Needs Help / General Public
        style_block = f"""
You are a professional Indian legal advisor.

User Situation:
- Location: {user_city}, {user_state}
- Age: {user_age}
- Language: {user_language}
- Status: Common person seeking legal help

Provide actionable advice:
- What happened legally (simple explanation)
- Your legal rights & position
- Immediate risks/consequences
- What to do next (step-by-step)
- When to hire a lawyer
- Important local considerations for {user_state}

Use simple language. Avoid jargon. Be practical and helpful.
"""

    return f"""
{style_block}

Use the provided legal context, relevant cases, and past chat history to answer helpfully.

PREVIOUS CHAT HISTORY (If relevant):
{history_context or "No relevant chat history found."}

RELEVANT LAWS & SECTIONS:
{law_context}

RELEVANT CASE LAW:
{case_context}

USER'S QUESTION:
{query}

ANSWER:
"""


@app.get("/")
def health_check():
    return {"status": "ok", "message": "LegalBuddy backend running"}


@app.post("/register")
def register(req: RegisterRequest):
    try:
        user = register_user(req.model_dump(exclude={"password"}), req.password)
        return {"user": user}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/login")
def login(req: LoginRequest):
    user = login_user(req.identifier, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"user": user, "sessions": get_user_sessions(user["id"])}


@app.get("/history/{user_id}")
def get_history(user_id: int):
    return {"sessions": get_user_sessions(user_id)}


@app.get("/history/{user_id}/{session_id}")
def get_session_history(user_id: int, session_id: int):
    return {"messages": get_session_messages(session_id, user_id)}


@app.get("/get_pdf")
def get_pdf(file: str, year: str):
    path = os.path.join(BASE_PATH, year, file)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="application/pdf")


@app.post("/chat")
def chat(req: ChatRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    user = get_user_profile(req.user_id)
    session_id = req.session_id or create_chat_session(req.user_id, query)
    save_message(session_id, req.user_id, "user", query)

    law_db = get_law_db()
    case_db = get_case_db()
    llm = get_llm()

    # ENHANCED RETRIEVAL: Get more documents for better context
    law_docs = law_db.similarity_search(query, k=8)  # Increased from 2 to 8
    case_docs = case_db.similarity_search(query, k=10)  # Increased from 3 to 10
    history_docs = get_semantic_history(req.user_id, query, limit=5)  # Increased from 2 to 5

    law_context = "\n\n".join([doc.page_content[:500] for doc in law_docs])
    case_context = "\n\n".join([doc.page_content[:500] for doc in case_docs])
    history_context = "\n\n".join(history_docs)

    case_insights = [
        {
            "file": doc.metadata.get("file", "Unknown"),
            "year": str(doc.metadata.get("year", "Unknown")),
        }
        for doc in case_docs
    ]

    if "vs" in query.lower() and "judgment" in query.lower():
        answer = "This appears to be a case lookup. Refer the judgment below."
        save_message(session_id, req.user_id, "assistant", answer)
        save_exchange_to_history_vectorstore(req.user_id, session_id, query, answer)
        return {
            "answer": answer,
            "case_type": ["Case Lookup"],
            "case_type_explanation": "Direct case search",
            "recommended_lawyers": [],
            "case_insights": case_insights,
            "session_id": session_id,
        }

    case_types = classify_case(query)
    lawyers = recommend_lawyer(case_types)

    case_type_explanation = {
        "Criminal": "This is a criminal matter involving police action or punishment.",
        "Civil": "This looks like a civil dispute between people or entities.",
        "Family": "This relates to family or personal relationship issues.",
        "Corporate": "This appears connected to business or company matters.",
        "Revenue": "This concerns land, tax, or revenue issues.",
        "General Legal Advice": "This is a broader legal guidance request.",
    }

    prompt = build_prompt(user, query, law_context, case_context, history_context)
    answer = llm.invoke(prompt).strip()

    save_message(session_id, req.user_id, "assistant", answer)
    save_exchange_to_history_vectorstore(req.user_id, session_id, query, answer)

    return {
        "answer": answer,
        "case_type": case_types,
        "case_type_explanation": case_type_explanation.get(case_types[0], ""),
        "recommended_lawyers": lawyers,
        "case_insights": case_insights,
        "session_id": session_id,
    }


# ═════════════════════════════════════════════════════════════════════════════
# LAWYER RECOMMENDATION SYSTEM ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/recommend-lawyers")
async def recommend_lawyers(request: LawyerRecommendationRequest):
    """Get lawyer recommendations based on case details"""
    if not LAWYER_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Lawyer recommendation system not available")
    
    try:
        recommender = get_recommender()
        
        recommendations = recommender.recommend_by_filters(
            case_type=request.case_type,
            state=request.state,
            city=request.city,
            language=request.language,
            court_level=request.court_level,
            top_n=request.top_n
        )
        
        # Log interaction
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_lawyer_interactions (user_id, interaction_type, details, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            request.user_id,
            'recommendation_view',
            json.dumps({'results_count': len(recommendations)}),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/lawyer/{lawyer_id}")
async def get_lawyer_details(lawyer_id: int):
    """Get complete details of a specific lawyer"""
    if not LAWYER_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Lawyer recommendation system not available")
    
    try:
        recommender = get_recommender()
        lawyer = recommender.get_lawyer_details(lawyer_id)
        
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        
        return {"success": True, "lawyer": lawyer}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/lawyer/search")
async def search_lawyers(request: LawyerSearchRequest):
    """Search lawyers by name or location with filters"""
    if not LAWYER_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Lawyer recommendation system not available")
    
    try:
        recommender = get_recommender()
        
        filters = {}
        if request.type_of_lawyer:
            filters['type_of_lawyer'] = request.type_of_lawyer
        if request.state:
            filters['state'] = request.state
        if request.language:
            filters['language'] = request.language
        if request.min_rating:
            filters['min_rating'] = request.min_rating
        if request.court_level:
            filters['court_level'] = request.court_level
        
        results = recommender.search_lawyers(
            query=request.query,
            filters=filters if filters else None,
            top_n=request.top_n
        )
        
        return {"success": True, "count": len(results), "results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/similar-lawyers/{lawyer_id}")
async def get_similar_lawyers(lawyer_id: int, top_n: int = 5):
    """Get lawyers similar to a specific lawyer"""
    if not LAWYER_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Lawyer recommendation system not available")
    
    try:
        recommender = get_recommender()
        similar = recommender.get_similar_lawyers(lawyer_id, top_n=top_n)
        return {"success": True, "count": len(similar), "similar_lawyers": similar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/book-lawyer")
async def book_lawyer(request: BookingRequest):
    """Book a lawyer for consultation"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO bookings (
                user_id, lawyer_id, case_description, 
                preferred_date, preferred_time, consultation_type,
                status, created_at, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.user_id,
            request.lawyer_id,
            request.case_description,
            request.preferred_date,
            request.preferred_time,
            request.consultation_type,
            'pending',
            datetime.now().isoformat(),
            request.notes or ""
        ))
        
        conn.commit()
        booking_id = cur.lastrowid
        conn.close()
        
        return {
            "success": True,
            "booking_id": booking_id,
            "status": "pending",
            "message": "Booking request created. Awaiting lawyer confirmation."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bookings/{user_id}")
async def get_user_bookings(user_id: int, status: Optional[str] = None):
    """Get all bookings for a user"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if status:
            cur.execute("""
                SELECT b.*, l.name as lawyer_name, l.type_of_lawyer
                FROM bookings b
                LEFT JOIN lawyers_profile l ON b.lawyer_id = l.id
                WHERE b.user_id = ? AND b.status = ?
                ORDER BY b.created_at DESC
            """, (user_id, status))
        else:
            cur.execute("""
                SELECT b.*, l.name as lawyer_name, l.type_of_lawyer
                FROM bookings b
                LEFT JOIN lawyers_profile l ON b.lawyer_id = l.id
                WHERE b.user_id = ?
                ORDER BY b.created_at DESC
            """, (user_id,))
        
        bookings = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return {"success": True, "count": len(bookings), "bookings": bookings}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/appointment/create")
async def create_appointment(request: AppointmentCreateRequest):
    """Create an appointment from a booking"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO appointments (
                booking_id, appointment_date, appointment_time,
                duration_minutes, status, created_at, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.booking_id,
            request.appointment_date,
            request.appointment_time,
            request.duration_minutes,
            'scheduled',
            datetime.now().isoformat(),
            request.notes or ""
        ))
        
        cur.execute("UPDATE bookings SET status = 'confirmed' WHERE id = ?", (request.booking_id,))
        conn.commit()
        appointment_id = cur.lastrowid
        conn.close()
        
        return {
            "success": True,
            "appointment_id": appointment_id,
            "status": "scheduled",
            "message": "Appointment confirmed"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/appointments/{user_id}")
async def get_user_appointments(user_id: int):
    """Get all appointments for a user"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT a.*, b.lawyer_id, l.name as lawyer_name
            FROM appointments a
            JOIN bookings b ON a.booking_id = b.id
            LEFT JOIN lawyers_profile l ON b.lawyer_id = l.id
            WHERE b.user_id = ?
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (user_id,))
        
        appointments = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return {"success": True, "count": len(appointments), "appointments": appointments}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/booking/cancel")
async def cancel_booking(booking_id: int):
    """Cancel a booking"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Booking cancelled", "booking_id": booking_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/lawyer/rate")
async def rate_lawyer(request: RatingRequest):
    """Rate a lawyer after consultation"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM bookings WHERE id = ?", (request.booking_id,))
        booking = cur.fetchone()
        user_id = booking['user_id'] if booking else None
        
        cur.execute("""
            INSERT INTO lawyer_ratings (booking_id, lawyer_id, user_id, rating, review, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.booking_id,
            request.lawyer_id,
            user_id,
            request.rating,
            request.review,
            datetime.now().isoformat()
        ))
        
        cur.execute("UPDATE bookings SET status = 'completed' WHERE id = ?", (request.booking_id,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Rating submitted", "booking_id": request.booking_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
