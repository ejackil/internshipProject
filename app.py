from flask import render_template, url_for, Flask

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("layout.html")