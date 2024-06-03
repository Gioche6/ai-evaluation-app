import sqlite3

conn = sqlite3.connect('local_database.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        score REAL NOT NULL
    )
''')
conn.commit()
conn.close()
