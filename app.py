# pylint: disable=no-member
import csv
from flask import Flask, render_template, request, session, redirect, url_for
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256
import re
import operator

app = Flask(__name__)
app.secret_key = 'random'

SQLALCHEMY_DATABASE_URL = "sqlite:///b.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

#session['INTERNAL_COMMENT_ERROR'] = ''

'''
try:
    db.execute("CREATE TABLE User (username VARCHAR PRIMARY KEY, password VARCHAR NOT NULL, time_of_registration DATETIME DEFAULT CURRENT_TIMESTAMP);")
    db.close()
except:
    pass
try:
    db.execute("CREATE TABLE UserDetails (username VARCHAR PRIMARY KEY, forename VARCHAR NOT NULL, surname VARCHAR NOT NULL, address VARCHAR NOT NULL, phone_number CHAR(10) NOT NULL);")
    db.close()
except:
    pass
try:
    db.execute("CREATE TABLE Manager (managerID INTEGER PRIMARY KEY, username VARCHAR NOT NULL UNIQUE, became_manager DATETIME DEFAULT CURRENT_TIMESTAMP);")
    db.close()
except:
    pass
try:
    db.execute("CREATE TABLE Inventory (isbn CHAR(13) PRIMARY KEY, price REAL NOT NULL DEFAULT 0.00, stock INTEGER NOT NULL DEFAULT 0);")
    db.close()
except:
    pass
try:
    db.execute("CREATE TABLE Book (isbn CHAR(13) PRIMARY KEY, title VARCHAR NOT NULL);")
    db.close()
except:
    pass
try:
    db.execute("CREATE TABLE ShoppingCart (cartID INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, copies INTEGER DEFAULT 0);")
    db.close()
except:
    pass

try:
    db.execute("CREATE TABLE Orders (order_number INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR NOT NULL, isbn CHAR(13) NOT NULL, copies INTEGER NOT NULL, total_cost REAL NOT NULL, time_ordered DATETIME DEFAULT CURRENT_TIMESTAMP);")
    db.close()
except:
    pass

def import_books():
    f = open("books_new.csv")
    reader = (csv.DictReader(f))
    for field in reader:
        try:
            db.execute("INSERT INTO Book (isbn, title) VALUES (:isbn, :title);", {"isbn":field["isbn13"], "title":field["title"]})
            db.commit()
            db.close()
        except:
            pass
        try:
            db.execute("INSERT INTO Inventory (isbn) VALUES (:isbn);", {"isbn":field["isbn13"]})
            db.commit()
            db.close()
        except:
            pass
try:
    pass
    #import_books()
except:
    pass
'''
message_to_pass = ''

'''
def lister(lst):
    i = 0
    new_lst = []
    while i < len(lst):
        new_lst.append()
'''
def manager_check():
    try:
        query = db.execute("SELECT * FROM Manager").fetchall()
        db.close()
        if query == []:
            first_user = db.execute("SELECT username FROM User ORDER BY time_of_registration").fetchall[0]
            db.close()
            print('working1')
            if first_user == []:
                print('working2')
                return False
            db.execute("INSERT INTO Manager (username) VALUES (:username);", {"username":first_user})
            db.commit()
            db.close()
            print('working3')
            return True
        print('working4')
        return True
    except:
        pass

#manager_check()

def waitlist_check(isbn):
    check = db.execute("SELECT stock, price FROM Inventory WHERE isbn = :isbn", {"isbn":isbn}).fetchall()
    db.close()
    inv = int(check[0][0])
    price = float(check[0][1])
    check2 = db.execute("SELECT * FROM Waitlist WHERE isbn = :isbn", {"isbn":isbn}).fetchall()
    if inv > 0 and check2:
        wl = db.execute("SELECT waitlist_number, username FROM Waitlist WHERE isbn = :isbn ORDER BY time_waitlisted LIMIT 1", {"isbn":isbn}).fetchall()
        print(wl)
        db.execute("INSERT INTO Orders (username, isbn, copies, total_cost) values (:username, :isbn, :copies, :total_cost)", {"username":wl[0][1], "isbn":isbn, "copies":1, "total_cost":(int(price*100)/100)})
        db.execute("UPDATE Inventory SET stock = stock - :stock WHERE isbn = :isbn", {"stock":1, "isbn":isbn})
        #db.execute("UPDATE Inventory SET stock = stock - :stock, sold = sold + :stock WHERE isbn = :isbn", {"stock":order[i][1], "isbn":order[i][0]})
        db.execute("DELETE FROM Waitlist WHERE waitlist_number = :waitlist_number", {"waitlist_number":wl[0][0]})
        db.commit()
        db.close_all()
        return waitlist_check(isbn)
    else:
        db.close_all()
        return

@app.route('/')
def index():
    #session['INTERNAL_COMMENT_ERROR'] = ''
    return render_template('index.html')

def par_check(username, password, forename, surname, address, phone_number):
    users = db.execute("SELECT username FROM User WHERE username = :username", {"username":username}).fetchall()
    db.close()
    if len(username) < 4 or len(password) < 5:
        return 1
    if users:
        return 2
    if len(forename) == 0 or len(surname) == 0:
        return 3
    if len(address) == 0:
        return 4
    if len(phone_number) != 10:
        return 5
    return 6

@app.route('/user_registration', methods=['POST', 'GET'])
def user_registration():
    if request.method == 'POST':
        check = par_check(request.form['username'], request.form['password'], request.form['forename'], request.form['surname'], request.form['address'], request.form['phone_number'])
        if check == 1:
            return render_template('registration.html', info='Unsuccessful: Password or username shorter than 5 characters.')
        elif check == 2:
            return render_template('registration.html', info='Unsuccessful: Username taken.')
        elif check == 3:
            return render_template('registration.html', info='Unsuccessful: Name not provided.')
        elif check == 4:
            return render_template('registration.html', info='Unsuccessful: Address not provided.')
        elif check == 5:
            return render_template('registration.html', info='Unsuccessful: Phone Number of improper length.')
        elif check == 6:
            db.execute("INSERT INTO User (username, password) VALUES (:username, :password);", {'username':request.form['username'], 'password':pbkdf2_sha256.hash(request.form['password'])})
            db.execute("INSERT INTO UserDetails (username, forename, surname, address, phone_number) VALUES (:username, :forename, :surname, :address, :phone_number)", {"username":request.form['username'], "forename":request.form['forename'], "surname":request.form['surname'], "address":request.form["address"], "phone_number":request.form['phone_number']})
            db.commit()
            db.close()
            query = db.execute("SELECT * FROM Manager").fetchall()
            db.close()
            if not query:
                db.execute("INSERT INTO Manager (username) VALUES (:username);", {'username':request.form['username']})
                db.commit()
            db.close()
        return render_template('registration.html', info='Successful')
    #except:
        #return render_template('registration.html', info='Username taken. Try a different username.')
    return render_template('registration.html')

@app.route('/test_site', methods=['POST'])
def test_site():
    pass



@app.route('/user_login', methods=['POST', 'GET'])
def user_login():
    '''
    if request.method == 'POST':
        try:
            user = db.execute("SELECT username, password FROM User WHERE username = :username", {"username":request.form['username']}).fetchall()[0]
            manager = db.execute("SELECT username FROM Manager WHERE username = :username", {"username":request.form['username']}).fetchall()[0] 
            if manager:
                if user[1] == request.form['password']:
                    session["username"] = user[0]
                    session["logged_in"] = True
                    session["manager"] = True
                    return render_template('manager_home.html', info=session["username"])
                else:
                    return render_template('login.html', info='Incorrect Password for Manager')
            #print(request.form['username'], request.form['password'], user[1])
            elif user:
                if user[1] == request.form['password']:
                    session["username"] = user[0]
                    session["logged_in"] = True
                    session["manager"] = False
                    return render_template('home.html', info=session["username"])
                else:
                    return render_template('login.html', info='Incorrect Password for User')
            else:
                return render_template('login.html', info='Unsuccessful here2')
    
        except:
            return render_template('login.html', info='Unsuccessful here3')
    return render_template('login.html')
    '''
    if request.method == 'POST':
        usrnm = request.form['username']
        pswd = request.form['password']
        user, manager = [], []
        users = db.execute("SELECT username, password FROM User WHERE username = :username", {'username':usrnm}).fetchall()
        db.close()
        if users:
            user = users[0]
        managers = db.execute("SELECT username FROM Manager WHERE username = :username", {'username':usrnm}).fetchall()
        db.close()
        if managers:
            manager = managers[0]
        if user:
            if pbkdf2_sha256.verify(pswd, user[1]):
                if manager:
                    session["username"] = user[0]
                    session["logged_in"] = True
                    session["manager"] = True
                    #return render_template('manager_home.html', info=session["username"])
                    return redirect(url_for('home'))
                session["username"] = user[0]
                session["logged_in"] = True
                session["manager"] = False
                #return render_template('home.html', info=session["username"])
                return redirect(url_for('home'))
            return render_template('login.html', info='Incorrect password')
        return render_template('login.html', info='User not found')
    return render_template('login.html')

@app.route('/home')
def home():
    if session["logged_in"]:
        if session["manager"]:
            return render_template('manager_home.html', info=session["username"])
        return render_template('home.html', info=session["username"])
    return render_template('index.html')
'''
@app.route('/manager_login', methods=['POST', 'GET'])
def manager_login():
    if request.method == 'POST':
        if manager_check():
            try:
                manager = db.execute("SELECT username FROM Manager WHERE username = :username", {"username":request.form['username']}).fetchall()[0]
                if manager:
                    user = db.exe
                if user[1] == request.form['password']:
                    session["username"] = request.form["username"]
                    session["logged_in"] = True
                    return render_template('home.html', info=session["username"])
                return render_template('login.html', info='Unsuccessful')
        
            except:
                return render_template('login.html', info='Unsuccessful')
    return render_template('login.html')
'''
@app.route('/user_logout')
def user_logout():
    session.pop("username", None)
    session["logged_in"] = False
    return render_template('index.html')

@app.route('/manager_list')
def manager_list():
    managers_2d = db.execute("SELECT username FROM Manager").fetchall()
    db.close()
    managers = []
    i = 0
    while i < len(managers_2d):

        managers.append(managers_2d[i][0])
        i = i+1
    
    return render_template('manager_list.html', managers=managers, len=len(managers))

@app.route('/add_manager', methods=["GET", "POST"])
def add_manager():
    users_2d = db.execute("SELECT User.username FROM User WHERE User.username NOT IN (SELECT Manager.username FROM Manager) ORDER BY time_of_registration").fetchall()
    db.close()
    users = []
    i = 0
    while i < len(users_2d):
        users.append(users_2d[i][0])
        i=i+1
    if request.method == "POST":
        db.execute("INSERT INTO Manager (username) VALUES (:username);", {'username':request.form["users"]})
        db.commit()
        db.close()
        new_2d = db.execute("SELECT User.username FROM User WHERE User.username NOT IN (SELECT Manager.username FROM Manager) ORDER BY time_of_registration").fetchall()
        db.close()
        new = []
        j = 0
        while j < len(new_2d):
            new.append(new_2d[j][0])
            j=j+1
        return render_template('add_manager.html', len=len(new), users=new, message=request.form["users"]) 
    return render_template('add_manager.html', len=len(users), users=users)


@app.route('/all_books', methods=["POST", "GET"])
def all_books():
    books_2d = db.execute("SELECT * FROM Book ORDER BY title").fetchall()
    db.close()
    return render_template('all_books.html', len=len(books_2d), all_books=books_2d)

@app.route('/all_users', methods=["POST", "GET"])
def all_users():
    users_2d = db.execute("SELECT A.username, B.forename, B.surname FROM User AS A, UserDetails AS B WHERE A.username = B.username ORDER BY A.time_of_registration").fetchall()
    db.close()
    return render_template('all_users.html', len=len(users_2d), all_users=users_2d)

@app.route('/books/<string:isbn>')
def books(isbn):
    #comment_error = session['INTERNAL_COMMENT_ERROR']
    #session['INTERNAL_COMMENT_ERROR'] = ''
    comment_error = ''
    session["isbn"] = isbn
    message = message_to_pass
    book = []
    books = db.execute("SELECT A.isbn, A.title, B.isbn10, B.language, B.num_pages, B.publication_date, B.publisher FROM Book AS A, BookDetails AS B WHERE A.isbn = B.isbn AND A.isbn = :isbn", {"isbn":isbn}).fetchall()
    authors = db.execute("SELECT A.author_name FROM Author AS A, Book AS B WHERE A.isbn = B.isbn AND B.isbn = :isbn", {"isbn":isbn}).fetchall()
    comments = db.execute("SELECT username, isbn, rating, comment_text FROM Comment WHERE isbn = :isbn ORDER BY comment_time ASC", {"isbn":isbn}).fetchall()
    print(authors)
    if books[0]:
        book = books[0]
    db.close()
    return render_template('book_details.html', book=book, info=message, len=len(comments), comments=comments, len_c=len(comments), len_e=len(comment_error), error_message=comment_error, user=session['username'], manager=str(session['manager']), len_authors=len(authors), authors=authors)

@app.route('/users/<string:username>')
def users(username):
    user = []
    users = db.execute("SELECT A.username, B.forename, B.surname, B.address, B.phone_number FROM User AS A, UserDetails AS B WHERE A.username = B.username AND A.username = :username", {"username":username}).fetchall()
    db.close()
    if users:
        user = users[0]
        #return render_template('user_details.html', user=user[0])
    return render_template('user_details.html', user=user, same_user=str(session['username'] == username))

@app.route('/to_inventory/<string:isbn>', methods=["POST", "GET"])
def to_inventory(isbn):
    message = ''
    stock = 0
    books = db.execute("SELECT price, stock FROM Inventory WHERE isbn = :isbn;", {"isbn":isbn}).fetchall()
    db.close()
    if books[0]:
        book = books[0]
        stock = int(book[1])
    
    price, new_copies = float(request.form["price"]), int(request.form["copies"])
    #price = price + new_price
    stock = stock + new_copies
    price, stock = str(price), str(stock)
    if request.method == "POST":
        #db.execute("DELETE FROM Inventory WHERE isbn = :isbn", {"isbn":session["isbn"]})
        #db.commit()
        #db.close()
        db.execute("UPDATE Inventory SET price = :price, stock = :stock WHERE isbn = :isbn", {"price":price, "stock":stock, "isbn":session["isbn"]})
        #db.execute("INSERT INTO Inventory (isbn, price, stock) VALUES (:isbn, :price, :stock)", {"isbn":session["isbn"], "price":price, "stock":stock})
        db.commit()
        db.close()
        message = request.form["copies"] + " copies of " + session["isbn"] + " added successfully to the inventory at price " + request.form["price"]
        message_to_pass = message
        waitlist_check(isbn)
        return redirect(url_for('books', isbn=session["isbn"]))
    waitlist_check(isbn)
    return redirect(url_for('books', isbn=session["isbn"]))

@app.route('/to_shopping_cart/<string:isbn>', methods=["POST", "GET"])
def to_shopping_cart(isbn):
    print(isbn)
    #check = []
    check = db.execute("SELECT username, isbn FROM ShoppingCart WHERE username = :username AND isbn = :isbn", {"username":session["username"], "isbn":isbn}).fetchall()
    db.close()
    if check:
        db.execute("UPDATE ShoppingCart SET copies = copies + 1 WHERE isbn = :isbn AND username = :username", {"isbn":isbn, "username":session["username"]})
        db.commit()
        db.close()
    else:
        db.execute("INSERT INTO ShoppingCart (username, isbn, copies) VALUES (:username, :isbn, :copies);", {"username":session["username"], "isbn":isbn, "copies":1})
        db.commit()
        db.close()
    #return redirect(url_for('inventory'))
    return redirect(request.referrer)

@app.route('/remove_from_shopping_cart/<string:isbn>', methods=["POST", "GET"])
def remove_from_shopping_cart(isbn):
    check = db.execute("SELECT username, isbn, copies FROM ShoppingCart WHERE username = :username AND isbn = :isbn", {"username":session["username"], "isbn":isbn}).fetchall()
    if check:
        if int(check[0][2]) > 1:
            db.execute("UPDATE ShoppingCart SET copies = copies - 1 WHERE isbn = :isbn AND username = :username", {"isbn":isbn, "username":session["username"]})
            db.commit()
            db.close()
        elif int(check[0][2]) == 1:
            db.execute("DELETE FROM ShoppingCart WHERE username = :username AND isbn = :isbn", {"username":session["username"], "isbn":isbn})
            db.commit()
            db.close()
    return redirect(request.referrer)

@app.route('/delete_from_shopping_cart/<string:isbn>', methods=["POST", "GET"])
def delete_from_shopping_cart(isbn):
    check = db.execute("SELECT username, isbn, copies FROM ShoppingCart WHERE username = :username AND isbn = :isbn", {"username":session["username"], "isbn":isbn}).fetchall()
    if check:
        db.execute("DELETE FROM ShoppingCart WHERE username = :username AND isbn = :isbn", {"username":session["username"], "isbn":isbn})
        db.commit()
        db.close()
    return redirect(request.referrer)

@app.route('/inventory', methods=["POST", "GET"])
def inventory():
    inv = []
    inv = db.execute("SELECT Inventory.isbn, Book.title, Inventory.price, Inventory.stock FROM Inventory, Book WHERE Book.isbn = Inventory.isbn ORDER BY Inventory.stock DESC").fetchall()
    db.close()
    return render_template('inventory.html', all_books=inv, len=len(inv))

@app.route('/shopping_cart')
def shopping_cart():
    checkout = 1
    #items = db.execute("SELECT A.isbn, A.copies, B.price FROM ShoppingCart AS A, Inventory AS B WHERE A.username = :username AND A.isbn = B.isbn AND A.copies >= B.stock", {"username":session['username']}).fetchall()
    items_t = db.execute("SELECT ShoppingCart.isbn, ShoppingCart.copies, Inventory.stock, Inventory.price FROM ShoppingCart, Inventory WHERE ShoppingCart.username = :username AND ShoppingCart.isbn = Inventory.isbn", {"username":session["username"]}).fetchall()
    db.close()
    items = []
    j = 0
    while j < len(items_t):
        items.append(list(items_t[j]))
        j = j+1
    if items:
        i = 0
        while i < len(items):
            if int(items[i][1]) <= int(items[i][2]):
                items[i].append('In Stock')
                print(items[i])
            else:
                items[i].append('Exceeds Stock')
                print(items[i])
                checkout = 0
            i = i+1
        text = 'Here is your cart'
        lst = items

    else:
        text = 'Empty Cart'
        lst = []
        checkout = 0
    total = 0
    if checkout == 1:
        x = 0
        while x < len(items):
            total = total + (items[x][1] * int(items[x][3] * 100))
            x = x+1
    session["checkout_total"] = total
    return render_template('shopping_cart.html', message=text, len=len(lst), cart=lst, checkout=checkout, total=(int(session["checkout_total"])/100))

@app.route('/checkout', methods=["POST", "GET"])
def checkout():
    if request.method == 'POST':
        order = db.execute("SELECT A.isbn, A.copies, B.price FROM ShoppingCart AS A, Inventory AS B WHERE A.username = :username AND B.isbn = A.isbn", {"username":session["username"]}).fetchall()
        i = 0
        while i < len(order):
            db.execute("INSERT INTO Orders (username, isbn, copies, total_cost) values (:username, :isbn, :copies, :total_cost)", {"username":session["username"], "isbn":order[i][0], "copies":order[i][1], "total_cost":(int(float(order[i][2])*100*order[i][1])/100)})
            db.execute("UPDATE Inventory SET stock = stock - :stock WHERE isbn = :isbn", {"stock":order[i][1], "isbn":order[i][0]})
            #db.execute("UPDATE Inventory SET stock = stock - :stock, sold = sold + :stock WHERE isbn = :isbn", {"stock":order[i][1], "isbn":order[i][0]})
            i = i+1
        db.execute("DELETE FROM ShoppingCart WHERE username = :username", {"username":session["username"]})
        db.commit()
        db.close_all()
        session["checkout_total"] = 0
        return redirect(url_for('home'))
    return render_template('checkout.html', total=(int(session["checkout_total"])/100))

@app.route('/past_orders')
def past_orders():
    orders = db.execute("SELECT isbn, copies, total_cost, time_ordered FROM Orders WHERE username = :username", {"username":session["username"]}).fetchall()
    db.close()
    message = ''
    if not orders:
        message = 'No past orders found'
    return render_template('past_orders.html', message=message, past=orders, len=len(orders))

def check_isbn(isbn, v):
    try:
        tmp = int(isbn)
    except ValueError:
        return False
    return tmp >= (10 ** (v-1)) and tmp <= ((10 ** v) - 1)
    

@app.route('/add_book', methods=["POST", "GET"])
def add_book():
    if request.method == "POST":
        if not check_isbn(request.form['isbn'], 13):
            return render_template('add_book.html', info='Incorrect ISBN13')
        check = db.execute("SELECT isbn FROM Book WHERE isbn = :isbn", {"isbn":request.form['isbn']}).fetchall()
        db.close()
        if check:
            return render_template('add_book.html', info='Book already exists')
        if not request.form['title']:
            return render_template('add_book.html', info='Title not provided')
        if not request.form['authors']:
            return render_template('add_book.html', info='Author(s) not provided')
        if request.form['isbn10']:
            if not check_isbn(request.form['isbn10'], 10):
                return render_template('add_book.html', info='ISBN10 of incorrect nature')
        try:
            db.execute("INSERT INTO Book (isbn, title) VALUES (:isbn, :title)", {"isbn":request.form['isbn'], "title":request.form['title']})
            db.execute("INSERT INTO BookDetails (isbn, isbn10, language, num_pages, publication_date, publisher) VALUES (:isbn, :isbn10, :language, :num_pages, :publication_date, :publisher)", {"isbn":request.form["isbn"], "isbn10":request.form["isbn10"], "language":request.form["language"], "num_pages":request.form["num_pages"], "publication_date":request.form["publication_date"], "publisher":request.form["publisher"]})
            db.execute("INSERT INTO Inventory (isbn) VALUES (:isbn)", {"isbn":request.form['isbn']})
            db.execute("INSERT INTO Reserve (isbn) VALUES (:isbn)", {"isbn":request.form['isbn']})
            for item in request.form['authors'].split('/'):
                try:
                    db.execute("INSERT INTO Author (author_name, isbn) VALUES (:author_name, :isbn)", {"author_name":item, "isbn":request.form['isbn']})
                except:
                    pass
            db.commit()
            db.close_all()
            return redirect(url_for('books', isbn=request.form['isbn']))
        except:
            db.commit()
            db.close_all()
            return render_template('add_book.html', info='Some Error')
    return render_template('add_book.html')

@app.route('/add_comment/<string:isbn>', methods=["POST", "GET"])
def add_comment(isbn):
    #isbn = session["isbn"]
    if request.method == "POST":
        print('1')
        check = db.execute("SELECT username, isbn FROM Comment WHERE username = :username AND isbn = :isbn", {"username":session['username'], "isbn":isbn}).fetchall()
        db.close()
        if check:
            #session['INTERNAL_COMMENT_ERROR'] = 'Unsuccessful. Comment already exists.'
            return redirect(url_for('books', isbn=isbn))
        if request.form["rating"] == '':
            #session['INTERNAL_COMMENT_ERROR'] = 'Unsuccessful. No rating given.'
            return redirect(url_for('books', isbn=isbn))
        db.execute("INSERT INTO Comment (username, isbn, rating, comment_text) VALUES (:username, :isbn, :rating, :comment_text)", {"username":session["username"], "isbn":isbn, "rating":int(request.form["rating"]), "comment_text":request.form["comment_text"]})
        db.commit()
        db.close()
        print('3')
        print(request.form)
        print('5')
        #session['INTERNAL_COMMENT_ERROR'] = 'Success.'
        return redirect(url_for('books', isbn=isbn))
    print('6')
    #session['INTERNAL_COMMENT_ERROR'] = ''
    return redirect(url_for('books', isbn=isbn))

@app.route('/update_comment/<string:isbn>', methods=["POST", "GET"])
def update_comment(isbn):
    #isbn = session["isbn"]
    print('before entering if')
    if request.method == "POST":
        #check = db.execute("SELECT username, isbn FROM Comment WHERE username = :username AND isbn = :isbn", {"username":session['username'], "isbn":isbn}).fetchall()
        #db.close()
        print('enters if')
        #if check:
            #session['INTERNAL_COMMENT_ERROR'] = 'Unsuccessful. Comment already exists.'
            #return redirect(url_for('books', isbn=isbn))
        if request.form["rating"] == '':
            #session['INTERNAL_COMMENT_ERROR'] = 'Unsuccessful. No rating given.'
            return redirect(url_for('books', isbn=isbn))
        db.execute("DELETE FROM Comment WHERE username = :username AND isbn = :isbn", {"username":session['username'], "isbn":isbn})
        db.execute("INSERT INTO Comment (username, isbn, rating, comment_text) VALUES (:username, :isbn, :rating, :comment_text)", {"username":session["username"], "isbn":isbn, "rating":int(request.form["rating"]), "comment_text":request.form["comment_text"]})
        #db.execute("UPDATE TABLE Comment SET ")
        db.commit()
        db.close_all()
        print('3')
        print(request.form)
        print('5')
        #session['INTERNAL_COMMENT_ERROR'] = 'Success.'
        return redirect(url_for('books', isbn=isbn))
    print('6')
    print('does not enter if')
    #session['INTERNAL_COMMENT_ERROR'] = ''
    return redirect(url_for('books', isbn=isbn))

@app.route('/add_usefulness/<string:isbn>/<string:username>', methods=["POST", "GET"])
def add_usefulness(isbn, username):
    print(isbn)
    print(username)
    if request.method == "POST" and username != session['username']:
        check = db.execute("SELECT * FROM Usefulness WHERE username = :username AND isbn = :isbn AND commenter = :commenter", {"username":username, "isbn":isbn, "commenter":session['username']}).fetchall()
        db.close()
        if check:
            try:
                db.execute("UPDATE Usefulness SET rating = :rating WHERE username = :username AND isbn = :isbn AND commenter = :commenter", {"rating":int(request.form['usefulness']), "username":username, "isbn":isbn, "commenter":session['username']})
                db.commit()
                db.close()
            except:
                db.close()
                pass
            return redirect(request.referrer)
        try:
            db.execute("INSERT INTO Usefulness (username, isbn, commenter, rating) VALUES (:username, :isbn, :commenter, :rating)", {"username":username, "isbn":isbn, "commenter":session['username'], "rating":int(request.form['usefulness'])})
            db.commit()
            db.close()
        except:
            db.close()
            pass
        return redirect(request.referrer)
    return redirect(url_for('books', isbn=isbn))

@app.route('/add_trustworthiness/<string:username>', methods=["POST", "GET"])
def add_trustworthiness(username):
    if request.method == "POST" and username != session['username']:
        check = db.execute("SELECT * FROM Trustworthiness WHERE username = :username AND assignee = :assignee", {"username":username, "assignee":session['username']}).fetchall()
        db.close()
        if check:
            try:
                db.execute("UPDATE Trustworthiness SET rating = :rating WHERE username = :username AND assignee = :assignee", {"rating":int(request.form['trustworthiness']), "username":username, "assignee":session['username']})
                db.commit()
                db.close()
            except:
                db.close()
                pass
            return redirect(request.referrer)
        try:
            db.execute("INSERT INTO Trustworthiness (username, assignee, rating) VALUES (:username, :assignee, :rating)", {"username":username, "assignee":session['username'], "rating":int(request.form['trustworthiness'])})
            db.commit()
            db.close()
        except:
            db.close()
            pass
        return redirect(request.referrer)
    return redirect(url_for('users', username=username))

def browse_helper(keyword):
    if keyword.split(' ')[0] == "NOT":
        key = '%' + keyword[4:] + '%'
        res = db.execute("SELECT C.isbn, D.title FROM BookBrowse AS C, Book AS D WHERE C.isbn = D.isbn EXCEPT SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
        db.close()
        return res
    key = '%' + keyword + '%'
    res = db.execute("SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
    db.close()
    return res
    '''
    if order == 0:
        if keyword.split(' ')[0] == "NOT":
            key = '%' + keyword[4:] + '%'
            res = db.execute("SELECT C.isbn, D.title FROM BookBrowse AS C, Book AS D WHERE C.isbn = D.isbn EXCEPT SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
            db.close()
            return res
        key = '%' + keyword + '%'
        res = db.execute("SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
        db.close()
        return res
    elif order == 1:
        if keyword.split(' ')[0] == "NOT":
            key = '%' + keyword[4:] + '%'
            res = db.execute("SELECT C.isbn, D.title FROM BookBrowse AS C, Book AS D, BookDetails AS X WHERE C.isbn = D.isbn AND C.isbn = X.isbn ORDER BY X.publication_date ASC EXCEPT SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
            db.close()
            return res
        key = '%' + keyword + '%'
        res = db.execute("SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B, BookDetails AS X WHERE A.isbn = B.isbn AND A.isbn = X.isbn AND A.keywords LIKE :key ORDER BY X.publication_date ASC", {"key":key}).fetchall()
        db.close()
        return res
    elif order == 2:
        if keyword.split(' ')[0] == "NOT":
            key = '%' + keyword[4:] + '%'
            res = db.execute("SELECT C.isbn, D.title FROM BookBrowse AS C, Book AS D, BookDetails AS X WHERE C.isbn = D.isbn AND C.isbn = X.isbn ORDER BY X.publication_date DESC EXCEPT SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
            db.close()
            return res
        key = '%' + keyword + '%'
        res = db.execute("SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B, BookDetails AS X WHERE A.isbn = B.isbn AND A.isbn = X.isbn AND A.keywords LIKE :key ORDER BY X.publication_date DESC", {"key":key}).fetchall()
        db.close()
        return res
    else:
        return []
    '''

def browse_helper_order(res, order):
    tmp = []
    if order == 0:
        return res
    elif order == 1 or order == 2:
        i = 0
        while i < len(res):
            check = db.execute("SELECT A.isbn, A.title, B.publication_date FROM Book AS A, BookDetails AS B WHERE A.isbn = B.isbn AND A.isbn = :isbn", {"isbn":res[i][0]}).fetchall()
            db.close()
            tmp.append(list(check[0]))
            i = i + 1
        if order == 1:
            tmp.sort(key = operator.itemgetter(2))
        else:
            tmp.sort(key = operator.itemgetter(2), reverse = True)
        return tmp
    elif order == 3 or order == 4:
        i = 0
        while i < len(res):
            check = db.execute("SELECT A.isbn, A.title, AVG(B.rating) AS comment_avg FROM Book AS A LEFT JOIN Comment AS B ON A.isbn = B.isbn WHERE A.isbn = :isbn", {"isbn":res[i][0]}).fetchall()
            db.close()
            tmp.append(list(check[0]))
            i = i + 1
        j = 0
        while j < len(tmp):
            if tmp[j][2] == None:
                tmp[j][2] = 0
            j = j + 1
        if order == 3:
            tmp.sort(key = operator.itemgetter(2))
        else:
            tmp.sort(key = operator.itemgetter(2), reverse = True)
        return tmp
    elif order == 5 or order == 6:
        i = 0
        while i < len(res):
            check = db.execute("SELECT D.isbn, D.title, AVG(E.rating * E.avg_trust) AS comment_avg FROM Book AS D LEFT JOIN (SELECT DISTINCT B.username, B.isbn, B.rating, C.avg_trust FROM Comment AS B LEFT JOIN (SELECT A.username, AVG(A.rating) AS avg_trust FROM Trustworthiness AS A) AS C ON B.username = C.username) AS E ON D.isbn = E.isbn WHERE D.isbn = :isbn", {"isbn":res[i][0]}).fetchall()
            db.close()
            tmp.append(list(check[0]))
            i = i + 1
        j = 0
        while j < len(tmp):
            if tmp[j][2] == None:
                tmp[j][2] = 0
            j = j + 1
        if order == 3:
            tmp.sort(key = operator.itemgetter(2))
        else:
            tmp.sort(key = operator.itemgetter(2), reverse = True)
        return tmp
    else:
        return []

'''
SELECT 
'''

@app.route('/browse_books', methods = ["POST", "GET"])
def browse_books():
    send = []
    if request.method == "POST":
        if not request.form["query"]:
            return render_template('browse_books.html', error_message='Empty Query')
        if request.form["query"].split(' ')[0] == "AND" or request.form["query"].split(' ')[0] == "OR" or request.form["query"].split(' ')[-1] == "AND" or request.form["query"].split(' ')[-1] == "OR" or request.form["query"].split(' ')[-1] == "NOT":
            return render_template('browse_books.html', error_message='Erroneous Query')
        for i in ["AND AND", "OR OR", "AND OR", "OR AND"]:
            if i in request.form["query"]:
                return render_template('browse_books.html', error_message='Erroneous Query')
        keywords = re.split(' AND | OR ', request.form["query"])
        '''
        for i in keywords:
            key = '%' + i + '%'
            res = db.execute("SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
            print(res)
        '''
        tmp = []
        for x in request.form["query"].split(' '):
            if x == "AND" or x == "OR":
                tmp.append(x)
        j, k, final = 0, 0, set([])
        '''
        while j < (len(keywords) + len(tmp)):
            if j % 2 == 0:
                key = '%' + keywords[k] + '%'
                res = db.execute("SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
                k = k + 1
                final = final | set(res)
            else:
                if tmp[(j-1)/2] == "AND":
                    final = 
        '''
        while j < len(keywords):
            '''
            key = '%' + keywords[j] + '%'
            res = db.execute("SELECT A.isbn, B.title FROM BookBrowse AS A, Book AS B WHERE A.isbn = B.isbn AND A.keywords LIKE :key", {"key":key}).fetchall()
            db.close()
            '''
            res = browse_helper(keywords[j])
            if j == 0:
                final = final | set(res)
            else:
                if tmp[j-1] == "AND":
                    final = final & set(res)
                else:
                    final = final | set(res)
            j = j + 1
        print(browse_helper_order(list(final), int(request.form["order"])))
        send = browse_helper_order(list(final), int(request.form["order"]))
        return render_template('browse_books.html', len=len(send), books=send)

    return render_template('browse_books.html', len=len(send))

@app.route('/comments_by_usefulness/<string:isbn>', methods=["POST", "GET"])
def comments_by_usefulness(isbn):
    check = db.execute("SELECT A.username, A.isbn, A.rating, A.comment_text, B.rating AS useful FROM Comment AS A LEFT JOIN Usefulness AS B ON A.username = B.username AND A.isbn = B.isbn WHERE A.isbn = :isbn ORDER BY useful DESC, A.rating DESC LIMIT :this_limit", {"isbn":isbn, "this_limit":int(request.form["limit"])}).fetchall()
    db.close()
    message = ''
    if check:
        #return render_template('comments_usefulness.html', comments=check, len=len(check))
        message = 'Success'
    return render_template('comments_usefulness.html', message=message, len=len(check), comments=check, isbn=isbn)

@app.route('/buying_suggestions', methods=["POST", "GET"])
def buying_suggestions():
    '''
    users = []
    orders = db.execute("SELECT isbn FROM Orders WHERE username = :username ORDER BY copies DESC", {"username":session["username"]}).fetchall()
    db.close()
    if not orders:
        return render_template('buying_suggestions.html', message='No suggestions')
    i = 0
    while i < len(orders):
        tmp = db.execute("SELECT username FROM Orders WHERE isbn = :isbn AND username != :username", {"isbn":orders[i][0], "username":session['username']}).fetchall()
        db.close()
        if tmp:
            users.append(tmp[0])
        i = i + 1
    print(users)
    if not users:
        return render_template('buying_suggestions.html', message='No suggestions')
    '''
    sug = []
    sug = db.execute("SELECT Y.isbn, X.title FROM Book AS X, (SELECT DISTINCT C.isbn FROM Orders AS C, (SELECT DISTINCT A.username FROM Orders AS A, (SELECT isbn FROM Orders WHERE username = :username) AS B WHERE A.isbn = B.isbn AND A.username != :username) AS D WHERE C.username = D.username ORDER BY C.copies DESC) AS Y WHERE X.isbn = Y.isbn", {"username":session['username']}).fetchall()
    db.close()
    print(sug)
    return render_template('buying_suggestions.html', all_books=sug, len=len(sug))

@app.route('/all_authors', methods=["POST", "GET"])
def all_authors():
    authors = db.execute("SELECT DISTINCT author_name FROM Author").fetchall()
    db.close()
    return render_template('all_authors.html', authors=authors, len=len(authors))

@app.route('/author/<string:name>', methods=["POST", "GET"])
def author(name):
    books = []
    info = ''
    if request.method == "POST":
        if int(request.form['manner']) == 1:
            books = db.execute("SELECT A.isbn, B.title FROM Author AS A, Book AS B WHERE A.isbn = B.isbn AND A.author_name = :author_name", {"author_name":name}).fetchall()
        elif int(request.form['manner']) == 2:
            #books = db.execute("SELECT D.isbn, E.title FROM (SELECT C.isbn FROM (SELECT A.isbn FROM Author AS A WHERE A.author_name = :author_name) AS B, Author AS C WHERE B.isbn = C.isbn AND C.author_name != :author_name) AS D, Book AS E WHERE D.isbn = E.isbn", {"author_name":name}).fetchall()
            books = db.execute("SELECT DISTINCT M.isbn, O.title FROM Author AS M, (SELECT DISTINCT C.author_name FROM (SELECT A.isbn FROM Author AS A WHERE A.author_name = :author_name) AS B, Author AS C WHERE B.isbn = C.isbn AND C.author_name != :author_name) AS N, Book AS O WHERE M.author_name = N.author_name AND M.isbn = O.isbn", {"author_name":name}).fetchall()
        elif int(request.form['manner']) == 3:
            #books = db.execute("SELECT Z.isbn, L.title FROM (SELECT X.isbn FROM Author AS X, (SELECT DISTINCT M.author_name FROM Author AS M, (SELECT DISTINCT C.isbn, C.author_name FROM (SELECT A.isbn FROM Author AS A WHERE A.author_name = :author_name) AS B, Author AS C WHERE B.isbn = C.isbn AND C.author_name != :author_name) AS N WHERE M.isbn = N.isbn AND M.author_name != :author_name EXCEPT SELECT DISTINCT C.author_name FROM (SELECT A.isbn FROM Author AS A WHERE A.author_name = :author_name) AS B, Author AS C WHERE B.isbn = C.isbn AND C.author_name != :author_name) AS Y WHERE X.author_name = Y.author_name) AS Z, Book AS L WHERE Z.isbn = L.isbn", {"author_name":name}).fetchall()
            books = db.execute("SELECT DISTINCT R.isbn, S.title FROM Author AS R, Book AS S, (SELECT DISTINCT CC.author_name FROM Author AS CC, (SELECT DISTINCT AA.isbn FROM Author AS AA, (SELECT DISTINCT C.author_name FROM (SELECT A.isbn FROM Author AS A WHERE A.author_name = :author_name) AS B, Author AS C WHERE B.isbn = C.isbn AND C.author_name != :author_name) AS BB WHERE AA.author_name = BB.author_name) AS DD WHERE CC.isbn = DD.isbn AND CC.author_name != :author_name EXCEPT SELECT DISTINCT C.author_name FROM (SELECT A.isbn FROM Author AS A WHERE A.author_name = :author_name) AS B, Author AS C WHERE B.isbn = C.isbn AND C.author_name != :author_name) AS T WHERE R.author_name = T.author_name AND R.isbn = S.isbn", {"author_name":name}).fetchall()
        else:
            books = []
        db.close_all()
        if not books:
            info = 'No Books'
        print(books)
    return render_template('author.html', author=name, books=books, len=len(books), info=info)

@app.route('/inventory_status/<string:isbn>', methods=["POST", "GET"])
def inventory_status(isbn):
    book = db.execute("SELECT A.isbn, A.price, A.stock, B.title FROM Inventory AS A, Book AS B WHERE A.isbn = :isbn AND B.isbn = A.isbn", {"isbn":isbn}).fetchall()
    db.close()
    return render_template('inventory_status.html', book=book[0])

@app.route('/inventory_status_add_copy/<string:isbn>', methods=["POST", "GET"])
def inventory_status_add_copy(isbn):
    copies = 1
    if request.method == "POST":
        try:
            if request.form['copies']:
                copies = int(request.form['copies'])
        except KeyError:
            pass
        try:
            if request.form['removals']:
                copies = 0 - int(request.form['removals'])
        except KeyError:
            pass
        db.execute("UPDATE Inventory SET stock = stock + :copies WHERE isbn = :isbn", {"copies":copies, "isbn":isbn})
        db.commit()
        db.close()
    waitlist_check(isbn)
    return redirect(url_for('inventory_status', isbn=isbn))
    
@app.route('/inventory_status_reserve_copies/<string:isbn>', methods = ["POST", "GET"])
def inventory_status_reserve_copies(isbn):
    if request.method == "POST":
        db.execute("UPDATE Inventory SET stock = stock - :copies WHERE isbn = :isbn", {"copies":int(request.form['reserves']), "isbn":isbn})
        db.execute("UPDATE Reserve SET stock = stock + :copies WHERE isbn = :isbn", {"copies":int(request.form['reserves']), "isbn":isbn})
        db.commit()
        db.close()
    return redirect(url_for('inventory_status', isbn=isbn))

@app.route('/add_to_waitlist/<string:isbn>', methods = ["POST", "GET"])
def add_to_waitlist(isbn):
    if request.method == "POST":
        db.execute("INSERT INTO Waitlist (username, isbn) VALUES (:username, :isbn)", {"username":session['username'], "isbn":isbn})
        db.commit()
        db.close()
    return redirect(request.referrer)

@app.route('/user_list')
def user_list():
    users = db.execute("SELECT username FROM User").fetchall()
    if users:
        return render_template('user_list.html', users=users, len=len(users))
    else:
        return 'Empty'

@app.route('/delete_user', methods=["GET", "POST"])
def delete_user():
    users_2d = db.execute("SELECT User.username FROM User WHERE User.username NOT IN (SELECT Manager.username FROM Manager) ORDER BY time_of_registration").fetchall()
    db.close()
    users = []
    i = 0
    while i < len(users_2d):
        users.append(users_2d[i][0])
        i=i+1
    if request.method == "POST":
        #db.execute("INSERT INTO Manager (username) VALUES (:username);", {'username':request.form["users"]})
        db.execute("DELETE FROM User WHERE username = :username", {"username":request.form['users']})
        db.commit()
        db.close()
        new_2d = db.execute("SELECT User.username FROM User WHERE User.username NOT IN (SELECT Manager.username FROM Manager) ORDER BY time_of_registration").fetchall()
        db.close()
        new = []
        j = 0
        while j < len(new_2d):
            new.append(new_2d[j][0])
            j=j+1
        return render_template('delete_user.html', len=len(new), users=new, message=request.form["users"]) 
    return render_template('delete_user.html', len=len(users), users=users)

if __name__ == "__main__":
    app.run(debug = True)