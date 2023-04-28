import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.http import HttpResponse
from .models import Book, Stock, Sale
from .forms import BookForm, SalesPriceForm
# Create your views here.


# view for the main page
def index(request):
    return render(request, "index.html")


# view for checking all the current inventories
@login_required
def inventory(request):
    books = Book.objects.all()
    search_term = request.GET.get('search')
    if search_term:
        books = books.filter(
            Q(book_id=search_term) |
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
@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book details updated successfully!')
            return redirect('inventory')
    else:
        form = BookForm(instance=book)
    context = {
        'form': form,
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
        return render(request, 'stock_complete.html')
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


