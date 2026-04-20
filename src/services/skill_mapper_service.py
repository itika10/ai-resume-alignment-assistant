from src.chains.skill_mapper_chain import get_skill_mapper_chain

def map_skills(resume_data, jd_data):
    chain = get_skill_mapper_chain()
    return chain.invoke(
        {
            "resume_data": resume_data.model_dump_json(indent=2),
            "jd_data": jd_data.model_dump_json(indent=2),}
    )