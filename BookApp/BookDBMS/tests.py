from django.test import TestCase

# Create your tests here.

import psycopg2
from django.contrib.auth.hashers import make_password

# Connect to the PostgreSQL database
conn = psycopg2.connect("dbname=book user=postgres password=tangtang1125")

# Create a cursor object
cur = conn.cursor()

# Define the user data
username = "tang"
password = "admin123456"
hashed_password = make_password(password)  # Generate the password hash
email = "tang@example.com"

# Insert the user into the database
cur.execute("INSERT INTO auth_user (username, password, email, is_superuser) VALUES (%s, %s, %s, %s)", (username, hashed_password, email, True))
conn.commit()

# Close the database connection
cur.close()
conn.close()