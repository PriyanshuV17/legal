def classify_case(text: str):
    text = text.lower()

    categories = {
        "Criminal": ["murder", "theft", "rape", "assault", "fraud", "kill", "attack"],
        "Family": ["divorce", "marriage", "custody", "domestic violence", "alimony"],
        "Civil": ["property", "contract", "agreement", "dispute", "money"],
        "Corporate": ["company", "share", "business", "startup"],
        "Revenue": ["land", "tax", "revenue", "property tax"]
    }

    detected = []

    for category, keywords in categories.items():
        for word in keywords:
            if word in text:
                detected.append(category)
                break

    if not detected:
        detected.append("General Legal Advice")

    return list(set(detected))


def recommend_lawyer(case_types):
    mapping = {
        "Criminal": "Criminal Lawyer",
        "Family": "Family Lawyer",
        "Civil": "Civil Lawyer",
        "Corporate": "Corporate Lawyer",
        "Revenue": "Revenue Lawyer",
        "General Legal Advice": "General Practice Lawyer"
    }

    return list(set([mapping[c] for c in case_types]))