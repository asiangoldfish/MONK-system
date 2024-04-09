from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .test_user_registration import register_user
import time

class TestSubjectCreationAndView(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_user_registration_and_subject_creation(self):
        # Register a new user
        register_user(self.browser, self.live_server_url)
        time.sleep(2)
        # Navigate to 'Add Subject' from the home page and create a new subject
        self.create_subject("S001", "John Doe", "Male", "1990-01-01")
        # View the details of the created subject
        self.view_subject_details("S001")


    def create_subject(self, subject_id, name, gender, birth_date):
        # Directly navigate to the 'Add Subject' page
        self.browser.get(f"{self.live_server_url}/addSubject/")

        # Fill the subject form
        self.browser.find_element(By.NAME, "subject_id").send_keys(subject_id)
        self.browser.find_element(By.NAME, "name").send_keys(name)
        self.browser.find_element(By.NAME, "gender").send_keys(gender)
        self.browser.find_element(By.NAME, "birth_date").send_keys(birth_date)
        time.sleep(1)

        # Find the submit button and click it to create the subject
        self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(2)

    def navigate_to_view_subjects(self):
        self.browser.get(f"{self.live_server_url}/viewSubject/")
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "container")))

    def view_subject_details(self, subject_id):
        # Replace LINK_TEXT with a more specific selector, for example using an ID or a data attribute
        self.browser.get(f"{self.live_server_url}/subject/{subject_id}")
        
