import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import SalesPriceForm
from .models import Book, Stock, Sale, User, Bill

# Create your views here.


# view for the main page
def index(request):
    return render(request, "index.html")


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print("success auth")
        print(user.username)
        print(user.password)
        if user is not None:
            login(request, user)
            print("login")
            return redirect('inventory.html')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def is_superadmin(user):
    return user.is_authenticated and user.is_superuser


# view for checking all the current inventories
@login_required
def inventory(request):
    books = Book.objects.all().order_by('book_id')
    search_term = request.GET.get('search')
    if search_term:
        books = books.filter(
            Q(book_id__icontains=search_term) |
            Q(isbn__icontains=search_term) |
            Q(title__icontains=search_term) |
            Q(author__icontains=search_term) |
            Q(publisher__icontains=search_term)
        )
    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'books': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'search_term': search_term,
    }
    return render(request, 'inventory.html', context)


# view for editing certain book
@csrf_exempt
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        new_title = request.POST.get('new_title')
        if new_title:
            book.title = new_title
        new_author = request.POST.get('new_author')
        if new_author:
            book.author = new_author
        new_publisher = request.POST.get('new_publisher')
        if new_publisher:
            book.publisher = new_publisher
        new_isbn = request.POST.get('new_isbn')
        if new_isbn:
            book.isbn = new_isbn
        new_sales_price = request.POST.get('new_sales_price')
        if new_sales_price:
            book.sales_price = new_sales_price
        book.save()
        if new_title is not None or new_author is not None or new_publisher is not None or new_isbn is not None or \
                new_sales_price is not None:
            return redirect('inventory')
        else:
            return render(request, 'edit_book.html', {'book': book})

    context = {
        'book': book,
    }
    return render(request, 'edit_book.html', context)


# view for checking stock by book_id
@login_required
@csrf_exempt
def stock(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book = Book.objects.filter(book_id=book_id).first()
        if book:
            return redirect('stock_partial')
        else:
            return redirect('stock_complete')
    else:
        return render(request, 'stock.html')


# view for stocking books which have occurred in inventory
@login_required
@csrf_exempt
def stock_partial(request):
    book_id = request.POST.get('book_id')
    book = Book.objects.filter(book_id=book_id).first()
    if request.method == 'POST':
        stock_num = request.POST.get('number_of_stock')
        stock_num = int(stock_num)
        stock_price = request.POST.get('stock_price')
        stock_price = float(stock_price)
        stock_entry = Stock(book=book, stock_number=stock_num, stock_price=stock_price, date=datetime.date.today(),
                            paid=False, returned=False)
        stock_entry.save()
        return render(request, 'stock_partial.html')
    else:
        return render(request, 'stock_partial.html')


# view for stocking books which have not occurred in inventory
@login_required
@csrf_exempt
def stock_complete(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        title = request.POST.get('title')
        author = request.POST.get('author')
        publisher = request.POST.get('publisher')
        isbn = request.POST.get('isbn')
        stock_num = request.POST.get('number_of_stock')
        stock_num = int(stock_num)
        stock_price = request.POST.get('stock_price')
        stock_price = float(stock_price)
        book = Book(book_id=book_id, title=title, author=author, publisher=publisher, isbn=isbn, sales_price=0, inventory=0)
        book.save()
        stock_entry = Stock(book=book, stock_number=stock_num, stock_price=stock_price, date=datetime.date.today(),
                            paid=False, returned=False)
        stock_entry.save()
        return render(request, 'stock.html')
    else:
        return render(request, 'stock_complete.html')


# view for checking all the unpaid and unreturned stocks
@login_required
@csrf_exempt
def check_unpaid(request):
    unpaid_books = Stock.objects.filter(paid=False, returned=False)
    context = {'unpaid_books': unpaid_books}
    return render(request, 'check_unpaid.html', context)


# view for payment
@login_required
@csrf_exempt
def payment(request, pk):
    book_stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = SalesPriceForm(request.POST)
        if form.is_valid():
            book_stock.paid = True
            book = Book.objects.filter(book_id=book_stock.book.book_id).first()
            book.inventory += book_stock.stock_number
            book.sales_price = form.cleaned_data['sales_price']
            book.save()
            total_price = book_stock.stock_price * book_stock.stock_number
            billitem = Bill(user=request.user, book=book, price=book_stock.stock_price, quantity=book_stock.stock_number,
                            total_price=total_price, txn_type="stock")
            billitem.save()
            book_stock.save()
            return redirect('check_unpaid')
    else:
        form = SalesPriceForm()
    return render(request, 'payment.html', {'book_stock': book_stock, 'form': form})


# view for checking all the unpaid and unreturned stocks
@login_required
@csrf_exempt
def check_unreturned(request):
    toreturn_books = Stock.objects.filter(paid=False, returned=False)
    context = {'toreturn_books': toreturn_books}
    return render(request, 'check_unreturned.html', context)


# view for return
@login_required
@csrf_exempt
def return_book(request, pk):
    book_stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        book_stock.returned = True
        book_stock.save()
        return redirect('check_unreturned')
    return redirect('check_unreturned')


# view for purchasing a book
@login_required
@csrf_exempt
def purchase(request):
    if request.method == 'GET':
        search_type = request.GET.get('search_type')
        search_text = request.GET.get('search_text')
        purchase_number = request.GET.get('purchase_number')

        if not search_type or not search_text or not purchase_number:
            return render(request, 'purchase.html')

        book = None
        if search_type == 'book_id':
            try:
                book = Book.objects.get(book_id=search_text)
            except Book.DoesNotExist:
                return render(request, 'purchase_fail.html', {'reason': 'Book not found'})
        elif search_type == 'isbn':
            try:
                book = Book.objects.get(isbn=search_text)
            except Book.DoesNotExist:
                return render(request, 'purchase_fail.html', {'reason': 'Book not found'})
        elif search_type == 'title':
            try:
                book = Book.objects.get(title=search_text)
            except Book.DoesNotExist:
                return render(request, 'purchase_fail.html', {'reason': 'Book not found'})

        if not book:
            return render(request, 'purchase_fail.html', {'reason': 'Book not found'})

        if book.inventory < int(purchase_number):
            return render(request, 'purchase_fail.html', {'reason': 'Not enough inventory', 'inventory': book.inventory})

        total_price = book.sales_price * int(purchase_number)

        return render(request, 'purchase_success.html',
                      {'book': book, 'quantity': purchase_number, 'total_price': total_price})


# view for confirmation of the purchase
@login_required
@csrf_exempt
def purchase_success(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        purchase_number = request.POST.get('quantity')
        book = get_object_or_404(Book, book_id=book_id)
        sale = Sale(book=book, sale_number=purchase_number)
        total_price = float(book.sales_price) * int(purchase_number)
        billitem = Bill(user=request.user, book=book, price=book.sales_price, quantity=purchase_number,
                        total_price=total_price, txn_type="sales")
        billitem.save()
        sale.save()

        return redirect(reverse('purchase'))

    return render(request, 'purchase_success.html')


# view for purchase failure
@login_required
@csrf_exempt
def purchase_fail(request):
    reason = request.GET.get('reason')
    inventory = request.GET.get('inventory')
    return render(request, 'purchase_fail.html', {'reason': reason, 'inventory': inventory})


@login_required
def profile_view(request):
    user = request.user
    context = {
        'username': user.username,
        'true_name': user.true_name,
        'work_id': user.work_id,
        'gender': user.gender,
        'email': user.email,
        'mobile_phone': user.mobile_phone,
    }
    return render(request, 'personal_profile.html', context)


@csrf_exempt
@login_required
def edit_profile(request):
    user = request.user
    context = {
        'true_name': user.true_name,
        'work_id': user.work_id,
        'email': user.email,
        'mobile_phone': user.mobile_phone
    }
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        if new_email:
            user.email = new_email
        new_mobile_phone = request.POST.get('new_mobile_phone')
        if new_mobile_phone:
            user.mobile_phone = new_mobile_phone
        user.save()
        return redirect('edit_profile')
    return render(request, 'edit_profile.html', context)


@csrf_exempt
@login_required
def admin_edit_profile(request, pk):
    user = User.objects.filter(pk=pk).first()
    context = {
        'true_name': user.true_name,
        'work_id': user.work_id,
        'email': user.email,
        'mobile_phone': user.mobile_phone
    }
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        if new_email:
            user.email = new_email
        new_mobile_phone = request.POST.get('new_mobile_phone')
        if new_mobile_phone:
            user.mobile_phone = new_mobile_phone
        user.save()
        if new_email is not None or new_mobile_phone is not None:
            return redirect('view_all_account')
        else:
            return render(request, 'admin_edit_profile.html', context)
    return render(request, 'admin_edit_profile.html', context)


@csrf_exempt
@login_required
def create_account(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        password = make_password(password)
        email = request.POST.get('email')
        true_name = request.POST.get('true_name')
        work_id = request.POST.get('work_id')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        age = int(age)
        mobile_phone = request.POST.get('mobile_phone')
        user = User(username=username, password=password, email=email, true_name=true_name, work_id=work_id,
                    gender=gender, age=age, mobile_phone=mobile_phone, is_superuser=False, is_active=True, is_staff=True)
        user.save()
        return redirect('create_account')
    return render(request, 'create_account.html')


@login_required
def view_all_account(request):
    users = User.objects.all().order_by('work_id')
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'users': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
    }
    return render(request, 'view_all_account.html', context)


@login_required
@csrf_exempt
def view_bill(request):
    bill = Bill.objects.all()
    paginator = Paginator(bill, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'bill': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
    }
    return render(request, 'bill.html', context)


# Experiment
from django.db.models import Sum
from .models import Bill


def test(request):
    context = {}
    date_filter = request.GET.get('date_filter', 'day')  # Default to filtering by day
    sales = Bill.objects.filter(txn_type='sales')
    payments = Bill.objects.filter(txn_type='stock')

    if date_filter == 'day':
        date = request.GET.get('date', timezone.now().date())
        sales = sales.filter(date__date=date)
        payments = payments.filter(date__date=date)
    elif date_filter == 'month':
        date = request.GET.get('month', timezone.now().strftime('%Y-%m'))
        year, month = map(int, date.split('-'))
        sales = sales.filter(date__year=year, date__month=month)
        payments = payments.filter(date__year=year, date__month=month)
    elif date_filter == 'year':
        year = request.GET.get('year', timezone.now().year)
        sales = sales.filter(date__year=year)
        payments = payments.filter(date__year=year)
    # Filter by date
    # if date_filter == 'day':
    #     sales = sales.filter(date__date=request.GET.get('date', timezone.now().date()))
    #     payments = payments.filter(date__date=request.GET.get('date', timezone.now().date()))
    # elif date_filter == 'month':
    #     sales = sales.filter(date__month=request.GET.get('month', timezone.now().month))
    #     payments = payments.filter(date__month=request.GET.get('month', timezone.now().month))
    # elif date_filter == 'year':
    #     sales = sales.filter(date__year=request.GET.get('year', timezone.now().year))
    #     payments = payments.filter(date__year=request.GET.get('year', timezone.now().year))

    # Calculate totals
    context['total_sales'] = sales.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    context['total_payments'] = payments.aggregate(total_payments=Sum('total_price'))['total_payments'] or 0
    context['sales_count'] = sales.aggregate(sales_count=Sum('quantity'))['sales_count'] or 0
    context['stock_count'] = payments.aggregate(stock_count=Sum('quantity'))['stock_count'] or 0

    return render(request, 'test.html', context)
