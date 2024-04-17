from django.test import TestCase
from django.contrib.auth.models import User
from base.models import UserProfile, File, Subject, Project, FileClaim
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import datetime

class TestModels(TestCase):

    def setUp(self):
        # User object
        self.user = User.objects.create_user(username='testuser', password='12345')

        # UserProfile object
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            name='Test User',
            mobile=123456789,
            specialization='Specialization'
        )

        # File object
        self.file = File.objects.create(
            title='Test File',
            file=SimpleUploadedFile(name='test_file.txt', content=b'Some file content', content_type='text/plain')
        )

        # Subject object
        self.subject = Subject.objects.create(
            subject_id='S001',
            name='Test Subject',
            gender='Male',
            birth_date=timezone.now().date() - datetime.timedelta(days=365*20),
            file=self.file
        )
    
    def test_user_profile_creation_and_str(self):
        self.assertEqual(str(self.user_profile), 'Test User')

    def test_file_creation_and_str(self):
        self.assertEqual(str(self.file), 'Test File')

    def test_subject_creation_and_str(self):
        self.assertEqual(str(self.subject), 'S001 - Test Subject')

    def test_project_creation_and_str(self):
        project = Project.objects.create(rekNummer='R001', description='Test Project Description')
        project.users.add(self.user_profile)
        self.assertEqual(str(project), 'R001')


    def test_file_claim_creation_and_str(self):
        file_claim = FileClaim.objects.create(
            user=self.user_profile,
            file=self.file
        )
        expected_str = f"{self.file.title} claimed by {self.user_profile.name}"
        self.assertEqual(str(file_claim), expected_str)
