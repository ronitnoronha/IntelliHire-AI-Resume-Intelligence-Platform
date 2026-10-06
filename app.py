import streamlit as st

from extractor import extract_name
from models import Resume
from nlp import preprocess_text
from parser import clean_resume_text, extract_text_from_pdf
from ranking import rank_resumes
from resume_parser import extract_sections

st.title("Resume Screener")

uploaded_files = st.file_uploader(
    "Upload Resumes", type=["pdf"], accept_multiple_files=True
)

jd_tab1, jd_tab2 = st.tabs(["Paste Job Description", "Upload Job Description File"])

with jd_tab1:
    job_description_input = st.text_area("Paste Job Description", height=180)

with jd_tab2:
    uploaded_jd_file = st.file_uploader(
        "Upload Job Description (PDF or TXT)", type=["pdf", "txt"]
    )

job_description = job_description_input
if uploaded_jd_file:
    if uploaded_jd_file.name.lower().endswith(".pdf"):
        job_description = clean_resume_text(
            extract_text_from_pdf(uploaded_jd_file.getvalue())
        )
    else:
        try:
            job_description = uploaded_jd_file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            job_description = uploaded_jd_file.getvalue().decode(
                "latin-1", errors="replace"
            )
    st.info(f"Loaded Job Description from: `{uploaded_jd_file.name}`")


if st.button("Analyze"):
    st.write("Processing...")

    if not uploaded_files:
        st.warning("Please upload at least one resume")
        st.stop()

    if not job_description:
        st.warning("Please enter a job description")
        st.stop()

    resumes = []

    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.getvalue()
        text = extract_text_from_pdf(file_bytes)
        text = clean_resume_text(text)
        processed_text = preprocess_text(text)
        name = extract_name(file_bytes)
        sections = extract_sections(text)

        # # ---------- DEBUG ----------
        # st.write("## Parsed Resume Sections")
        # st.json(sections)
        #
        # st.write("Processed Resume")
        # st.code(processed_text[:1000])
        # # ---------------------------

        resume = Resume(
            name=name,
            file=uploaded_file.name,
            content=text,
            processed_content=processed_text,
            education=sections["education"],
            experience=sections["experience"],
            projects=sections["projects"],
            skills=sections["skills"],
            certifications=sections["certifications"],
        )

        resumes.append(resume)

    results = rank_resumes(resumes, job_description)

    for candidate in results:
        st.subheader(candidate["name"])

        st.caption(candidate["resume"])

        st.metric("Overall ATS Score", f"{candidate['ats_score']}%")

        st.write(f"Semantic Match: {candidate['score']:.2f}%")

        st.write(f"Skill Coverage: {candidate['skill_coverage']}%")

        st.success(candidate["decision"])

        st.progress(candidate["ats_score"] / 100)

        if "ai" in candidate:
            ai = candidate["ai"]

            st.write("## 📝 Candidate Summary")
            st.info(ai.candidate_summary)

            st.write("## 💪 Strengths")
            for item in ai.strengths:
                st.success(item)

            st.write("## ⚠ Weaknesses")
            for item in ai.weaknesses:
                st.warning(item)

            st.write("## 📈 Resume Improvements")
            for item in ai.resume_improvements:
                st.write("•", item)

            st.write("## 💻 Technical Questions")
            for q in ai.technical_questions:
                st.write("•", q)

            st.write("## 🤝 Behavioral Questions")
            for q in ai.behavioral_questions:
                st.write("•", q)

            st.success(ai.recommendation)

        st.write("### ✅ Matched Skills")

        if candidate["matched_skills"]:
            for skill in candidate["matched_skills"]:
                st.write(f"• {skill.title()}")
        else:
            st.write("None")

        st.write("### ❌ Missing Skills")

        if candidate["missing"]:
            for skill in candidate["missing"]:
                st.write(f"• {skill.title()}")
        else:
            st.write("None")

        if candidate["email"]:
            st.write("📧", candidate["email"][0])
        else:
            st.write("📧 Not Found")

        if candidate["phone"]:
            st.write("📱", candidate["phone"][0])
        else:
            st.write("📱 Not Found")
