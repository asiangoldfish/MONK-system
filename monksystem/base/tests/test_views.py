import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from base.models import UserProfile, File, Subject, Project, Vitals, FileClaim
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile

class TestViews(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        
        # Create a UserProfile instance
        self.user_profile = UserProfile.objects.create(
            user=self.user, name='Test User', mobile='1234567890', specialization='Test Specialization')
        
        # Create a File instance
        self.test_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        self.test_file.write(b'Some file content')
        self.test_file.seek(0)
        self.file = File.objects.create(title="Test File", file=SimpleUploadedFile(self.test_file.name, self.test_file.read(), content_type='text/plain'))
        
        # Create a Subject instance
        self.subject = Subject.objects.create(subject_id='S001', name='Test Subject', gender='Male', file=self.file)

        
        # Create a Project instance
        self.project = Project.objects.create(rekNummer='R001', description='Test Project Description')
        self.project.users.add(self.user_profile)
        self.project.subjects.add(self.subject)
        
        # Create a Vitals instance
        self.vitals = Vitals.objects.create(subject=self.subject, description='Test Vitals', heartRate=80)

        # Create a FileClaim instance
        self.file_claim = FileClaim.objects.create(user=self.user_profile, file=self.file)
    
    def tearDown(self):
        # Clean up files and temporary files
        self.test_file.close()
    
    def test_homePage_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')
        self.assertTrue('files' in response.context)

    def test_subject_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('subject', kwargs={'pk': self.subject.subject_id}))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/subject.html')
    
    def test_project_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('project', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/project.html')
        self.assertEqual(response.context['project'], self.project)
        
    def test_viewUser(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('viewUser'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/view_user.html')
        
    def test_user_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user', kwargs={'pk': self.user.id}))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/user.html')  

    def test_registerPage_POST(self):
        # Simulate a POST request to register a new user
        response = self.client.post(reverse('register'), data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'name': 'New User',
            'mobile': '0987654321',
            'specialization': 'New Specialization'
        })
        # redirect to home page upon successful registration
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(name='New User').exists())
            

    def test_importFile_POST(self):
            self.client.login(username='testuser', password='testpass')
            # Create a temporary file mimicking an .MWF file upload
            with tempfile.NamedTemporaryFile(suffix=".MWF", delete=False) as tmp_file:
                tmp_file.write(b'This is a test MWF content')
                tmp_file.seek(0)  # Go back to the beginning of the file
                # Prepare the POST data
                post_data = {
                    'title': 'Uploaded Test File',
                    'file': SimpleUploadedFile(name='test.MWF', content=tmp_file.read(), content_type='application/octet-stream'),
                    'submitted': 'true'  # Include the hidden field 'submitted'
                }
                # Make a POST request to the importFile view
                response = self.client.post(reverse('importFile'), data=post_data, follow=True)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertTrue(File.objects.filter(title='Uploaded Test File').exists(), msg="File object was not created")