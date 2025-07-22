# accounts/forms.py
from django import forms
from .models import Medicine

class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=150)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['type', 'name', 'code']
