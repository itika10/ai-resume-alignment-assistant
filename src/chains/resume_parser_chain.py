from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.resume_models import ResumeData

def get_resume_parser_chain():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    structured_llm = llm.with_structured_output(ResumeData)

    prompt = ChatPromptTemplate.from_messages(
        [
         (
                "system",
                """
                    You are an expert resume parser.

                    Extract structured information from the resume text.
                    Follow these rules carefully:
                    - Do not invent information.
                    - If a field is missing, return an empty string or empty list.
                    - Extract only what is explicitly stated or strongly implied in the resume.
                    - Keep bullet points concise.
                    - Normalize skills into clean short phrases.
                    - Preserve factual accuracy.
                """.strip(),
            ),
            (
                "human", 
                """
                    Parse the following resume text into the required structured format.
                    Resume text:
                    {resume_text}
                """.strip(),
            )
        ]
    )

    return prompt | structured_llm