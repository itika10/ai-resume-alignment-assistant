from src.chains.validation_chain import get_validation_chain


def validate_rewrite(resume_data, jd_data, skill_mapping, rewrite_result, openai_api_key: str):
    chain = get_validation_chain(openai_api_key=openai_api_key)
    return chain.invoke(
        {
            "resume_data": resume_data.model_dump_json(indent=2),
            "jd_data": jd_data.model_dump_json(indent=2),
            "skill_mapping": skill_mapping.model_dump_json(indent=2),
            "rewrite_result": rewrite_result.model_dump_json(indent=2),
        }
    )