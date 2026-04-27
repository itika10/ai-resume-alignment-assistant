from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.resume_models import SkillCategorizationResult


def get_skill_categorizer_chain(openai_api_key: str):
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=openai_api_key)

    structured_llm = llm.with_structured_output(SkillCategorizationResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert resume skill organizer.

Your task is to group a candidate's skills into a small set of meaningful categories
that fit the candidate's domain and the target job description.

Hard rules:
- Group every input skill into exactly ONE category. No skill may be dropped.
- Do NOT invent skills. Use only the skills provided in the input.
- Choose between 3 and 6 categories total. Fewer when the skill set is small.
- Order the categories by relevance to the job description, most relevant first.
- Within each category, list items in the order most relevant to the job description.
- Keep category names short, professional, and resume-friendly (1 to 3 words).

Soft suggestion list of preferred category names:
- Programming
- Backend
- Frontend
- AI/ML & Data
- Cloud
- Databases
- DevOps & Tools
- Data & Analytics
- Methodologies
- Domain Knowledge
- Soft Skills

Use a name from the soft suggestion list whenever it fits. Only invent a new
category name if none of the suggestions fit well (for example, for non-tech
domains such as finance, design, marketing, or healthcare). Prefer broad,
recognizable names over highly specific ones.

Output rules:
- Return a SkillCategorizationResult with the skill_categories field populated.
- Each category must contain at least one item.
- Do not include empty categories.
                """.strip(),
            ),
            (
                "human",
                """
Group the following skills into appropriate categories for this candidate.

Candidate skills (group all of these):
{skills}

Candidate professional summary:
{summary}

Candidate experience snapshot (roles and companies only, for domain context):
{experience_snapshot}

Job description signals (use these to choose and order categories):
{jd_signals}
                """.strip(),
            ),
        ]
    )

    return prompt | structured_llm
