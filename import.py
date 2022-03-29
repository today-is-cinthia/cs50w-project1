import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

create_engine=DATABASE_URL("postgresql://digzomnzkndovc:d887b572e5808373d9198fb680e19a6932461bb3796090f897ad2cb8335f6214@ec2-44-194-92-192.compute-1.amazonaws.com:5432/dcjqndie5uia2a")
db = scoped_session(sessionmaker(bind=engine))

def main():
    a=open("books.csv")
    reader=csv.reader(a)
    for isbn,title, author, year in reader:
        db.execute("INSERT INTO (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",{"isbn": isbn, "title": title, "author": author, "year": year})
        db.commit()
        print("exportado correctamente")

 if __name__ == "__main__":
     main()
