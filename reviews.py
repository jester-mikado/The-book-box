from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Review
from schemas import ReviewCreate
from auth import get_current_user

router = APIRouter()


@router.post("/reviews/{book_id}")
def add_review(
    book_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    existing_review = db.query(Review).filter(
        Review.book_id == book_id,
        Review.user_id == current_user.id
    ).first()

    if existing_review:

        return {
            "message": "You already reviewed this book"
        }

    new_review = Review(
        book_id=book_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )

    db.add(new_review)

    db.commit()

    db.refresh(new_review)

    return {
        "message": "Review Added",
        "review": new_review
    }
    return reviews
@router.get("/reviews/{book_id}")
def get_reviews(
    book_id: int,
    db: Session = Depends(get_db)
):

    reviews = db.query(Review).filter(
        Review.book_id == book_id
    ).all()

    result = []

    for review in reviews:

        result.append({

            "id": review.id,

            "rating": review.rating,

            "comment": review.comment,

            "username": review.user.username
        })

    return result