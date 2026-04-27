from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.models.resume_models import ResumeData

def get_resume_parser_chain(openai_api_key: str):
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=openai_api_key)

    structured_llm = llm.with_structured_output(ResumeData)

    prompt = ChatPromptTemplate.from_messages(
        [
         (
                "system",
                """
                    You are an expert resume parser.

                    Extract structured information from the resume text into the required schema.

                    Follow these rules carefully:
                    - Do not invent information.
                    - If a field is missing, return an empty string, null, or an empty list as appropriate.
                    - Extract only what is explicitly stated or strongly implied in the resume.
                    - Preserve factual accuracy.
                    - Keep bullet points concise and resume-friendly.
                    - Normalize skills into clean short phrases.
                    - Do not merge unrelated fields together.

                    Parsing guidance:

                    1. Header / Contact
                    - Extract name, email, phone, and primary location from the header if available.
                    - Extract social/profile links into the socials field.
                    - For socials:
                    - label should be something like "LinkedIn", "GitHub", or "Portfolio"
                    - url should be the full URL when available
                    - if only the platform name is present without a URL, you may leave url empty

                    2. Skills
                    - Put all extracted skills into the flat skills list for MVP compatibility.
                    - Only populate skill_categories if the resume clearly groups skills by category.
                    - If categories are present, preserve them faithfully.

                    3. Experience
                    For each experience entry, extract:
                    - role
                    - company
                    - client, if the employer and client are both shown
                    - location, if shown for that specific role
                    - start_date
                    - end_date
                    - bullets

                    Experience parsing rules:
                    - If a role is written like "TCS, Canada – BMO | 04/2021 – Present":
                    - company = "TCS"
                    - location = "Canada"
                    - client = "BMO"
                    - start_date = "04/2021"
                    - end_date = "Present"
                    - If a role is written like "Tech Mahindra Americas – AT&T":
                    - company = "Tech Mahindra Americas"
                    - client = "AT&T"
                    - If location is attached to the company line, extract it into location rather than leaving it inside company.
                    - Keep company names clean and separate from location/date where possible.

                    4. Projects
                    For each project, extract:
                    - title
                    - bullets
                    - tech_stack if explicitly mentioned

                    5. Education
                    For each education entry, extract:
                    - degree
                    - institution
                    - location if available
                    - graduation_date if available

                    6. Certifications
                    - Extract certifications as a list of strings.

                    General formatting rules:
                    - Keep dates exactly as written when possible, such as "04/2021", "03/2021", or "Present".
                    - Do not rewrite achievements into stronger claims.
                    - Do not infer missing dates or locations.
                    - Do not create fake URLs for socials.
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