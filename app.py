import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from helper_functions.save_to_pdf import save_to_pdf
from helper_functions.scrape_jobs import scrape_jobs
from helper_functions.apply_to_job import apply_to_job

from models.resume_creator_model import resume_creator_model
from models.cv_creator_model import cv_creator_model
from models.success_analyzer_model import application_success_analyer

load_dotenv()


# Set up API key environment variable
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Streamlit App Title and Subtitle
st.title('AI Career Companion')
st.subheader('Automate your professional career with us')

# Choose Operation
st.write('<h3 style="font-size:20px">Choose Operation</h3>', unsafe_allow_html=True)

# Initialize session state for operation
if 'operation' not in st.session_state:
    st.session_state.operation = None

# Layout for operation selection buttons
col1, col2 = st.columns(2)

with col1:    
    resource_creator = st.button('Job Resource Creator')
    if resource_creator:
        st.session_state.operation = 'resource-creator'

with col2:
    automate_application = st.button('Automate Application')
    if automate_application:
        st.session_state.operation = 'automate_application'

# Display content based on the selected operation
if st.session_state.operation == 'resource-creator':
    st.write('<h4 style="font-size:19px">Upload your profile, job description, and our AI model will check the chances of getting an interview and create a resume and CV specifically for that job opening.</h4>', unsafe_allow_html=True)

    # Input for user profile
    st.session_state.user_profile = st.text_area(
        "Enter your profile",
        placeholder="Tell us about yourself and your professional background. The more detailed you are, the better we will perform",
        value=st.session_state.get('user_profile', "")
    )

    # Input for job description
    st.session_state.job_description = st.text_area(
        "Enter job description",
        placeholder="Enter the job description you want to apply for",
        value=st.session_state.get('job_description', "")
    )

    create_button = st.button('Create Resume and CV')

    if create_button:
        if st.session_state.user_profile and st.session_state.job_description:
            with st.spinner('Creating resume and CV for your job application...'):
                resume_response = resume_creator_model(st.session_state.user_profile, st.session_state.job_description, client)
                cv_response = cv_creator_model(st.session_state.user_profile, st.session_state.job_description, client)

            st.subheader('Generated Resume')
            st.write(resume_response)
            st.subheader('Generated CV')
            st.write(cv_response)

            with st.spinner('Analyzing candidate application'):
                analysis_response = application_success_analyer(cv_response, resume_response, st.session_state.job_description, client)
            st.subheader('Application analysis')
            st.write(analysis_response)

            with st.spinner('Converting to PDF...'):
                resume_pdf = save_to_pdf(resume_response)
                cv_pdf = save_to_pdf(cv_response)

            resume_downloader = st.download_button(
                label="Download Resume",
                data=resume_pdf,
                file_name="resume.pdf",
                mime="application/pdf"
            )
            cv_downloader = st.download_button(
                label="Download CV",
                data=cv_pdf,
                file_name="resume.pdf",
                mime="application/pdf"
            )
        else:
            st.error('Please enter both user profile and job description')

elif st.session_state.operation == 'automate_application':
    st.write('<h4 style="font-size:19px">Enter the job title you want to search for, and our AI model will apply on your behalf.</h4>', unsafe_allow_html=True)

    # Inputs for the job search
    user_profile = st.text_area(
        "Enter your profile",
        placeholder="Tell us about yourself and your professional background. The more detailed you are, the better we will perform",
    )

    job_title = st.text_input("Enter the job title", placeholder="e.g., Data Scientist")
    location = st.text_input("Enter the job location", placeholder="e.g., New York")

    search_button = st.button('Search Jobs')

    # Use session_state to store job search results
    if search_button and job_title and location:
        jobs = scrape_jobs(job_title, location)
        st.session_state['jobs'] = jobs  # Store jobs in session state
        st.write(f"Found {len(jobs)} jobs for {job_title} in {location}")
        
    # Display jobs if available in session state
    if 'jobs' in st.session_state:
        jobs = st.session_state['jobs']
        for job in jobs:
            st.write(f"[{job['title']}]({job['link']})")
        
        # Generate Resume
        if st.button("Generate Resume"):
            if jobs:
                job_details = jobs[0]
                resume = resume_creator_model(user_profile, job_details, client)
                st.write("Generated Resume:")
                st.text(resume)
                st.session_state['resume'] = resume  

        resume_pdf_generated = save_to_pdf(st.session_state['resume'])

        # Apply Automatically
        if st.button("Apply Automatically"):
            if 'resume' in st.session_state:
                resume = resume_pdf_generated
                job_link = jobs[0]['link']
                apply_to_job(job_link, resume)
                st.write("Applied to the job successfully!")