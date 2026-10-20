<div align="center">
  <h1>⚖️ LegalBuddy AI</h1>
  <p><strong>AI-assisted legal discovery · Case insights · Lawyer recommendations</strong></p>
  <p>An evolving software project exploring ways to make legal information more approachable.</p>
  <p>
    <a href="https://github.com/PriyanshuV17/legal">Repository</a> ·
    <a href="https://priyanshuv17.github.io/legal/">Project page</a> ·
    <a href="https://github.com/PriyanshuV17">Author</a>
  </p>
</div>

---

<<<<<<< HEAD
## ✦ About

**LegalBuddy AI** is an exploratory legal-assistance project that brings together a chat-oriented interface, case and law exploration components, and lawyer recommendation experiments. The repository includes Python application code, backend modules, a React + Vite frontend scaffold, and saved model/data artifacts.
=======
## Overview
>>>>>>> 3d6e4812eb05288af5a982c97efedc1a574025ab

> **Project status:** evolving prototype. Repository components may differ in maturity; this documentation does not imply that every feature is deployed or production-ready.

## ◈ Project areas

| Area | Description |
|---|---|
| Conversational assistant | Chat-style interface for asking legal questions |
| Case & law insights | Backend and ingestion modules for exploring legal content |
| Lawyer recommendations | Recommendation artifacts and feature-importance data |
| Web interfaces | Streamlit UI and a React + Vite scaffold |

## ⌘ Technology overview

`Python` · `FastAPI` · `Streamlit` · `React` · `Vite` · `scikit-learn` · `PyTorch` · `LangChain` · `ChromaDB`

See [`requirements.txt`](requirements.txt) and the individual project folders for dependency details.

## ⇢ Repository map

```text
legal/
├── docs/                 # Static GitHub Pages project site
├── frontend/              # Streamlit interface
├── future/
│   └── backend/           # Backend, ingestion, and model-related code
├── models/                # Model artifacts, metadata, and processed data
├── webapp/
│   └── frontend/          # React + Vite application scaffold
├── requirements.txt
└── README.md
```

## 🚀 Run locally

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/PriyanshuV17/legal.git
cd legal
python -m venv .venv
```

Activate it, then install the listed dependencies:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

The repository contains multiple app/backend areas. Check the relevant folder's README and configuration for the correct entry point and required services before running a component.

## 🌐 GitHub Pages

The static landing page is in [`docs/index.html`](docs/index.html). To publish it, go to **Settings → Pages**, choose **Deploy from a branch**, then select **main** and **/docs**. The site URL is expected to be:

**https://priyanshuv17.github.io/legal/**

GitHub Pages hosts only the static project page; it does not run the Python backend or model inference.

## ⚠️ Responsible use

This is a software project for exploring legal information workflows, not a substitute for a qualified legal professional. Verify source materials and seek professional advice for legal decisions. Do not rely on generated or ranked outputs as authoritative legal advice.

## 👤 Author

**Priyanshu Verma** · [GitHub @PriyanshuV17](https://github.com/PriyanshuV17)
