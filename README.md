<div align="center">

# ⚖️ LegalBuddy AI

### Legal discovery, made more approachable.

An evolving project exploring AI-assisted legal information, case discovery, conversational support, and lawyer recommendations.

<p>
  <a href="https://github.com/PriyanshuV17/legal"><img src="https://img.shields.io/badge/Repository-PriyanshuV17%2Flegal-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub repository"></a>
  <a href="https://priyanshuv17.github.io/legal/"><img src="https://img.shields.io/badge/Project%20Page-GitHub%20Pages-e9a45e?style=for-the-badge&logo=githubpages&logoColor=11110f" alt="Project page"></a>
  <img src="https://img.shields.io/badge/Status-Prototype-c9d8a0?style=for-the-badge" alt="Project status: prototype">
</p>

[Explore the project](https://priyanshuv17.github.io/legal/) · [Browse source code](https://github.com/PriyanshuV17/legal) · [Author profile](https://github.com/PriyanshuV17)

</div>

---

## ✦ Overview

LegalBuddy AI is a software project exploring how AI-driven tools can make legal information easier to navigate. The repository brings together application interfaces, backend components, and model/data artifacts for experimentation with legal assistance and discovery.

> **Project status:** This is an evolving prototype. The availability and maturity of individual components may vary. The descriptions below are intended as a high-level guide to the repository, not a claim that every feature is production-ready or deployed.

## ◈ Project areas

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>💬 Conversational support</h3>
      A chat-oriented interface for exploring legal questions and information.
    </td>
    <td width="50%" valign="top">
      <h3>⚖️ Case and legal discovery</h3>
      Backend and ingestion components related to legal content and case exploration.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>✧ Recommendation experiments</h3>
      Recommendation-related model artifacts and feature-importance data.
    </td>
    <td width="50%" valign="top">
      <h3>⌘ Multiple interfaces</h3>
      A Streamlit interface and a React + Vite frontend scaffold are present in the repository.
    </td>
  </tr>
</table>

## ⌘ Technology overview

The repository includes code and artifacts associated with the following technologies. Check the relevant project files for exact dependencies and versions.

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch">
</p>

See [`requirements.txt`](requirements.txt) and each component's configuration for dependency details.

## ⇢ Repository structure

```text
legal/
├── docs/
│   └── index.html          # Static GitHub Pages landing page
├── frontend/               # Streamlit interface
├── future/
│   ├── backend/             # Backend and related project modules
│   └── models/              # Serialized model artifact(s)
├── models/                  # Model artifacts and supporting data
├── webapp/
│   └── frontend/            # React + Vite frontend scaffold
├── requirements.txt
└── README.md
```

This is a simplified map of the main project areas; consult the repository for the complete, current file tree.

## 🚀 Getting started

### 1. Clone the repository

```bash
git clone https://github.com/PriyanshuV17/legal.git
cd legal
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it with the command for your operating system:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run a component

The repository contains multiple application areas. Review the relevant folder, configuration, and any component-specific instructions to identify its entry point and required environment variables or services before launching it. No single universal run command is specified here because the components may have different startup requirements.

## 🌐 Project website

The static project landing page is available at:

**[priyanshuv17.github.io/legal](https://priyanshuv17.github.io/legal/)**

The page source is [`docs/index.html`](docs/index.html). To publish or change it, open **Settings → Pages** in the repository and configure **Deploy from a branch**, branch `main`, folder `/docs`.

GitHub Pages serves the static website only. It does not execute the Python backend, Streamlit app, or model inference code.

## 🧭 Responsible use

Legal information can be context-dependent and jurisdiction-specific. This project is for software exploration and educational purposes; it is **not legal advice** and should not replace a qualified legal professional. Independently verify sources and consult appropriate counsel before making legal decisions. Do not treat model-generated, retrieved, or ranked results as authoritative without review.

## 🤝 Contributing

Suggestions, bug reports, and improvements are welcome. Before opening a pull request:

1. Describe the issue or proposed change clearly.
2. Keep configuration and setup instructions up to date.
3. Avoid committing secrets, credentials, or unnecessary generated artifacts.
4. Include tests or reproducible steps when applicable.

## 📄 License

No license has been confirmed in this README. Check the repository for a `LICENSE` file before reusing or distributing the project. If you intend to publish it for reuse, add an appropriate license.

---

<div align="center">

**Built by [Priyanshu Verma](https://github.com/PriyanshuV17)**

<sub>LegalBuddy AI · An evolving project in AI-assisted legal discovery</sub>

</div>
