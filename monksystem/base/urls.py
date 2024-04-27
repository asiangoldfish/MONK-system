from django.urls import path
from . import views 



urlpatterns = [
    path('', views.homePage, name="home"),
    path('about/', views.aboutPage, name="about"),
    path('contact/', views.contactPage, name="contact"),
    
    path('accounts/login/', views.loginPage, name='login'),
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser, name = "logout"),
    path('register/', views.registerPage, name = "register"),

    path('viewFile/', views.viewFile, name='viewFile'),    
    path('uploadFile/', views.uploadFile, name='uploadFile'),
    path('uploadMultipleFiles/', views.uploadMultipleFiles, name='uploadMultipleFiles'),

    path('file/<int:file_id>/', views.file, name='file'),    
    path('import/<int:file_id>/', views.importFile, name='importFile'),

    path('user/<str:pk>', views.user, name="user"),
    path('viewUser/', views.viewUser, name = "viewUser"),

    path('subject/<str:pk>', views.subject, name="subject"),
    path('viewSubject/', views.viewSubject, name = "viewSubject"),
    path('addSubject/', views.addSubject, name = "addSubject"),

    path('project/<str:pk>', views.project, name="project"),
    path('viewProject/', views.viewProject, name = "viewProject"),
    path('addProject/', views.addProject, name = "addProject"),
    path('leaveProject/<int:project_id>/', views.leaveProject, name='leaveProject'),
    path('editProject/<int:project_id>/', views.editProject, name='editProject'),
    
    path('download-MFER-Header/<int:file_id>/', views.downloadHeaderMFER, name='downloadHeaderMFER'),
    path('download-MWF/<int:file_id>/', views.downloadMWF, name='downloadMWF'),
    path('plotGraph/<int:file_id>/', views.plotGraph, name='plotGraph'),
    path('download-CSV-Format/<int:file_id>/', views.downloadFormatCSV, name='downloadFormatCSV'),
    
]