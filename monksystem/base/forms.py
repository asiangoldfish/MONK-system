from django import forms
from .models import File
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('title', 'file',)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if isinstance(data, list):
            return [super(MultipleFileField, self).clean(d, initial) for d in data]
        return super(MultipleFileField, self).clean(data, initial)

class FileFieldForm(forms.Form):
    file_field = MultipleFileField()


class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=50, help_text='Required. Add your full name.')
    mobile = forms.IntegerField(help_text='Required. Add a contact number.')
    
    class Meta:
        model = User
        fields = ['username', 'name', 'mobile', 'password1', 'password2']
