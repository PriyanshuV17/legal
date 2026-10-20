import re


# =========================
# OUTCOME EXTRACTION (IMPROVED)
# =========================
def extract_outcome(text):
    text = text.lower()

    # focus on last part (decision usually there)
    last_part = text[-6000:]

    # -------------------------
    # BAIL
    # -------------------------
    if any(x in last_part for x in [
        "bail is granted", "granted bail", "released on bail"
    ]):
        return "Bail Granted"

    if any(x in last_part for x in [
        "bail is rejected", "bail denied", "application for bail rejected"
    ]):
        return "Bail Rejected"

    # -------------------------
    # CRIMINAL OUTCOME
    # -------------------------
    if "acquitted" in last_part:
        return "Acquitted"

    if "convicted" in last_part:
        return "Convicted"

    # -------------------------
    # SENTENCING
    # -------------------------
    if "death sentence" in last_part:
        return "Death Sentence"

    if "life imprisonment" in last_part:
        return "Life Imprisonment"

    match = re.search(r'(\d+)\s+years?\s+imprisonment', last_part)
    if match:
        return f"{match.group(1)} Years Imprisonment"

    # -------------------------
    # APPEAL
    # -------------------------
    if any(x in last_part for x in [
        "appeal is allowed", "appeal allowed", "petition allowed"
    ]):
        return "Appeal Allowed"

    if any(x in last_part for x in [
        "appeal is dismissed", "appeal dismissed", "petition dismissed"
    ]):
        return "Appeal Dismissed"

    if any(x in last_part for x in [
        "partly allowed", "partially allowed"
    ]):
        return "Partially Allowed"

    # -------------------------
    # FINANCIAL
    # -------------------------
    if any(x in last_part for x in [
        "fine of", "penalty", "compensation"
    ]):
        return "Financial Penalty"

    return "Unknown"


# =========================
# SECTION EXTRACTION (IMPROVED)
# =========================
def extract_sections(text):
    text = text.lower()

    sections = set()

    # -------------------------
    # IPC / BNS Sections
    # -------------------------
    matches = re.findall(r'section\s+(\d+)', text)
    for m in matches:
        sections.add(f"Section {m}")

    # -------------------------
    # IPC Explicit
    # -------------------------
    ipc_matches = re.findall(r'section\s+(\d+)\s+of\s+ipc', text)
    for m in ipc_matches:
        sections.add(f"IPC {m}")

    # -------------------------
    # BNS Explicit
    # -------------------------
    bns_matches = re.findall(r'section\s+(\d+)\s+of\s+bns', text)
    for m in bns_matches:
        sections.add(f"BNS {m}")

    # -------------------------
    # Constitution Articles
    # -------------------------
    article_matches = re.findall(r'article\s+(\d+)', text)
    for a in article_matches:
        sections.add(f"Article {a}")

    # limit output (clean UI)
    return list(sections)[:5]