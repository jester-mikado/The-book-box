import sqlite3
import psycopg2

SQLITE_DB = "test.db"

POSTGRES_URL = "postgresql://jester_books_user:m7UzjL6L5J0vH7dAmf3aQ5ceN237eB0O@dpg-d89dhpp9rddc7396mp50-a.virginia-postgres.render.com/jester_books"

sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

pg_conn = psycopg2.connect(POSTGRES_URL)
pg_cursor = pg_conn.cursor()


# Create tables in PostgreSQL
pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE,
    email VARCHAR UNIQUE,
    password VARCHAR
);
""")

pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    author VARCHAR,
    genre VARCHAR,
    summary TEXT,
    added_by INTEGER REFERENCES users(id)
);
""")

pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books(id),
    user_id INTEGER REFERENCES users(id),
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP
);
""")


# Copy users
sqlite_cursor.execute("SELECT * FROM users")
users = sqlite_cursor.fetchall()

for user in users:
    pg_cursor.execute("""
        INSERT INTO users (id, username, email, password)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (
        user["id"],
        user["username"],
        user["email"],
        user["password"]
    ))


# Copy books
sqlite_cursor.execute("SELECT * FROM books")
books = sqlite_cursor.fetchall()

for book in books:
    pg_cursor.execute("""
        INSERT INTO books (id, title, author, genre, summary, added_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (
        book["id"],
        book["title"],
        book["author"],
        book["genre"],
        book["summary"],
        book["added_by"]
    ))


# Copy reviews
sqlite_cursor.execute("SELECT * FROM reviews")
reviews = sqlite_cursor.fetchall()

for review in reviews:
    created_at = review["created_at"] if "created_at" in review.keys() else None

    pg_cursor.execute("""
        INSERT INTO reviews (id, book_id, user_id, rating, comment, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (
        review["id"],
        review["book_id"],
        review["user_id"],
        review["rating"],
        review["comment"],
        created_at
    ))


# Fix PostgreSQL auto increment IDs
pg_cursor.execute("SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1));")
pg_cursor.execute("SELECT setval('books_id_seq', COALESCE((SELECT MAX(id) FROM books), 1));")
pg_cursor.execute("SELECT setval('reviews_id_seq', COALESCE((SELECT MAX(id) FROM reviews), 1));")

pg_conn.commit()

sqlite_conn.close()
pg_cursor.close()
pg_conn.close()

print("SQLite data migrated to Render PostgreSQL successfully!")