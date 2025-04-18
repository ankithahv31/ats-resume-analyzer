import streamlit as st
import fitz  # PyMuPDF for PDF handling
import google.generativeai as genai
import os
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
    st.write(f"Job Description: {input_text[:200]}...")  # Show part of the job description
    st.write(f"Resume Text: {resume_text[:200]}...")  # Show part of the resume text

    # Generate response from Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, resume_text, prompt])
    return response.text

# Streamlit interface
st.title("ATS Resume Analyzer")

# File uploader for resume PDF
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

# Input field for job description
input_text = st.text_area("Enter Job Description")

# Buttons for actions
button_analyze = st.button("Analyze Resume")
button_reset = st.button("Reset Fields")
button_exit = st.button("Exit")

# If the user clicks the 'Analyze Resume' button
if button_analyze:
    if uploaded_file and input_text:
        prompt = f"Analyze the following resume and job description for relevance and skills match. Provide a match percentage and highlight skill gaps.\n\nJob Description: {input_text}\n\nResume: {extract_text_from_pdf(uploaded_file)}"
        
        with st.spinner("Analyzing... Please wait."):
            # Get response from Gemini model
            response_text = get_gemini_response(input_text, uploaded_file, prompt)
        
        # Display response
        st.subheader("Match Results")
        st.write(response_text)
    else:
        st.error("Please upload a resume and enter the job description to get started.")

# Reset button functionality
if button_reset:
    st.experimental_rerun()  # To reset the app and clear inputs

# Exit button functionality
if button_exit:
    st.stop()  # Stops the app execution
