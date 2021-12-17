from flask import Flask

app = Flask(__name__)

@app.route("/")
def hellow_world():
    return "<h1>Hello from flask</h1>"
