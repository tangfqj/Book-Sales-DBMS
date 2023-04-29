from .models import Book, CommonAdmin, SuperAdmin, User
from django import forms


class SalesPriceForm(forms.Form):
    sales_price = forms.DecimalField(label='Sales Price')


class CommonAdminForm(forms.ModelForm):
    class Meta:
        model = CommonAdmin
        fields = ['true_name', 'work_id', 'gender', 'age', 'mobile_phone']
