import sqlite3
from datetime import datetime

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

# check existing columns
cursor.execute("PRAGMA table_info(reviews)")
columns = [column[1] for column in cursor.fetchall()]

# add created_at column if missing
if "created_at" not in columns:
    cursor.execute("ALTER TABLE reviews ADD COLUMN created_at DATETIME")
    print("created_at column added")

# fill old empty created_at values
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cursor.execute(
    """
    UPDATE reviews
    SET created_at = ?
    WHERE created_at IS NULL
    """,
    (current_time,)
)

conn.commit()
conn.close()

print("Migration completed successfully")