from fastapi import FastAPI

from pydantic import BaseModel
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder


app = FastAPI()


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
@app.post("/books/", response_model=Book)
def add_book(book:Book):
	books_db.append(book)
	return book

# ENDPOINT to add reviews
@app.post("/review/")#, response_model=Review)
def add_review(review:Review):
	# book_exists = any(book.book_id == review.book_id for book in books_db)
	if review.book_id >= len(books_db):
		raise HTTPException(status_code=404, detail="Book not found")
	reviews_db.append(review)
	return review


# ENDPOINT to get books details
@app.get("/books/", response_model=list[Book])
def get_books(author: str=None, publication_year:int = None):
	filtered_book = books_db
	if author:
		filtered_book = [book for book in filtered_book if book.author == author]

	if publication_year:
		filtered_book = [book for book in filtered_book if book.publication_year == publication_year]
	else:
		filtered_book = books_db

	return filtered_book


# ENDPOINT to get books reviews
@app.get("/reviews/{book_id}", response_model=list[Review])
def get_reviews(book_id: int):
	# if book_id >= len(books_db):
	# 	raise HTTPException(status_code=404, detail="Book not available")

	book_reviews = [review for review in reviews_db if review.book_id == book_id]
	if not book_reviews:
		raise HTTPException(status_code=404, detail="No reviews found for the book")
	return book_reviews


# Exception Handling
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
    		status_code = exc.status_code,
    		content = {
    			"message":"endpoint not found"
    		}
    )