import sqlite3

try:
    conn = sqlite3.connect('ai_gym_coach.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users;")
    emails = cursor.fetchall()
    print("Registered emails:")
    for email in emails:
        print(f" - {email[0]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
