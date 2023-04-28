from .models import Book, CommonAdmin, SuperAdmin, User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'book_id',
            'title',
            'author',
            'publisher',
            'isbn',
            'sales_price',
            'inventory',
        ]


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


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class CommonAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('true_name', 'gender', 'age', 'mobile_phone')
        labels = {
            'true_name': 'Name',
            'gender': 'Gender',
            'age': 'Age',
            'mobile_phone': 'Mobile Phone',
        }
        widgets = {
            'true_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }