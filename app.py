import os

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_wtf.csrf import CSRFProtect
from passlib.hash import pbkdf2_sha256

from CommentForm import CommentForm
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
        followed_posts=followed_posts(), 
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
            session['user_details'] = get_db().get_user(username)
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
        session['user_details'] =  get_db().get_user(session['user'])
        return render_template("MakePost.html", session=session)
    else:
        flash("SIGN IN FIRST BEFORE MAKING A POST!!")
        return redirect(url_for('sign_in_page'))
########################################################################
#                         END MAKE POST PAGE
########################################################################

########################################################################
#                         VIEW POST PAGE
########################################################################
@app.route('/view_post/<int:pid>', methods=['GET'])
def view_post_page(pid):
    if request.method == 'GET':
        if 'user' in session:
            session['user_details'] =  get_db().get_user(session['user'])
        return render_template("ViewPost.html", session=session, canDelete=canDelete(pid))
    else:
        return redirect(url_for('home_page'))
########################################################################
#                         END VIEW POST PAGE
########################################################################

########################################################################
#                         DELETE POST PAGE
########################################################################

@app.route('/delete/<int:pid>', methods=['POST'])
def delete(pid):
    delete_post(pid)
    return redirect(url_for(request.referrer))

########################################################################
#                       END DELETE POST PAGE
########################################################################

########################################################################
#                         FOLLOW AN AUTHOR
########################################################################

@app.route('/follow_author/<int:pid>', methods=['POST'])
def follow_author(pid):
    follow(pid)
    return redirect(url_for(request.referrer))

########################################################################
#                       END FOLLOW AN AUTHOR
########################################################################

########################################################################
#                         UNFOLLOW AN AUTHOR
########################################################################

@app.route('/unfollow_author/<int:pid>', methods=['POST'])
def unfollow_author(pid):
    unfollow(pid)
    return redirect(url_for(request.referrer))

########################################################################
#                       END UNFOLLOW AN AUTHOR
########################################################################

########################################################################
#                        FIND AUTHORS PAGE
########################################################################
@app.route('/authors', methods=['GET', 'POST'])
def authors_page():
    return render_template("FindAuthors.html")
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
        return render_template("FollowedAuthors.html", session=session)
########################################################################
#                         END FOLLOWED AUTHORS PAGE
########################################################################

########################################################################
#                           MAKE COMMENT PAGE
########################################################################
@app.route('/make_comment/<int:pid>', methods=['GET', 'POST'])
def make_comment_page(pid):
    if 'user' in session:
        session['user_details'] =  get_db().get_user(session['user'])
        form = CommentForm()
        if request.method == 'GET':
            return render_template("MakeComment.html", form=form, session=session)
        elif request.method == 'POST':
            if form.validate_on_submit():
                get_db().create_comment(session['user_details']['user_id'], pid, request.form.get('title'), request.form.get('content'), request.form.get('img'))

########################################################################
#                         END MAKE COMMENT PAGE
########################################################################


########################################################################
#                           LOG OUT
########################################################################
@app.route('/logout', methods=['POST'])
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

def canDelete(pid):
    db = get_db()
    if 'user' in session:
        if post := db.get_post_by_id(pid)['posts']:
            if (user := db.get_user_by_id(post["uid"])) is not None:
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
csrf.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
