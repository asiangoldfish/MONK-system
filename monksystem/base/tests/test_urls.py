from django.test import SimpleTestCase
from django.urls import reverse, resolve
from base.views import *

class TestUrls(SimpleTestCase):
    
    def test_home_url_resolves(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, homePage)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, loginPage)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, logoutUser)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, registerPage)

    def test_file_detail_url_resolves(self):
        url = reverse('file', kwargs={'file_id': 1})
        self.assertEquals(resolve(url).func, file)

    def test_view_file_url_resolves(self):
        url = reverse('viewFile')
        self.assertEquals(resolve(url).func, viewFile)

    def test_import_file_url_resolves(self):
        url = reverse('importFile')
        self.assertEquals(resolve(url).func, importFile)

    def test_import_multiple_files_url_resolves(self):
        url = reverse('importMultipleFiles')
        self.assertEquals(resolve(url).func, importMultipleFiles)

    def test_user_detail_url_resolves(self):
        url = reverse('user', kwargs={'pk': '1'})
        self.assertEquals(resolve(url).func, user)

    def test_subject_detail_url_resolves(self):
        url = reverse('subject', kwargs={'pk': 'S001'})
        self.assertEquals(resolve(url).func, subject)

    def test_view_subject_url_resolves(self):
        url = reverse('viewSubject')
        self.assertEquals(resolve(url).func, viewSubject)

    def test_project_detail_url_resolves(self):
        url = reverse('project', kwargs={'pk': 'P001'})
        self.assertEquals(resolve(url).func, project)

    def test_view_project_url_resolves(self):
        url = reverse('viewProject')
        self.assertEquals(resolve(url).func, viewProject)

    def test_add_project_url_resolves(self):
        url = reverse('addProject')
        self.assertEquals(resolve(url).func, addProject)

    def test_leave_project_url_resolves(self):
        url = reverse('leaveProject', kwargs={'project_id': 1})
        self.assertEquals(resolve(url).func, leaveProject)

    def test_edit_project_url_resolves(self):
        url = reverse('editProject', kwargs={'project_id': 1})
        self.assertEquals(resolve(url).func, editProject)

    def test_download_mfer_header_url_resolves(self):
        url = reverse('downloadHeaderMFER', kwargs={'file_id': 1})
        self.assertEquals(resolve(url).func, downloadHeaderMFER)

    def test_download_mwf_url_resolves(self):
        url = reverse('downloadMWF', kwargs={'file_id': 1})
        self.assertEquals(resolve(url).func, downloadMWF)

    def test_plot_graph_url_resolves(self):
        url = reverse('plotGraph', kwargs={'file_id': 1})
        self.assertEquals(resolve(url).func, plotGraph)

    def test_download_csv_format_url_resolves(self):
        url = reverse('downloadFormatCSV', kwargs={'file_id': 1})
        self.assertEquals(resolve(url).func, downloadFormatCSV)
