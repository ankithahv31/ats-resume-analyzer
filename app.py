import base64
import streamlit as st
import io
from PIL import Image
import fitz  # PyMuPDF for PDF handling
import google.generativeai as genai
import re

# Configure Gemini API key
api_key = st.secrets["google"]["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Function to get response from Gemini
def get_gemini_response(input_text, pdf_content_text, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content_text, prompt])
    return response.text

# Function to process PDF and extract text content
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            # Open the PDF file using fitz (PyMuPDF)
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            # Check if PDF has any pages
            if doc.page_count > 0:
                # Extract text from the first page
                page = doc.load_page(0)
                pdf_text = page.get_text("text")  # Extract text content from the page
                
                # If text is found, return it, otherwise raise an error
                if pdf_text:
                    return pdf_text
                else:
                    raise ValueError("No text found in the PDF")
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

# Function to extract skills from text
def extract_skills(text):
    return [skill for skill in skills_list if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE)]

# Function to generate skill improvement advice
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

# Prompts for Gemini API
input_prompt1 = """You are an HR with tech expertise. Evaluate the resume based on job role. Highlight strengths and weaknesses."""
input_prompt3 = """You are an ATS scanner. Evaluate the resume and provide match percentage, missing keywords, and final remarks."""

if submit1 and uploaded_file:
    # Process the uploaded resume PDF and extract text content using fitz
    pdf_content_text = input_pdf_setup(uploaded_file)
    
    # Generate the response using Gemini
    response = get_gemini_response(input_prompt1, pdf_content_text, input_text)
    st.subheader("Evaluation:")
    st.write(response)

elif submit3 and uploaded_file:
    # Process the uploaded resume PDF and extract text content using fitz
    pdf_content_text = input_pdf_setup(uploaded_file)
    
    # Generate the response using Gemini
    response = get_gemini_response(input_prompt3, pdf_content_text, input_text)
    st.subheader("Match Percentage:")
    st.write(response)

elif submit2 and uploaded_file:
    # Process the uploaded resume and extract skills
    resume_content = input_pdf_setup(uploaded_file)
    
    # Extract skills from resume and job description
    resume_skills = extract_skills(resume_content)
    job_skills = extract_skills(input_text)
    
    # Generate and display skill improvement advice
    advice = generate_skill_improvement_advice(resume_skills, job_skills)
    st.subheader("Skill Advice:")
    st.write(advice)

elif (submit1 or submit2 or submit3) and not uploaded_file:
    st.warning("Please upload a resume.")
