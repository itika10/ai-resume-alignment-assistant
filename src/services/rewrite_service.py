from src.chains.rewrite_chain import get_rewrite_chain

def rewrite_resume_content(resume_data, jd_data, skill_mapping, openai_api_key: str):
    rewrite_chain = get_rewrite_chain(openai_api_key=openai_api_key)
    rewritten_result = rewrite_chain.invoke(
        {
            "resume_data": resume_data.model_dump_json(indent=2),
            "jd_data": jd_data.model_dump_json(indent=2),
            "skill_mapping": skill_mapping.model_dump_json(indent=2)

        }
    )
    return rewritten_result