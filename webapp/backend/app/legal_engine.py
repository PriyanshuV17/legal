from pathlib import Path
import sys


ROOT_BACKEND = Path(__file__).resolve().parents[3] / "backend"
if str(ROOT_BACKEND) not in sys.path:
    sys.path.append(str(ROOT_BACKEND))

from llm import get_llm  # type: ignore
from rag import get_case_db, get_law_db, get_history_db  # type: ignore
from recommender import classify_case, recommend_lawyer  # type: ignore


def generate_legal_response(query: str, user: dict):
    law_db = get_law_db()
    case_db = get_case_db()
    llm = get_llm()

    law_docs = law_db.similarity_search(query, k=2)
    case_docs = case_db.similarity_search(query, k=3)

    law_context = "\n\n".join([doc.page_content[:500] for doc in law_docs])
    case_context = "\n\n".join([doc.page_content[:500] for doc in case_docs])

    profession = user.get("profession", "Need Legal Help")
    if profession == "Student / Learner":
        prompt = f"""
You are a legal teacher.
Explain in simple terms.
- Easy explanation
- Relevant law sections
- Example

LAW CONTEXT:
{law_context}

QUESTION:
{query}
"""
    elif profession == "Lawyer":
        prompt = f"""
You are a legal research assistant.
- Relevant sections
- Interpretation
- Case references
- Argument direction

LAW CONTEXT:
{law_context}

CASE CONTEXT:
{case_context}

QUERY:
{query}
"""
    else:
        prompt = f"""
You are a professional Indian legal advisor.
User location: {user.get('city')}, {user.get('state')}
Age: {user.get('age')}

Structure:
- What Happened
- Legal Position
- Risk / Consequences
- What You Should Do
- Important Advice

LAW CONTEXT:
{law_context}

CASE CONTEXT:
{case_context}

USER QUERY:
{query}
"""

    answer = llm.invoke(prompt).strip()
    case_types = classify_case(query)
    lawyers = recommend_lawyer(case_types)
    case_insights = [
        {
            "file": doc.metadata.get("file", "Unknown"),
            "year": str(doc.metadata.get("year", "Unknown")),
            "title": doc.metadata.get("file", "Unknown").replace("_", " "),
        }
        for doc in case_docs
    ]

    return {
        "answer": answer,
        "case_type": case_types,
        "recommended_lawyers": lawyers,
        "case_insights": case_insights,
    }


def store_history_embedding(user_id: int, session_id: int, query: str, answer: str):
    history_db = get_history_db()
    history_db.add_texts(
        texts=[f"User question: {query}\nAssistant answer: {answer}"],
        metadatas=[{"user_id": user_id, "session_id": session_id, "query": query[:500]}],
    )
