[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://ai-resume-alignment-assistant.streamlit.app/)

# AI Resume Alignment Assistant

An AI-powered tool that tailors resumes based on job descriptions and generates clean, ATS-friendly resumes in DOCX and PDF formats.

> Looking for the technical details? See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for a module-by-module map, Pydantic model field reference, chain/service responsibilities, and dependency diagrams.

---

## Features

* Resume parsing (PDF and DOCX) with hyperlink-aware URL detection
* Job description analysis (required/preferred skills, responsibilities, ATS keywords)
* Skill mapping with safety flags (exact_match, category_match, adjacent_framework, concept_match, partial_match, no_match)
* LLM-based skill categorization into JD-relevant groups
* Bullet point rewriting tailored to the JD
* Validation layer that flags unsupported claims, overstatements, and AI/ML inflation
* Bullet condensation with duration-based quotas (1 or 3 bullets per role)
* ATS optimization scoring with section and content warnings
* Per-run token usage and cost tracking shown in the sidebar
* Resume generation in DOCX (python-docx)
* Resume generation in PDF using ReportLab and RenderCV

---

## How It Works

1. Upload your master resume
2. Provide a job description
3. The system parses and analyzes both inputs
4. AI maps skills, categorizes them, and tailors bullets to the JD
5. A validation layer reviews the rewrite for factual safety
6. Bullets are condensed to a clean final shape
7. The tailored resume is generated in a professional format

---

## Tech Stack

* Python
* Streamlit
* LangChain
* OpenAI API (gpt-4.1-mini)
* Pydantic v2
* RenderCV
* ReportLab
* python-docx
* pdfplumber

The current MVP uses Streamlit for the interface.
In a later version, the backend can be moved to FastAPI with a separate frontend.

---

## Project Structure

```
AI-Resume-Assistant/
  samples/
  src/
    chains/        # LangChain prompt + parser factories
    services/      # Orchestrators that wrap each chain
    models/        # Pydantic schemas for structured LLM output
    utils/         # cost tracking, date math, skill dedupe
  app.py
  requirements.txt
  ARCHITECTURE.md
  README.md
  .env.example
  .gitignore
```

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/itika10/ai-resume-alignment-assistant.git
cd ai-resume-alignment
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
```

---

## Run the project

```bash
streamlit run app.py
```

---

## Current Status

This version includes:

* Resume parsing (PDF, DOCX) with URL detection
* Job description analysis
* Skill mapping and LLM-based skill categorization
* Resume tailoring (summary + bullets)
* Validation of structured output with issue typing and severity
* Bullet condensation with duration-based quotas
* ATS compatibility scoring
* Per-run cost tracking in the sidebar
* DOCX generation
* PDF generation with ReportLab and RenderCV

---

## Upcoming Improvements

* Caching layer for repeated chain calls (skip the LLM on identical inputs)
* Parallel execution of independent chains (skill_mapper, skill_categorizer, ats_checker)
* LLM abstraction with fallback (Claude/local) for rate-limit resilience and cheaper routing
* Centralized telemetry wrapper around chain calls (tokens, latency, cost per run)
* FastAPI backend with a separate frontend

---

## Why This Project?

This project demonstrates:

* Real-world AI application design
* LLM integration into structured workflows
* Validation of model-generated outputs
* Resume optimization for job applications

---

## Author

Itika Sharma

* GitHub: https://github.com/itika10
* LinkedIn: https://linkedin.com/in/itika-sharma

---

## Support

If you found this project useful, give it a star on GitHub.
