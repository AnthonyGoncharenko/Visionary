import os

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_wtf.csrf import CSRFProtect
from passlib.hash import pbkdf2_sha256

from database import Database
from SignInForm import SignInForm
from SignUpForm import SignUpForm

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
    return render_template("Home.html", 
        session=session, 
        followed_posts=followed_posts() if 'user' in session else [], 
        trending_posts=trending_posts(), 
        recent_posts=recent_posts())
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
            return redirect(url_for("home_page"))
    return render_template("SignIn.html", form=form)
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
    return render_template("SignUp.html", form=form)
########################################################################
#                         END SIGN UP PAGE
########################################################################



########################################################################
#                           MAKE POST PAGE
########################################################################
@app.route('/makepost', methods=['GET', 'POST'])
def make_post_page():
    if 'user' in session:
        return render_template("MakePost.html", session=session)
    else:
        flash("SIGN IN FIRST BEFORE MAKING A POST!!")
        return redirect(url_for('sign_in_page'))
########################################################################
#                         MAKE POST PAGE
########################################################################

########################################################################
#                           FIND AUTHORS PAGE
########################################################################
@app.route('/authors', methods=['GET', 'POST'])
def authors_page():
    return render_template("FindAuthors.html")
########################################################################
#                         FIND AUTHORS PAGE
########################################################################


########################################################################
#                           LOG OUT
########################################################################
@app.route('/logout', methods=['POST'])
def logout_page():
    if 'user' in session:
        session.pop('user')
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
    m['author'] = post['author']
    m['title'] = post['title']
    m['data'] = post['data']
    return m

def trending_posts():
    """
    trending_posts Get top 10 posts from the database, and return them in a list

    :return: List of Post dictionaries
    :rtype: List[dict]
    """ 
    posts = get_db().get_n_trending_posts(10)['posts']
    return [ post_to_dict(post) for post in posts ]
    
def recent_posts():
    """
    recent_posts Get 10 most recent posts from the database, and return them in a list

    :return: List of Post dictionaries
    :rtype: List[dict]
    """    
    posts = get_db().get_n_recent_posts(10)['posts']
    return [ post_to_dict(post) for post in posts ]

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

def delete_post(pid):
    if 'user' in session:
        if post := get_db().get_post_by_id(pid)['posts']:
            if (user := get_db().get_user_by_id(post["uid"])) is not None:
                if user['username'] == session['user']:
                    get_db().delete_post(pid)
def follow(pid):
    if 'user' in session:
        db = get_db()
        uid = db.get_user(session['user'])["user_id"]
        db.follow(uid, pid)

csrf.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
