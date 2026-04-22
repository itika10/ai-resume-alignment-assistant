from src.chains.jd_analyzer_chain import get_jd_analyzer_chain

def parse_job_description(job_description: str, openai_api_key: str):
    jd_analyzer_chain = get_jd_analyzer_chain(openai_api_key=openai_api_key)
    return jd_analyzer_chain.invoke({"job_description": job_description})