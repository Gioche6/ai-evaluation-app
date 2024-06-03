import sqlite3

def reset_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS evaluations')
    c.execute('''
        CREATE TABLE evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            score REAL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    reset_db()
    print("Database reset and initialized.")
