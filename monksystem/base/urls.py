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
    path('importFile/', views.importFile, name='importFile'),

    path('file/<int:file_id>/', views.file, name='file'),    
    path('claim/<int:file_id>/', views.claimFile, name='claimFile'),

    path('user/<str:pk>', views.user, name="user"),
    path('viewUser/', views.viewUser, name = "viewUser"),
    path('addUser/', views.viewUser, name = "addUser"),

    path('subject/<str:pk>', views.subject, name="subject"),
    path('viewSubject/', views.viewSubject, name = "viewSubject"),
    path('addSubject/', views.addSubject, name = "addSubject"),

    path('project/<str:pk>', views.project, name="project"),
    path('viewProject/', views.viewProject, name = "viewProject"),
    path('addProject/', views.addProject, name = "addProject"),

    path('viewVitals/', views.viewVitals, name = "viewVitals"),
    #path('addVitals/', views.addVitals, name = "addVitals"),
    
]