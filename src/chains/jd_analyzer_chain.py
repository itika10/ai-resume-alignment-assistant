from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.jd_models import JobDescriptionData

def get_jd_analyzer_chain(openai_api_key: str):
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=openai_api_key)

    structured_llm = llm.with_structured_output(JobDescriptionData)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                    You are an expert job description analyzer.

                    Extract structured information from the job description text.
                    Follow these rules carefully:
                    - Do not invent information.
                    - If a field is missing, return an empty string or empty list.
                    - Extract only what is explicitly stated or strongly implied in the job description.
                    - Keep bullet points concise.
                    - Normalize skills into clean short phrases.
                    - Preserve factual accuracy.
                """.strip(),
            ),
            (
                "human", 
                """
                    Analyze the following job description text and extract the required structured information.
                    Job description text:
                    {job_description}
                """.strip(),
            )
        ]
    )

    return prompt | structured_llm