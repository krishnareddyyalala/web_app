import sqlite3

def create_table():
 conn=sqlite3.connect('database.db')
 cursor=conn.cursor()

 cursor.execute("""
 create table if not exists users(
     id integer primary key autoincrement,
     username text unique not null,
     password text not null
 )  
 """                                                      
 )

 cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        day TEXT,
        purpose TEXT,
        type TEXT,
        amount REAL,
        balance REAL,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
 """
 )

 conn.commit()
 conn.close()

if __name__ == '__main__':
    create_table()
    print("Tables created successfully!")
