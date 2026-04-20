from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.validation_models import ValidationResult


def get_validation_chain():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    structured_llm = llm.with_structured_output(ValidationResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a strict resume validation agent.

Your task is to validate a tailored resume rewrite against:
1. the original structured resume,
2. the structured job description,
3. the approved skill mapping output.

Your job is NOT to improve style. Your job is to detect factual and contextual risk.

Validation rules:
- Do not allow claims that are not explicitly supported by the resume or safely supported by the skill mapping.
- If a specific tool or framework was not used directly, do not allow the rewrite to present it as direct experience.
- Treat adjacent frameworks carefully.
- Do not allow AI/ML/LLM terminology unless it is explicitly present in the original resume or strongly justified by safe mappings.
- Reject bullets that drift too far from the meaning of the original bullet.
- Flag temporal or contextual mismatches when modern terminology is injected into unrelated historical roles.
- Be conservative and strict.

Issue types:
- unsupported_claim
- overstatement
- unsafe_tool_inference
- ai_irrelevance
- temporal_mismatch
- meaning_drift

Output rules:
- approved_summary should contain a safe final summary. If the tailored summary is fine, keep it. If not, correct it conservatively.
- approved_bullets should contain only safe rewritten bullets.
- For each approved bullet, include:
  - source_section
  - original_bullet
  - approved_bullet
- If a bullet is unsafe, do not include the unsafe version in approved_bullets.
- suggested_fix should offer a safer alternative where possible.
                """.strip(),
            ),
            (
                "human",
                """
Validate the tailored resume rewrite using the following inputs.

Structured resume data:
{resume_data}

Structured job description data:
{jd_data}

Approved skill mapping output:
{skill_mapping}

Rewrite output:
{rewrite_result}
                """.strip(),
            ),
        ]
    )

    return prompt | structured_llm