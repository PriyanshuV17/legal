import os
import pandas as pd

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

BASE_PATH = r"D:\legal\data\raw"
DB_PATH = r"D:\legal\vectorstore\laws_db"


def load_all_files():
    documents = []

    for file in os.listdir(BASE_PATH):
        file_path = os.path.join(BASE_PATH, file)

        # CSV
        if file.endswith(".csv"):
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except:
                try:
                    df = pd.read_csv(file_path, encoding="latin-1")
                except:
                    df = pd.read_csv(file_path, encoding="cp1252")
            for _, row in df.iterrows():
                text = " ".join([str(v) for v in row.values if pd.notna(v)])

                if len(text) < 50:
                    continue

                documents.append(Document(
                    page_content=text,
                    metadata={"source": file}
                ))

        # TXT
        elif file.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

                documents.append(Document(
                    page_content=text,
                    metadata={"source": file}
                ))

        # PDF
        elif file.endswith(".pdf"):
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()

                for doc in docs:
                    doc.metadata["source"] = file

                documents.extend(docs)

            except Exception as e:
                print(f"❌ Error reading {file}: {e}")

    return documents


def ingest():
    print("📥 Loading ALL law files...")

    docs = load_all_files()
    print(f"📄 Total raw docs: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80
    )

    split_docs = splitter.split_documents(docs)
    print(f"🔹 Total chunks: {len(split_docs)}")

    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        split_docs,
        embedding,
        persist_directory=DB_PATH
    )

    db.persist()

    print("✅ LAW DATABASE REBUILT")


if __name__ == "__main__":
    ingest()