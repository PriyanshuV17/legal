import os
import json
import torch

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# =========================
# PATHS
# =========================
BASE_PATH = r"D:\legal\data\supreme_court_judgments"
DB_PATH = r"D:\legal\vectorstore\cases_db"
PROGRESS_FILE = r"D:\legal\backend\processed_years.json"


# =========================
# GPU / CPU DETECTION
# =========================
def get_device():
    if torch.cuda.is_available():
        print("🚀 Using GPU")
        return "cuda"
    else:
        print("💻 Using CPU")
        return "cpu"


# =========================
# LOAD PROCESSED YEARS
# =========================
def load_processed_years():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_processed_year(years_set):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(list(years_set), f)


# =========================
# LOAD PDFs FOR ONE YEAR
# =========================
def load_year(year):
    documents = []
    year_path = os.path.join(BASE_PATH, str(year))

    if not os.path.exists(year_path):
        print(f"⚠️ Year {year} not found")
        return documents

    print(f"\n📂 Processing Year: {year}")

    files = [f for f in os.listdir(year_path) if f.lower().endswith(".pdf")]
    print(f"📄 PDFs found: {len(files)}")

    for i, file in enumerate(files):
        file_path = os.path.join(year_path, file)

        print(f"➡️ [{i+1}/{len(files)}] {file}")

        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            if not docs:
                continue

            for doc in docs:
                doc.metadata["year"] = year
                doc.metadata["source"] = "supreme_court"
                doc.metadata["file"] = file

            documents.extend(docs)

        except Exception:
            print(f"❌ Failed: {file}")

    print(f"✅ Loaded pages from {year}: {len(documents)}")
    return documents


# =========================
# INGEST YEAR WITH BATCHING
# =========================
def ingest_year(year, db, splitter, processed_years):
    if str(year) in processed_years:
        print(f"⏭ Skipping {year} (already processed)")
        return

    docs = load_year(year)

    if not docs:
        return

    split_docs = splitter.split_documents(docs)
    print(f"🔹 Chunks for {year}: {len(split_docs)}")

    batch_size = 5000

    for i in range(0, len(split_docs), batch_size):
        batch = split_docs[i:i + batch_size]

        print(f"➡️ Inserting batch {i // batch_size + 1}")
        db.add_documents(batch)

    print(f"✅ Added year {year} to DB")

    # 🔥 mark as processed
    processed_years.add(str(year))
    save_processed_year(processed_years)


# =========================
# MAIN PIPELINE
# =========================
def main():
    device = get_device()

    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": device}
    )

    # Load existing DB or create new
    if os.path.exists(DB_PATH):
        db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)
        print("📦 Existing DB loaded")
    else:
        db = Chroma(persist_directory=DB_PATH, embedding_function=embedding)
        print("🆕 New DB created")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )

    processed_years = load_processed_years()
    print(f"📁 Already processed years: {processed_years}")

    # Process from latest → oldest
    for year in range(2025, 1949, -1):
        ingest_year(year, db, splitter, processed_years)

    print("\n🎉 ALL YEARS PROCESSED")


if __name__ == "__main__":
    main()