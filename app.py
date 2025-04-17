import base64
import streamlit as st
import os
import io
from PIL import Image
from pdf2image import convert_from_bytes
import google.generativeai as genai
import re

# Configure Gemini API key
api_key = st.secrets["google"]["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Function to get response from Gemini
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Function to process PDF and convert to base64
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            images = convert_from_bytes(uploaded_file.read())
            if images:
                first_page = images[0]
                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                pdf_parts = [{
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }]
                return pdf_parts
            else:
                raise ValueError("No pages found in PDF")
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
    else:
        st.warning("No file uploaded.")

# Skill extraction helpers
skills_list = [
    "Python", "Java", "JavaScript", "HTML", "CSS", "SQL", "Machine Learning", "Data Analysis",
    "Big Data", "AWS", "Docker", "Kubernetes", "React", "Node.js", "Git", "DevOps"
]

def extract_skills(text):
    return [skill for skill in skills_list if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE)]

def generate_skill_improvement_advice(resume_skills, job_skills):
    missing_skills = set(job_skills) - set(resume_skills)
    if missing_skills:
        return f"You might want to improve: {', '.join(missing_skills)}"
    return "Your skills align well with the job description!"

# Streamlit App UI
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Resume Analyzer")

input_text = st.text_area("Job Description:")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file:
    st.success("Resume uploaded successfully.")

submit1 = st.button("Professional Evaluation")
submit2 = st.button("Skill Gap Advice")
submit3 = st.button("Match Percentage")

input_prompt1 = """You are an HR with tech expertise. Evaluate the resume based on job role. Highlight strengths and weaknesses."""
input_prompt3 = """You are an ATS scanner. Evaluate the resume and provide match percentage, missing keywords, and final remarks."""

if submit1 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_prompt1, pdf_content, input_text)
    st.subheader("Evaluation:")
    st.write(response)

elif submit3 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_prompt3, pdf_content, input_text)
    st.subheader("Match Percentage:")
    st.write(response)

elif submit2 and uploaded_file:
    resume_content = input_pdf_setup(uploaded_file)
    resume_text = resume_content[0]['data']
    resume_text_decoded = base64.b64decode(resume_text).decode("utf-8", errors='ignore')
    resume_skills = extract_skills(resume_text_decoded)
    job_skills = extract_skills(input_text)
    advice = generate_skill_improvement_advice(resume_skills, job_skills)
    st.subheader("Skill Advice:")
    st.write(advice)

elif (submit1 or submit2 or submit3) and not uploaded_file:
    st.warning("Please upload a resume.")
