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
    m["followed"] = [] if user[4] == '' else list(map(int, user[4].strip().split(" ")))
    m["posts"] = [] if user[5] == '' else list(map(int, user[5].strip().split(" ")))
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

def string_list_to_list(s):
    return s.strip().split(" ")
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
            FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE CASCADE,
            FOREIGN KEY(imid) REFERENCES images(imid) ON DELETE CASCADE
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
            img TEXT NOT NULL,
            FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE CASCADE
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
            FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE CASCADE,
            FOREIGN KEY(pid) REFERENCES posts(uid) ON DELETE CASCADE
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

    def delete_user(self, username):
        self.__execute('DELETE FROM users WHERE username=?', [username])

    def get_user(self, username):
        data = self.__select('SELECT * FROM users WHERE username=?', [username])
        if data:
            return user_to_dict(data[0])

    def get_user_by_uid(self, uid):
        data = self.__select('SELECT * FROM users WHERE uid=?', [uid])
        if data:
            return user_to_dict(data[0])

    def create_post(self, username, title, content, imid, date):
        if (user := self.get_user(username)) is None:
            return 

        self.__execute('INSERT INTO posts (uid, title, content, imid, date) VALUES (?, ?, ?, ?, ?)', [user['user_id'], title, content, imid, date])

        pid = self.__select("SELECT pid FROM posts WHERE uid=? AND title=? AND content=? AND imid=?", [user['user_id'], title, content, imid])[0][0]
        posts = user["posts"]
        if pid not in (s := set(posts)):
            s.add(pid)
            new_posts = " ".join(list(map(str, s)))
            self.__execute("UPDATE users SET posts=? WHERE uid=?", [new_posts, user['user_id']])

    def delete_post(self, pid):
        self.__execute("DELETE FROM posts where pid=?", [pid])

    def create_img(self, uid, img):
        self.__execute('INSERT INTO images (uid, img) VALUES (?, ?)', [uid, img])

    def get_img(self, imid):
        image = self.__select('SELECT * FROM images WHERE imid=?', [imid])
        return image_to_dict(image[0])

    def get_img_id(self, uid, img):
        return self.__select('SELECT imid FROM images WHERE uid=? AND img=?', [uid, img])[0][0]
    
    def click_on_post(self, pid):
        clicks = self.__select("SELECT clicks FROM posts WHERE pid=?", [pid])[0][0]
    
        self.__execute("UPDATE posts SET clicks=? WHERE pid=?", [clicks+1, pid])

    def get_posts_ids_by_author(self, author):
        data = self.__select('SELECT posts FROM users WHERE username=?', [author])
        if data:
            return {
                'pids' : string_list_to_list(data[0][0])
            }

    def get_posts_from_author(self, author):
        post_ids = self.get_posts_ids_by_author(author)['pids']
        res = []
        for pid in post_ids:
            if pid == '':
                continue
            post = self.__select('SELECT * FROM posts where pid=?', [pid])
            if len(post) > 0:
                v = post_to_dict(post[0])
                v["author"] = self.get_user_by_uid(v["uid"])['username']
                res.append(v)
        return { 
            'posts' : res
         }
    def get_posts_by_uid(self, uid):
        posts = self.__select("SELECT * FROM posts WHERE uid=?", [uid])
        
        res = []
        for post in posts:
            v = post_to_dict(post)
            v["author"] = self.get_user_by_uid(v["uid"])['username']
            res.append(v)

        return {
            'posts' : res
        }

    def get_n_trending_posts(self, n):
        posts = self.__select('SELECT * FROM posts ORDER BY clicks DESC LIMIT ?', [n])

        res = []
        for post in posts:
            v = post_to_dict(post)
            v["author"] = self.get_user_by_uid(v["uid"])['username']
            res.append(v)

        return {
            'posts' : res
        }

    def get_n_recent_posts(self, n):
        posts = self.__select('SELECT * FROM posts ORDER BY DATE DESC LIMIT ?', [n])

        res = []
        for post in posts:
            v = post_to_dict(post)
            v["author"] = self.get_user_by_uid(v["uid"])['username']
            res.append(v)

        return {
            'posts' : res
        }

    def get_n_followed_posts(self, username, n):
        from itertools import chain

        followed = list(self.__select("SELECT followed FROM users where username=?", [username])[0])[0].split(" ")
        followed_posts = [self.get_posts_by_uid(follow)['posts'] for follow in followed if follow != '']

        res = list(chain.from_iterable(followed_posts))

        res.sort(key = lambda post: post['date'], reverse=True)
        res = res[:n]
        return {
            'posts' : res
        }

    def get_post_by_id(self, pid):
        posts = self.__select("SELECT * FROM posts WHERE pid=?", [pid])

        res = []
        for post in posts:
            v = post_to_dict(post)
            v["author"] = self.get_user_by_uid(v["uid"])['username']
            res.append(v)

        return {
            'posts' : res
        }

    def follow(self, uid, pid):
        if (user := self.get_user_by_uid(uid)) is not None:
            followed = user["followed"]
            if pid not in (s := set(followed)):
                s.add(pid)
                new_followed = " ".join(list(map(str, s)))
                self.__execute("UPDATE users SET followed=? WHERE uid=?", [new_followed, uid])

    def unfollow(self, uid, pid):
        if (user := self.get_user_by_uid(uid)) is not None:
            followed = user["followed"]
            if pid in (s := set(followed)):
                s.remove(pid)
                new_followed = " ".join(list(map(str, s)))
                self.__execute("UPDATE users SET followed=? WHERE uid=?", [new_followed, uid])

    def create_comment(self, uid, pid, content):
        self.__execute("INSERT INTO comments (uid, pid, content) VALUES (?, ?, ?)", [uid, pid, content])

    def get_comment(self, uid,pid):
        data = self.__select('SELECT * FROM comments WHERE uid=? and  pid=?', [uid,pid])
        return {
            'comments' : [comment_to_dict(comment) for comment in data]
        }
        

    def close(self):
        self.conn.close()