from llm import get_llm


llm = get_llm()


def extract_case_info(text):
    prompt = f"""
Extract structured legal information from this judgment.

Return ONLY in this format:

Outcome: <one line>
Sections: <comma separated>
Reasoning: <short summary>

Judgment:
{text[:2000]}
"""

    try:
        response = llm.invoke(prompt)

        return parse_response(response)

    except:
        return None


def parse_response(response):
    result = {
        "outcome": "Unknown",
        "sections": [],
        "reasoning": ""
    }

    lines = response.split("\n")

    for line in lines:
        if line.lower().startswith("outcome"):
            result["outcome"] = line.split(":", 1)[-1].strip()

        elif line.lower().startswith("sections"):
            sections = line.split(":", 1)[-1]
            result["sections"] = [s.strip() for s in sections.split(",")]

        elif line.lower().startswith("reasoning"):
            result["reasoning"] = line.split(":", 1)[-1].strip()

    return result