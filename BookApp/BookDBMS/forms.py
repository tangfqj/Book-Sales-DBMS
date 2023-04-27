from django import forms
from .models import Book


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