from django.test import SimpleTestCase
from django.urls import reverse, resolve
from base.views import *


class TestUrls(SimpleTestCase):
    
    #  Checks if the URL named 'home' resolves to the home view function as defined in views.py
    def test_home_url_resolves(self):
        # Use reverse to find the URL path associated with a name. Reverse the 'home' URL.
        url = reverse('home')
        # Use resolve to find the view function associated with the path. Resolve the URL to a view function. 
        resolved = resolve(url).func
        # Use assertEqual to ensure the view function is the one intended. Assert that the resolved view function is homePage.
        self.assertEquals(resolved, homePage)
    
    def test_about_url_resolves(self):
        url = reverse('about')
        resolved = resolve(url).func
        self.assertEquals(resolved, aboutPage)
    
    def test_contact_url_resolves(self):
        url = reverse('contact')
        resolved = resolve(url).func
        self.assertEquals(resolved, contactPage)
    
    def test_login_url_resolves(self):
        url = reverse('login')
        resolved = resolve(url).func
        self.assertEquals(resolved, loginPage)
    
    def test_logout_url_resolves(self):
        url = reverse('logout')
        resolved = resolve(url).func
        self.assertEquals(resolved, logoutUser)
    
    def test_register_url_resolves(self):
        url = reverse('register')
        resolved = resolve(url).func
        self.assertEquals(resolved, registerPage)
    
    def test_view_user_url_resolves(self):
        # Testing the URL for viewing all users
        url = reverse('viewUser')
        resolved = resolve(url).func
        self.assertEquals(resolved, viewUser)

    def test_subject_detail_url_resolves(self):
        # Testing dynamic URL for subject detail view
        url = reverse('subject', kwargs={'pk': 'S001'})
        resolved = resolve(url).func
        self.assertEquals(resolved, subject)

    def test_view_subject_url_resolves(self):
        # Testing the URL for viewing all subjects
        url = reverse('viewSubject')
        resolved = resolve(url).func
        self.assertEquals(resolved, viewSubject)

    def test_add_subject_url_resolves(self):
        # Testing the URL for adding a new subject
        url = reverse('addSubject')
        resolved = resolve(url).func
        self.assertEquals(resolved, addSubject)

    def test_project_detail_url_resolves(self):
        # Testing dynamic URL for project detail view
        url = reverse('project', kwargs={'pk': 'P001'})
        resolved = resolve(url).func
        self.assertEquals(resolved, project)

    def test_view_project_url_resolves(self):
        # Testing the URL for viewing all projects
        url = reverse('viewProject')
        resolved = resolve(url).func
        self.assertEquals(resolved, viewProject)

    def test_add_project_url_resolves(self):
        # Testing the URL for adding a new project
        url = reverse('addProject')
        resolved = resolve(url).func
        self.assertEquals(resolved, addProject)

    def test_view_vitals_url_resolves(self):
        # Testing the URL for viewing all vitals
        url = reverse('viewVitals')
        resolved = resolve(url).func
        self.assertEquals(resolved, viewVitals)
    
    def test_view_file_url_resolves(self):
        url = reverse('viewFile')
        resolved = resolve(url).func
        self.assertEquals(resolved, viewFile)
    
    def test_import_file_url_resolves(self):
        url = reverse('importFile')
        resolved = resolve(url).func
        self.assertEquals(resolved, importFile)
        
    # For URLs with dynamic segments, we need to provide example values:
    def test_file_detail_url_resolves(self):
        url = reverse('file', kwargs={'file_id': 1})
        resolved = resolve(url).func
        self.assertEquals(resolved, file)
        
    def test_user_detail_url_resolves(self):
        url = reverse('user', kwargs={'pk': 'some-username'})
        resolved = resolve(url).func
        self.assertEquals(resolved, user)