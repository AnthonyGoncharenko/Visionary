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
        ###############################################
        #              CREATE USERS TABLE
        ###############################################
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
        (
            uid SERIAL PRIMARY KEY,
            username VARCHAR(25) UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            email VARCHAR(120) NOT NULL
         );''')
        self.conn.commit()
        ###############################################
        #            END CREATE USERS TABLE
        ###############################################

        ###############################################
        #              CREATE POSTS TABLE
        ###############################################
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posts 
        (
            pid SERIAL PRIMARY KEY, 
            uid INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            imid INTEGER,
            FOREIGN KEY(uid) REFERENCES users(uid),
            FOREIGN KEY(imid) REFERENCES images(imid)
        );''')
        self.conn.commit()
        ###############################################
        #            END CREATE POSTS TABLE
        ###############################################
        
        ###############################################
        #              CREATE IMAGES TABLE
        ###############################################        
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS images 
        (
            imid SERIAL PRIMARY KEY,
            uid INTEGER NOT NULL,
            img VARBINARY(8000) NOT NULL,
            FOREIGN KEY(uid) REFERENCES users(uid)
        );''')
        self.conn.commit()
        ###############################################
        #            END CREATE IMAGES TABLE
        ###############################################        
        c.close()

    def __select(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        return c.fetchall()

    def __execute(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        self.conn.commit()

    def create_user(self, username, encrypted_password, email):
        self.__execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, encrypted_password, email])

    def get_user(self, username):
        data = self.__select('SELECT * FROM users WHERE username=?', [username])
        if data:
            d = data[0]
            return {
            'user_id' : d[0],
            'username': d[1],
            'encrypted_password': d[2],
            'email': d[3],
            }

    def create_post(self, username, title, content, img):
        if (response := self.get_user(username)) is None:
            return 
        self.create_img(response['user_id'], img)
        imid = self.__get_img_id(response['user_id'], img)[0]
        self.__execute('INSERT INTO posts (uid, title, content, imid) VALUES (?, ?, ?, ?)', [response['user_id'], title, content, imid])

    def create_img(self, uid, img):
        self.__execute('INSERT INTO images (uid, img) VALUES (?, ?)', [uid, img])

    def __get_img_id(self, uid, img):
        return self.__select('SELECT FROM images WHERE uid=? AND img=?', [uid, img])

    def close(self):
        self.conn.close()