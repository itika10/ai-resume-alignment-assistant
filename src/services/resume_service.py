from src.chains.resume_parser_chain import get_resume_parser_chain

def parse_resume(resume_text: str):
    parser_chain = get_resume_parser_chain()
    return parser_chain.invoke({"resume_text": resume_text})