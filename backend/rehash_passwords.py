import sys
import os
import pymysql

# Make sure backend utils is available
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from utils import hash_password

# --- Database connection ---
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Wc1983***",  # change if needed
    database="expense_tracker"
)
cursor = conn.cursor()

# Fetch all users
cursor.execute("SELECT user_ID, user_name, password FROM user")
users = cursor.fetchall()

updated_count = 0

for user_id, username, password in users:
    # Skip already hashed passwords (they start with "$2b$")
    if password.startswith("$2b$"):
        continue

    # Hash plaintext passwords
    new_hashed = hash_password(password)

    cursor.execute("UPDATE user SET password=%s WHERE user_ID=%s", (new_hashed, user_id))
    updated_count += 1
    print(f"✅ Rehashed password for user: {username}")

conn.commit()
cursor.close()
conn.close()

print(f"\n🎯 Done! Rehashed {updated_count} users successfully.")
