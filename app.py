import os

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_wtf.csrf import CSRFProtect
from passlib.hash import pbkdf2_sha256
import datetime

from CommentForm import CommentForm
from database import Database
from PostForm import PostForm
from SignInForm import SignInForm
from SignUpForm import SignUpForm
from AuthorForm import AuthorForm

SECRET_KEY = os.urandom(32)
csrf = CSRFProtect()
app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = SECRET_KEY


########################################################################
#                           GET DATABASE
########################################################################
def get_db():
    DATABASE = 'visionary_database.db'
    db = getattr(g, '_database', None)
    if db is None:
        db = Database(DATABASE)
        setattr(g, '_database', db)
    return db
########################################################################
#                         END GET DATABASE
########################################################################

########################################################################
#                           HOME PAGE
########################################################################
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    if 'page' in request.args:
        n = int(request.args['page'])
    else:
        n = 1
    return render_template("Home.html", 
        session=session, 
        followed_posts=followed_posts(), 
        trending_posts=trending_posts(), 
        recent_posts=pagination(n))
########################################################################
#                         END HOME PAGE
########################################################################

########################################################################
#                           SIGN IN PAGE
########################################################################
@app.route('/', methods=['GET', 'POST'])
@app.route('/signin', methods=['GET', 'POST'])
def sign_in_page():
    form = SignInForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            password = request.form['password']
            print("CHECKING THE DATABASE FOR THE USER DATA...")
            if ((user := get_db().get_user(request.form['username'])) is None or not pbkdf2_sha256.verify(password, user['encrypted_password'])):
                print('USERNAME OR PASSWORD DOES NOT MATCH')
                return render_template("SignIn.html", form=SignInForm(), error_messages = ['USER DOES NOT EXIST IN DATABASE'])
            print("REDIRECT TO THE HOME PAGE...")
            username = request.form['username']
            session['user'] = username
            session['user_details'] = get_db().get_user(username)
            return redirect(url_for("home_page"))
    return render_template("SignIn.html", form=form, trending_posts=trending_posts())
########################################################################
#                         END SIGN IN PAGE
########################################################################


########################################################################
#                           SIGN UP PAGE
########################################################################
@app.route('/signup', methods=['GET', 'POST'])
def sign_up_page():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            encrypted_password = pbkdf2_sha256.encrypt(request.form['password'],rounds=200000, salt_size=16)

            print("CHECKING THE DATABASE FOR THE USER DATA...")

            if (response := get_db().get_user(request.form['username'])) is not None:
                print('USER ALREADY EXISTS IN DATABASE...')
                return render_template("SignUp.html", form=SignUpForm(), error_messages = ['USER ALREADY EXISTS IN DATABASE'])

            print("ADDING USER TO THE DATABASE...")

            get_db().create_user(request.form['username'], encrypted_password, request.form['email'])

            print("REDIRECTING TO SIGN IN...")

            return redirect(url_for("sign_in_page"))
    return render_template("SignUp.html", form=form, trending_posts=trending_posts())
########################################################################
#                         END SIGN UP PAGE
########################################################################

########################################################################
#                           MAKE POST PAGE
########################################################################
@app.route('/makepost', methods=['GET', 'POST'])
def make_post_page():
    if 'user' in session and request.method == 'POST':
        get_db().create_post(session['user'], request.form['post_title'], request.form['post_content'], request.form['post_image'], datetime.datetime.now())
    if 'user' in session:
        form = PostForm()
        session['user_details'] =  get_db().get_user(session['user'])
        return render_template(
            "MakePost.html", 
            session=session, 
            form=form, 
            trending_posts=trending_posts())
    else:
        flash("SIGN IN FIRST BEFORE MAKING A POST!!")
        return redirect(url_for('sign_in_page'))
########################################################################
#                         END MAKE POST PAGE
########################################################################

########################################################################
#                         VIEW POST PAGE
########################################################################
@app.route('/view_post', methods=['GET'])
def view_post_page():
    return render_template("ViewPost.html",
        session=session,
        post = get_db().get_post_by_id(request.args.get('post_id'))['posts'][0],
        canDelete=canDelete(request.args.get('post_id')),
        form=CommentForm())

########################################################################
#                         END VIEW POST PAGE
########################################################################

########################################################################
#                         DELETE POST PAGE
########################################################################

@app.route('/delete', methods=['POST'])
def delete_post():
    if 'pid' in request.args:
        pid = request.args['pid']
        delete_post(pid)
        return redirect(url_for(request.referrer))

########################################################################
#                       END DELETE POST PAGE
########################################################################

########################################################################
#                         FOLLOW AN AUTHOR
########################################################################

@app.route('/follow_author/', methods=['POST'])
def follow_author():
    if 'pid' in request.args:
        pid = request.args['pid']
        follow(pid)
        return redirect(url_for(request.referrer))

########################################################################
#                       END FOLLOW AN AUTHOR
########################################################################

########################################################################
#                         UNFOLLOW AN AUTHOR
########################################################################

@app.route('/unfollow_author', methods=['POST'])
def unfollow_author():
    if 'pid' in request.args:
        unfollow(requet.args['pid'])
    return redirect(url_for(request.referrer))

########################################################################
#                       END UNFOLLOW AN AUTHOR
########################################################################

########################################################################
#                        FIND AUTHORS PAGE
########################################################################
@app.route('/authors', methods=['GET', 'POST'])
def authors_page():
    form = AuthorForm()
    return render_template("FindAuthors.html", form=form)
########################################################################
#                        END FIND AUTHORS PAGE
########################################################################

########################################################################
#                           FOLLOWED AUTHORS PAGE
########################################################################
@app.route('/followed_authors', methods=['GET', 'POST'])
def followed_authors_page():
    if 'user' in session:
        session['user_details'] =  get_db().get_user(session['user'])
        return render_template(
            "FollowedAuthors.html", 
            session=session,
            followed_posts= get_followed_posts(),
            followed = get_followed(),
            form = AuthorForm())
########################################################################
#                         END FOLLOWED AUTHORS PAGE
########################################################################

########################################################################
#                           MAKE COMMENT PAGE
########################################################################
@app.route('/make_comment', methods=['GET', 'POST'])
def make_comment_page():
    if 'user' in session and request.method == 'POST':
        if form.validate_on_submit():
            if 'pid' in request.args:
                pid = request.args['pid']
                get_db().create_comment(session['user']['uid'], request.args.get('post_id'), request.form['comment_content'])

########################################################################
#                         END MAKE COMMENT PAGE
########################################################################


########################################################################
#                           PROFILE PAGE
########################################################################

@app.route('/profile', methods=['GET'])
def profile_page():
    if request.method == 'GET':
        db = get_db()

        if 'uid' in request.args:
            user = db.get_user_by_uid(request.args['uid'])
            posts=db.get_posts_from_author(user['username']['posts'])
            return render_template("Profile.html", user=user, session=session, posts=posts)

        elif 'user' in session:
            session['user_details'] = db.get_user(session['user'])
            posts = db.get_posts_from_author(session['user'])['posts']
            user = db.get_user_by_uid(session['user_details']['user_id'])
            return render_template(
                "Profile.html", 
                user=user, 
                session=session, 
                posts=posts, 
                followed=get_followed(),
                form=AuthorForm())
        else:
            return redirect(url_for('sign_in_page'))

########################################################################
#                         END PROFILE PAGE
########################################################################




########################################################################
#                           LOG OUT
########################################################################
@app.route('/logout', methods=['GET'])
def logout_page():
    if 'user' in session:
        session.pop('user_details', None)
        session.pop('user', None)
    return redirect(url_for('sign_in_page'))
########################################################################
#                         END LOG OUT
########################################################################


########################################################################
#                      DATABASE QUERYING
########################################################################
@app.route('/api/db/', methods=['GET', 'POST', 'DELETE'])
def database_querying():
    #TODO
    
    if request.method == 'GET':
        ...
    elif request.method == 'POST':
        ...
    elif request.method == 'DELETE':
        ...


    if 'user' in session:
        session['user_details'] =  get_db().get_user(session['user'])

        ...
########################################################################
#                    END DATABASE QUERYING
########################################################################

########################################################################
#             CLOSE DB CONNECTION ON APP DISCONNECT
########################################################################
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
########################################################################
#             END CLOSE DB CONNECTION ON APP DISCONNECT
########################################################################

def post_to_dict(post):
    m = {}
    m['pid'] = post['pid']
    m['uid'] = post['uid']
    m['title'] = post['title']
    m['content'] = post['content']
    return m

def trending_posts():
    """
    trending_posts Get top 10 posts from the database, and return them in a list

    :return: List of Post dictionaries
    :rtype: List[dict]
    """ 
    posts = get_db().get_n_trending_posts(10)['posts']
    return [ post_to_dict(post) for post in posts ]

def recent_posts(n):
    """
    recent_posts Get n most recent posts from the database, and return them in a list

    :return: List of Post dictionaries
    :rtype: List[dict]
    """    
    posts = get_db().get_n_recent_posts(n)['posts']
    return [ post_to_dict(post) for post in posts ]

def pagination(n):
    return recent_posts(n * 10)[(n-1)*10:n*10]

def followed_posts():
    """
    followed_posts Get 10 newest posts from followed authors

    :return: List of Post dictionaries
    :rtype: List[dict]
    """    
    if 'user' in session:
        posts = get_db().get_n_followed_posts(session['user'], 10)['posts']
        return [ post_to_dict(post) for post in posts ]
    return []

def canDelete(pid):
    db = get_db()
    if 'user' in session:
        print(session)
        if post := db.get_post_by_id(pid)['posts'][0]:
            print(post)
            if (user := db.get_user_by_uid(post["uid"])) is not None:
                if user['username'] == session['user']:
                    return True
    return False

def delete_post(pid):
    if canDelete(pid):
        db.delete_post(pid)

def follow(pid):
    if 'user' in session:
        db = get_db()
        uid = db.get_user(session['user'])["user_id"]
        db.follow(uid, pid)

def unfollow(pid):
    if 'user' in session:
        db = get_db()
        uid = db.get_user(session['user'])["user_id"]
        db.unfollow(uid, pid)
def get_followed():
    if 'user' in session:
        db = get_db()
        session['user_details'] = db.get_user(session['user'])
        followed = session['user_details']['followed']
        followed = [db.get_user_by_uid(int(follow)) for follow in followed if follower != ""]
        return followed
    else:
        return []

def get_followed_posts():
    return []

csrf.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
