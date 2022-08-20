import os

from flask import Flask, g
from flask_wtf.csrf import CSRFProtect

from database import Database
from routes import home, logout, signin, signup

SECRET_KEY = os.urandom(32)
csrf = CSRFProtect()
app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = SECRET_KEY

app.register_blueprint(home)
app.register_blueprint(signup)
app.register_blueprint(signin)
app.register_blueprint(logout)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

csrf.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
