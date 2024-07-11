from sqlalchemy import select, func
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps

USERNAME = "root"
PASSWORD = ""
HOST = "localhost"
DB_NAME = "internship_project"

app = Flask(__name__)
app.config["SECRET_KEY"] = '0EHLMjwfynimjRhI6Nl3mOaZMmmTu7JE'
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Table(db.Model):
    __tablename__ = "tables"
    table_id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(64))
    password = db.Column(db.String(20))

    def __init__(self, first_name, last_name, phone_number=None, email=None, password=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email
        self.password = password


class Email(db.Model):
    __tablename__ = "mailing_list"
    email_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
   
    def __init__(self, email):
        self.email = email


class Reservation(db.Model):
    __tablename__ = "reservations"
    reservation_id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey("tables.table_id"), nullable=False)

    def __init__(self, start_time, end_time, user_id, table_id):
        self.start_time = start_time
        self.end_time = end_time
        self.user_id = user_id
        self.table_id = table_id


class Complaint(db.Model):
    __tablename__ = 'contact_table'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    complaint = db.Column(db.String(100))

    def __init__(self, fname, lname, email, complaint):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.complaint = complaint


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        complaint = request.form['reason']

        contact = Complaint(fname, lname, email, complaint)
        db.session.add(contact)
        db.session.commit()

    return render_template('contact.html')


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/reviews")
def reviews():
    return render_template("reviews.html")

@app.route("/mybookings")
def mybookings():
    return render_template("mybookings.html")


@app.route("/mailinglist", methods=["POST"])
def add_email():
    email = request.form.get("email")
    
    statement = (select(Email)
                 .where(Email.email == email)
                 )
    
    emails = db.session.execute(statement)

    if len(list(emails)) == 0:
        email = Email(email)
        db.session.add(email)
        db.session.commit()
    
    return redirect(request.origin)


@app.route("/api/bookings/<table_id>")
def get_bookings(table_id):
    date = request.args.get("date")

    statement = (select(Reservation.start_time, Reservation.end_time)
                 .where(Reservation.table_id == table_id)
                 .where(func.datediff(Reservation.start_time, date) == 0)
                 )

    reservations = []
    for row in db.session.execute(statement):
        start_time, end_time = row
        start_time, end_time = start_time.time(), end_time.time()

        time_format = "%H:%M"
        start_time_str = start_time.strftime(time_format)
        end_time_str = end_time.strftime(time_format)

        reservations.append({"start_time": start_time_str, "end_time": end_time_str})

    return reservations


@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone_number = request.form.get("phone_number")
        date = request.form.get("date")
        time = request.form.get("time")
        table_id = request.form.get("table_id")

        if not all((first_name, last_name, phone_number, date, time, table_id)):
            return render_template("booking.html")

        # date format is "YYYY-MM-DD HH:MM"
        start_time = datetime.strptime(f"{date} {time}",
                                       "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=2)

        user = User(first_name, last_name, phone_number=phone_number)
        db.session.add(user)
        db.session.flush()

        reservation = Reservation(start_time, end_time, user.user_id, table_id)
        db.session.add(reservation)

        db.session.commit()

    statement = select(Table)
    rows = db.session.execute(statement)
    tables = [{"id": row[0].table_id, "capacity": row[0].capacity} for row in rows]

    return render_template("booking.html", tables=tables)


def require_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        if 'user_id' not in session:
# TODO flash access denied
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return check_token


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not all((first_name, last_name, email, password)):
        flash("All fields must be filled out")
        return render_template("signup.html")

    statement = (select(User)
                 .where(User.email == email))
    users = db.session.execute(statement)

    if list(users):
        flash("Email in use")
        return render_template("signup.html")

# TODO: hash password
    user = User(first_name, last_name, email=email, password=password)

    db.session.add(user)
    db.session.commit()

    # code 307 preserves the http method of the request
    return redirect(url_for("login", email=email, password=password), code=307)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')

    email = request.form.get("email")
    password = request.form.get("password")

    statement = (select(User.user_id)
                 .where(User.email == email)
                 .where(User.password == password)
                 )
    user_id = db.session.execute(statement)

    if not user_id:
        flash("Invalid username or password")
        return render_template("login.html")

    session["logged_in"] = True
    session['user_id'] = list(user_id)[0][0]

    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    if session["logged_in"]:
        session["logged_in"] = False
        session["user_id"] = None

    return redirect(url_for("index"))