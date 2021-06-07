import os
import requests
import re
import hashlib
import random

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import sqlalchemy

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#db = sqlalchemy(app)

def Validate(name, email, user, passw, repeatpass):
    message=""
    check=True
    if not (re.match("^[a-zA-z ]+$",name)):
        check=False
        message="Invalid Name"
        
    if check and not (re.match(r"^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$",email)):
        check=False
        message="Invalid Email"
    else:
        for u in db.execute("SELECT email from USERS").fetchall():
            if re.match(u[0],email,re.I):
                check=False
                message="Email aldready exists"

    if check and not (re.match("^[a-zA-z0-9_]*$",user)):
        check=False
        message="Invalid Username"
        
    else:
        for u in db.execute("SELECT username from USERS").fetchall():
            if re.match(u[0],user,re.I):
                check=False
                message="Username aldready exists"
        
    if check and not (re.match("^[A-Za-z0-9@#$%^&+=]{8,}$",passw)):
        check=False
        message="Invalid Password"
        if len(passw)<8: message+=" (Minimum 8 charachters)"
        else: message+=" (only alphabets, numbers and @#$%^&+=] are allowed)"

    if check and not  passw==repeatpass:
        check=False
        message="Passwords do not match"
    
    if check:
        passw=hashlib.md5(passw.encode()).hexdigest()
        db.execute("INSERT INTO users (name, email, username, passw) VALUES (:name, :email, :username, :passw);",{'name':name, 'email':email,'username':user,'passw':passw})
        db.commit()
        message="Registered Successfully"

    return (message, check)

@app.route("/")
def index():
    if request.method == "GET" :
        if request.args.get('logout'):
            session.pop('username', None)
            session.pop('logged_in', False)
            session.pop('user', None)
            session.pop('user_no', None)
    
    return render_template("index.html")

@app.route("/results")
def results():
    data=[]
    query=request.args.get('q')
    if query:
        srt=request.args.get('sort')
        if not srt: srt="title"
        page=int(request.args.get('page')) if request.args.get('page') else 1 
        regex=".*"+query+".*"
        data = db.execute(f"SELECT * from BOOKS where (title ~* :rgx) or (author ~* :rgx) or (isbn ~* :rgx)  or (CAST(year AS TEXT) ~* :rgx) ORDER BY {srt} ASC;"
                ,{'rgx':regex}).fetchall()
        pages=1
        lpage=len(data)
        if len(data)>15:
            pages, lpage=divmod(len(data),15)
            if lpage!=0: pages=pages+1 
            else: lpage=15

        data=data[(page-1)*15:page*15] if pages!=page else data[(page-1)*15:(page-1)*15+lpage]

        return render_template("result.html", data=data, error=False, q=query,page=page,pages=pages,sort=srt)
    else:
        return render_template("result.html", data=data, error=True)



@app.route("/signup",methods=['POST','GET'])
def signup():
    message=""
    check=None
    if request.method=="POST":
        message, check= Validate(request.form.get("name"), request.form.get("email"),request.form.get("user"), request.form.get("pass"), request.form.get("repeatpass"))

    rang = "green" if check else "red"
    return render_template("signup.html",message=message,rang=rang)

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == "GET" :
        if request.args.get('logout'):
            session["logged_in"]=False

    if request.method == "POST" :
        for usr in db.execute("SELECT * from USERS where username = :usr",{"usr":request.form.get("username")}).fetchall():
            if re.match(usr[4], hashlib.md5(request.form.get('password').encode()).hexdigest()):
                session["logged_in"]=True
                session["username"]=usr[3]
                session["user"]=usr[1]
                session["user_no"]=usr[0]
                return render_template("index.html")

    return render_template("login.html")
'''
@app.route("/book/<string:isbn>",methods=["GET","POST"])
def book(isbn):
    remove=request.args.get('remove') if request.args.get('remove') else False
    book=usrev=[]
    error=''
    book= db.execute("SELECT * from BOOKS WHERE ISBN = :isbn",{'isbn':isbn}).fetchall()[0]
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "fcJPItrdhaNf8KQuAd1bQ", "isbns": isbn})
    if "logged_in" in session:
        if session["logged_in"]:
            if remove:
                usrev = db.execute("DELETE from reviews r where isbn = :i and user_id = :u",{'i':isbn,'u':session["user_no"]})
                db.commit()

            usrev = db.execute("SELECT username, rating, review from users u, reviews r where isbn = :i and u.id = r.user_id and u.id = :u",{'i':isbn,'u':session["user_no"]}).fetchall()
            if request.method=="POST" and usrev==[]:
                if not len(request.form.get("review")):
                    error="Please enter a valid review"
                elif not request.form.get("rating"):
                    error="Please enter a valid rating in stars"
                else:
                    db.execute("INSERT INTO REVIEWS (isbn, user_id, review, rating) VALUES (:i, :u, :rev, :rate)",
                                {'i':book[0], 'u':session["user_no"], 'rev':request.form.get("review"), 'rate':request.form.get("rating")})
                    usrev = db.execute("SELECT username, rating, review from users u, reviews r where isbn = :i and u.id = r.user_id and u.id = :u",{'i':isbn,'u':session["user_no"]}).fetchall()
                    db.commit()         
    rev = db.execute("SELECT username, rating, review from users u, reviews r where isbn = :i and u.id = r.user_id",{'i':isbn}).fetchall()
    res=res.json()['books'][0]['average_rating']    
    star=str(float(res)*16)+"px"
    scr={1:[0,0],2:[0,0],3:[0,0],4:[0,0],5:[0,0]}
    avg=0
    l=len(rev) if len(rev)>0 else 1
    for i in rev:
        scr[i[1]][0]+=1
        avg+=i[1]
    for i in scr:
        scr[i][1]=str((scr[i][0]/l)*100)+"%"
    avg=["{0:.2f}".format(avg/l),str("{0:.2f}".format(avg/l*20))+"px"]
    l=len(rev)
    return render_template("book_details.html",book=book,rev=rev,usrev=usrev,res=res,star=star,l=l,error=error,avg=avg, scr=scr)
    
@app.route("/api/<string:isbn>")
def book_api(isbn):
    try:
        book = db.execute("SELECT title, author, year from BOOKS WHERE isbn=:isbn",{"isbn":isbn}).fetchall()[0]
    except:
        return jsonify({"error": "Invalid ISBN"}), 404

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "fcJPItrdhaNf8KQuAd1bQ", "isbns": isbn})
    res=res.json()['books'][0]

    return jsonify({
        "title": book[0],
        "author": book[1],
        "year": book[2],
        "isbn": isbn,
        "review_count": res['reviews_count'],
        "average_score": res['average_rating']
    })
'''