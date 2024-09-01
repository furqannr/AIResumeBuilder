from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

def apply_to_job(job_link, resume):
    driver = webdriver.Chrome()
    driver.get(job_link)
    
    # Wait until the element is present
    try:
        # Adjust the time to wait as needed (e.g., 10 seconds)
        resume_upload = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "resume_upload"))
        )
        resume_upload.send_keys(resume)
        
        apply_button = driver.find_element(By.ID, "apply_button")
        apply_button.click()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
