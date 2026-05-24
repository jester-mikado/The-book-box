from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from models import Book, Review


from database import get_db
from models import Book
from schemas import BookCreate
from auth import get_current_user

router = APIRouter()


@router.post("/books")
def add_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    existing_book = db.query(Book).filter(
        Book.title == book.title,
        Book.author == book.author
    ).first()

    if existing_book:
        raise HTTPException(
            status_code=400,
            detail="This book already exists"
        )

    new_book = Book(
        title=book.title,
        author=book.author,
        genre=book.genre,
        summary=book.summary,
        added_by=current_user.id
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return {
        "message": "Book Added",
        "book": new_book
    }

@router.get("/books")
def get_books(db: Session = Depends(get_db)):

    books = db.query(Book).all()

    result = []

    for book in books:

        result.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "summary": book.summary,
            "uploaded_by": book.user.username
        })

    return result
@router.get("/my-books")
def my_books(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    books = db.query(Book).filter(
        Book.added_by == current_user.id
    ).all()

    return books


@router.get("/my-book-reviews")
def my_book_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    books = db.query(Book).filter(
        Book.added_by == current_user.id
    ).all()

    result = []

    for book in books:

        reviews = db.query(Review).filter(
            Review.book_id == book.id
        ).all()

        for review in reviews:

            result.append({
                "book_title": book.title,
                "rating": review.rating,
                "comment": review.comment,
                "username": review.user.username
            })

    return result

@router.get("/my-books")
def my_books(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    books = db.query(Book).filter(
        Book.added_by == current_user.id
    ).all()

    result = []

    for book in books:

        result.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "summary": book.summary
        })

    return result


@router.get("/my-book-reviews")
def my_book_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    books = db.query(Book).filter(
        Book.added_by == current_user.id
    ).all()

    result = []

    for book in books:

        reviews = db.query(Review).filter(
            Review.book_id == book.id,
            Review.user_id != current_user.id
        ).all()

        for review in reviews:

            result.append({
                "book_title": book.title,
                "rating": review.rating,
                "comment": review.comment,
                "username": review.user.username,
                "time": review.created_at.strftime("%d %b %Y, %I:%M %p")
            })

    return result

@router.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not book:

        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    # only uploader can delete
    if book.added_by != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Not allowed to delete this book"
        )

    # delete reviews first
    db.query(Review).filter(
        Review.book_id == book.id
    ).delete()

    db.delete(book)

    db.commit()

    return {
        "message": "Book deleted successfully"
    }