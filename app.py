import os
import datetime
import urllib.request
from webbrowser import get

from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from passlib.hash import pbkdf2_sha256
import datetime

from AuthorForm import AuthorForm
from CommentForm import CommentForm
from database import Database
from PostForm import PostForm
from SignInForm import SignInForm
from SignUpForm import SignUpForm

SECRET_KEY = os.urandom(32)
csrf = CSRFProtect()
app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = SECRET_KEY

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = os.path.join("static", UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  #change to increase max file size currently 64 mb file

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
                flash("We don't have a username with that password.")
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
                flash("Username already taken.")
                return render_template("SignUp.html", form=SignUpForm(), trending_posts=trending_posts())

            print("ADDING USER TO THE DATABASE...")

            get_db().create_user(request.form['username'], encrypted_password, request.form['email'])

            print("REDIRECTING TO SIGN IN...")

            return redirect(url_for("sign_in_page"))
    return render_template("SignUp.html", form=form, trending_posts=trending_posts())
########################################################################
#                         END SIGN UP PAGE
########################################################################

########################################################################
#                          Image Upload Helper functions
########################################################################

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_image(request, user):
    file = request.files['post_image']  
    if file and allowed_file(file.filename):
        filename = file.filename
        uid = session['user_details']['user_id']
        get_db().create_img(uid, filename)
        imid = get_db().get_img_id(uid, filename)
        dirname = os.path.join(app.config['UPLOAD_FOLDER'], user)
        os.makedirs(dirname, exist_ok=True)
        new_filename = f'{imid}{os.path.splitext(filename)[1]}'
        save_dir = os.path.join( dirname, new_filename)
        file.save(save_dir)
        get_db().update_img(imid, save_dir)
        return str(imid)
    else:
        return "-1"

########################################################################
#                          End Image Upload Helper functions
########################################################################


########################################################################
#                           MAKE POST PAGE
########################################################################
@app.route('/makepost', methods=['GET', 'POST'])
def make_post_page():
    if 'user' in session:
        user = session['user']
        if request.method == 'POST':
            if 'post_image' in request.files:
                imid = handle_image(request, user)
                get_db().create_post(user, request.form['post_title'], request.form['post_content'], imid, datetime.datetime.now() )
                return redirect(url_for('home_page'))
            else:
                return redirect(url_for('make_post_page'))
        elif request.method == 'GET':
            form = PostForm()
            session['user_details'] =  get_db().get_user(user)
            return render_template("MakePost.html", session=session, form=form, trending_posts=trending_posts())
    else:
        flash("Log-In before you make a post.")
        return redirect(url_for('sign_in_page'))
########################################################################
#                         END MAKE POST PAGE
########################################################################

########################################################################
#                         VIEW POST PAGE
########################################################################
@app.route('/view_post', methods=['GET'])
def view_post_page():
    pid = request.args.get('post_id')
    return render_template("ViewPost.html",
        session=session,
        post = get_db().get_post_by_id(pid)['posts'][0],
        canDelete=canDelete(pid),
        form=CommentForm(),
        comments=get_db().get_comments(pid))

########################################################################
#                         END VIEW POST PAGE
########################################################################

########################################################################
#                         DELETE POST PAGE
########################################################################

@app.route('/delete', methods=['GET'])
def delete_post():
    if 'pid' in request.args:
        pid = request.args['pid']
        delete_post(pid)
        return redirect(url_for('home_page'))
    return redirect(request.referrer)

########################################################################
#                       END DELETE POST PAGE
########################################################################

########################################################################
#                         DELETE USER PAGE
########################################################################

@app.route('/delete_user', methods=['GET'])
def delete_user():
    if 'uid' in request.args:
        uid = request.args['uid']
        if (int(uid) == int(session['user_details']['user_id'])):
            get_db().delete_user(uid)
            session.pop('user', None)
            session.pop('user_details', None)
            return redirect(url_for('home_page'))
    return redirect(request.referrer)

########################################################################
#                       END DELETE POST PAGE
########################################################################

########################################################################
#                         FOLLOW AN AUTHOR
########################################################################

@app.route('/follow_author', methods=['GET'])
def follow_author():
    print("hello")
    if 'uid' in request.args:
        uid = request.args['uid']
        follow(uid)
        return redirect(request.referrer)

########################################################################
#                       END FOLLOW AN AUTHOR
########################################################################

########################################################################
#                         UNFOLLOW AN AUTHOR
########################################################################

@app.route('/unfollow_author', methods=['GET'])
def unfollow_author():
    if 'uid' in request.args:
        unfollow(request.args['uid'])
    return redirect(request.referrer)

########################################################################
#                       END UNFOLLOW AN AUTHOR
########################################################################

########################################################################
#                        FIND AUTHORS PAGE
########################################################################
@app.route('/authors', methods=['GET', 'POST'])
def authors_page():
    form = AuthorForm()
    if 'user' in session:
        db = get_db();
        session['user_details'] = db.get_user(session['user'])
        user = db.get_user_by_uid(session['user_details']['user_id'])
        posts=db.get_n_followed_posts(user['username'],10)['posts']
        print(posts)
        return render_template("FindAuthors.html",
            user=user, 
            session=session, 
            posts=posts, 
            followed=get_followed(),
            form=AuthorForm())
    else:
        flash("You need an account to follow authors.")
        return redirect(url_for('sign_in_page'))
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
#                           FIND AUTHOR
########################################################################
@app.route('/find_authors', methods=['POST'])
def find_authors():
    if 'user' in session:
        if 'author_name' in request.form:
            if (user := get_db().get_user(request.form['author_name'])) is not None:
                uid = user["user_id"]
                return redirect(url_for("profile_page", uid=uid))
    else:
        return redirect(url_for('home_page'))
########################################################################
#                         END FIND AUTHOR
########################################################################


########################################################################
#                           MAKE COMMENT PAGE
########################################################################
@app.route('/make_comment', methods=['POST'])
def make_comment_page():
    if 'user' in session:
        if request.method == 'POST':
            if 'comment_content' in request.form:
                if 'post_id' in request.args:
                    get_db().create_comment(session['user_details']['user_id'], request.args['post_id'], request.form['comment_content'])
                    redirect(request.referrer)
    return redirect(request.referrer)
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
        if 'uid' in request.args or 'user' in session:
            if 'uid' in request.args:
                user = db.get_user_by_uid(request.args['uid'])
                if (user == None):
                    return redirect(url_for('home_page'))
                posts=db.get_posts_from_author(user['username'])['posts']
            elif 'user' in session:
                session['user_details'] = db.get_user(session['user'])
                user = db.get_user_by_uid(session['user_details']['user_id'])
                posts=db.get_posts_from_author(user['username'])['posts']
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
#                           TESTING
########################################################################
@app.route('/<int:n1>', methods=['GET'])
def testing(n1):
    import datetime
    import os 
    
    database_name = "visionary_database.db"
    if os.path.exists(database_name):
        os.remove(database_name)
    
    with open(database_name, 'wb'):
        ...
    
    get_db().create_user('amg568', 'definitely encrypted', 'amg568@gmail.com')
    get_db().create_user('jeff69420', 'definitely encrypted', 'jeff69@gmail.com')
    get_db().create_user('elizbeth', 'definitely encrypted', 'elizabeth+netflix@gmail.com')
    
    session['user'] = 'amg568'
    session['user_details']= get_db().get_user(session['user'])

    
    get_db().create_post('jeff69420', 'jeff\'s first post', 'my favorite color is pink', 'test.jog', datetime.datetime.now())
    get_db().create_post('jeff69420', 'jeff\'s second post', 'my second favorite color is orange', 'test2.jog', datetime.datetime.now())
    get_db().create_post('elizbeth', 'I am the queen of england', 'I love my dogs <3', 'test2.jog', datetime.datetime.now())

    #get_db().create_post(session['user'], request.form['post_title'], request.form['post_content'], file.filename, datetime.datetime.now() )
    posts = get_db().get_posts_ids_by_author('jeff69420')
    print("These are posts", posts)
    if(len(posts['pids'])!=0):
        firstpost = posts['pids'][0]
        get_db().create_comment(get_db().get_user(session['user'])['user_id' ], firstpost, "Comment1")
        get_db().create_comment(get_db().get_user(session['user'])['user_id' ], firstpost, "comment2")
        ret_comment = get_db().get_comment(get_db().get_user(session['user'])['user_id' ], firstpost)
        
        return jsonify(ret_comment)
    else:
        print("no posts for author")
    # follow(session['user_details']['user_id'] + 1)
    # follow(session['user_details']['user_id'] + 2)
    # ant = {'ant' : get_db().get_user('amg568')}
    get_db().click_on_post(1)
    get_db().click_on_post(1)
    get_db().click_on_post(1)
    get_db().click_on_post(1)
    get_db().click_on_post(2)
    get_db().click_on_post(2)
    get_db().click_on_post(2)
    get_db().click_on_post(3)
    get_db().click_on_post(3)
    get_db().click_on_post(3)
    get_db().click_on_post(3)
    get_db().click_on_post(3)
    get_db().delete_post(n1)
    data = {'data' :  get_db().get_posts_from_author(get_db().get_user_by_uid(n1)["username"])}
    unfollow(session['user_details']['user_id'] + 1)
    unfollow(session['user_details']['user_id'] + 2)
    ant2 = {'ant' : get_db().get_user('amg568')}
    get_db().delete_user('jeff69420')
    get_db().delete_user('amg568')
    get_db().delete_user('elizbeth')
    session.pop('user', None)
    session.pop('user_details', None)
    return jsonify(data, ant, ant2)
########################################################################
#                         END TESTING
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

def trending_posts():
    """
    trending_posts Get top 10 posts from the database, and return them in a list

    :return: List of Post dictionaries
    :rtype: List[dict]
    """ 
    posts = get_db().get_n_trending_posts(10)['posts']
    return posts

def recent_posts(n):
    """
    recent_posts Get n most recent posts from the database, and return them in a list

    :return: List of Post dictionaries
    :rtype: List[dict]
    """    
    posts = get_db().get_n_recent_posts(n)['posts']
    return posts

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
        return posts
    return []

def canDelete(pid):
    db = get_db()
    if 'user' in session:
        if post := db.get_post_by_id(pid)['posts'][0]:
            if (user := db.get_user_by_uid(post["uid"])) is not None:
                if user['username'] == session['user']:
                    return True
    return False

def delete_post(pid):
    if canDelete(pid):
        get_db().delete_post(pid)

def follow(pid):
    if 'user' in session:
        db = get_db()
        uid = db.get_user(session['user'])["user_id"]
        print(pid, uid)
        db.follow(uid, pid)

def unfollow(pid):
    if 'user' in session:
        db = get_db()
        uid = db.get_user(session['user'])["user_id"]
        print(pid, uid)
        db.unfollow(uid, pid)
def get_followed():
    if 'user' in session:
        db = get_db()
        session['user_details'] = db.get_user(session['user'])
        followed = session['user_details']['followed']
        followed = [db.get_user_by_uid(int(follow)) for follow in followed if follow != ""]
        return followed
    else:
        return []

def get_followed_posts():
    return []

csrf.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
