from pathlib import Path
import os

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "legalbuddy_webapp.db"
PDF_BASE_PATH = DATA_DIR / "supreme_court_judgments"

CONTACT_NAME = "Priyanshu Verma"
CONTACT_EMAIL = "priyasnhu.22190503040@cuj.ac.in"
CONTACT_PHONE = "7376021218"
SIGNATURE = "Priyanshu.Verma17"

DEFAULT_ADMIN_EMAIL = CONTACT_EMAIL
DEFAULT_ADMIN_PASSWORD = os.getenv("LEGALBUDDY_ADMIN_PASSWORD", "verma123")
