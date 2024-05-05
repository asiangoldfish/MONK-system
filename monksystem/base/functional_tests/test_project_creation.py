from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .test_user_registration import register_user
import time

class TestProjectCreationAndView(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_register_user_and_create_project(self):
        # Register a new user
        register_user(self.browser, self.live_server_url)
        time.sleep(2)
        # Create a new project and add self as the user
        self.create_project("Test REK", "Test Description")
        # View, edit and update project
        self.edit_and_update_project()
        # Leave project
        self.leave_project()

    def create_project(self, rek_nummer, description):
        # Navigate to the Add Project page
        self.browser.get(f"{self.live_server_url}/addProject/")
        # Fill out the REK nummer and description fields
        self.browser.find_element(By.NAME, "rekNummer").send_keys(rek_nummer)
        self.browser.find_element(By.NAME, "description").send_keys(description)
        # Locate the user dropdown and create a Select object
        user_select = Select(self.browser.find_element(By.NAME, "users"))
        # Select the first user in the dropdown
        user_select.select_by_index(0)  # index 0 might be a placeholder or empty option, hence index 1 is used
        # Submit the form to create the project
        time.sleep(1)
        submit_button = self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()
        time.sleep(2)  # Wait for the submission to process and for the page to load

    def edit_and_update_project(self):
        # Navigate to the edit page of the project
        self.browser.find_element(By.LINK_TEXT, "Edit Project").click()
        time.sleep(2)  # Wait for the edit page to load

        # Update project by clicking the appropriate button
        # We find the button by its text and tag name since it's a <button> and not a <input>
        update_button = self.browser.find_element(By.XPATH, "//button[text()='Update Project']")
        update_button.click()
        time.sleep(2)  # Wait for the update to process


    def leave_project(self):
        # Click on leave project
        self.browser.find_element(By.LINK_TEXT, "Leave Project").click()
        time.sleep(2)  # Wait for the leave process to complete
