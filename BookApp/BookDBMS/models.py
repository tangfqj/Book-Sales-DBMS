from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    true_name = models.CharField(max_length=100)
    work_id = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    age = models.IntegerField()
    mobile_phone = models.CharField(max_length=20)

    USERNAME_FIELD = 'username'


class SuperAdminManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_superuser=True)


class SuperAdmin(User):
    objects = SuperAdminManager()

    class Meta:
        proxy = True
        ordering = ('-date_joined',)

    def __str__(self):
        return self.true_name


class CommonAdmin(User):
    class Meta:
        proxy = True
        ordering = ('-date_joined',)

    def __str__(self):
        return self.true_name


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    sales_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inventory = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Stock(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    stock_number = models.IntegerField()
    stock_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.book.title} ({self.stock_number})'


class Sale(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    sale_number = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.book.title} ({self.sale_number})'

    def save(self, *args, **kwargs):
        if self.book.inventory >= int(self.sale_number):
            self.book.inventory -= int(self.sale_number)
            self.book.save()
        else:
            raise ValueError('Not enough inventory')
        super().save(*args, **kwargs)


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through='BillItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Bill {self.pk}'

    def save(self, *args, **kwargs):
        self.total_amount = sum(item.total_price for item in self.billitem_set.all())
        super().save(*args, **kwargs)


class BillItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.book.title} ({self.quantity})'

    @property
    def total_price(self):
        return self.quantity * self.price