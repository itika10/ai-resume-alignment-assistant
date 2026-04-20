from src.chains.ats_checker_chain import get_ats_checker_chain


def check_ats_compatibility(resume_data, jd_data, skill_mapping, validation_result):
    chain = get_ats_checker_chain()
    return chain.invoke(
        {
            "resume_data": resume_data.model_dump_json(indent=2),
            "jd_data": jd_data.model_dump_json(indent=2),
            "skill_mapping": skill_mapping.model_dump_json(indent=2),
            "validation_result": validation_result.model_dump_json(indent=2),
        }
    )