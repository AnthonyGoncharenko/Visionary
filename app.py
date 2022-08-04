from flask import Flask
from flask_wtf.csrf import CSRFProtect
from routes import backend, home
import os

SECRET_KEY = os.urandom(32)

csrf = CSRFProtect()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.register_blueprint(backend)
app.register_blueprint(home)

csrf.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
