from django.db import models
from django.db.models import CASCADE


# Create your models here.
class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=50, null=False)
    user_name = models.CharField(max_length=200, null=False)
    name = models.CharField(max_length=200, null=False)
    personal_id = models.CharField(max_length=50, null=False)
    gender = models.CharField(max_length=50, null=True)
    age = models.IntegerField()
    is_superuser = models.BooleanField()


class Book(models.Model):
    book_id = models.CharField(primary_key=True, max_length=200, null=False)
    isbn = models.CharField(max_length=200, null=False)
    title = models.CharField(max_length=200, null=False)
    publisher = models.CharField(max_length=200, null=False)
    author = models.CharField(max_length=200, null=False)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    inventory = models.IntegerField()


class Book_Stock(models.Model):
    stock_id = models.CharField(primary_key=True, max_length=200, null=False)
    book_id = models.CharField(max_length=200, null=False, default="")
    isbn = models.CharField(max_length=200, null=False, default="")
    title = models.CharField(max_length=200, null=False, default="")
    publisher = models.CharField(max_length=200, null=False, default="")
    author = models.CharField(max_length=200, null=False, default="")
    price = models.DecimalField(decimal_places=2, max_digits=7, null=True)
    number_of_stock = models.IntegerField()
    stock_date = models.DateField(auto_now=True)
    is_paid = models.BooleanField()
    is_returned = models.BooleanField()


class Stock_Return(models.Model):
    return_id = models.CharField(primary_key=True, max_length=200, null=False)
    ref_stock_id = models.ForeignKey(Book_Stock, on_delete=CASCADE, default="")
    return_date = models.DateField()


class Stock_Payment(models.Model):
    payment_id = models.CharField(primary_key=True, max_length=200, null=False)
    ref_stock_id = models.ForeignKey(Book_Stock, on_delete=CASCADE, default="")
    payment_date = models.DateField()


class Book_Purchase(models.Model):
    purchase_id = models.CharField(primary_key=True, max_length=200, null=False)
    ref_book_id = models.ForeignKey(Book_Stock, on_delete=CASCADE, default="")
    number_of_purchase = models.IntegerField()
    purchase_date = models.DateField()

