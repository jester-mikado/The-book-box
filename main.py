from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import get_current_user
from fastapi.responses import RedirectResponse
from database import Base, engine, get_db
from models import User

from schemas import UserCreate

from auth import (
    hash_password,
    verify_password,
    create_access_token
)

from books import router as book_router
from reviews import router as review_router

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request


# Create Database Tables
Base.metadata.create_all(bind=engine)

# Create FastAPI App
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(book_router)
app.include_router(review_router)


# Home Route
# @app.get("/")
# def home():
#     return {
#         "message": "Online Book Review System Running"
#     }



@app.get("/")
def home():
    return RedirectResponse(url="/ui")

@app.post("/auth/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Registered Successfully"
    }


@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    print(form_data.username)

    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Username"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/ui", response_class=HTMLResponse)
def ui_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/login-page", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.get("/register-page", response_class=HTMLResponse)
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@app.get("/add-book-page", response_class=HTMLResponse)
def add_book_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="add_book.html"
    )

@app.get("/book/{book_id}", response_class=HTMLResponse)
def book_detail_page(
    request: Request,
    book_id: int
):

    return templates.TemplateResponse(
        request=request,
        name="book_detail.html",
        context={
            "book_id": book_id
        }
    )

@app.get("/profile-page", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="profile.html"
    )
@app.get("/my-space", response_class=HTMLResponse)
def my_space(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="my_space.html"
    )
    
@app.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "username": current_user.username
    }
