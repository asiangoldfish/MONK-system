from django.contrib import admin

# Register your models here.

from .models import Doctor, Subject, Project, Vitals, File, FileClaim

admin.site.register(Doctor)
admin.site.register(Subject)
admin.site.register(Project)
admin.site.register(Vitals)
admin.site.register(File)
admin.site.register(FileClaim)


