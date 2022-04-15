import requests
import json

isbn = '0425285049'

response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
    
count = response['items'][0]['volumeInfo']['ratingsCount']
rating = response['items'][0]['volumeInfo']['averageRating']

print(count)
print(rating)



@app.route("/libros/<isbn>",methods=['GET','POST'])
def libros(isbn):
    #query = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    #book_id = query[0]
    book_id = request.
    if request.method == "POST":
        rating = request.form.get("rating")
        comentario = request.form.get("comentario")

        if rating == "" or comentario == "":
            return render_template("error.html")
        else:
            db.execute("INSERT INTO reviews \
             (comentario, rating, id_book, id_user) VALUES (:comentario, :rating, :id_book, :id)",
              { "comentario": comentario, "rating": rating, "id_book": book_id, "id": session["user_id"]})
            db.commit()
  
    validation = db.execute("SELECT * FROM books WHERE isbn=:isbn;",{'isbn':isbn}).fetchall() 
    if validation == None:
        return render_template('libros.html')
    
    reviews = db.execute("SELECT * FROM reviews WHERE id_book=:id;",{'id':book_id}).fetchall()
    if request.method == "GET":
        try:
            validation2 = db.execute("SELECT id_user FROM reviews WHERE id_book = :id_book AND id_user :=id_user",
             {"id_book":book_id, "id_user":session["user_id"]})
        except:
            pass
        
        try:
            response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
            count = response['items'][0]['volumeInfo']['ratingsCount']
            rating = response['items'][0]['volumeInfo']['averageRating']  
        except:
            count,rating = 0,0
    return render_template("libros.html",val = validation,count=count, rating=rating,reviews=reviews)