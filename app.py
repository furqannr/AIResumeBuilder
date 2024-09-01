import streamlit as st
import os
from groq import Groq
from docx import Document
from fpdf import FPDF
import pandas as pd
from datasets import load_dataset
import requests
from bs4 import BeautifulSoup

os.environ["GROQ_API_KEY"] = "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"
# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Streamlit app
st.title("Professional Resume Builder")

# Document Upload and Text Extraction
st.header("Document Upload")
uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        text = "\n".join([p.text for p in doc.paragraphs])
    
    st.text_area("Extracted Text", text, height=300)

# Resume Generation Using Meta LLaMA 3 70B Model
st.header("Resume Generation")

if st.button("Generate Resume"):
    if text:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a professional resume based on the following text: {text}"
                }
            ],
            model="meta-llama-3-70b",
        )
        resume_text = response.choices[0].message.content
        st.text_area("Generated Resume", resume_text, height=300)
    else:
        st.warning("Please upload a document first.")

# Resume Preview and Real-Time Editing
st.header("Resume Preview and Editing")

# Allow users to make real-time edits
if 'resume_text' in locals():
    edited_resume = st.text_area("Edit Resume", resume_text, height=300)
else:
    edited_resume = ""

# PDF Download and Copy Management
st.header("Download and Save Resume")

if st.button("Download Resume"):
    if edited_resume:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, edited_resume)
        pdf_output_path = "/tmp/resume.pdf"
        pdf.output(pdf_output_path)
        st.success("Resume PDF generated!")
        with open(pdf_output_path, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="resume.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Please generate or edit the resume first.")

# Job Search Integration
st.header("Job Search")

job_title = st.text_input("Enter Job Title")

if st.button("Search Jobs"):
    if job_title:
        url = f"https://api.indeed.com/ads/apisearch?q={job_title}&format=json&v=2"
        response = requests.get(url)
        jobs = response.json().get("results", [])
        if jobs:
            job_df = pd.DataFrame(jobs)
            st.write(job_df)
            job_df.to_excel("/tmp/job_list.xlsx", index=False)
            with open("/tmp/job_list.xlsx", "rb") as f:
                st.download_button(
                    label="Download Job List",
                    data=f,
                    file_name="job_list.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No jobs found.")
    else:
        st.warning("Please enter a job title.")

# Resume Customization Based on Job Postings
st.header("Resume Customization")

# Example usage of dataset integration for resume design
designs_dataset = load_dataset("Kunling/layoutlm_resume_data")

# Inspect dataset columns and use accordingly
st.write("Available columns:", designs_dataset['train'].column_names)
sample_data = designs_dataset['train'].select(range(5))
st.write("Sample data:", sample_data)

# Assuming you need a column to work with, adjust based on actual column names
# design_names = designs_dataset['train']['design_name']
# selected_design = st.selectbox("Choose a Resume Design", design_names)

# Automated Job Application
st.header("Automated Job Application")

# Placeholder for automated application logic
st.write("Automated job application is under development.")

# Set up environment variables and API keys
os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
