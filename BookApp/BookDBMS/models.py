from BookApp import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext as _

# Create your models here.


class User(AbstractUser):
    true_name = models.CharField(max_length=100)
    work_id = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    age = models.IntegerField()
    mobile_phone = models.CharField(max_length=20)

    USERNAME_FIELD = 'username'

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='auth_user_permissions_bookdbms'
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='auth_user_set_bookdbms'
    )


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
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    txn_type = models.CharField(max_length=10)  # 'purchase' or 'payment'
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.book.title} ({self.quantity}, {self.txn_type})'
