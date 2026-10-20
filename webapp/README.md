# LegalBuddy WebApp

This folder contains the production-oriented scaffold for the next phase of LegalBuddy:

- `backend/` -> FastAPI + SQLAlchemy + SQLite + audit logging + admin APIs
- `frontend/` -> React + Vite multi-page product UI

## Theme

- Dark base for a professional feel
- Orange accent for energy
- Soft contrast for friendliness
- Smooth card-based modern AI layout

## Run Plan

### Backend

```bash
cd D:\legal\webapp\backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd D:\legal\webapp\frontend
npm install
npm run dev
```

### Backup Streamlit

```bash
cd D:\legal\streamlit_backup
streamlit run app.py
```
