from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

LAW_DB_PATH = r"D:\legal\vectorstore\laws_db"
CASE_DB_PATH = r"D:\legal\vectorstore\cases_db"
HISTORY_DB_PATH = r"D:\legal\vectorstore\history_db"


def get_embedding():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )


# =========================
# LAW DATABASE
# =========================
def get_law_db():
    return Chroma(
        persist_directory=LAW_DB_PATH,
        embedding_function=get_embedding()
    )


# =========================
# CASE DATABASE
# =========================
def get_case_db():
    return Chroma(
        persist_directory=CASE_DB_PATH,
        embedding_function=get_embedding()
    )


def get_history_db():
    return Chroma(
        collection_name="user_history",
        persist_directory=HISTORY_DB_PATH,
        embedding_function=get_embedding()
    )
