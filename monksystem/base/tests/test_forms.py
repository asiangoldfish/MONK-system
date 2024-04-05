from django.test import TestCase
from base.forms import FileForm, UserRegistrationForm
from django.core.files.uploadedfile import SimpleUploadedFile

class TestForms(TestCase):

    def test_file_form_valid_data(self):
        file = SimpleUploadedFile(name='test_file.txt', content=b'Some file content', content_type='text/plain')
        form = FileForm(data={'title': 'Test File'}, files={'file': file})
        self.assertTrue(form.is_valid())

    def test_file_form_no_data(self):
        form = FileForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Expecting errors for 'title' and 'file'

    def test_user_registration_form_valid_data(self):
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'name': 'Test User',
            'mobile': 1234567890,
            'specialization': 'Tester',
            'password1': 'verysecurepassword123',
            'password2': 'verysecurepassword123'
        })
        self.assertTrue(form.is_valid())

    def test_user_registration_form_no_data(self):
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        # Expected to fail on required fields
        self.assertTrue(len(form.errors), 6)  # Expecting errors for 'username', 'name', 'mobile', 'specialization', 'password1', 'password2'
