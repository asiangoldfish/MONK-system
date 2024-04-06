from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time

class TestProjectCreationAndView(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_register_create_and_view_project(self):
        # Register a new user
        self.register_user("newuser", "Test User", "1234567890", "Tester", "testpassword123")

        # Create a new project and add self as the user
        self.create_project("Test REK", "Test Description")

        # View the details of the created project
        self.view_project_details("Test REK")

    def register_user(self, username, full_name, mobile, specialization, password):
        self.browser.get(f"{self.live_server_url}/register/")
        self.browser.find_element(By.NAME, "username").send_keys(username)
        self.browser.find_element(By.NAME, "name").send_keys(full_name)
        self.browser.find_element(By.NAME, "mobile").send_keys(mobile)
        self.browser.find_element(By.NAME, "specialization").send_keys(specialization)
        self.browser.find_element(By.NAME, "password1").send_keys(password)
        self.browser.find_element(By.NAME, "password2").send_keys(password)
        self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(2)
        WebDriverWait(self.browser, 10).until(EC.url_changes)
        
    def create_project(self, rek_nummer, description):
        # Navigate to the Add Project page
        self.browser.get(f"{self.live_server_url}/addProject/")

        # Fill out the REK nummer and description fields
        self.browser.find_element(By.NAME, "rekNummer").send_keys(rek_nummer)
        self.browser.find_element(By.NAME, "description").send_keys(description)
    
        user_dropdown_trigger = self.browser.find_element(By.XPATH, "//label[contains(text(), 'User(s)')]/following-sibling::div")
        user_dropdown_trigger.click()
        time.sleep(2)  # Adjust based on the responsiveness of your application

        # Select the "Test User" option from the dropdown
        # The exact method to locate and click the option depends on how the dropdown is implemented
        test_user_option = self.browser.find_element(By.XPATH, "//option[contains(text(), 'Test User')]")
        test_user_option.click()
        time.sleep(2)  # Give some time for the action to be registered

        # Submit the form to create the project
        submit_button = self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()
        time.sleep(2)  # Wait for the submission to process and for the page to load
    
        
    def view_project_details(self, rek_nummer):
        self.browser.get(f"{self.live_server_url}/viewProject/")
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, rek_nummer))
        )
        project_link = self.browser.find_element(By.LINK_TEXT, rek_nummer)
        project_link.click()
        time.sleep(2)
        WebDriverWait(self.browser, 10).until(EC.url_changes)