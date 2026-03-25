import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

email = "test@example.com"
new_password = "Password123"
hashed_password = hash_password(new_password)

try:
    conn = sqlite3.connect('ai_gym_coach.db')
    cursor = conn.cursor()
    # Update password for test@example.com
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed_password, email))
    if cursor.rowcount == 0:
        # If user doesn't exist, create it (though we saw it exists)
        import uuid
        user_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO users (user_id, email, password_hash) VALUES (?, ?, ?)", (user_id, email, hashed_password))
        print(f"Created user {email} with password {new_password}")
    else:
        print(f"Updated user {email} with password {new_password}")
    conn.commit()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
