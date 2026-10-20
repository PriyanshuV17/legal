import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_PATH = r"D:\legal\data\supreme_court_judgments"
DB_PATH = r"D:\legal\vectorstore\cases_db"


def load_pdfs():
    documents = []

    for year in os.listdir(BASE_PATH):
        year_path = os.path.join(BASE_PATH, year)

        if not os.path.isdir(year_path):
            continue

        print(f"📂 Processing year: {year}")

        for file in os.listdir(year_path):
            if file.endswith(".pdf"):
                file_path = os.path.join(year_path, file)

                try:
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()

                    for doc in docs:
                        doc.metadata["year"] = year
                        doc.metadata["source"] = "supreme_court"

                    documents.extend(docs)

                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")

    return documents


def ingest():
    print("📥 Loading Supreme Court PDFs...")

    docs = load_pdfs()
    print(f"📄 Total documents: {len(docs)}")

    print("✂️ Chunking...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    split_docs = splitter.split_documents(docs)
    print(f"🔹 Total chunks: {len(split_docs)}")

    print("🧠 Creating embeddings...")

    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        split_docs,
        embedding,
        persist_directory=DB_PATH
    )

    db.persist()

    print("✅ CASE DATABASE READY")


if __name__ == "__main__":
    ingest()