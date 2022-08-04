from flask import Blueprint, render_template, url_for, redirect, request
import asyncio
from DocumentUploadForm import DocumentUploadForm
from pprint import pprint
from time import sleep
import os
import json
from threading import Thread

backend = Blueprint('server', __name__)
home = Blueprint('home', __name__)

ALLOWED_EXTENSIONS = {'tiff', 'svs', 'jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'}

def allowed_file(File):
    return '.' in File.filename and File.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@home.route('/')
@home.route('/home')
def home_page():
    form = DocumentUploadForm()
    return render_template("home.html", form=form, loadingbar=False)

@backend.route('/server', methods=['GET', 'POST'])
def server():
    form = DocumentUploadForm()
    files = list(filter(allowed_file, request.files.getlist('file')))
    if request.method == 'POST':
        if files:
            print("Creating the thread and kicking it off")
            diagnosis_thread = Thread(target=do_diagnosis, args=("",))
            diagnosis_thread.start()
    return render_template("diagnosis.html")

@backend.get('/modelStatus')
def modelStatus():
    status_file = "diagnosis_status.json"
    def get_status():
        if not os.path.isfile(status_file):
            return {"error": "no status file"}
        else:
            with open(status_file) as f:
                return json.load(f)
    return get_status()


def do_diagnosis(path_to_image: str, model_name: str = "dummy_model"):
    print("Starting diagnosis function")
    status = {}
    status_file = "diagnosis_status.json"
    def publish_status():
        print("publishing diagnosis status")
        with open(status_file, 'w' if os.path.exists(status_file) else 'x') as f:
            json.dump(status, f)
    # for 10 seconds, update status as progress
    status["status"] = "processing"
    for i in range(10):
        status["processing"] = i
        publish_status()
        sleep(1)
    status["status"] = "complete"
    publish_status()
