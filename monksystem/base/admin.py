from django.contrib import admin

# Register your models here.

from .models import UserProfile, Subject, Project, File, FileClaim

admin.site.register(UserProfile)
admin.site.register(Subject)
admin.site.register(Project)
admin.site.register(File)
admin.site.register(FileClaim)


