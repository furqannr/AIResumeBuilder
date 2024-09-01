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

# Initialize session state for storing resume text
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'edited_resume' not in st.session_state:
    st.session_state.edited_resume = ""

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
    if uploaded_file:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a professional resume based on the following text: {text}"
                }
            ],
            model="llama3-70b-8192",
        )
        st.session_state.resume_text = response.choices[0].message.content
        st.text_area("Generated Resume", st.session_state.resume_text, height=300)
    else:
        st.warning("Please upload a document first.")

# Resume Preview and Real-Time Editing
st.header("Resume Preview and Editing")

# Allow users to make real-time edits
if st.session_state.resume_text:  # Check if resume_text is not empty
    st.session_state.edited_resume = st.text_area("Edit Resume", st.session_state.resume_text, height=300)
else:
    st.session_state.edited_resume = ""

# PDF Download and Copy Management
st.header("Download and Save Resume")

if st.button("Download Resume"):
    if st.session_state.edited_resume:  # Check if edited_resume is not empty
        pdf = FPDF()
        pdf.add_page()

        # Add a Unicode font
        pdf.add_font("DejaVu", "", "/path/to/DejaVuSans.ttf", uni=True)  # Specify the correct path to the font file
        pdf.set_font("DejaVu", '', 24)
        pdf.cell(0, 10, "LISANDRO MILANESI", ln=True, align='C')
        pdf.set_font("DejaVu", '', 12)
        pdf.cell(0, 10, "716-555-0100 | lisandro@example.com | www.interestingsite.com", ln=True, align='C')
        pdf.ln(10)  # Line break

        # Add Profile section
        pdf.set_font("DejaVu", '', 16)
        pdf.cell(0, 10, "PROFILE", ln=True)
        pdf.set_font("DejaVu", '', 12)
        pdf.multi_cell(0, 10, "Assistant Hotel Manager with a warm and friendly demeanor. Skilled at conflict resolution. Team builder who is acutely attentive to employee and guest needs. Punctual problem solver and avid multitasker. Track record of being an essential part of the management team and instrumental in providing effective solutions that produce immediate impact and contribute to the establishment’s long-term success.")
        pdf.ln(5)  # Line break

        # Work Experience
        pdf.set_font("DejaVu", '', 16)
        pdf.cell(0, 10, "WORK EXPERIENCE", ln=True)
        pdf.set_font("DejaVu", '', 12)
        pdf.multi_cell(0, 10, st.session_state.edited_resume)  # Use the edited_resume text directly
        pdf.ln(5)  # Line break

        # Key Skills
        pdf.set_font("DejaVu", '', 16)
        pdf.cell(0, 10, "KEY SKILLS", ln=True)
        pdf.set_font("DejaVu", '', 12)
        pdf.multi_cell(0, 10, "\n".join([
            "• Budget management",
            "• Excellent listener",
            "• Friendly, courteous, & service oriented",
            "• Poised under pressure",
            "• Staff training & coaching",
            "• Recruiting & hiring talent",
            "• Quality assurance",
            "• Solid written & verbal communicator"
        ]))
        pdf.ln(5)  # Line break

        # Education
        pdf.set_font("DejaVu", '', 16)
        pdf.cell(0, 10, "EDUCATION", ln=True)
        pdf.set_font("DejaVu", '', 12)
        pdf.multi_cell(0, 10, "Bachelor of Science in Hospitality Management\nBellows College, June 20XX")
        pdf.ln(5)  # Line break

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
