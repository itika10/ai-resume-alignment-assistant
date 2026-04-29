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
                    - label should be something like "LinkedIn", "GitHub", "Portfolio", or "Twitter"
                    - url should be the full URL when available
                    - if only the platform name is present without a URL, you may leave url empty
                    - If the resume text ends with a "DETECTED URLS (from hyperlinks in source file):" block,
                      treat those URLs as authoritative — they were extracted from clickable hyperlinks
                      in the original file and may not be visible elsewhere in the text. Match each URL to
                      a social label by inferring the platform from the domain:
                      linkedin.com -> LinkedIn, github.com -> GitHub, twitter.com or x.com -> Twitter,
                      medium.com -> Medium, stackoverflow.com -> Stack Overflow, gitlab.com -> GitLab,
                      youtube.com -> YouTube, scholar.google.com -> Google Scholar, orcid.org -> ORCID.
                      For any other domain, use a sensible label such as "Portfolio" or "Website".
                      Populate the socials list with these URLs even if the visible resume text only
                      showed an icon or a generic label.
                    - Do not include the DETECTED URLS block in any other field.

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
                    - description: a single short header sentence summarizing what the project does, if
                      one appears between the title and the bullets. Leave empty if no such sentence exists;
                      the downstream pipeline will generate one from the bullets.
                    - bullets
                    - tech_stack if explicitly mentioned
                    - start_date and end_date if a date or date range is shown for the project.
                      If only a single date appears, treat it as end_date.
                      Leave both empty if no project dates are shown — do not guess.

                    5. Education
                    For each education entry, extract:
                    - degree: the SHORT degree label only, such as "B.Tech", "PhD", "M.Sc", "BA", "MBA".
                      If the resume shows a long form like "Bachelor of Technology (B.Tech)", use the
                      abbreviation in parentheses ("B.Tech"). If no abbreviation is present, use a
                      reasonable short form (for example, "Bachelor of Science" -> "B.Sc").
                    - area: the field of study, such as "Computer Science", "Mechanical Engineering",
                      "Mathematics". Leave empty if the resume does not mention a field of study.
                    - institution
                    - location if available
                    - start_date if a start date or start year is shown
                    - end_date if an end date or graduation year is shown.
                      If only a single graduation year is shown, populate end_date and leave start_date empty.

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