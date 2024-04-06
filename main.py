from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import List


MONGODB_URI = "mongodb+srv://teghsingh2:teghsingh@cluster0.qjwhcoi.mongodb.net/"

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)
db = client['library'] 
collection = db['books']  
app = FastAPI()

# Pydantic models
class Book(BaseModel):
    id: str
    title: str
    author: str
    year: int

    class Config:
        orm_mode = True

# API endpoints
@app.post("/books/", response_model=Book)
async def create_book(book: Book):
    book_dict = book.dict()
    inserted_book = collection.insert_one(book_dict)
    book_id = str(inserted_book.inserted_id)
    return {**book_dict, "id": book_id}

@app.get("/books/", response_model=List[Book])
async def list_books():
    books = list(collection.find())
    return [{"id": str(book.pop('_id')), **book} for book in books]

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    book = collection.find_one({"_id": ObjectId(book_id)})
    if book:
        return {**book, "id": str(book['_id'])}
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: str, book: Book):
    book_dict = book.dict()
    updated_book = collection.update_one({"_id": ObjectId(book_id)}, {"$set": book_dict})
    if updated_book.modified_count == 1:
        return {**book_dict, "id": book_id}
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    deleted_book = collection.delete_one({"_id": ObjectId(book_id)})
    if deleted_book.deleted_count == 1:
        return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")
