from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('uemail', 'uname', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('uemail', 'uname')


# class RegisterForm(Form):
#     gender = (
#         ('male', "男"),
#         ('female', "女"),
#     )
#     username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
#     password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
#     email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
#     sex = forms.ChoiceField(label='性别', choices=gender)
#     captcha = CaptchaField(label='验证码')

# class RenewBookForm(forms.Form):
#     renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")
#
#     def clean_renewal_date(self):
#         data = self.cleaned_data['renewal_date']
#
#         # Check date is not in past.
#         if data < datetime.date.today():
#             raise ValidationError(_('Invalid date - renewal in past'))
#
#         # Check date is in range librarian allowed to change (+4 weeks).
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
#
#         # Remember to always return the cleaned data.
#         return data
from .models import *


class BookcopyForm(forms.ModelForm):
    class Meta:
        model = Bookcopy
        fields = ('rid',)


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('bauthor', 'bname',)


class BorrowForm(forms.ModelForm):
    class Meta:
        fields = ('bcid',)
        model = Borrow
