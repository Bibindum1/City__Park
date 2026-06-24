from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re

from .models import CustomUser


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(label='ФИО', max_length=150)
    phone = forms.CharField(label='Телефон', max_length=16)
    email = forms.EmailField(label='Email')

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'full_name',
            'phone',
            'email',
            'password1',
            'password2'
        )
        labels = {
            'username': 'Логин'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'username': 'Введите логин',
            'full_name': 'Иванов Иван Иванович',
            'phone': '8(999)123-45-67',
            'email': 'example@mail.ru',
            'password1': 'Введите пароль',
            'password2': 'Повторите пароль'
        }

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': placeholders.get(name, '')
            })

        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повтор пароля'

    def clean_username(self):
        username = self.cleaned_data['username']

        if not re.fullmatch(r'[A-Za-z0-9]+', username):
            raise ValidationError(
                'Логин должен содержать только латинские буквы и цифры.'
            )

        if len(username) < 6:
            raise ValidationError(
                'Логин должен быть не короче 6 символов.'
            )

        return username

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name'].strip()

        if not re.fullmatch(r'[А-Яа-яЁё\s-]+', full_name):
            raise ValidationError(
                'ФИО должно содержать только кириллицу, пробелы и дефис.'
            )

        return full_name

    def clean_phone(self):
        phone = self.cleaned_data['phone']

        if not re.fullmatch(r'8\(\d{3}\)\d{3}-\d{2}-\d{2}', phone):
            raise ValidationError(
                'Телефон должен быть в формате 8(999)123-45-67.'
            )

        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError(
                'Пользователь с таким телефоном уже существует.'
            )

        return phone

    def clean_email(self):
        email = self.cleaned_data['email']

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(
                'Пользователь с такой электронной почтой уже существует.'
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
    )

    error_messages = {
        'invalid_login': 'Неверный логин или пароль.',
        'inactive': 'Учётная запись отключена.'
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите логин',
            'autocomplete': 'off'
        })

        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'off'
        })