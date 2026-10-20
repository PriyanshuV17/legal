from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

ROOT_BACKEND = Path(__file__).resolve().parents[3] / "backend"
if str(ROOT_BACKEND) not in sys.path:
    sys.path.append(str(ROOT_BACKEND))

# Lazy imports to avoid blocking startup
_llm_module = None
_rag_module = None
_recommender_module = None

def get_llm():
    """Lazy load LLM module"""
    global _llm_module
    if _llm_module is None:
        from llm import get_llm as _get_llm  # type: ignore
        _llm_module = _get_llm
    return _llm_module()

def get_case_db():
    """Lazy load case DB"""
    global _rag_module
    if _rag_module is None:
        from rag import get_case_db as _get_case_db  # type: ignore
        _rag_module = _get_case_db
    return _rag_module()

def get_law_db():
    """Lazy load law DB"""
    global _rag_module
    if _rag_module is None:
        from rag import get_law_db as _get_law_db  # type: ignore
        _rag_module = _get_law_db
    return _rag_module()

def get_history_db():
    """Lazy load history DB"""
    global _rag_module
    if _rag_module is None:
        from rag import get_history_db as _get_history_db  # type: ignore
        _rag_module = _get_history_db
    return _rag_module()

def classify_case(query: str):
    """Lazy load classifier"""
    global _recommender_module
    if _recommender_module is None:
        from recommender import classify_case as _classify_case  # type: ignore
        _recommender_module = _classify_case
    return _recommender_module(query)

def recommend_lawyer(case_types):
    """Lazy load recommender"""
    global _recommender_module
    if _recommender_module is None:
        from recommender import recommend_lawyer as _recommend_lawyer  # type: ignore
        _recommender_module = _recommend_lawyer
    return _recommender_module(case_types)


def get_fallback_response(query: str, law_context: str, case_context: str) -> str:
    """Return a fallback response when LLM is unavailable."""
    return f"""I'm currently unable to generate a detailed legal response due to a service issue.

However, based on your query about "{query[:100]}...", here are relevant resources:

**Applicable Laws & Precedents:**
{law_context[:300] if law_context else "No specific laws found for your query."}

**Related Case References:**
{case_context[:300] if case_context else "No related cases found."}

**Recommendation:**
Please try again in a moment or consult with a qualified legal professional for immediate assistance.
"""


def generate_legal_response(query: str, user: dict):
    law_db = get_law_db()
    case_db = get_case_db()
    llm = get_llm()

    user_state = user.get('state', '').lower()
    user_language = user.get('language', 'English').lower()
    user_city = user.get('city', '').lower()
    user_profession = str(user.get('profession', 'Need Legal Help')).lower()  # Convert to string and lowercase
    user_name = user.get('name', 'User')
    user_age = user.get('age', 25)
    user_gender = user.get('gender', 'Not specified')

    # FIXED: Increased k values from 2,3 to 10,15 to get more results
    # This ensures we show all relevant laws and cases, not just 2-3
    law_docs = law_db.similarity_search(query, k=10)
    case_docs = case_db.similarity_search(query, k=15)

    law_context = "\n\n".join([doc.page_content[:500] for doc in law_docs]) if law_docs else "No relevant laws found"
    case_context = "\n\n".join([doc.page_content[:500] for doc in case_docs]) if case_docs else "No relevant cases found"

    if llm is None:
        logger.warning("LLM service unavailable, using fallback response")
        answer = get_fallback_response(query, law_context, case_context)
    else:
        try:
            if "student" in user_profession or "learner" in user_profession:
                prompt = f"""
You are an expert legal teacher explaining complex legal concepts in simple terms.

Student Profile:
- Name: {user_name}, Age: {user_age}
- Location: {user_city}, {user_state}
- Language: {user_language}

Guidelines:
- Use simple, easy-to-understand language
- Avoid complex legal jargon
- Include a real-world example or scenario
- Reference relevant law sections

RELEVANT LAWS & PRECEDENTS:
{law_context}

RELATED CASES:
{case_context}

STUDENT'S QUESTION:
{query}

Please provide a clear, educational explanation:
"""
            elif "lawyer" in user_profession:
                prompt = f"""
You are a senior legal counsel providing expert analysis.

Lawyer Details:
- Name: {user_name}
- Location: {user_city}, {user_state}
- Language: {user_language}

Provide comprehensive legal analysis including:
- Applicable law sections with interpretations
- Relevant case law and precedents (especially from {user_state})
- Legal arguments and counterarguments
- Procedural implications and strategy

APPLICABLE LAWS:
{law_context}

RELEVANT PRECEDENTS:
{case_context}

LEGAL QUERY:
{query}

Provide detailed professional analysis:
"""
            else:
                # Default: General citizen seeking legal help
                prompt = f"""
You are a professional Indian legal advisor helping a citizen understand their legal situation.

Client Profile:
- Name: {user_name}, Age: {user_age}, Gender: {user_gender}
- Location: {user_city}, {user_state}
- Language: {user_language}

Provide clear, practical guidance including:
1. **What Happened** - Summarize the situation briefly
2. **Legal Position** - Relevant laws and your legal rights
3. **Risks & Consequences** - What could happen if not addressed
4. **Action Steps** - Concrete steps to take immediately
5. **Important Advice** - Critical points to know

Prefer using precedents from {user_state} when available.

RELEVANT LAWS & SECTIONS:
{law_context}

SIMILAR CASES & JUDGMENTS:
{case_context}

CLIENT'S SITUATION:
{query}

Please provide practical legal guidance:
"""
            answer = llm.invoke(prompt).strip()
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            answer = get_fallback_response(query, law_context, case_context)
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
        "personalization": {
            "location": f"{user_city}, {user_state}",
            "language": user_language,
            "user_type": user_profession,
            "name": user_name,
            "age": user_age,
            "gender": user_gender
        }
    }


def store_history_embedding(user_id: int, session_id: int, query: str, answer: str):
    """Store user query and response in history vectorstore"""
    try:
        history_db = get_history_db()
        history_db.add_texts(
            texts=[f"User question: {query}\nAssistant answer: {answer}"],
            metadatas=[{"user_id": user_id, "session_id": session_id, "query": query[:500]}],
        )
        logger.info(f"History stored for user {user_id}, session {session_id}")
    except Exception as e:
        logger.error(f"Failed to store history: {e}")
