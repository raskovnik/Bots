import os
import threading

import heroku3
from flask import Flask

app = Flask(__name__)
heroku_conn = heroku3.from_key(os.getenv("HEROKU_API_TOKEN"))
heroku_app = heroku_conn.apps()[os.getenv("HEROKU_APP_NAME")]


@app.route('/')
def hello_world():
    thread = threading.Thread(
        target=heroku_app.run_command, args=("worker",))
    thread.daemon = True
    thread.start()
    return "OK"