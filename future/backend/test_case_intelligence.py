from rag import get_case_db
from case_extractor import extract_outcome, extract_sections, extract_reasoning

db = get_case_db()

query = "murder self defense case"

docs = db.similarity_search(query, k=3)

for i, doc in enumerate(docs):
    print(f"\n🔹 CASE {i+1}")

    text = doc.page_content

    outcome = extract_outcome(text)
    sections = extract_sections(text)
    reasoning = extract_reasoning(text)

    print(f"Outcome: {outcome}")
    print(f"Sections: {sections}")
    print(f"Reasoning: {reasoning[:200]}")