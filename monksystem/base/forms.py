from django import forms
from .models import File
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('title', 'file',)


class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=50, help_text='Required. Add your full name.')
    mobile = forms.IntegerField(help_text='Required. Add a contact number.')
    
    class Meta:
        model = User
        fields = ['username', 'name', 'mobile', 'password1', 'password2']
