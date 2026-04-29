import streamlit as st
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

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
from src.utils.cost_calculator import UsageTracker, MODEL_NAME
import os

load_dotenv()


def get_secret(name: str, default: str | None = None) -> str | None:
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)


def resolve_openai_key(admin_access_input: str, user_openai_key: str) -> str | None:
    admin_access_key = get_secret("ADMIN_ACCESS_KEY")
    app_openai_key = get_secret("OPENAI_API_KEY")

    admin_access_input = (admin_access_input or "").strip()
    user_openai_key = (user_openai_key or "").strip()

    if admin_access_input and admin_access_key and admin_access_input == admin_access_key:
        return app_openai_key
    elif user_openai_key:
        return user_openai_key

    return None


st.set_page_config(page_title="AI Resume Alignment Assistant", page_icon=":briefcase:", layout="wide")

st.title("AI Resume Alignment Assistant :briefcase:")

if "results_ready" not in st.session_state:
    st.session_state["results_ready"] = False

with st.sidebar:

    st.subheader("Access the AI Resume Alignment Assistant")

    admin_access_input = st.text_input("Admin Access Key", type="password", help="For private/demo access.")

    user_openai_key = st.text_input("Your OpenAI API Key", type="password", placeholder="sk-...", help="Used only for the current session. Not stored or shared.")

    st.caption("To generate a resume, provide either your one OpenAI API Key of the admin access key.")

    if st.button("Reset App"):
        for key in [
            "results_ready",
            "parsed_resume",
            "parsed_jd",
            "skill_mapping",
            "rewrite_result",
            "validation_result",
            "ats_result",
            "final_resume",
            "docx_bytes",
            "pdf_bytes_rendercv",
            "rendercv_pdf_error",
            "usage_tracker",
        ]:
            st.session_state.pop(key, None)

        st.rerun()

st.write("Upload your resume and paste the job description to generate a tailored version of your resume that highlights the most relevant skills and experiences for the job.")

uploaded_resume = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

job_description = st.text_area("Paste the job description here", height=300, placeholder="Copy and paste the job description for the position you're applying for.")

if st.button("Generate Tailored Resume"):

    active_openai_key = resolve_openai_key(admin_access_input, user_openai_key)

    if not active_openai_key:
        st.warning("Missing API Key: Please provide either a valid admin access key or your OpenAI API key to proceed.")

    if not uploaded_resume:
        st.error("Please upload a resume.")
    elif not job_description.strip():
        st.error("Please paste the job description.")
    else:
        try:
            resume_text = load_resume_text(uploaded_resume)
            st.success("Resume loaded successfully!")

            tracker = UsageTracker()

            with get_openai_callback() as cb:
                parsed_resume = parse_resume(resume_text, openai_api_key=active_openai_key)
            tracker.record("Resume Parser", cb.prompt_tokens, cb.completion_tokens)

            with get_openai_callback() as cb:
                parsed_jd = parse_job_description(job_description, openai_api_key=active_openai_key)
            tracker.record("JD Parser", cb.prompt_tokens, cb.completion_tokens)

            with get_openai_callback() as cb:
                skill_mapping = map_skills(parsed_resume, parsed_jd, openai_api_key=active_openai_key)
            tracker.record("Skill Mapper", cb.prompt_tokens, cb.completion_tokens)

            with get_openai_callback() as cb:
                rewrite_result = rewrite_resume_content(
                    parsed_resume,
                    parsed_jd,
                    skill_mapping,
                    openai_api_key=active_openai_key,
                )
            tracker.record("Rewrite", cb.prompt_tokens, cb.completion_tokens)

            with get_openai_callback() as cb:
                validation_result = validate_rewrite(
                    parsed_resume,
                    parsed_jd,
                    skill_mapping,
                    rewrite_result,
                    openai_api_key=active_openai_key,
                )
            tracker.record("Validation", cb.prompt_tokens, cb.completion_tokens)

            with get_openai_callback() as cb:
                ats_result = check_ats_compatibility(
                    parsed_resume,
                    parsed_jd,
                    skill_mapping,
                    validation_result,
                    openai_api_key=active_openai_key,
                )
            tracker.record("ATS Check", cb.prompt_tokens, cb.completion_tokens)

            # Assembler internally calls the bullet condenser and skill categorizer chains.
            with get_openai_callback() as cb:
                final_resume = build_approved_tailored_resume(
                    parsed_resume,
                    parsed_jd,
                    rewrite_result,
                    validation_result,
                    openai_api_key=active_openai_key,
                )
            tracker.record("Condense + Categorize", cb.prompt_tokens, cb.completion_tokens)

            docx_file = generate_resume_docx(final_resume)
            # pdf_file_reportlab = generate_resume_pdf(final_resume)

            try:
                pdf_bytes_rendercv = generate_resume_pdf_rendercv(final_resume)
                rendercv_pdf_error = None
            except Exception as e:
                pdf_bytes_rendercv = None
                rendercv_pdf_error = str(e)

            # Save to session state
            st.session_state["parsed_resume"] = parsed_resume
            st.session_state["parsed_jd"] = parsed_jd
            st.session_state["skill_mapping"] = skill_mapping
            st.session_state["rewrite_result"] = rewrite_result
            st.session_state["validation_result"] = validation_result
            st.session_state["ats_result"] = ats_result
            st.session_state["final_resume"] = final_resume
            st.session_state["docx_bytes"] = docx_file.getvalue()
            st.session_state["pdf_bytes_rendercv"] = pdf_bytes_rendercv
            st.session_state["rendercv_pdf_error"] = rendercv_pdf_error
            st.session_state["usage_tracker"] = tracker
            st.session_state["results_ready"] = True

        except ValueError as e:
            st.error(f"Error processing resume: {e}")

if st.session_state.get("results_ready"):
    parsed_resume = st.session_state["parsed_resume"]
    parsed_jd = st.session_state["parsed_jd"]
    skill_mapping = st.session_state["skill_mapping"]
    rewrite_result = st.session_state["rewrite_result"]
    validation_result = st.session_state["validation_result"]
    ats_result = st.session_state["ats_result"]
    final_resume = st.session_state["final_resume"]
    docx_bytes = st.session_state["docx_bytes"]
    pdf_bytes_rendercv = st.session_state["pdf_bytes_rendercv"]
    rendercv_pdf_error = st.session_state["rendercv_pdf_error"]
    usage_tracker = st.session_state.get("usage_tracker")

    # Sidebar token & cost summary
    if usage_tracker is not None:
        with st.sidebar:
            st.markdown("---")
            st.subheader("Token Usage")
            st.caption(f"Model: `{MODEL_NAME}`")
            st.metric("Input tokens", f"{usage_tracker.total_input:,}")
            st.metric("Output tokens", f"{usage_tracker.total_output:,}")
            st.metric("Estimated cost (USD)", f"${usage_tracker.total_cost:.4f}")

            with st.expander("Per-chain breakdown"):
                if usage_tracker.breakdown:
                    for chain_name, usage in usage_tracker.breakdown.items():
                        st.markdown(
                            f"**{chain_name}** — "
                            f"{usage.input_tokens:,} in / "
                            f"{usage.output_tokens:,} out · "
                            f"${usage.cost:.4f}"
                        )
                else:
                    st.write("No usage recorded.")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "Parsed Resume",
            "Parsed JD",
            "Skill Mapping",
            "Tailored Rewrite",
            "Validation",
            "ATS Check",
            "Tailored Resume",
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

        # Header
        if final_resume.get("name"):
            st.markdown(f"### {final_resume['name']}")

        contact_bits = []
        if final_resume.get("email"):
            contact_bits.append(final_resume["email"])
        if final_resume.get("phone"):
            contact_bits.append(final_resume["phone"])
        if final_resume.get("location"):
            contact_bits.append(final_resume["location"])
        if contact_bits:
            st.caption(" · ".join(contact_bits))

        socials = final_resume.get("socials") or []
        if socials:
            social_bits = []
            for s in socials:
                label = (s.get("label") or "").strip()
                url = (s.get("url") or "").strip()
                if label and url:
                    social_bits.append(f"[{label}]({url})")
                elif label:
                    social_bits.append(label)
            if social_bits:
                st.markdown(" · ".join(social_bits))

        # Summary
        if final_resume.get("summary"):
            st.markdown("**Professional Summary**")
            st.write(final_resume["summary"])

        # Categorized skills
        skill_categories = final_resume.get("skill_categories") or []
        if skill_categories:
            st.markdown("**Skills**")
            for cat in skill_categories:
                cat_name = (cat.get("category") or "").strip()
                items = [str(i).strip() for i in (cat.get("items") or []) if str(i).strip()]
                if cat_name and items:
                    st.markdown(f"**{cat_name}:** {', '.join(items)}")
        elif final_resume.get("skills"):
            st.markdown("**Skills**")
            st.write(", ".join(final_resume["skills"]))

        # Experience
        experience_items = final_resume.get("experience") or []
        if experience_items:
            st.markdown("**Experience**")
            for exp in experience_items:
                role = (exp.get("role") or "").strip()
                company = (exp.get("company") or "").strip()
                client = (exp.get("client") or "").strip()
                location = (exp.get("location") or "").strip()
                start_date = (exp.get("start_date") or "").strip()
                end_date = (exp.get("end_date") or "").strip()

                title_parts = [p for p in [role, company] if p]
                if client:
                    title_parts.append(f"(Client: {client})")
                if title_parts:
                    st.markdown(f"**{' — '.join(title_parts)}**")

                meta_parts = [p for p in [location] if p]
                if start_date or end_date:
                    meta_parts.append(f"{start_date} – {end_date}".strip(" –"))
                if meta_parts:
                    st.caption(" · ".join(meta_parts))

                for bullet in exp.get("bullets") or []:
                    if bullet:
                        st.markdown(f"- {bullet}")

        # Projects
        project_items = final_resume.get("projects") or []
        if project_items:
            st.markdown("**Projects**")
            for proj in project_items:
                title = (proj.get("title") or "").strip()
                description = (proj.get("description") or "").strip()
                start_date = (proj.get("start_date") or "").strip()
                end_date = (proj.get("end_date") or "").strip()

                if title:
                    st.markdown(f"**{title}**")

                date_range = " – ".join(p for p in [start_date, end_date] if p)
                if date_range:
                    st.caption(date_range)

                if description:
                    st.write(description)

                for bullet in proj.get("bullets") or []:
                    if bullet:
                        st.markdown(f"- {bullet}")
                tech_stack = [str(t).strip() for t in (proj.get("tech_stack") or []) if str(t).strip()]
                if tech_stack:
                    st.caption(f"Tech Stack: {', '.join(tech_stack)}")

        # Certifications
        certs = final_resume.get("certifications") or []
        if certs:
            st.markdown("**Certifications**")
            for cert in certs:
                if cert:
                    st.markdown(f"- {cert}")

        # Education
        education_items = final_resume.get("education") or []
        if education_items:
            st.markdown("**Education**")
            for edu in education_items:
                degree = (edu.get("degree") or "").strip()
                area = (edu.get("area") or "").strip()
                institution = (edu.get("institution") or "").strip()
                location = (edu.get("location") or "").strip()
                start_date = (edu.get("start_date") or "").strip()
                end_date = (edu.get("end_date") or "").strip()

                head = ""
                if degree and area:
                    head = f"{degree}, {area}"
                elif degree:
                    head = degree
                elif area:
                    head = area

                line_parts = [p for p in [head, institution] if p]
                if line_parts:
                    st.markdown(f"**{' — '.join(line_parts)}**")

                meta_parts = [p for p in [location] if p]
                date_range = " – ".join(p for p in [start_date, end_date] if p)
                if date_range:
                    meta_parts.append(date_range)
                if meta_parts:
                    st.caption(" · ".join(meta_parts))

        with st.expander("View raw JSON"):
            st.json(final_resume)

        st.download_button(
            label="Download DOCX Resume",
            data=docx_bytes,
            file_name="approved_tailored_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
