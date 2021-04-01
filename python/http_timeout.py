import time

from flask import Flask

app = Flask(__name__)

SLEEP = 10


@app.route("/")
def hello_timeout():
    time.sleep(SLEEP)
    return f"Hello, world! (sleep: {SLEEP}s)\n"
