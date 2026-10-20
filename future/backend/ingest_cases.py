import os
from multiprocessing import Pool, cpu_count

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_PATH = r"D:\legal\data\supreme_court_judgments"
DB_PATH = r"D:\legal\vectorstore\cases_db"


def process_pdf(file_path):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        for doc in docs:
            doc.metadata["source"] = "supreme_court"
            doc.metadata["file"] = os.path.basename(file_path)

        return docs

    except:
        return []


def collect_all_pdfs():
    pdf_files = []

    for root, dirs, files in os.walk(BASE_PATH):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    return pdf_files


def ingest():
    print("📥 Collecting PDFs...")

    pdf_files = collect_all_pdfs()
    print(f"📄 Total PDFs: {len(pdf_files)}")

    # LOAD ALL CASES (27000+)
    # pdf_files = pdf_files[:200]  # REMOVED - now loading all

    print("⚡ Using multiprocessing...")

    with Pool(cpu_count()) as p:
        results = p.map(process_pdf, pdf_files)

    docs = [doc for sublist in results for doc in sublist]

    print(f"📄 Loaded pages: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )

    split_docs = splitter.split_documents(docs)
    print(f"🔹 Chunks: {len(split_docs)}")

    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        split_docs,
        embedding,
        persist_directory=DB_PATH
    )

    print("✅ CASE DATABASE READY")


if __name__ == "__main__":
    ingest()