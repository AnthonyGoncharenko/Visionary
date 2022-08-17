import sqlite3
import os
class Database:
    def __init__(self, database_name):
        if not os.path.exists(database_name):
            with open(database_name, 'wb'):
                ...
        self.conn = sqlite3.connect(database_name)
        print('------------------------------------------------------------')
        print('I am Connected')
        print('------------------------------------------------------------')
        self.create()

    def create(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE if not exists users 
        (
            id SERIAL PRIMARY KEY,
            username VARCHAR(25) UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            email TEXT NOT NULL
         );
        ''')
        self.conn.commit()
        c.close()

    def select(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        return c.fetchall()
    def execute(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        self.conn.commit()
    def create_user(self, username, encrypted_password, email):
        self.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, encrypted_password, email])
    def get_user(self, username):
        data = self.select('SELECT * FROM users WHERE username=?', [username])
        if data:
            d = data[0]
            return {
            'username': d[1],
            'encrypted_password': d[2],
            'email': d[3],
            }
        else:
            return None
    def close(self):
        self.conn.close()