

import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import re
from pdf2image import convert_from_bytes
import google.generativeai as genai
genai.configure(api_key=st.secrets["google"]["GOOGLE_API_KEY"])
def get_gemini_response(input,pdf_content,prompt):
    model=genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input,pdf_content[0],prompt])
    return response.text
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            # Convert the PDF to image
            images = convert_from_bytes(uploaded_file.read(), poppler_path=r"C:\Program Files\poppler\Library\bin")
            
            # Check if the conversion produced any images
            if len(images) > 0:
                first_page = images[0]
                
                # Convert the first page image to bytes
                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                # Encode the image to base64
                pdf_parts = [{
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
                }]
                return pdf_parts
            else:
                raise ValueError("No pages found in the PDF")
        except Exception as e:
            raise ValueError(f"Error processing PDF: {e}")
    else:
        raise FileNotFoundError("No File Uploaded")
# Example list of skills to look for (you can expand this list)
skills_list = [
    "Python", "Java", "JavaScript", "HTML", "CSS", "SQL", "Machine Learning", "Data Analysis",
    "Big Data", "AWS", "Docker", "Kubernetes", "React", "Node.js", "Git", "DevOps"
]

# Function to extract skills from the job description and resume
def extract_skills(text):
    found_skills = []
    for skill in skills_list:
        if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills

# Function to generate skill improvement advice
def generate_skill_improvement_advice(resume_skills, job_skills):
    missing_skills = set(job_skills) - set(resume_skills)
    
    if missing_skills:
        improvement_advice = f"You might want to improve the following skills to better match the job description: {', '.join(missing_skills)}."
    else:
        improvement_advice = "Your skills align well with the job description! Keep up the good work."
    
    return improvement_advice

##Streamlit app
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description:",key="input")
uploaded_file=st.file_uploader("upload your resume(PDF)...",type=["pdf"])
if uploaded_file is not None:
    st.write("PDF uploaded Successfully")
submit1=st.button("Tell Me About the Resume")
submit2 = st.button("How Can I Improvise my skills")
submit3 = st.button("Percentage Match")

input_prompt1 = """
You are an experienced HR with Tech Experience in the field of any one job role from Data Science , Full stack ,Web Development,Big Data Engineering,DEVops,Data Analyst, your task is to review the provided resume aganist the job description for these profiles.
Please Share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the Strengths and weakness of the applicant in relation to the specified job requirements.   
"""
input_prompt3="""
you are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of any one job role data science,Data Science , Full stack ,Web Development,Big Data Engineering,DEVops,Data Analyst and ATS Functionality,
your task is to evaluate the resume aganist the provided job description. give me the percentage of match if the resume matches the job decription.First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt1,pdf_content,input_text)
        st.subheader("The Response is")
        st.write(response)
        
    else:
        st.write("please upload a resume")
elif submit3:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt3,pdf_content,input_text)
        st.subheader("The Response is")
        st.write(response)
        
    else:
        st.write("please upload a resume")
elif submit2:
       if uploaded_file is not None:
        # Extract text from resume and job description
        resume_content = input_pdf_setup(uploaded_file)
        resume_text = resume_content[0]['data']  # Extract text (base64)
        resume_text_decoded = base64.b64decode(resume_text).decode("utf-8", errors='ignore')
        
        # Extract skills from resume and job description
        resume_skills = extract_skills(resume_text_decoded)
        job_skills = extract_skills(input_text)
        
        # Generate skill improvement advice
        skill_improvement_advice = generate_skill_improvement_advice(resume_skills, job_skills)
        
        # Display the result
        st.subheader("How to Improve Your Skills")
        st.write(skill_improvement_advice)
        
       else:
        st.write("Please upload a resume")
       
