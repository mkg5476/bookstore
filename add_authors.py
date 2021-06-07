import csv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///test1.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "isolation_level":None})
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def author_adder(names, isbn):
    tmp = names.split('/')
    for i in names.split('/'):
        #try:
        db.execute("INSERT INTO Author (author_name, isbn) VALUES (:author_name, isbn);", {"author_name":i, "isbn":isbn})
        db.commit()
        db.close()
        #except:
            #pass

def import_books():
    f = open("books_new.csv")
    reader = (csv.DictReader(f))
    for field in reader:
        #print('herehh')
        #print('here4')
        author_adder(field["authors"], field["isbn13"])