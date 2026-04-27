# GTM Audit Agent MVP

A backend-first MVP tool that audits a Google Tag Manager (GTM) container export using deterministic rules and optional LLM refinement.

The tool accepts a GTM container export JSON file, runs audit checks, scores audit layers, and returns a structured audit report that can be reviewed by analysts.

---

## Project Goal

The goal of this MVP is to help marketing analytics teams automate the first pass of GTM container audits.

Current manual GTM audits can be time-consuming and inconsistent. This project provides a structured workflow to:

- Parse a GTM container export
- Run rule-based audit checks
- Identify potential hygiene and maintainability issues
- Score audit layers
- Optionally refine findings using an LLM and business context
- Display results in a simple Streamlit demo UI
- Export a structured JSON audit report

---

## Current MVP Scope

This MVP currently supports:

- GTM JSON upload
- GTM container parsing
- Basic container summary
- Business context input when LLM refinement is enabled
- Container hygiene audit rules
- Structured findings with evidence
- Audit layer scoring
- Optional OpenAI-based LLM refinement
- FastAPI backend
- Streamlit demo frontend
- JSON report download

---

## Current Audit Rules

The current MVP starts with the **Container Hygiene** audit layer.

Implemented checks:

| Rule ID | Check | Description |
|---|---|---|
| `HYG-001` | Paused tags | Detects tags that are currently paused |
| `HYG-002` | Tags without firing triggers | Detects tags that do not have firing triggers |
| `HYG-003` | High Custom HTML usage | Detects containers with multiple Custom HTML tags |
| `HYG-004` | Orphaned triggers | Detects triggers not referenced by any tag |
| `HYG-005` | Possibly orphaned variables | Detects variables that do not appear to be referenced |

More audit layers will be added later.

Planned layers:

- Trigger & Tag Logic
- Data Layer / Event Quality
- Consent & Privacy
- Governance / Maintainability

---

## Architecture

```txt
GTM JSON Export
        ↓
Parser
        ↓
Normalized GTM Models
        ↓
Rule-Based Auditors
        ↓
Raw Findings with Evidence
        ↓
Scoring Service
        ↓
Report Builder
        ↓
Optional LLM Refiner
        ↓
Audit Report JSON
        ↓
Streamlit Demo UI
```

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

### AI Layer

- OpenAI SDK
- Optional LLM Refinement

### Demo Frontend

- Streamlit
- Requests

### Testing/Development

- Pytest
- Python-dotenv

## Project Structure
```
gtm-audit-agent/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── schemas/
│   │   ├── gtm_container.py
│   │   ├── gtm_entities.py
│   │   ├── business_context.py
│   │   ├── findings.py
│   │   └── audit_report.py
│   │
│   ├── ingestion/
│   │   └── gtm_parser.py
│   │
│   ├── audit_layers/
│   │   ├── hygiene.py
│   │   ├── trigger_logic.py
│   │   ├── data_layer.py
│   │   ├── consent.py
│   │   └── governance.py
│   │
│   └── services/
│       ├── audit_runner.py
│       ├── scoring.py
│       ├── report_builder.py
│       └── llm_refiner.py
│
├── data/
│   ├── sample_container.json
│   └── sample_container_with_orphans.json
│
├── tests/
│   └── test_audit.py
│
├── streamlit_app.py
├── requirements.txt
├── requirements_demo.txt
├── README.md
└── .gitignore
```

---

## Setup Instructions

#### 1. Clone the repository
```
git clone <your-repo-url>
cd gtm-audit-agent
```
#### 2. Create a virtual environment
```
python -m venv venv
```

Activate it:
###### Windows PowerShell
```
venv\Scripts\activate
```
###### macOS / Linux
```
source venv/bin/activate
```
#### 3. Install backend dependencies
```
pip install -r requirements.txt
```
#### 4. Install Streamlit demo dependencies
```
pip install -r requirements_demo.txt
```

---

## Environment Variables

Create a .env file in the project root:
```
APP_NAME=GTM Audit Agent
ENVIRONMENT=local

OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o-mini

ADMIN_ACCESS_KEY=your-demo-access-key
DATABASE_URL=sqlite:///./data/gtm_audit.db
```

## Notes

- OPENAI_API_KEY is only required if you want to use LLM refinement.
- ADMIN_ACCESS_KEY is used by the Streamlit demo to allow private/demo access to the app’s OpenAI key.
- Users can also provide their own OpenAI API key directly in the Streamlit sidebar.
- Do not commit .env to GitHub.
 
---

## Running the FastAPI Backend

Start the backend server:
```
uvicorn app.main:app --reload
```
Then open:
```
http://127.0.0.1:8000/docs
```
Available endpoints:
```text
Method	Endpoint	Description
GET	/	Root health message
GET	/health	Health check
POST	/audit/run	Run GTM audit
```

---

## Running the Streamlit Demo

In a second terminal, run:
```
streamlit run streamlit_app.py
```
Then open the Streamlit URL shown in the terminal.

Typical local URL:
```
http://localhost:8501
```

---

## How to Use the Demo

- Start the FastAPI backend.
- Start the Streamlit app.
- Upload a GTM container export JSON.
- Choose whether to use LLM refinement.
- If LLM refinement is enabled, provide either:
  -- Admin Access Key, or
  -- Your own OpenAI API key
- Add business context.
- Click Run Audit.
- Review scores, findings, evidence, recommendations, and open questions.
- Download the JSON report.

---

## LLM Access Logic

The Streamlit demo supports two ways to use LLM refinement:

#### Option 1: Admin Access Key

If the user enters the correct admin access key, the app uses the OpenAI key stored in .env or Streamlit secrets.

#### Option 2: User OpenAI Key

If the user provides their own OpenAI key, the app uses that key only for the current session/request.

#### No Key

If LLM refinement is turned on but no valid key is provided, the audit does not run.

If LLM refinement is turned off, the audit runs using deterministic rules only.

---

## API Example

Endpoint:
```
POST /audit/run
```
Form data:
```
Field	Type	Required	Description
gtm_file	File	Yes	GTM export JSON file
business_context_text	Text	No	Business context for LLM refinement
use_llm	Boolean	No	Whether to use LLM refinement
openai_api_key	Text	No	Request-level OpenAI API key
```
Example response:
```
{
  "audit_report_id": "R-AB12CD34",
  "client_name": null,
  "container_name": "Sample Container With Orphans",
  "container_public_id": "GTM-ORPHAN",
  "summary": "The audit found 4 findings in the container.",
  "scores": [
    {
      "layer": "container_hygiene",
      "score": 75,
      "band": "needs_review"
    }
  ],
  "findings": [],
  "open_questions": [],
  "review_status": "pending"
}
```

---

## Current Limitations

This is an MVP and has some known limitations:

- Only the Container Hygiene audit layer is implemented.
- The GTM parser supports the fields needed for the current MVP but may need more coverage for real-world containers.
- Orphaned variable detection is pattern-based and may not catch every GTM reference style.
- LLM refinement does not create new findings; it only improves existing deterministic findings.
- No database persistence yet.
- No authentication beyond demo-level access key handling.
- No review workflow persistence yet.
- No Markdown/PDF/PowerPoint export yet.
- No GTM API integration yet.
- No live website validation yet.

## Planned Next Steps

Short-term:

-Add Markdown report export
Add analyst review workflow: accept, reject, edit findings
Add SQLite persistence
Add more audit rules
Improve tests
Improve Streamlit UI layout

Next audit layers:

Trigger & Tag Logic
Data Layer / Event Quality
Consent & Privacy
Governance / Maintainability

Future enhancements:

GTM API integration
Measurement plan comparison
Browser-assisted validation
DOCX/PDF export
Presentation Agent integration
Implementation Agent integration
Long-term remediation roadmap generation
Security Notes
Never commit .env.
Never commit .streamlit/secrets.toml.
Use .streamlit/secrets.toml.example for placeholder examples only.
User-provided OpenAI keys should only be used for the current request/session.
Restrict CORS before production deployment.
Add proper authentication before allowing external users to access private/client audit data.
Development Status

Current status: MVP backend + Streamlit demo working locally

Implemented:

GTM parser
GTM schemas
Container hygiene rules
Structured evidence
Scoring service
Audit report builder
Optional LLM refinement
FastAPI /audit/run
Streamlit demo UI