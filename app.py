from sqlalchemy import select, func
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

USERNAME = "root"
PASSWORD = ""
HOST = "localhost"
DB_NAME = "internship_project"

app = Flask(__name__)
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
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(20), nullable=False)



    def __init__(self, first_name, last_name, phone_number, email, password):
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


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/reviews")
def reviews():
    return render_template("reviews.html")

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

    reservations = [{"start_time": row[0], "end_time": row[1]}
                    for row in db.session.execute(statement)]

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

        user = User(first_name, last_name, phone_number)
        db.session.add(user)
        db.session.flush()

        reservation = Reservation(start_time, end_time, user.user_id, table_id)
        db.session.add(reservation)

        db.session.commit()

    return render_template("booking.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    statement = (select(User.email, User.password)
                 .where(User.email == email)
                 .where(User.password == password)
                 )
    users = db.session.execute(statement)

    if len(list(users)) == 0:
        return render_template("login.html")

    return redirect(request.origin)

    return render_template("login.html")
