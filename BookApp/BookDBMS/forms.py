from .models import Book, CommonAdmin, SuperAdmin, User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class SalesPriceForm(forms.Form):
    sales_price = forms.DecimalField(label='Sales Price')


class CommonAdminForm(forms.ModelForm):
    class Meta:
        model = CommonAdmin
        fields = ['true_name', 'work_id', 'gender', 'age', 'mobile_phone']


class SuperAdminForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class CommonAdminLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

