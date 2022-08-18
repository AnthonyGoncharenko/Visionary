import sqlite3
import os

def post_to_dict(post):
    m = {}
    m["pid"] = post[0]
    m["uid"] = post[1]
    m["title"] = post[2]
    m["content"] = post[3]
    m["imid"] = post[4]
    m["clicks"] = post[5]
    m["date"] = post[6]
    return m

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
            uid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username VARCHAR(25) UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            email VARCHAR(120) NOT NULL,
            followed INTEGER[],
            posts INTEGER[]
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
            pid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            uid INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            imid INTEGER,
            clicks INTEGER,
            date DATE,
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
            imid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
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
            print(d)
            return {
            'user_id' : d[0],
            'username': d[1],
            'encrypted_password': d[2],
            'email': d[3],
            'followed': d[4],
            'posts' : d[5],
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

    def get_posts_ids_by_author(self, author):
        data = self.__select('SELECT posts FROM users WHERE username=?', [author])
        if data:
            return {
                'pids' : data[0]
            }

    def get_posts_from_author(self, author):
        if (post_ids := self.get_posts_ids_by_author(author)) is None:
            return
        res = []
        for pid in post_ids:
            post = self.__select('SELECT * FROM posts where pid=?', [pid])[0]
            res.append(post_to_dict(post))
        return { 
            'posts' : res
         }
    def get_n_trending_posts(self, n):
        data = self.__select('SELECT * FROM posts ORDER BY clicks LIMIT ?', [n])

        return {
            'posts' : [post_to_dict(post) for post in data]
        }

    def get_n_recent_posts(self, n):
        data = self.__select('SELECT * FROM posts ORDER BY DATE DESC LIMIT ?', [n])

        return {
            'posts' : [post_to_dict(post) for post in data]
        }

    def get_n_followed_posts(self, username, n):
        data = self.__select("SELECT * FROM posts, ( SELECT followed FROM users where username=? ) WHERE posts.pid = followed ORDER BY posts.DATE LIMIT ?", [username, n])
        
        return {
            'posts' : [post_to_dict(post) for post in data]
        }
    def close(self):
        self.conn.close()

