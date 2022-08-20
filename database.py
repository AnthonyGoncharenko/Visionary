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

def user_to_dict(user):
    m = {}
    m["user_id"] = user[0]
    m["username"] = user[1]
    m["encrypted_password"] = user[2]
    m["email"] = user[3]
    m["followed"] = user[4]
    m["posts"] = user[5]
    return m

def image_to_dict(image):
    m = {}
    m["imid"] = image[0]
    m["uid"] = image[1]
    m["img"] = image[2]
    return m

def comment_to_dict(comment):
    m = {}
    m["user_id"] = comment[0]
    m["pid"] = comment[1]
    m["content"] = comment[2]
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
            followed TEXT DEFAULT "",
            posts TEXT DEFAULT ""
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
            clicks INTEGER DEFAULT 0,
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

        ###############################################
        #              CREATE COMMENTS TABLE
        ###############################################        
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS comments
        (
            uid INTEGER NOT NULL,
            pid INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(uid) REFERENCES users(uid),
            FOREIGN KEY(pid) REFERENCES posts(uid)
        );''')
        self.conn.commit()
        ###############################################
        #            END CREATE COMMENTS TABLE
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
            return user_to_dict(data[0])
    def get_user_by_uid(self, uid):
        data = self.__select('SELECT * FROM users WHERE uid=?', [uid])
        if data:
            return user_to_dict(data[0])

    def create_post(self, username, title, content, img):
        if (user := self.get_user(username)) is None:
            return 
        self.create_img(user['user_id'], img)
        imid = self.__get_img_id(user['user_id'], img)[0][0]
        self.__execute('INSERT INTO posts (uid, title, content, imid) VALUES (?, ?, ?, ?)', [user['user_id'], title, content, imid])

        pid = self.__select("SELECT pid FROM posts WHERE uid=? AND title=? AND content=? AND imid=?", [user['user_id'], title, content, imid])
        posts = user["posts"].split(" ")

        if str(pid) not in posts:
            posts.append(str(pid))
            new_posts = " ".join(posts)
            self.__execute("UPDATE users SET posts=? WHERE uid=?", [new_posts, user['user_id']])

    def delete_post(self, pid):
        self.__execute("DELETE FROM posts where pid=?", [pid])
    def create_img(self, uid, img):
        self.__execute('INSERT INTO images (uid, img) VALUES (?, ?)', [uid, img])

    def get_img(self, imid):
        image = self.__select('SELECT * FROM images WHERE imid=?', [imid])[0]
        return image_to_dict(image)

    def __get_img_id(self, uid, img):
        return self.__select('SELECT imid FROM images WHERE uid=? AND img=?', [uid, img])

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
    def get_post_by_id(self, pid):
        data = self.__select("SELECT * FROM posts WHERE pid=?", [pid])
        return {
            'posts' : [post_to_dict(post) for post in data]
        }

    def follow(self, uid, pid):
        if (user := self.get_user_by_uid(uid)) is not None:
            followed = user["followed"].split(" ")
            if str(pid) not in followed:
                followed.append(str(pid))
                new_followed = " ".join(followed)
                self.__execute("UPDATE users SET followed=? WHERE uid=?", [new_followed, uid])

    def unfollow(self, uid, pid):
        if (user := self.get_user_by_uid(uid)) is not None:
            followed = user["followed"].split(" ")
            if str(pid) in followed:
                followed.pop(followed.index(str(pid)))
                new_followed = " ".join(followed)
                self.__execute("UPDATE users SET followed=? WHERE uid=?", [new_followed, uid])

    def create_comment(self, uid, pid, content):
        self.__execute("INSERT INTO comments (uid, pid, content) VALUES (?, ?, ?)", [uid, pid, content])

    def close(self):
        self.conn.close()