from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from . import models
# Create your views here.


def index(request):
    return render(request, "index.html")


def inventory(request):
    book_list = models.Book.objects.all()
    paginator = Paginator(book_list, 20)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, 'inventory.html', {'books': books})

@csrf_exempt
def stock(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book = models.Book.objects.filter(book_id=book_id).first()
        if book:
            stocknum = request.POST.get('number_of_stock')
            stocknum = int(stocknum)
            stock_entry = models.Book_Stock(book_id=book_id, isbn=book.isbn, title=book.title, publisher=book.publisher,
                                            author=book.author, price=book.price, number_of_stock=stocknum, is_paid=False,
                                            is_returned=False)
            stock_entry.save()
            return redirect('stock_success')
        else:
            title = request.POST.get('title')
            author = request.POST.get('author')
            publisher = request.POST.get('publisher')
            isbn = request.POST.get('isbn')
            price = request.POST.get('price')
            price = float(price)
            stocknum = request.POST.get('number_of_stock')
            stocknum = int(stocknum)
            stock_entry = models.Book_Stock(book_id=book_id, isbn=isbn, title=title, publisher=publisher,
                                            author=author, price=price, number_of_stock=stocknum, is_paid=False,
                                            is_returned=False)
            stock_entry.save()
            return redirect('stock_success')
    else:
        return render(request, 'stock.html')
