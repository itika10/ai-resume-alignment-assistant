from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.rewrite_models import RewrittenResult

def get_rewrite_chain(openai_api_key: str):
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=openai_api_key)

    structured_llm = llm.with_structured_output(RewrittenResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert resume rewriting assistant.

Your task is to tailor resume content to a job description while preserving factual accuracy.

Rules:
- Do not fabricate skills, tools, projects, achievements, or responsibilities.
- Rewrite only using information explicitly stated in the resume or safely supported by the approved skill mappings.
- Use the job description language when it truthfully aligns with the candidate's background.
- Prefer strong but honest phrasing.
- Keep rewritten bullets concise, professional, and ATS-friendly.
- Do not claim direct experience with a tool if the mapping only supports adjacent familiarity.
- Only rewrite bullets that improve alignment meaningfully.
- Preserve the original meaning of each bullet.

CRITICAL SAFETY RULES:
- Do NOT introduce AI, ML, LLM, or data-driven terminology unless explicitly present in the original resume or strongly supported by evidence.
- Respect the time context of experience. Do not modernize older roles with recent technologies.
- Do not generalize generic software work as AI-related.

For tailored_summary:
- Write a short summary aligned to the job description.
- Keep it truthful and grounded in the resume.

For skills_to_highlight:
- Include only skills that are both relevant to the JD and supported by the resume or safe mappings.
                """.strip(),
            ),
            (
                "human",
                """
Use the following inputs to create a tailored resume rewrite.

Structured resume data:
{resume_data}

Structured job description data:
{jd_data}

Approved skill mapping output:
{skill_mapping}
                """.strip(),
            ),
        ]
    )

    return prompt | structured_llm


