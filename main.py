from fastapi import FastAPI

from pydantic import BaseModel
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
import sqlite3


app = FastAPI()


conn = sqlite3.connect('book_review.db')
cursor = conn.cursor()


# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    publication_year INTEGER
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY,
                    book_id INTEGER,
                    review_text TEXT,
                    rating INTEGER,
                    FOREIGN KEY(book_id) REFERENCES books(id)
                )''')


# Temporary db 
books_db = []
reviews_db = []



class Book(BaseModel):
	title: str
	author: str | None=None
	publication_year: int

class Review(BaseModel):
	book_id: int
	comment: str | None=None
	rating: int #= Field(..., ge=1, le=10)


# ENDPOINT to add books
@app.post("/books/", response_model=Book, tags=["Books"])
def add_book(book:Book):
	cursor.execute('''INSERT INTO books (title, author, publication_year) 
                      VALUES (?, ?, ?)''', (book.title, book.author, book.publication_year))
    conn.commit()

    #it is used to get id of the last row inserted into DB using .execute()
    book.id = cursor.lastrowid
	
	return book



# ENDPOINT to add reviews
@app.post("/review/")#, response_model=Review)
def add_review(review:Review):
	cursor.execute('''INSERT INTO reviews (book_id, review_text, rating) 
                      VALUES (?, ?, ?)''', (review.book_id, review.review_text, review.rating))

	conn.commit()
	review.id = cursor.lastrowid

	return review


# ENDPOINT to get books details
@app.get("/books/", response_model=list[Book])
def get_books(author: str=None, publication_year:int = None):

	query = "SELECT * FROM books"
	if author:
        query += f" WHERE author = '{author}'"

	if publication_year:
		if author:
            query += " AND"
        else:
			query += " WHERE"
		query += f" publication_year = '{publication_year}'"
	cursor.execute(query)
    books = cursor.fetchall()

	return book


# ENDPOINT to get books reviews
@app.get("/reviews/{book_id}", response_model=list[Review])
def get_reviews(book_id: int):
	cursor.execute("SELECT * FROM reviews WHERE book_id = ?", (book_id))
	reviews = cursor.fetchall()

	if not reviews:
		raise HTTPException(status_code = 404, details = "Reviews not found")
	
	return reviews


# Exception Handling
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
    		status_code = exc.status_code,
    		content = {
    			"message": exc.details
    		}
    )