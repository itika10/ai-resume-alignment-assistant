from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.ats_models import ATSResult


def get_ats_checker_chain():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    structured_llm = llm.with_structured_output(ATSResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an ATS compatibility checker for resume alignment.

Your task is to evaluate how well the candidate's resume aligns with the job description in an ATS-friendly and recruiter-friendly way.

You must be honest and conservative.
Do not claim to predict real ATS outcomes.
Do not reward keyword stuffing.
Prefer skills and keywords that appear in meaningful context.

Scoring rules:
- alignment_score must be an integer from 0 to 100.
- Base the score on content alignment, keyword coverage, relevance of validated bullets, and whether important JD requirements are represented truthfully.
- Do not penalize the candidate for missing tools that should not be claimed dishonestly.
- Give credit for conceptual and category-level alignment when supported by the resume and validated rewrite.

Evaluation rules:
- matched_keywords should include important JD terms that are clearly reflected in the parsed resume, safe skill mappings, or validated rewrite.
- missing_keywords should include important JD terms that remain absent or weakly represented.
- section_warnings should note missing or weak sections such as summary, skills, projects, certifications, or experience relevance.
- content_warnings should note vague language, weak alignment, or unsupported emphasis.
- suggestions should be concrete, truthful, and useful.

Important:
- Use the validated rewrite, not the raw rewrite, as the trusted tailored output.
- Prefer recruiter realism over inflated scoring.
                """.strip(),
            ),
            (
                "human",
                """
Evaluate ATS compatibility using the following inputs.

Structured resume data:
{resume_data}

Structured job description data:
{jd_data}

Skill mapping output:
{skill_mapping}

Validation result:
{validation_result}
                """.strip(),
            ),
        ]
    )

    return prompt | structured_llm