from flask import Flask
from flask_wtf.csrf import CSRFProtect
from routes import backend, home, signup, signin
import os

SECRET_KEY = os.urandom(32)

csrf = CSRFProtect()

app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = SECRET_KEY
app.register_blueprint(backend)
app.register_blueprint(home)
app.register_blueprint(signup)
app.register_blueprint(signin)

csrf.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
