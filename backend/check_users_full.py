import sqlite3

try:
    conn = sqlite3.connect('ai_gym_coach.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users;")
    columns = [description[0] for description in cursor.description]
    users = cursor.fetchall()
    print(f"Columns: {columns}")
    for user in users:
        user_dict = dict(zip(columns, user))
        # Mask password hash for security but show if it looks like a hash
        hash_val = user_dict['password_hash']
        user_dict['password_hash'] = hash_val[:10] + "..." if hash_val else "None"
        print(user_dict)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
