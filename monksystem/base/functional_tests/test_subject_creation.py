from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time

class TestSubjectCreationAndView(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_subject_creation_and_view(self):
        # Register a new user
        self.register_user("newuser", "Test User", "1234567890", "Tester", "testpassword123")

        # Navigate to 'Add Subject' from the home page and create a new subject
        self.create_subject("S001", "John Doe", "Male", "1990-01-01")

        # View the details of the created subject
        self.view_subject_details("S001")

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

    def create_subject(self, subject_id, name, gender, birth_date):
        self.browser.get(f"{self.live_server_url}/addSubject/")

        #self.browser.find_element(By.LINK_TEXT, "Add Subject").click()
        self.browser.find_element(By.NAME, "subject_id").send_keys(subject_id)
        self.browser.find_element(By.NAME, "name").send_keys(name)
        self.browser.find_element(By.NAME, "gender").send_keys(gender)
        self.browser.find_element(By.NAME, "birth_date").send_keys(birth_date)
        self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h5")))

    def navigate_to_view_subjects(self):
        self.browser.find_element(By.LINK_TEXT, "View Subjects").click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "container")))

    def view_subject_details(self, subject_id):
        self.browser.find_element(By.LINK_TEXT, subject_id).click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "card-header")))
