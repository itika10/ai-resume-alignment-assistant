import streamlit as st
from dotenv import load_dotenv

from src.services.file_loader import load_resume_text
from src.services.resume_service import parse_resume
from src.services.jd_service import parse_job_description
from src.services.skill_mapper_service import map_skills
from src.services.rewrite_service import rewrite_resume_content
from src.services.validation_service import validate_rewrite
from src.services.ats_service import check_ats_compatibility
from src.services.resume_assembler_service import build_approved_tailored_resume
from src.services.export_docx_service import generate_resume_docx
from src.services.export_pdf_service import generate_resume_pdf
from src.services.export_rendercv_service import generate_resume_pdf_rendercv

load_dotenv()   

st.set_page_config(page_title="AI Resume Alignment Assistant", page_icon=":briefcase:", layout="wide")

st.title("AI Resume Alignment Assistant :briefcase:")
st.write("Upload your resume and paste the job description to generate a tailored version of your resume that highlights the most relevant skills and experiences for the job.")

uploaded_resume = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

job_description = st.text_area("Paste the job description here", height=300, placeholder="Copy and paste the job description for the position you're applying for.")

generate_button = st.button("Generate Tailored Resume")

if generate_button:
    if not uploaded_resume:
        st.error("Please upload a resume.")
    elif not job_description.strip():
        st.error("Please paste the job description.")
    else:
        try:
            resume_text = load_resume_text(uploaded_resume)
            st.success("Resume loaded successfully!")

            parsed_resume = parse_resume(resume_text)
            parsed_jd = parse_job_description(job_description)
            skill_mapping = map_skills(parsed_resume, parsed_jd)
            rewrite_result = rewrite_resume_content(parsed_resume, parsed_jd, skill_mapping)
            validation_result = validate_rewrite(
                parsed_resume,
                parsed_jd,
                skill_mapping,
                rewrite_result,
            )
            ats_result = check_ats_compatibility(
                parsed_resume,
                parsed_jd,
                skill_mapping,
                validation_result,
            )
            final_resume = build_approved_tailored_resume(
                parsed_resume,
                rewrite_result,
                validation_result,
            )

            docx_file = generate_resume_docx(final_resume)
            pdf_file = generate_resume_pdf(final_resume)
            docx_file = generate_resume_docx(final_resume)
            pdf_file_reportlab = generate_resume_pdf(final_resume)

            try:
                pdf_bytes_rendercv = generate_resume_pdf_rendercv(final_resume)
                rendercv_pdf_error = None
            except Exception as e:
                pdf_bytes_rendercv = None
                rendercv_pdf_error = str(e)

            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
                [
                    "Parsed Resume",
                    "Parsed JD",
                    "Skill Mapping",
                    "Tailored Rewrite",
                    "Validation",
                    "ATS Check",
                    "Tailored Resume"
                ]
            )

            with tab1:
                st.subheader("Parsed Resume Data")
                st.json(parsed_resume.model_dump())

            with tab2:
                st.subheader("Parsed Job Description Data")
                st.json(parsed_jd.model_dump())

            with tab3:
                st.subheader("Skill Mapping Output")
                st.json(skill_mapping.model_dump())
            
            with tab4:
                st.subheader("Tailored summary")
                st.write(rewrite_result.tailored_summary)

                st.subheader("Skills to Highlight")
                st.write(rewrite_result.skills_to_highlight)

                st.subheader("Rewritten Bullet Points")
                for item in rewrite_result.rewritten_bullets:
                    st.markdown(f"**Source Section:** {item.source_section}")
                    st.markdown(f"- Original: {item.original_bullet}")
                    st.markdown(f"- Rewritten: {item.rewritten_bullet}")
                    st.markdown(f"- Reason: {item.reason}")
                    st.markdown("---")

            with tab5:
                st.subheader("Validation Status")
                st.write(f"Overall valid: {validation_result.is_valid}")

                st.subheader("Approved Summary")
                st.write(validation_result.approved_summary)

                st.subheader("Approved Bullets")
                for bullet in validation_result.approved_bullets:
                    st.markdown(f"- {bullet}")

                st.subheader("Validation Issues")
                if validation_result.issues:
                    for issue in validation_result.issues:
                        st.markdown(f"**Issue Type:** {issue.issue_type}")
                        st.markdown(f"**Severity:** {issue.severity}")
                        st.markdown(f"**Original Text:** {issue.original_text}")
                        st.markdown(f"**Rewritten Text:** {issue.rewritten_text}")
                        st.markdown(f"**Reason:** {issue.reason}")
                        st.markdown(f"**Suggested Fix:** {issue.suggested_fix}")
                        st.markdown("---")
                else:
                    st.success("No validation issues found.")

            with tab6:
                st.subheader("ATS Alignment Score")
                st.metric("Alignment Score", ats_result.alignment_score)

                st.subheader("Matched Keywords")
                if ats_result.matched_keywords:
                    for keyword in ats_result.matched_keywords:
                        st.markdown(f"- {keyword}")
                else:
                    st.write("No matched keywords identified.")

                st.subheader("Missing Keywords")
                if ats_result.missing_keywords:
                    for keyword in ats_result.missing_keywords:
                        st.markdown(f"- {keyword}")
                else:
                    st.write("No major missing keywords identified.")

                st.subheader("Section Warnings")
                if ats_result.section_warnings:
                    for warning in ats_result.section_warnings:
                        st.markdown(f"- {warning}")
                else:
                    st.write("No major section warnings.")

                st.subheader("Content Warnings")
                if ats_result.content_warnings:
                    for warning in ats_result.content_warnings:
                        st.markdown(f"- {warning}")
                else:
                    st.write("No major content warnings.")

                st.subheader("Suggestions")
                if ats_result.suggestions:
                    for suggestion in ats_result.suggestions:
                        st.markdown(f"- {suggestion}")
                else:
                    st.write("No additional suggestions.")

            with tab7:
                st.subheader("Approved Tailored Resume")
                st.json(final_resume)

                st.download_button(
                    label="Download DOCX Resume",
                    data=docx_file.getvalue(),
                    file_name="approved_tailored_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

                st.download_button(
                    label="Download PDF Resume (Simple - ReportLab)",
                    data=pdf_file.getvalue(),
                    file_name="approved_tailored_resume_reportlab.pdf",
                    mime="application/pdf",
                )

                if pdf_bytes_rendercv:
                    st.download_button(
                        label="Download PDF Resume (Polished - RenderCV)",
                        data=pdf_bytes_rendercv,
                        file_name="approved_tailored_resume_rendercv.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.warning("RenderCV PDF could not be generated.")
                    if rendercv_pdf_error:
                        st.code(rendercv_pdf_error)

        except ValueError as e:
            st.error(f"Error processing resume: {e}")

