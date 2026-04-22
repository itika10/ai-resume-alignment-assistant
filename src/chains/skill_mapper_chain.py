from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.mapping_models import SkillMappingResult

def get_skill_mapper_chain(openai_api_key: str):
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=openai_api_key)

    structured_llm = llm.with_structured_output(SkillMappingResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert skill mapping engine for resume alignment.

Your task is to compare the candidate's resume data with the job description data and identify safe, truthful relationships between them.

Rules:
- Do not fabricate experience.
- Only map JD skills to resume evidence that is explicitly present or strongly supported by the resume.
- Use one of these relation values only:
  - exact_match
  - category_match
  - adjacent_framework
  - concept_match
  - partial_match
  - no_match
- exact_match: same skill/tool clearly appears in resume.
- category_match: resume contains a specific tool that belongs to the JD category.
- adjacent_framework: resume shows experience with a similar framework, but not the exact one.
- concept_match: resume demonstrates the underlying concept, even if the JD term is not used directly.
- partial_match: some overlap exists, but not enough for strong alignment.
- no_match: no meaningful evidence in the resume.

Safety rules:
- safe_to_add should be true only if the JD term can be reflected safely without implying direct hands-on experience when it is not present.
- If the JD asks for a specific framework not used by the candidate, do not represent it as direct experience.
- For adjacent tools like LangChain vs LlamaIndex, phrase carefully such as familiarity with similar frameworks.
- suggested_resume_phrase must be honest and conservative.
- Keep reasons short and clear.

Matching rules:
- Compare JD required_skills, preferred_skills, and keywords against resume skills, projects, certifications, summary, and experience bullets.
- If no evidence exists, set relation=no_match and safe_to_add=false.
                """.strip(),
            ),
            (
                "human",
                """
Compare the following structured resume data and structured job description data.

Resume data:
{resume_data}

Job description data:
{jd_data}
                """.strip(),
            ),
        ]
    )

    return prompt | structured_llm