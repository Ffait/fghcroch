from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from creditcards.forms import *

from .models import *


class AddProdForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label = "Категория не выбрана"

    class Meta:
        model = Products
        fields = ['name', 'content', 'structure', 'thickness', 'tr_length', 'material', 'size', 'color', 'photo', 'price', 'cat', 'slug']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control text-bg-light'}),
                   'content': forms.Textarea(attrs={'class': 'form-control text-bg-light'}),
                   'structure': forms.TextInput(attrs={'class': 'form-control text-bg-light'}),
                   'thickness': forms.NumberInput(attrs={'class': 'form-control text-bg-light'}),
                   'tr_length': forms.NumberInput(attrs={'class': 'form-control text-bg-light'}),
                   'material': forms.TextInput(attrs={'class': 'form-control text-bg-light'}),
                   'size': forms.NumberInput(attrs={'class': 'form-control text-bg-light'}),
                   'color': forms.TextInput(attrs={'class': 'form-control text-bg-light'}),
                   'photo': forms.FileInput(attrs={'class': 'form-control form-control-sm text-bg-light'}),
                   'price': forms.NumberInput(attrs={'class': 'form-control text-bg-light'}),
                   'cat': forms.Select(attrs={'class': 'form-control text-bg-light'}),
                   'slug': forms.TextInput(attrs={'class': 'form-control text-bg-light'})
                   }


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control text-bg-light'}))
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control text-bg-light'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control text-bg-light'}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control text-bg-light'}))
    first_name = forms.CharField(label='Имя', required=False, widget=forms.TextInput(attrs={'class': 'form-control text-bg-light'}))
    last_name = forms.CharField(label='Фамилия', required=False, widget=forms.TextInput(attrs={'class': 'form-control text-bg-light'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control text-bg-light'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control text-bg-light'}))


class ContactForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control text-bg-light'}))
    content = forms.CharField(label='Сообщение', widget=forms.Textarea(attrs={'class': 'form-control text-bg-light'}))
    subject = forms.CharField(label='Тема сообщения', widget=forms.TextInput(attrs={'class': 'form-control text-bg-light'}))

    class Meta:
        model = Feedback
        fields = ('subject', 'email', 'content')


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class': 'form-control text-bg-light'}))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-control text-bg-light'}))
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control text-bg-light'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('birth_date', 'avatar')
        widgets = {'birth_date': forms.DateInput(attrs={'class': 'form-control text-bg-light', 'type': 'date'}),
                   'avatar': forms.FileInput(attrs={'class': 'form-control text-bg-light'})}


class UserPasswordChangeForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Введите новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-control text-bg-light'}))
    new_password2 = forms.CharField(label='Повторите новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-control text-bg-light'}))


class CommentCreateForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 5, 'placeholder': 'Комментарий', 'class': 'form-control text-bg-light'}))

    class Meta:
        model = Comment
        fields = ('content',)


class CartItemForm(forms.ModelForm):
    class Meta:
        model = Cartitem
        fields = []


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method', 'delivery_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control text-bg-light'}),
            'delivery_method': forms.Select(attrs={'class': 'form-control text-bg-light'}),
                   }


class PaymentForm(forms.ModelForm):
    cc_number = CardNumberField()
    cc_expiry = CardExpiryField()
    cc_code = SecurityCodeField()

    class Meta:
        model = Payment
        fields = ('cc_number', 'cc_expiry', 'cc_code')
