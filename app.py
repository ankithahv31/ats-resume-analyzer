import base64
import streamlit as st
import io
from PIL import Image
from pdf2image import convert_from_bytes
import google.generativeai as genai
import re

# Configure Gemini API key
api_key = st.secrets["google"]["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Set of known technical skills
skills_list = [
    "Python", "Java", "JavaScript", "HTML", "CSS", "SQL", "Machine Learning", "Data Analysis",
    "Big Data", "AWS", "Docker", "Kubernetes", "React", "Node.js", "Git", "DevOps"
]

# Function to extract skills from text
def extract_skills(text):
    return [skill for skill in skills_list if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE)]

# Suggest improvements
def generate_skill_improvement_advice(resume_skills, job_skills):
    missing_skills = set(job_skills) - set(resume_skills)
    return (
        f"You might want to improve: {', '.join(missing_skills)}"
        if missing_skills else
        "Your skills align well with the job description!"
    )

# Convert PDF to image and encode first page
def input_pdf_setup(uploaded_file):
    try:
        images = convert_from_bytes(uploaded_file.read())
        if not images:
            raise ValueError("No pages found in PDF")
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        return [{
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }]
    except Exception as e:
        st.error(f"PDF Processing Error: {e}")
        return None

# Gemini call
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Streamlit UI
st.set_page_config(page_title="ATS Resume Expert")
st.title("🔍 ATS Resume Analyzer")

job_description = st.text_area("📄 Job Description")
uploaded_file = st.file_uploader("📎 Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume uploaded successfully.")

# Buttons
submit_eval = st.button("🧠 Professional Evaluation")
submit_advice = st.button("📌 Skill Gap Advice")
submit_match = st.button("📊 Match Percentage")

# Prompts
prompt_eval = (
    "You are an HR with tech expertise. Evaluate the resume based on job role. "
    "Highlight strengths and weaknesses."
)
prompt_match = (
    "You are an ATS scanner. Evaluate the resume and provide match percentage, "
    "missing keywords, and final remarks."
)

# Logic
if uploaded_file and (submit_eval or submit_advice or submit_match):
    pdf_content = input_pdf_setup(uploaded_file)
    if pdf_content is None:
        st.stop()

    if submit_eval:
        response = get_gemini_response(job_description, pdf_content, prompt_eval)
        st.subheader("📝 Evaluation:")
        st.write(response)

    elif submit_match:
        response = get_gemini_response(job_description, pdf_content, prompt_match)
        st.subheader("📊 Match Percentage:")
        st.write(response)

    elif submit_advice:
        resume_text_b64 = pdf_content[0]['data']
        resume_text = base64.b64decode(resume_text_b64).decode("utf-8", errors="ignore")
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_description)
        advice = generate_skill_improvement_advice(resume_skills, job_skills)
        st.subheader("📌 Skill Advice:")
        st.write(advice)

elif (submit_eval or submit_advice or submit_match) and not uploaded_file:
    st.warning("⚠️ Please upload a resume first.")
