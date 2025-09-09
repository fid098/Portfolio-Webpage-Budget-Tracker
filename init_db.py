import sqlite3

def init_db():
    conn = sqlite3.connect("users_information.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        hash TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    cash REAL DEFAULT 0 NOT NULL,
    rent REAL DEFAULT 0 NOT NULL,
    savings REAL DEFAULT 0 NOT NULL,
    investments REAL DEFAULT 0 NOT NULL,
    miscellaneous REAL DEFAULT 0 NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
    categories_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    user_created BOOLEAN
    )
    """)

    
    cur.execute(""" 
        INSERT OR IGNORE INTO categories (name, user_created)
    VALUES 
    ('Food', 0),
    ('Transport', 0),
    ('Entertainment', 0),
    ('Utilities', 0),
    ('Health', 0),
    ('Wage', 0),
    ('Gift', 0),
    ('Other', 0);
        """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions(
    transaction_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    category_id INTEGER,
    amount REAL,
    transaction_type TEXT,
    description TEXT,
    date DATE,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(category_id) REFERENCES categories(categories_id)
);
                """)
    
    cur.execute(""" ALTER TABLE transactions 
    ADD COLUMN budget_category TEXT;
    """)
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        goal_id INTEGER PRIMARY KEY,
        category_id INTEGER,
        goal_amount REAL,
        current_amount REAL,
        target_date DATE,
        FOREIGN KEY(category_id) REFERENCES categories(category_id)
    )''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()