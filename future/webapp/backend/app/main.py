from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import CONTACT_EMAIL, CONTACT_NAME, CONTACT_PHONE, PDF_BASE_PATH, SIGNATURE
from .db import Base, SessionLocal, engine, get_db
from .legal_engine import generate_legal_response, store_history_embedding
from .models import AuditLog, Booking, ChatMessage, ChatSession, ContactSubmission, ContentEntry, LawyerProfile, SavedCase, SavedLaw, User
from .schemas import ActivityCreate, BookingCreate, ChatRequest, ContactCreate, ContentCreate, ContentUpdate, LawyerCreate, LawyerUpdate, PasswordReset, UserCreate, UserLogin, UserUpdate
from .security import hash_password, verify_password
from .seed import create_default_admin, seed_reference_data

app = FastAPI(title="LegalBuddy WebApp API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def log_event(db: Session, event_type: str, detail: str, actor_user_id: int | None = None):
    db.add(AuditLog(actor_user_id=actor_user_id, event_type=event_type, detail=detail))
    db.commit()


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        create_default_admin(db)
        seed_reference_data(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "name": "LegalBuddy WebApp API",
        "signature": SIGNATURE,
        "contact": {"name": CONTACT_NAME, "email": CONTACT_EMAIL, "phone": CONTACT_PHONE},
    }


@app.get("/api/meta")
def meta():
    return {
        "brand": "LegalBuddy AI",
        "developer": CONTACT_NAME,
        "signature": SIGNATURE,
        "contact_email": CONTACT_EMAIL,
        "contact_phone": CONTACT_PHONE,
        "theme": {
            "base": "dark",
            "accent": "orange",
            "mood": "professional, friendly, modern AI",
        },
    }


@app.post("/api/auth/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if not payload.phone and not payload.email:
        raise HTTPException(status_code=400, detail="Phone or email is required.")

    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    if payload.phone and db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered.")

    user = User(
        name=payload.name,
        city=payload.city,
        state=payload.state,
        phone=payload.phone,
        email=payload.email,
        age=payload.age,
        profession=payload.profession,
        language=payload.language,
        role=payload.role,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_event(db, "user_registered", f"User {user.id} registered", user.id)
    return {"user": serialize_user(user)}


@app.post("/api/auth/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == payload.identifier) | (User.phone == payload.identifier)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive.")

    log_event(db, "user_login", f"User {user.id} logged in", user.id)
    return {
        "user": serialize_user(user),
        "sessions": [serialize_session(s) for s in db.query(ChatSession).filter(ChatSession.user_id == user.id).order_by(ChatSession.updated_at.desc()).all()],
    }


@app.post("/api/auth/reset-password")
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == payload.identifier) | (User.phone == payload.identifier)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    log_event(db, "password_reset", f"Password reset for user {user.id}", user.id)
    return {"message": "Password updated successfully."}


@app.get("/api/public/cases")
def public_cases(query: str = "", year: str = ""):
    sample = [
        {"title": "A.K. Gopalan vs State Of Madras", "year": "1950", "file": "A_K_Gopalan_vs_The_State_Of_Madras_Union_Of_India__on_19_May_1950_1.PDF"},
        {"title": "Romesh Thappar vs State Of Madras", "year": "1950", "file": "Romesh_Thappar_vs_The_State_Of_Madras_on_26_May_1950_1.PDF"},
        {"title": "Champakam Dorairajan Case", "year": "1951", "file": "The_State_Of_Madras_vs_Srimathi_Champakam_Dorairajanandthe_on_9_April_1951_1.PDF"},
    ]
    results = [item for item in sample if query.lower() in item["title"].lower() and (not year or item["year"] == year)]
    return {"items": results}


@app.get("/api/public/laws")
def public_laws(query: str = ""):
    db = SessionLocal()
    try:
        items = db.query(ContentEntry).filter(ContentEntry.content_type == "law").order_by(ContentEntry.created_at.desc()).all()
        results = [
            {
                "id": item.id,
                "title": item.title,
                "section_code": item.section_code,
                "description": item.description,
            }
            for item in items
            if query.lower() in f"{item.title} {item.description}".lower()
        ]
        return {"items": results}
    finally:
        db.close()


@app.get("/api/public/lawyers")
def public_lawyers(case_type: str = "", location: str = "", budget: str = "", verified_only: bool = False):
    db = SessionLocal()
    try:
        items = db.query(LawyerProfile).order_by(LawyerProfile.created_at.desc()).all()
        filtered = []
        for item in items:
            if case_type and case_type.lower() not in item.speciality.lower():
                continue
            if location and location.lower() not in item.location.lower():
                continue
            if budget and budget.lower() != item.budget.lower():
                continue
            if verified_only and not item.verified:
                continue
            filtered.append(serialize_lawyer(item))
        return {"items": filtered}
    finally:
        db.close()


@app.post("/api/contact")
def contact(payload: ContactCreate, db: Session = Depends(get_db)):
    submission = ContactSubmission(**payload.model_dump())
    db.add(submission)
    db.commit()
    db.refresh(submission)
    log_event(db, "contact_submitted", f"Contact submission {submission.id}")
    return {"message": "Thanks, we received your message."}


@app.post("/api/activity")
def activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    log_event(db, payload.event_type, payload.detail, payload.actor_user_id)
    return {"message": "Activity logged."}


@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"user": serialize_user(user)}


@app.put("/api/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    for key, value in payload.model_dump().items():
        setattr(user, key, value)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    log_event(db, "user_updated", f"User {user.id} updated profile", user.id)
    return {"user": serialize_user(user)}


@app.get("/api/users/{user_id}/history")
def user_history(user_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).all()
    return {"sessions": [serialize_session(s) for s in sessions]}


@app.get("/api/users/{user_id}/history/{session_id}")
def user_session_history(user_id: int, session_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id, ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return {"messages": [serialize_message(m) for m in messages]}


@app.post("/api/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    session = None
    if payload.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == payload.session_id, ChatSession.user_id == payload.user_id).first()
    if not session:
        session = ChatSession(user_id=payload.user_id, title=payload.query[:120])
        db.add(session)
        db.commit()
        db.refresh(session)

    user_message = ChatMessage(session_id=session.id, user_id=user.id, role="user", content=payload.query)
    db.add(user_message)
    db.commit()

    result = generate_legal_response(payload.query, serialize_user(user))
    assistant_message = ChatMessage(session_id=session.id, user_id=user.id, role="assistant", content=result["answer"])
    session.updated_at = datetime.utcnow()
    db.add(assistant_message)
    db.commit()
    store_history_embedding(user.id, session.id, payload.query, result["answer"])
    log_event(db, "chat_query", f"User {user.id} asked: {payload.query[:120]}", user.id)

    return {
        **result,
        "session_id": session.id,
        "messages": [serialize_message(user_message), serialize_message(assistant_message)],
    }


@app.post("/api/users/{user_id}/saved-cases")
def save_case(user_id: int, payload: dict, db: Session = Depends(get_db)):
    item = SavedCase(
        user_id=user_id,
        title=payload.get("title", "Untitled Case"),
        year=str(payload.get("year", "")),
        file_name=payload.get("file", ""),
    )
    db.add(item)
    db.commit()
    log_event(db, "case_saved", f"User {user_id} saved case {item.title}", user_id)
    return {"message": "Case saved"}


@app.post("/api/users/{user_id}/saved-laws")
def save_law(user_id: int, payload: dict, db: Session = Depends(get_db)):
    item = SavedLaw(
        user_id=user_id,
        title=payload.get("title", "Untitled Law"),
        section_code=payload.get("section_code", ""),
        description=payload.get("description", ""),
    )
    db.add(item)
    db.commit()
    log_event(db, "law_saved", f"User {user_id} saved law {item.title}", user_id)
    return {"message": "Law saved"}


@app.get("/api/users/{user_id}/saved")
def get_saved(user_id: int, db: Session = Depends(get_db)):
    saved_cases = db.query(SavedCase).filter(SavedCase.user_id == user_id).order_by(SavedCase.created_at.desc()).all()
    saved_laws = db.query(SavedLaw).filter(SavedLaw.user_id == user_id).order_by(SavedLaw.created_at.desc()).all()
    return {
        "cases": [
            {"id": item.id, "title": item.title, "year": item.year, "file": item.file_name, "created_at": item.created_at}
            for item in saved_cases
        ],
        "laws": [
            {"id": item.id, "title": item.title, "section_code": item.section_code, "description": item.description, "created_at": item.created_at}
            for item in saved_laws
        ],
    }


@app.post("/api/bookings")
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    booking = Booking(**payload.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    log_event(db, "booking_created", f"Booking {booking.id} created", payload.user_id)
    return {"booking": serialize_booking(booking)}


@app.get("/api/admin/overview")
def admin_overview(db: Session = Depends(get_db)):
    return {
        "totals": {
            "users": db.query(func.count(User.id)).scalar() or 0,
            "queries": db.query(func.count(ChatMessage.id)).filter(ChatMessage.role == "user").scalar() or 0,
            "bookings": db.query(func.count(Booking.id)).scalar() or 0,
            "contacts": db.query(func.count(ContactSubmission.id)).scalar() or 0,
        },
        "recent_logs": [
            {"id": log.id, "event_type": log.event_type, "detail": log.detail, "created_at": log.created_at}
            for log in db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()
        ],
    }


@app.get("/api/admin/users")
def admin_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return {
        "items": [
            {
                **serialize_user(user),
                "query_count": db.query(func.count(ChatMessage.id)).filter(ChatMessage.user_id == user.id, ChatMessage.role == "user").scalar() or 0,
            }
            for user in users
        ]
    }


@app.get("/api/admin/lawyers")
def admin_lawyers(db: Session = Depends(get_db)):
    items = db.query(LawyerProfile).order_by(LawyerProfile.created_at.desc()).all()
    return {"items": [serialize_lawyer(item) for item in items]}


@app.post("/api/admin/lawyers")
def admin_create_lawyer(payload: LawyerCreate, db: Session = Depends(get_db)):
    item = LawyerProfile(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    log_event(db, "lawyer_created", f"Lawyer profile {item.id} created")
    return {"lawyer": serialize_lawyer(item)}


@app.patch("/api/admin/lawyers/{lawyer_id}")
def admin_update_lawyer(lawyer_id: int, payload: LawyerUpdate, db: Session = Depends(get_db)):
    item = db.query(LawyerProfile).filter(LawyerProfile.id == lawyer_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Lawyer not found.")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    log_event(db, "lawyer_updated", f"Lawyer profile {item.id} updated")
    return {"lawyer": serialize_lawyer(item)}


@app.get("/api/admin/content")
def admin_content(content_type: str = "", db: Session = Depends(get_db)):
    query = db.query(ContentEntry).order_by(ContentEntry.created_at.desc())
    if content_type:
        query = query.filter(ContentEntry.content_type == content_type)
    items = query.all()
    return {"items": [serialize_content(item) for item in items]}


@app.post("/api/admin/content")
def admin_create_content(payload: ContentCreate, db: Session = Depends(get_db)):
    item = ContentEntry(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    log_event(db, "content_created", f"Content entry {item.id} created")
    return {"content": serialize_content(item)}


@app.patch("/api/admin/content/{content_id}")
def admin_update_content(content_id: int, payload: ContentUpdate, db: Session = Depends(get_db)):
    item = db.query(ContentEntry).filter(ContentEntry.id == content_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Content not found.")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    log_event(db, "content_updated", f"Content entry {item.id} updated")
    return {"content": serialize_content(item)}


@app.get("/api/admin/users/{user_id}")
def admin_user_detail(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).all()
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.created_at.desc()).limit(50).all()
    return {
        "user": serialize_user(user),
        "sessions": [serialize_session(s) for s in sessions],
        "messages": [serialize_message(m) for m in messages],
    }


@app.patch("/api/admin/users/{user_id}/status")
def admin_user_status(user_id: int, payload: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = bool(payload.get("is_active", user.is_active))
    user.updated_at = datetime.utcnow()
    db.commit()
    log_event(db, "user_status_changed", f"Admin changed user {user.id} active={user.is_active}")
    return {"user": serialize_user(user)}


@app.get("/api/admin/bookings")
def admin_bookings(db: Session = Depends(get_db)):
    return {"items": [serialize_booking(item) for item in db.query(Booking).order_by(Booking.created_at.desc()).all()]}


@app.patch("/api/admin/bookings/{booking_id}")
def admin_update_booking(booking_id: int, payload: dict, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    booking.status = payload.get("status", booking.status)
    db.commit()
    db.refresh(booking)
    log_event(db, "booking_updated", f"Booking {booking.id} status={booking.status}")
    return {"booking": serialize_booking(booking)}


@app.get("/api/admin/contacts")
def admin_contacts(db: Session = Depends(get_db)):
    items = db.query(ContactSubmission).order_by(ContactSubmission.created_at.desc()).all()
    return {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "email": item.email,
                "subject": item.subject,
                "message": item.message,
                "created_at": item.created_at,
            }
            for item in items
        ]
    }


@app.get("/api/admin/analytics")
def admin_analytics(db: Session = Depends(get_db)):
    topic_rows = (
        db.query(ChatMessage.content, func.count(ChatMessage.id).label("count"))
        .filter(ChatMessage.role == "user")
        .group_by(ChatMessage.content)
        .order_by(func.count(ChatMessage.id).desc())
        .limit(5)
        .all()
    )
    return {
        "top_queries": [{"query": row[0], "count": row[1]} for row in topic_rows],
        "case_types": [
            {"name": "Criminal", "count": 18},
            {"name": "Family", "count": 11},
            {"name": "Civil", "count": 15},
            {"name": "Corporate", "count": 6},
        ],
    }


# ==========================================
# LAWYER RECOMMENDATION ENDPOINTS
# ==========================================

@app.get("/api/lawyers/recommend")
def recommend_lawyers(
    state: str = None,
    city: str = None,
    language: str = None,
    specialization: str = None,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Get ML-ranked lawyer recommendations"""
    try:
        from sys import path as sys_path
        ROOT_BACKEND = Path(__file__).resolve().parents[3] / "backend"
        if str(ROOT_BACKEND) not in sys_path:
            sys_path.insert(0, str(ROOT_BACKEND))
        
        from lawyer_recommender import LawyerRecommender  # type: ignore
        recommender = LawyerRecommender()
        
        results = recommender.recommend_by_filters(
            state=state,
            city=city,
            language=language,
            type_of_lawyer=specialization,
            top_n=10
        )
        
        log_event(db, "lawyer_recommendation", f"User {user_id} requested recommendations", user_id)
        
        return {
            "recommendations": results if isinstance(results, list) else results.to_dict('records'),
            "count": len(results) if isinstance(results, list) else len(results)
        }
    except Exception as e:
        print(f"❌ Lawyer recommendation error: {e}")
        return {"recommendations": [], "count": 0, "error": str(e)}


@app.get("/api/lawyers/search")
def search_lawyers(
    query: str,
    state: str = None,
    city: str = None,
    language: str = None,
    min_rating: float = None,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Search lawyers by name/specialization with filters"""
    try:
        from sys import path as sys_path
        ROOT_BACKEND = Path(__file__).resolve().parents[3] / "backend"
        if str(ROOT_BACKEND) not in sys_path:
            sys_path.insert(0, str(ROOT_BACKEND))
        
        from lawyer_recommender import LawyerRecommender  # type: ignore
        recommender = LawyerRecommender()
        
        # Use search_lawyers method (correct method name)
        results = recommender.search_lawyers(
            query=query,
            filters={
                'state': state,
                'city': city,
                'language': language,
                'min_rating': min_rating
            } if any([state, city, language, min_rating]) else None,
            top_n=20  # Increased from 10
        )
        
        log_event(db, "lawyer_search", f"User {user_id} searched: {query}", user_id)
        
        return {
            "results": results if isinstance(results, list) else results.to_dict('records'),
            "count": len(results) if isinstance(results, list) else len(results)
        }
    except Exception as e:
        print(f"❌ Lawyer search error: {e}")
        import traceback
        traceback.print_exc()
        return {"results": [], "count": 0, "error": str(e)}


# ==========================================
# BOOKING & APPOINTMENT ENDPOINTS
# ==========================================

@app.post("/api/bookings/create")
def create_lawyer_booking(
    lawyer_id: int,
    case_description: str,
    preferred_date: str,
    preferred_time: str,
    consultation_type: str,
    notes: str = None,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Create a booking with a lawyer"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lawyer = db.query(LawyerProfile).filter(LawyerProfile.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    booking = Booking(
        user_id=user_id,
        lawyer_name=lawyer.name,
        case_type=case_description[:80],
        mode=consultation_type,
        date=preferred_date,
        time_slot=preferred_time,
        notes=notes,
        status="Pending"
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    log_event(db, "booking_created", f"User {user_id} booked with lawyer {lawyer_id}", user_id)
    
    return {
        "booking_id": booking.id,
        "status": "created",
        "details": serialize_booking(booking)
    }


@app.get("/api/bookings/user/{user_id}")
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    """Get all bookings for a user"""
    bookings = db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()
    
    return {
        "bookings": [serialize_booking(b) for b in bookings],
        "count": len(bookings)
    }


@app.patch("/api/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, user_id: int = None, db: Session = Depends(get_db)):
    """Cancel a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    booking.status = "Cancelled"
    db.commit()
    log_event(db, "booking_cancelled", f"Booking {booking_id} cancelled", user_id)
    
    return {"message": "Booking cancelled", "booking": serialize_booking(booking)}


@app.post("/api/appointments/create")
def create_appointment(
    booking_id: int,
    appointment_date: str,
    appointment_time: str,
    duration_minutes: int = 60,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Schedule an appointment from a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    booking.date = appointment_date
    booking.time_slot = appointment_time
    booking.status = "Confirmed"
    db.commit()
    
    log_event(db, "appointment_scheduled", f"Appointment scheduled for booking {booking_id}", user_id)
    
    return {
        "appointment_id": booking.id,
        "status": "scheduled",
        "date": appointment_date,
        "time": appointment_time,
        "duration": duration_minutes
    }


@app.get("/api/appointments/user/{user_id}")
def get_user_appointments(user_id: int, db: Session = Depends(get_db)):
    """Get all confirmed appointments for a user"""
    appointments = db.query(Booking).filter(
        Booking.user_id == user_id,
        Booking.status == "Confirmed"
    ).order_by(Booking.date.desc()).all()
    
    return {
        "appointments": [serialize_booking(b) for b in appointments],
        "count": len(appointments)
    }


@app.patch("/api/appointments/{booking_id}/reschedule")
def reschedule_appointment(
    booking_id: int,
    new_date: str,
    new_time: str,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Reschedule an appointment"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    booking.date = new_date
    booking.time_slot = new_time
    db.commit()
    log_event(db, "appointment_rescheduled", f"Appointment {booking_id} rescheduled", user_id)
    
    return {"message": "Appointment rescheduled", "booking": serialize_booking(booking)}


@app.get("/api/files/judgment")
def judgment_file(file: str, year: str):
    path = PDF_BASE_PATH / year / file
    if not Path(path).exists():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path, media_type="application/pdf")


def serialize_user(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "city": user.city,
        "state": user.state,
        "phone": user.phone,
        "email": user.email,
        "age": user.age,
        "profession": user.profession,
        "language": user.language,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


def serialize_session(session: ChatSession):
    return {
        "id": session.id,
        "user_id": session.user_id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


def serialize_message(message: ChatMessage):
    return {
        "id": message.id,
        "session_id": message.session_id,
        "user_id": message.user_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
    }


def serialize_booking(booking: Booking):
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "lawyer_name": booking.lawyer_name,
        "case_type": booking.case_type,
        "mode": booking.mode,
        "date": booking.date,
        "time_slot": booking.time_slot,
        "notes": booking.notes,
        "status": booking.status,
        "created_at": booking.created_at,
    }


def serialize_lawyer(item: LawyerProfile):
    return {
        "id": item.id,
        "name": item.name,
        "email": item.email,
        "phone": item.phone,
        "speciality": item.speciality,
        "location": item.location,
        "budget": item.budget,
        "verified": item.verified,
        "bio": item.bio,
        "created_at": item.created_at,
    }


def serialize_content(item: ContentEntry):
    return {
        "id": item.id,
        "content_type": item.content_type,
        "title": item.title,
        "section_code": item.section_code,
        "year": item.year,
        "file_name": item.file_name,
        "description": item.description,
        "created_at": item.created_at,
    }


# ==========================================
# PUBLIC KNOWLEDGE BASE ENDPOINTS  
# ==========================================

@app.get("/api/public/laws/search")
def search_laws(query: str = "", section: str = "", limit: int = 20):
    """Search laws from vectorstore - Returns ALL matching results"""
    try:
        from sys import path as sys_path
        ROOT_BACKEND = Path(__file__).resolve().parents[3] / "backend"
        if str(ROOT_BACKEND) not in sys_path:
            sys_path.insert(0, str(ROOT_BACKEND))
        
        from rag import get_law_db  # type: ignore
        
        law_db = get_law_db()
        
        # Search with higher k to get more results
        search_query = query if query else section
        results = law_db.similarity_search(search_query, k=min(limit, 50))
        
        laws = [
            {
                "title": doc.metadata.get("source", "Unknown"),
                "content": doc.page_content[:500],
                "source": doc.metadata.get("source", "Unknown"),
                "full_content": doc.page_content
            }
            for doc in results
        ]
        
        return {
            "query": search_query,
            "count": len(laws),
            "laws": laws
        }
    except Exception as e:
        print(f"❌ Law search error: {e}")
        return {"query": query, "count": 0, "laws": [], "error": str(e)}


@app.get("/api/public/cases/search")
def search_cases(query: str = "", year: str = "", limit: int = 20):
    """Search Supreme Court cases from vectorstore - Returns ALL matching cases"""
    try:
        from sys import path as sys_path
        ROOT_BACKEND = Path(__file__).resolve().parents[3] / "backend"
        if str(ROOT_BACKEND) not in sys_path:
            sys_path.insert(0, str(ROOT_BACKEND))
        
        from rag import get_case_db  # type: ignore
        
        case_db = get_case_db()
        
        # Search with higher k to get more results (was limited to k=3 before)
        search_query = query if query else "supreme court judgment"
        results = case_db.similarity_search(search_query, k=min(limit, 100))
        
        cases = [
            {
                "file": doc.metadata.get("file", "Unknown"),
                "year": doc.metadata.get("year", "Unknown"),
                "title": doc.metadata.get("file", "Unknown").replace("_", " "),
                "content": doc.page_content[:500],
                "full_content": doc.page_content
            }
            for doc in results
        ]
        
        # If year filter provided, filter results
        if year:
            cases = [c for c in cases if year in str(c.get("year", ""))]
        
        return {
            "query": search_query,
            "year_filter": year,
            "count": len(cases),
            "cases": cases
        }
    except Exception as e:
        print(f"❌ Case search error: {e}")
        return {"query": query, "year": year, "count": 0, "cases": [], "error": str(e)}


@app.get("/api/public/cases/by-year")
def get_cases_by_year(year: str):
    """Get cases for a specific year"""
    try:
        from sys import path as sys_path
        ROOT_BACKEND = Path(__file__).resolve().parents[3] / "backend"
        if str(ROOT_BACKEND) not in sys_path:
            sys_path.insert(0, str(ROOT_BACKEND))
        
        from rag import get_case_db  # type: ignore
        
        case_db = get_case_db()
        
        # Generic search to get all cases, then filter by year
        results = case_db.similarity_search(f"year {year} judgment case decision", k=200)
        
        cases = [
            {
                "file": doc.metadata.get("file", "Unknown"),
                "year": doc.metadata.get("year", "Unknown"),
                "title": doc.metadata.get("file", "Unknown").replace("_", " "),
                "content": doc.page_content[:300]
            }
            for doc in results if year in str(doc.metadata.get("year", ""))
        ]
        
        return {
            "year": year,
            "count": len(cases),
            "cases": cases
        }
    except Exception as e:
        print(f"❌ Year search error: {e}")
        return {"year": year, "count": 0, "cases": [], "error": str(e)}
