import asyncio
import json
import os
from pprint import pprint
from threading import Thread
from time import sleep

from flask import Blueprint, g, redirect, render_template, request, url_for, session
from passlib.hash import pbkdf2_sha256

from database import Database
from DocumentUploadForm import DocumentUploadForm
from SignInForm import SignInForm
from SignUpForm import SignUpForm

# backend = Blueprint('server', __name__)

home = Blueprint('home', __name__, static_folder='static')
signup = Blueprint('signup', __name__, static_folder='static')
signin = Blueprint('signin', __name__, static_folder='static')
logout = Blueprint('logout', __name__)

# ALLOWED_EXTENSIONS = {'tiff', 'svs', 'jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'}

# def allowed_file(File):
#     return '.' in File.filename and File.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
#                           SIGN IN PAGE
########################################################################
@signin.route('/', methods=['GET', 'POST'])
@signin.route('/signin', methods=['GET', 'POST'])
def sign_in_page():
    form = SignInForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            password = request.form['password']
            print("CHECKING THE DATABASE FOR THE USER DATA...")
            if (response := get_db().get_user(request.form['username'])) is None:
                print('USER ALREADY EXISTS IN DATABASE')
                return render_template("SignIn.html", form=SignInForm(), error_messages = ['USER DOES NOT EXIST IN DATABASE'])
            if not pbkdf2_sha256.verify(password, response['encrypted_password']):
                print('PASSWORD DOES NOT MATCH')
                return render_template("SignIn.html", form=SignInForm(), error_messages = ['PASSWORD DOES NOT MATCH'])
            print("REDIRECT TO THE HOME PAGE...")
            username = request.form['username']
            session['user'] = username
            return redirect(url_for("home.home_page"))
    return render_template("SignIn.html", form=form)
########################################################################
#                         END SIGN IN PAGE
########################################################################


########################################################################
#                           SIGN UP PAGE
########################################################################
@signup.route('/signup', methods=['GET', 'POST'])
def sign_up_page():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            encrypted_password = pbkdf2_sha256.encrypt(request.form['password'],rounds=200000, salt_size=16)

            print("CHECKING THE DATABASE FOR THE USER DATA...")

            if (response := get_db().get_user(request.form['username'])) is not None:
                print('USER ALREADY EXISTS IN DATABASE...')
                print('REDIRECTING TO SIGNUP')
                return render_template("SignUp.html", form=SignUpForm(), error_messages = ['USER ALREADY EXISTS IN DATABASE'])

            print("ADDING USER TO THE DATABASE...")

            get_db().create_user(request.form['username'], encrypted_password, request.form['email'])

            print("REDIRECTING TO THE SIGNIN...")

            return redirect(url_for("signin.sign_in_page"))
    return render_template("SignUp.html", form=form)
########################################################################
#                         END SIGN UP PAGE
########################################################################


########################################################################
#                           HOME PAGE
########################################################################
@home.route('/home', methods=['GET', 'POST'])
def home_page():
    if 'user' in session:
        return render_template("Home.html", trending_posts=trending_posts(), recent_posts=recent_posts())
    else:
        return redirect(url_for('signin.sign_in_page'))
########################################################################
#                         END HOME PAGE
########################################################################


########################################################################
#                           LOG OUT
########################################################################
@logout.route('/logout', methods=['POST'])
def logout_page():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('signin.sign_in_page'))
########################################################################
#                         END LOG OUT
########################################################################

def post_to_dict(post):
    m = {}
    m['pid'] = post['pid']
    m['author'] = post['author']
    m['title'] = post['title']
    m['data'] = post['data']

def trending_posts():
    """
    trending_posts Get top 10 posts from the database, and return them in a list
    """
    posts = get_db().get_n_trending_posts(n)
    return [ post_to_dict(post) for post in posts ]
    
def recent_posts():
    """
    recent_posts Get 10 most recent posts from the database, and return them in a list
    """
    posts = get_db().get_n_recent_posts(n)
    return [ post_to_dict(post) for post in posts ]

def followed_posts():
    if 'user' in session:
        posts = get_db().get_n_followed_posts(session['user'], 10)
        return [ post_to_dict(post) for post in posts ]
    return []

def delete_post():
    #TODO
    return

# @home.route('/')
# @home.route('/home')
# def home_page():
#     form = DocumentUploadForm()
#     return render_template("home.html", form=form, loadingbar=False)

# @backend.route('/server', methods=['GET', 'POST'])
# def server():
#     form = DocumentUploadForm()
#     files = list(filter(allowed_file, request.files.getlist('file')))
#     if request.method == 'POST':
#         if files:
#             print("Creating the thread and kicking it off")
#             diagnosis_thread = Thread(target=do_diagnosis, args=("",))
#             diagnosis_thread.start()
#     return render_template("diagnosis.html")

# @backend.get('/modelStatus')
# def modelStatus():
#     status_file = "diagnosis_status.json"
#     def get_status():
#         if not os.path.isfile(status_file):
#             return {"error": "no status file"}
#         else:
#             with open(status_file) as f:
#                 return json.load(f)
#     return get_status()


# def do_diagnosis(path_to_image: str, model_name: str = "dummy_model"):
#     print("Starting diagnosis function")
#     status = {}
#     status_file = "diagnosis_status.json"
#     def publish_status():
#         print("publishing diagnosis status")
#         with open(status_file, 'w' if os.path.exists(status_file) else 'x') as f:
#             json.dump(status, f)
#     # for 10 seconds, update status as progress
#     status["status"] = "processing"
#     for i in range(10):
#         status["processing"] = i
#         publish_status()
#         sleep(1)
#     status["status"] = "complete"
#     publish_status()
