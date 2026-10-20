from sqlalchemy.orm import Session

from .config import CONTACT_EMAIL, CONTACT_NAME, CONTACT_PHONE, DEFAULT_ADMIN_PASSWORD
from .models import ContentEntry, LawyerProfile, User
from .security import hash_password


def create_default_admin(db: Session):
    admin = db.query(User).filter(User.role == "admin").first()
    if admin:
        return admin

    admin = User(
        name=CONTACT_NAME,
        city="Ranchi",
        state="Jharkhand",
        phone=CONTACT_PHONE,
        email=CONTACT_EMAIL,
        age=24,
        profession="Platform Admin",
        language="English",
        role="admin",
        password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def seed_reference_data(db: Session):
    if not db.query(LawyerProfile).first():
        db.add_all(
            [
                LawyerProfile(
                    name="Aarav Mehta",
                    email="aarav.mehta@legalbuddy.ai",
                    phone="9000000001",
                    speciality="Criminal Lawyer",
                    location="Delhi",
                    budget="Premium",
                    verified=True,
                    bio="Trial strategy and criminal defence specialist.",
                ),
                LawyerProfile(
                    name="Riya Sinha",
                    email="riya.sinha@legalbuddy.ai",
                    phone="9000000002",
                    speciality="Family Lawyer",
                    location="Ranchi",
                    budget="Moderate",
                    verified=True,
                    bio="Family settlements, maintenance, custody, and mediation.",
                ),
                LawyerProfile(
                    name="Kabir Anand",
                    email="kabir.anand@legalbuddy.ai",
                    phone="9000000003",
                    speciality="Corporate Lawyer",
                    location="Bengaluru",
                    budget="Premium",
                    verified=False,
                    bio="Commercial contracts and founder advisory.",
                ),
            ]
        )

    if not db.query(ContentEntry).first():
        db.add_all(
            [
                ContentEntry(
                    content_type="law",
                    title="IPC Section 420",
                    section_code="IPC 420",
                    description="Cheating and dishonestly inducing delivery of property.",
                ),
                ContentEntry(
                    content_type="law",
                    title="Constitution Article 21",
                    section_code="Art. 21",
                    description="Protection of life and personal liberty.",
                ),
                ContentEntry(
                    content_type="case",
                    title="A.K. Gopalan vs State Of Madras",
                    year="1950",
                    file_name="A_K_Gopalan_vs_The_State_Of_Madras_Union_Of_India__on_19_May_1950_1.PDF",
                    description="Landmark preventive detention and personal liberty case.",
                ),
            ]
        )

    db.commit()
