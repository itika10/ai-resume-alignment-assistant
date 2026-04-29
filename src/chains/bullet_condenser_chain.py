from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.resume_models import BulletCondensationResult


def get_bullet_condenser_chain(openai_api_key: str):
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=openai_api_key)

    structured_llm = llm.with_structured_output(BulletCondensationResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a resume condensation specialist.

Your task is to take validated resume bullets and produce a SHORT, focused
final list per experience and per project. You do not invent new content.

For each input section, you will receive a precomputed `bullet_count`
(either 1 or 3). You MUST output exactly that many bullets for that section.

Hard rules:
- Output EXACTLY `bullet_count` bullets for each section. Never more, never fewer.
- Never introduce information that is not present in the input bullets,
  description, or tech_stack. This is selection + light combination, not generation.
- Preserve quantitative details (numbers, percentages, scale, tools) from the
  source bullets when carrying them forward.
- Prefer bullets that mention JD-relevant skills, tools, or measurable impact.
- When combining bullets, keep the result a single sentence. Avoid bullet
  points that contain "and" twice — that usually means you are stuffing.
- Do not add AI/ML/LLM terminology that is not already in the source.
- Match each output to the input by exact role+company (experiences) or
  exact title (projects). Do not rename them.

Project description rules:
- For each project, return a `description` that is a SINGLE SENTENCE,
  MAXIMUM 25 WORDS, summarizing what the project does or is for.
- If the input project already has a description, polish it for concision
  while preserving meaning. Do NOT exceed 25 words.
- If the input project has no description, generate one from the bullets,
  tech_stack, and title. Keep it factual and grounded.
- Do not duplicate the project title inside the description.

Output rules:
- Return a BulletCondensationResult.
- experiences: same order as input.
- projects: same order as input. Each project must include a description.
                """.strip(),
            ),
            (
                "human",
                """
Condense the following resume sections.

Job description signals (use these to choose which bullets are most relevant):
{jd_signals}

Experiences (each entry includes a precomputed bullet_count to enforce):
{experiences}

Projects (each entry includes a precomputed bullet_count and an optional
existing description):
{projects}
                """.strip(),
            ),
        ]
    )

    return prompt | structured_llm
