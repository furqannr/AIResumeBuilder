from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import urllib.parse
import streamlit as st

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def scrape_jobs(job_title: str, location: str):
    encoded_job_title = urllib.parse.quote_plus(job_title.lower())
    encoded_location = urllib.parse.quote_plus(location.lower())
    search_url = f"https://www.indeed.com/jobs?q={encoded_job_title}&l={encoded_location}&from=searchOnDesktopSerp"

    with st.spinner(f"Accessing URL: {search_url}"):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--headless')  # Optionally comment this out to debug

        with st.spinner("Starting Chrome WebDriver..."):
            driver = webdriver.Chrome(options=options)
            driver.get(search_url)

            print("Waiting for page to load...")
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'job_seen_beacon'))
                )
            except Exception as e:
                print(f"Error: {e}")
                driver.quit()
                return []

    with st.spinner("Parsing page content with BeautifulSoup..."):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

    jobs = []
    with st.spinner("Extracting job data..."):
        for job_card in soup.find_all('div', class_='job_seen_beacon'):
            try:
                # Extract title, company, and other fields
                title_element = job_card.find('h2', class_='jobTitle')
                title = title_element.get_text(strip=True) if title_element else 'N/A'
                link_element = job_card.find('a')
                link = "https://www.indeed.com" + link_element['href'] if link_element and link_element.has_attr('href') else 'N/A'

                # Check if the job title includes the search term (case insensitive)
                if job_title.lower() in title.lower():
                    jobs.append({
                        "title": title,
                        "link": link
                    })
                else:
                    print(f"Skipping job due to title mismatch: {title}")

            except AttributeError as e:
                print(f"Error extracting job details: {e}")

        print(f"Found {len(jobs)} jobs.")
    return jobs
