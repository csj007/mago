# accounts/forms.py
from django import forms
from .models import Medicine
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=150)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['type', 'name', 'code', 'cas_number', 'specification', 'unit', 'quantity', 'manufacturer']
        widgets = {
            'cas_number': forms.TextInput(attrs={'placeholder': '可选'}),
            'specification': forms.TextInput(attrs={'placeholder': '可选'}),
            'unit': forms.TextInput(attrs={'placeholder': '可选'}),
            'quantity': forms.NumberInput(attrs={'placeholder': '可选'}),
            'manufacturer': forms.TextInput(attrs={'placeholder': '可选'}),
        }


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=150)
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("该用户名已存在")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            # 抛出错误，并绑定到 password2 字段
            self.add_error('password2', "两次输入的密码不一致")
