import csv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlite3


SQLALCHEMY_DATABASE_URL = "sqlite:///b.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
#conn = sqlite3.connect(SQLALCHEMY_DATABASE_URL, check_same_thread=False)
#db = conn.cursor()
'''
app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost/test_bookstore"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
'''

#conn = psycopg2.connect(host="localhost", database="test_bookstore", user="postgres", password="password")
#db = conn.cursor()

try:
    db.execute("CREATE TABLE User (username VARCHAR PRIMARY KEY, password VARCHAR NOT NULL, time_of_registration DATETIME DEFAULT CURRENT_TIMESTAMP);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE UserDetails (username VARCHAR PRIMARY KEY, forename VARCHAR NOT NULL, surname VARCHAR NOT NULL, address VARCHAR NOT NULL, phone_number CHAR(10) NOT NULL);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Manager (managerID INTEGER PRIMARY KEY, username VARCHAR NOT NULL UNIQUE, became_manager DATETIME DEFAULT CURRENT_TIMESTAMP);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Inventory (isbn CHAR(13) PRIMARY KEY, price REAL NOT NULL DEFAULT 0.00, stock INTEGER NOT NULL DEFAULT 0, sold INTEGER NOT NULL DEFAULT 0);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Reserve (isbn CHAR(13) PRIMARY KEY, price REAL NOT NULL DEFAULT 0.00, stock INTEGER NOT NULL DEFAULT 0);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Book (isbn CHAR(13) PRIMARY KEY, title VARCHAR NOT NULL);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE BookDetails (isbn CHAR(13) PRIMARY KEY, isbn10 VARCHAR, language VARCHAR, num_pages INTEGER, publication_date TEXT, publisher VARCHAR)")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE ShoppingCart (cartID INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, copies INTEGER DEFAULT 0);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Orders (order_number INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, copies INTEGER NOT NULL, total_cost REAL NOT NULL, time_ordered DATETIME DEFAULT CURRENT_TIMESTAMP);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Waitlist (waitlist_number INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, time_waitlisted DATETIME DEFAULT CURRENT_TIMESTAMP);")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Author (author_name VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, PRIMARY KEY (author_name, isbn));")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Comment (username VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, rating INTEGER NOT NULL, comment_text VARCHAR(100), comment_time DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (username, isbn))")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Usefulness (username VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, commenter VARCHAR NOT NULL, rating INTEGER NOT NULL, PRIMARY KEY (username, isbn, commenter))")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE Trustworthiness (username VARCHAR NOT NULL, assignee VARCHAR NOT NULL, rating INTEGER NOT NULL, PRIMARY KEY(username, assignee))")
    db.close()
except:
    db.close()
    pass
try:
    db.execute("CREATE TABLE BookBrowse (isbn CHAR(13) NOT NULL PRIMARY KEY, keywords TEXT NOT NULL)")
    db.close()
except:
    db.close()
    pass

def written_by(isbn, author):
    try:
        db.execute("INSERT INTO WrittenBy (isbn, author) VALUES (:isbn, :author)", {"isbn":isbn, "author":author})
        #print('here1')
        db.commit()
        #print('here2')
        db.close()
        #print('here3')
    except:
        db.close()
        pass

def author_adder(names, isbn):
    #tmp = names.split('/')
    for i in names.split('/'):
        try:
        #print(i)
            db.execute("INSERT INTO Author (author_name, isbn) VALUES (:author_name, :isbn)", {"author_name":i, "isbn":isbn})
            db.commit()
            db.close()
        except:
            db.close()
            pass
        #written_by(isbn, i)
    db.close_all()

def book_details_adder(isbn, isbn10, language, num_pages, publication_date, publisher):
    try:
        db.execute("INSERT INTO BookDetails (isbn, isbn10, language, num_pages, publication_date, publisher) VALUES (:isbn, :isbn10, :language, :num_pages, :publication_date, :publisher)", {"isbn":isbn, "isbn10":isbn10, "language":language, "num_pages":num_pages, "publication_date":publication_date, "publisher":publisher})
        db.commit()
        db.close()
    except:
        db.close()
        pass

def import_books():
    f = open("books_new.csv")
    reader = (csv.DictReader(f))
    for field in reader:
        #print('herehh')
        #print(field)
        try:
            db.execute("INSERT INTO Book (isbn, title) VALUES (:isbn, :title);", {"isbn":field["isbn13"], "title":field["title"]})
            db.commit()
            db.close()
        except:
            db.close()
            pass
        db.close_all()
        #book_details_adder(field["isbn13"], field["isbn"], field["language"], field["num_pages"], field["publication_date"], field["publisher"])
        
        try:
            db.execute("INSERT INTO BookDetails (isbn, isbn10, language, num_pages, publication_date, publisher) VALUES (:isbn, :isbn10, :language, :num_pages, :publication_date, :publisher)", {"isbn":field["isbn13"], "isbn10":field["isbn"], "language":field["language_code"], "num_pages":field["  num_pages"], "publication_date":datetime.datetime.strptime(field["publication_date"], '%m/%d/%Y').strftime('%Y-%m-%d'), "publisher":field["publisher"]})
            db.commit()
            db.close()
        except:
            db.close()
            pass

        try:
            db.execute("INSERT INTO Inventory (isbn) VALUES (:isbn);", {"isbn":field["isbn13"]})
            db.commit()
            db.close()
        except:
            db.close()
            pass
        try:
            db.execute("INSERT INTO Reserve (isbn) VALUES (:isbn);", {"isbn":field["isbn13"]})
            db.commit()
            db.close()
        except:
            db.close()
            pass

        try:
            db.execute("INSERT INTO BookBrowse (isbn, keywords) VALUES (:isbn, :keywords)", {"isbn":field["isbn13"], "keywords":'#'.join([field["title"], field["authors"], field["isbn"], field["isbn13"], field["publisher"]])})
            db.commit()
            db.close()
        except:
            db.close()
            pass

        #print('here4')
        db.close_all()
        #print('going into author')
        author_adder(field["authors"], field["isbn13"])
        #print('here5')
try:
    pass
    import_books()
except:
    db.close_all()
    pass
