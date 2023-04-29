# Book-Sales-DBMS

[![Hex.pm](https://img.shields.io/hexpm/l/plug.svg)](https://github.com/tangfqj/Book-Sales-DBMS)
## Description
This is a book sales management system using Django and PostgresSQL. It is not only the assignment for my Database course, but also the first application with **fullstack** backend and frontend completed by myself.

## Get Started
Open the project in ```BookApp``` directory.

Restore the example data in PostgresSQL.

Make sure you've installed ```Django``` and ```psycopg2-binary```

Run the following command to start server:
```angular2html
python manage.py runserver
```

Now you can log in with the provided super administrator account.


## Project File Structure
```
.
|--BookApp
   |-- .idea
   |-- BookApp
   |    |-- __init__.py
   |    |-- asgi.py
   |    |-- settings.py
   |    |-- urls.py
   |    |-- wsgi.py
   |-- BookDBMS
   |    |-- migrations
   |	|-- __init__.py
   |	|-- admin.py
   |	|-- apps.py
   |	|-- forms.py
   |	|-- models.py
   |	|-- views.py
   |-- static
   |    |-- user.png
   |-- templates
   |-- manage.py
```

## Database Schema
### E-R Diagram
![](D:\Book-Sales-DBMS\images\er-diagram.png)

### Relational Schema & Constraints
**The entity sets are listed below:**

_User:_ with attributes _(<u>user_id</u>, username, password, true_name, work_id, email, mobile_phone, gender, age, is_superuser)_

_Book:_ with attributes *(<u>book_id</u>, title, author, publisher, isbn, sales_price, inventory)*

_Bill:_ with attributes *(<u>bill_id</u>, book_id, user_id, quantity, price, txn_type, date)*

**The relationship sets are listed below:**

_stock:_ relating User with Book

_payment:_ relating User with Book through Bill

_sell:_ relating User with Book through Bill

_create_account:_ relating User(common) with User(super)