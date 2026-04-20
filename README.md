[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://ai-resume-alignment-assistant.streamlit.app/)

# AI Resume Alignment Assistant

An AI-powered tool that tailors resumes based on job descriptions and generates clean, ATS-friendly in DOCX PDF formats.

---

## Features

* Resume Parsing
* Job Description Analysis
* Skill Mapping
* Bullet Point Rewriting
* Validation Layer
* ATS Optimization
* Resume Generation in DOCX
* Resume Generation in PDF using ReportLab and RenderCV

---

## How It Works

1. Upload your master resume
2. Provide a job description
3. The system parses and analyzes both inputs
4. AI aligns the resume to the job description
5. A validation layer checks the structured output
6. The tailored resume is generated in a professional format

---

## Tech Stack

* Python
* Streamlit
* LangChain
* OpenAI API
* RenderCV
* ReportLab
* Python-Docx

The current MVP uses Streamlit for the interface.
In a later version, the backend can be moved to FastAPI with a separate frontend.

---

## Project Structure

```
AI-Resume-Assistant/
  samples/
  src/
    chains/
    services/
    models/
  app.py
  requirements.txt
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

## Current Status (MVP)

This version includes:

* Resume parsing
* Job description analysis
* Resume tailoring
* Validation of structured output
* DOCX generation
* PDF generation with ReportLab and RenderCV

---

## Upcoming Improvements

* LLM-based skill categorization
* Improved resume schema
* Social links support (LinkedIn, GitHub)
* Experience normalization for dates, location, and client
* Better frontend and backend separation
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
