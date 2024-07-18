import werkzeug.routing.exceptions
from werkzeug.exceptions import HTTPException
from sqlalchemy import select, func
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date, time
from functools import wraps
from flask_bcrypt import Bcrypt
from random import randint, seed

USERNAME = "root"
PASSWORD = ""
HOST = "localhost"
DB_NAME = "internship_project"

app = Flask(__name__)
app.config["SECRET_KEY"] = '0EHLMjwfynimjRhI6Nl3mOaZMmmTu7JE'
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)


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
    password = db.Column(db.BINARY(60))
    user_type = db.Column(db.Enum("customer", "employee", "admin"), nullable=False)

    def __init__(self, first_name, last_name, phone_number=None, email=None, password=None, user_type="customer"):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.user_type = user_type


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
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="SET NULL"))
    table_id = db.Column(db.Integer, db.ForeignKey("tables.table_id"), nullable=False)
    phone_number = db.Column(db.String(20))

    def __init__(self, start_time, end_time, user_id, table_id, phone_number):
        self.start_time = start_time
        self.end_time = end_time
        self.user_id = user_id
        self.table_id = table_id
        self.phone_number = phone_number


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


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="SET NULL"))
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, user_id, title, body, rating, date):
        self.user_id = user_id
        self.title = title
        self.body = body
        self.rating = rating
        self.date = date


class Giftcard(db.Model):
    __tablename__ = "giftcard"
    giftcard_id = db.Column(db.Integer, primary_key=True)
    giftcard_value = db.Column(db.String(255), nullable=False)
    giftcard_firstname = db.Column(db.String(255), nullable=False)
    giftcard_lastname = db.Column(db.String(255), nullable=False)
    giftcard_email = db.Column(db.String(255), nullable=False)
    giftcard_recipient = db.Column(db.String(255), nullable=False)
    giftcard_gifter = db.Column(db.String(255), nullable=False)

    def __init__(self, giftcard_id, giftcard_value, giftcard_firstname, giftcard_lastname,
                 giftcard_email, giftcard_recipient, giftcard_gifter):
        self.giftcard_id = giftcard_id
        self.giftcard_value = giftcard_value
        self.giftcard_firstname = giftcard_firstname
        self.giftcard_lastname = giftcard_lastname
        self.giftcard_email = giftcard_email
        self.giftcard_recipient = giftcard_recipient
        self.giftcard_gifter = giftcard_gifter


with app.app_context():
    db.create_all()


@app.errorhandler(HTTPException)
def error(e):
    return render_template("error.html", error=e)


def require_login(user_type="customer"):
    def check_token_wrapper(func):
        @wraps(func)
        def check_token(*args, **kwargs):
            if not session.get("logged_in"):
                flash("You must be logged in to view this page", "error")
                return redirect(url_for("login", next=request.endpoint))

            if session.get("user_type") == "admin":
                return func(*args, **kwargs)

            if user_type:
                if user_type != "customer" and session.get("user_type") != user_type:
                    flash(f"You must be an {'employee' if session.get('user_type') == 'customer' else 'admin'} to access this page", "error")
                    return redirect(url_for("login", next=request.endpoint))

            return func(*args, **kwargs)
        return check_token
    return check_token_wrapper


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

        flash("Contact form sent", "message")

    return render_template('contact.html')


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    if request.method == "POST":
        if not session.get("logged_in"):
            return redirect(url_for("reviews"))

        title = request.form.get("heading")
        body = request.form.get("message")
        rating = int(request.form.get("rating"))

        review = Review(session.get("user_id"), title, body, rating, date.today())
        db.session.add(review)
        db.session.commit()

        flash("Review submitted", "message")

        return redirect(url_for("reviews"))

    statement = select(Review)
    reviews = [row[0] for row in db.session.execute(statement)]
    users = []

    for review in reviews:
        if review.user_id:
            statement = select(User).where(review.user_id == User.user_id)
            user = db.session.execute(statement).first()[0]
            users.append(user)
        else:
            users.append(None)

    reviews = [{
        "review": pair[0],
        "user": pair[1]
    } for pair in zip(reviews, users)]

    return render_template("reviews.html", reviews=reviews)


@app.route("/api/delete_review/<review_id>")
def delete_review(review_id):
    if not session.get("logged_in"):
        flash("You must be logged in to delete a review", "error")
        return redirect(url_for("reviews"))

    statement = select(Review).where(Review.id == review_id)
    rows = [row[0] for row in db.session.execute(statement)]

    if len(rows) == 0:
        flash("No review with that ID", "error")
        return redirect(url_for("reviews"))

    review = rows[0]
    if review.user_id != session.get("user_id"):
        flash("You may only delete your own reviews", "error")
        return redirect(url_for("reviews"))

    db.session.delete(review)
    db.session.commit()

    flash("Review deleted", "message")
    return redirect(url_for("reviews"))


@app.route("/mybookings")
@require_login()
def mybookings():
    statement = (select(Reservation)
                 .where(Reservation.user_id == session["user_id"])
                 .where(Reservation.start_time <= datetime.now())
                 )

    rows = db.session.execute(statement)
    past_bookings = [row[0] for row in rows]

    statement = (select(Reservation)
                 .where(Reservation.user_id == session["user_id"])
                 .where(Reservation.start_time > datetime.now())
                 )
    rows = db.session.execute(statement)
    upcoming_bookings = [row[0] for row in rows]

    return render_template("mybookings.html", past_bookings=past_bookings, upcoming_bookings=upcoming_bookings)


@app.route("/view_bookings")
@require_login("employee")
def view_bookings():
    time_list = [(datetime.combine(date.today(), time(hour=12)) + timedelta(minutes=30 * x)).time().strftime("%H:%M") for x in range(25)]

    statement = select(Table)
    num_tables = len(list(db.session.execute(statement)))

    table_bookings = [get_bookings(table_id, date.today()) for table_id in range(1, num_tables + 1)]
    for table in table_bookings:
        for booking in table:
            seed(booking["booking_id"])
            booking["color"] = randint(1, 255)

    return render_template("bookingview.html", time_list=time_list, table_bookings=table_bookings)


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

        flash("Email added to mailing list", "message")

    else:
        flash("Email already in mailing list", "error")

    return redirect(request.origin)


@app.route("/api/bookings/<table_id>/<date>")
def get_bookings(table_id, date):
    statement = (select(Reservation.start_time, Reservation.end_time, Reservation.reservation_id)
                 .where(Reservation.table_id == table_id)
                 .where(func.datediff(Reservation.start_time, date) == 0)
                 )

    reservations = []
    for row in db.session.execute(statement):
        start_time, end_time, booking_id = row
        start_time, end_time = start_time.time(), end_time.time()

        time_format = "%H:%M"
        start_time_str = start_time.strftime(time_format)
        end_time_str = end_time.strftime(time_format)

        reservations.append({"start_time": start_time_str, "end_time": end_time_str, "booking_id": booking_id})

    return reservations


@app.route("/api/booking/<booking_id>", methods=["GET"])
@require_login("employee")
def get_booking(booking_id):
    statement = select(Reservation).where(Reservation.reservation_id == booking_id)
    reservation = db.session.execute(statement).first()[0]

    if not reservation:
        return {}

    if reservation.user_id:
        statement = select(User).where(User.user_id == reservation.user_id)
        user = db.session.execute(statement).first()[0]

        first_name, last_name = user.first_name, user.last_name

    reservation_info = {
        "start_time": reservation.start_time.strftime("%H:%M"),
        "end_time": reservation.end_time.strftime("%H:%M"),
        "name": f"{first_name} {last_name}" if reservation.user_id else None,
        "phone_number": reservation.phone_number,
    }

    return reservation_info


@app.route("/booking", methods=["GET", "POST"])
def booking():
    phone_number = request.form.get("phone_number")
    date = request.form.get("date")
    time = request.form.get("time")
    table_id = request.form.get("table_id")

    if request.method == "POST":
        if session.get("logged_in"):
            if not all((phone_number, date, time, table_id)):
                flash("You must fill out every field", "error")
                return display_tables()

            user_id = session["user_id"]

        else:
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")

            if not all((first_name, last_name, phone_number, date, time, table_id)):
                flash("You must fill out every field", "error")
                return display_tables()

            user = User(first_name, last_name, phone_number=phone_number)
            db.session.add(user)
            db.session.flush()

            user_id = user.user_id

        # date format is "YYYY-MM-DD HH:MM"
        start_time = datetime.strptime(f"{date} {time}",
                                       "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)

        reservation = Reservation(start_time, end_time, user_id, table_id, phone_number)
        db.session.add(reservation)

        db.session.commit()

        flash("Reservation created", "message")

        if session.get("logged_in"):
            return redirect(url_for("mybookings"))

    return display_tables()


def display_tables():
    statement = select(Table)
    rows = db.session.execute(statement)
    tables = [{"id": row[0].table_id, "capacity": row[0].capacity} for row in rows]

    user = None

    if session.get("logged_in") == True:
        statement = (select(User)
                     .where(User.user_id == session["user_id"]))
        row = next(db.session.execute(statement))
        user = row[0]

    return render_template("booking.html", tables=tables, user=user)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not all((first_name, last_name, email, password)):
        flash("All fields must be filled out", "error")
        return render_template("signup.html")

    statement = (select(User)
                 .where(User.email == email))
    users = db.session.execute(statement)

    if list(users):
        flash("Email in use", "error")
        return render_template("signup.html")

    hashed = bcrypt.generate_password_hash(password, 10)
    user = User(first_name, last_name, email=email, password=hashed)

    db.session.add(user)
    db.session.commit()

    flash("Signup successful", "message")

    # code 307 preserves the http method of the request
    return redirect(url_for("login", email=email, password=password), code=307)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html', next=request.args.get("next"))

    email = request.form.get("email")
    password = request.form.get("password")

    statement = (select(User)
                 .where(User.email == email))

    rows = list(db.session.execute(statement))

    if len(rows) == 0:
        flash("Invalid username or password", "error")
        return redirect(url_for("login"))

    row = rows[0]
    user = row[0]

    if not bcrypt.check_password_hash(user.password, password):
        flash("Invalid username or password", "error")
        return redirect(url_for("login"))

    session["logged_in"] = True
    session['user_id'] = user.user_id
    session['user_type'] = user.user_type

    print(request.referrer)
    if not request.referrer == "http://127.0.0.1:5000/signup":
        flash("Login successful", "message")

    if next := request.args.get("next"):
        try:
            return redirect(url_for(next))
        except werkzeug.routing.exceptions.BuildError:
            return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    if session["logged_in"]:
        session["logged_in"] = False
        session["user_id"] = None
        session['user_type'] = None

        flash("Logout successful", "message")

    return redirect(url_for("index"))

# @app.route('/giftcard', methods=['GET', 'POST'])
# def giftcard():
#     return render_template("giftcard.html")


@app.route("/accountsettings", methods=["POST", "GET"])
@require_login()
def accountsettings():
    return render_template("accountsettings.html")


@app.route("/api/accountsettings/deleteaccount", methods=["POST", "GET"])
def delete_account():
    entered_password = request.form.get("password")

    user = db.session.execute(select(User).where(User.user_id == session.get("user_id"))).first()[0]

    if not bcrypt.check_password_hash(user.password, entered_password):
        flash("Incorrect password", "error")
        return redirect(url_for("accountsettings", _anchor="del-account"))

        if not bcrypt.check_password_hash(user.password, password):
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    return redirect(url_for('index'))


@app.route('/giftcard', methods=["POST", "GET"])
def giftcard():
    if request.method == 'POST':
        giftcard_value = request.form.get('giftcard_value')
        giftcard_firstname = request.form.get('giftcard_firstname')
        giftcard_lastname = request.form.get('giftcard_lastname')
        giftcard_email = request.form.get('giftcard_email')
        giftcard_recipient = request.form.get('giftcard_recipient')
        giftcard_gifter = request.form.get('giftcard_gifter')



        if not (giftcard_firstname and giftcard_lastname and giftcard_email and giftcard_recipient and giftcard_gifter):
            flash("All fields are required!", "error")
        else:
            giftcard = Giftcard(giftcard_value, giftcard_firstname, giftcard_lastname, giftcard_email,
                                giftcard_recipient, giftcard_gifter)
            db.session.add(giftcard)
            db.session.commit()
            flash("Gift Card Purchased", "message")

    return render_template("giftcard.html")
