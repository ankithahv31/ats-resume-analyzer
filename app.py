import streamlit as st
import openai
import fitz  # PyMuPDF for PDF handling
import google.generativeai as genai
from google.generativeai import gapic as generativeai

from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Google API key from Streamlit secrets
api_key = st.secrets["google"]["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Function to extract text from PDF using PyMuPDF
def extract_text_from_pdf(uploaded_file):
    # Open the PDF using PyMuPDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()  # Extract text from each page
    return text

# Function to handle the Gemini response
def get_gemini_response(input_text, uploaded_file, prompt):
    # Extract text from the uploaded resume PDF
    resume_text = extract_text_from_pdf(uploaded_file)
    print(f"Input Text: {input_text}")
    print(f"Resume Text: {resume_text[:500]}...")  # Print first 500 characters of the resume text for debugging

    # Generate response from Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, resume_text, prompt])
    return response.text

# Streamlit interface
st.title("ATS Resume Analyzer")

# File uploader
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

# Input field for job description
input_text = st.text_area("Enter Job Description")

# If both job description and resume are provided
if uploaded_file and input_text:
    prompt = f"Analyze the following resume and job description for relevance and skills match. Provide a match percentage and highlight skill gaps.\n\nJob Description: {input_text}\n\nResume: {extract_text_from_pdf(uploaded_file)}"
    
    # Get response from Gemini model
    response_text = get_gemini_response(input_text, uploaded_file, prompt)
    
    # Display response
    st.subheader("Match Results")
    st.write(response_text)

else:
    st.write("Please upload a resume and enter the job description to get started.")
