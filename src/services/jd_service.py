from src.chains.jd_analyzer_chain import get_jd_analyzer_chain

def parse_job_description(job_description: str):
    jd_analyzer_chain = get_jd_analyzer_chain()
    return jd_analyzer_chain.invoke({"job_description": job_description})