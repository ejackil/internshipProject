import werkzeug.routing.exceptions
import smtplib
from werkzeug.exceptions import HTTPException
from sqlalchemy import select, func, update
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date, time
from functools import wraps
from flask_bcrypt import Bcrypt
from random import randint, seed
from email.message import EmailMessage
from itsdangerous import TimestampSigner, SignatureExpired

USERNAME = "root"
PASSWORD = ""
HOST = "localhost"
DB_NAME = "internship_project"

app = Flask(__name__)
app.config["SECRET_KEY"] = '0EHLMjwfynimjRhI6Nl3mOaZMmmTu7JE'
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.jinja_env.filters['zip'] = zip
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
timestamp_signer = TimestampSigner(app.config["SECRET_KEY"])


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
    reset_password_token = db.Column(db.BINARY)

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
    resolved = db.Column(db.Boolean)

    def __init__(self, fname, lname, email, complaint, resolved=False):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.complaint = complaint
        self.resolved = resolved


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(100))
    order_details = db.Column(db.String(100))
    specifications = db.Column(db.String(100))

    def __init__(self, name, phone_number, order_details, specifications):
        self.name = name
        self.phone_number = phone_number
        self.order_details = order_details
        self.specifications = specifications


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

    def __init__(self, giftcard_value, giftcard_firstname, giftcard_lastname,
                 giftcard_email, giftcard_recipient, giftcard_gifter):
            self.giftcard_value = giftcard_value
            self.giftcard_firstname = giftcard_firstname
            self.giftcard_lastname = giftcard_lastname
            self.giftcard_email = giftcard_email
            self.giftcard_recipient = giftcard_recipient
            self.giftcard_gifter = giftcard_gifter

class Cart(db.Model):
    __tablename__ = "cart"
    cart_id = db.Column(db.Integer, primary_key=True)
    cart_country = db.Column(db.String(255), nullable=False)
    cart_cardfullname = db.Column(db.String(255), nullable=False)
    cart_cardcsc = db.Column(db.String(255), nullable=False)
    cart_expirydate = db.Column(db.String(255), nullable=False)

    def __init__(self, cart_country, cart_cardfullname, cart_cardnumber, cart_cardcsc, cart_expirydate):
        self.cart_country = cart_country
        self.cart_cardfullname = cart_cardfullname
        self.cart_cardnumber = cart_cardnumber
        self.cart_cardcsc = cart_cardcsc
        self.cart_expirydate = cart_expirydate




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

@app.route("/about/andwhatelse")
def andwhatelse():
    return render_template("andwhatelse.html")


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
        title = request.form.get("heading")
        body = request.form.get("message")
        rating = int(request.form.get("rating"))

        if not session.get("logged_in"):
            user = User(request.form.get("first-name"), request.form.get("last-name"))
            db.session.add(user)
            db.session.flush()

            user_id = user.user_id
        else:
            user_id = session.get("user_id")

        review = Review(user_id, title, body, rating, date.today())
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

    booking_date = None
    if request.args.get("date"):
        booking_date = datetime.strptime(request.args.get("date"),
                                 "%Y-%m-%d").date()

    table_bookings = [get_bookings(table_id, booking_date or date.today()) for table_id in range(1, num_tables + 1)]
    for table in table_bookings:
        for booking in table:
            seed(booking["booking_id"])
            booking["color"] = randint(1, 255)

    return render_template("bookingview.html", time_list=time_list, table_bookings=table_bookings, date=booking_date or date.today())


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
        "reservation_id": reservation.reservation_id,
    }

    return reservation_info


@app.route("/api/cancel_booking/<booking_id>", methods=["POST"])
@require_login()
def cancel_booking(booking_id):
    redirect_to = "mybookings" if "mybookings" in request.referrer else "view_bookings"

    row = db.session.execute(select(Reservation).where(Reservation.reservation_id == booking_id)).first()

    if not row:
        flash("Reservation could not be deleted", "error")
        return redirect(url_for(redirect_to))

    reservation = row[0]

    if (reservation.user_id == session.get("user_id")
            or session.get("user_type") == "employee"
            or session.get("user_type") == "admin"):
        db.session.delete(reservation)
        db.session.commit()

        flash("Reservation cancelled successfully", "message")
    else:
        flash("Reservation could not be deleted", "error")

    return redirect(url_for(redirect_to))

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

    hashed = bcrypt.generate_password_hash(password)
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


@app.route("/accountsettings", methods=["POST", "GET"])
@require_login()
def accountsettings():
    user = db.session.execute(select(User).where(User.user_id == session.get("user_id"))).first()[0]
    email = user.email
    phonenumber = user.phone_number

    if phonenumber is None:
        phonenumber = ""

    return render_template("accountsettings.html", email=email, phonenumber=phonenumber)

@app.route("/api/accountsettings/changeaccountdetails", methods=["POST", "GET"])
@require_login()
def change_account_details():
    entered_email = request.form.get("email-change")
    entered_password = request.form.get("password-change")
    entered_phonenumber = request.form.get("phonenumber-change")
    old_password = request.form.get("old-password")

    user = db.session.execute(select(User).where(User.user_id == session.get("user_id"))).first()[0]
   
    if old_password:
        if bcrypt.check_password_hash(user.password, old_password):
            if entered_email != user.email and entered_email:
                check_email = list(db.session.execute(select(User).where(User.email == entered_email)))
                if len(check_email) == 0:
                    user.email = entered_email
                else:
                    flash("Email in use", "error")
                    return redirect(url_for("accountsettings", _anchor="settings")) 
        
            if entered_phonenumber != user.phone_number and entered_phonenumber:
                user.phone_number = entered_phonenumber

            if not bcrypt.check_password_hash(user.password, entered_password) and entered_password:
                user.password = bcrypt.generate_password_hash(entered_password)

            db.session.commit()

            flash("Account details changed successfully")
            return redirect(url_for("accountsettings"))

    flash("Incorrect password", "error")
    return redirect(url_for("accountsettings", _anchor="settings")) 
    
@app.route("/api/accountsettings/deleteaccount", methods=["POST", "GET"])
def delete_account():
    entered_password = request.form.get("password")

    user = db.session.execute(select(User).where(User.user_id == session.get("user_id"))).first()[0]

    if not bcrypt.check_password_hash(user.password, entered_password):
        flash("Incorrect password", "error")
        return redirect(url_for("accountsettings", _anchor="del-account"))

    session["logged_in"] = False
    session["user_id"] = None
    session['user_type'] = None

    db.session.delete(user)
    db.session.commit()

    flash("Account Deleted", "message")
    return redirect(url_for('index'))


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    message = ""

    if request.method == 'POST':
        recipient_email = request.form.get("email")
        if not recipient_email:
            flash("You must enter an email", "error")
            return redirect(url_for("forgotpassword"))

        row = db.session.execute(select(User).where(User.email == recipient_email)).first()
        if not row:
            message = f"An email has been sent to {recipient_email} if a user with that email exists in our system"
        else:
            user = row[0]
            token = timestamp_signer.sign(int.to_bytes(user.user_id))

            user.reset_password_token = token

            content = f"""Click here to reset your password: {url_for("resetpassword", token=token.hex(), _external=True, _scheme='http', _host='localhost:5000')}.
    This link will expire in 20 minutes."""
            subject = "Reset Password - Finch & Goose"

            if send_email(recipient_email, content, subject):
                message = f"An email has been sent to {recipient_email} if a user with that email exists in our system"
            else:
                message = "Something went wrong"

    return render_template('forgotpassword.html', message=message)


def send_email(recipient, content, subject):
    try:
        msg = EmailMessage()
        msg.set_content(content, subtype="plain", charset="us-ascii")
        msg['Subject'] = subject
        msg['From'] = "finchandgoose@gmail.com"
        msg['To'] = recipient

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login("finchandgoose@gmail.com", "hhfw jzkl gpec ojlv")
            s.send_message(msg)
            s.quit()

        return True
    except:
        return False

@app.route('/resetpassword/<token>', methods=["GET", "POST"])
def resetpassword(token):
    if request.method == "GET":
        return render_template('resetpassword.html')

    try:
        user_id = int.from_bytes(timestamp_signer.unsign(bytes.fromhex(token), max_age=20 * 60))
    except SignatureExpired:
        flash("Invalid token. You may need to create a new token if you last requested one more than 20 minutes ago.","error")
        return redirect(url_for("forgotpassword"))

    row = db.session.execute(select(User).where(User.user_id == user_id)).first()
    if not row:
        flash("Invalid token. You may need to create a new token if you last requested one more than 20 minutes ago.", "error")
        return redirect(url_for("forgotpassword"))

    user = row[0]
    user.reset_password_token = None
    user.password = bcrypt.generate_password_hash(request.form.get("new_password"))

    db.session.commit()
    flash("Password reset successfully")
    return redirect(url_for("login"))




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
            flash("Added to cart", "message")

            return render_template(
                "cart.html",
                giftcard_value=giftcard_value,
                giftcard_firstname=giftcard_firstname,
                giftcard_lastname=giftcard_lastname,
                giftcard_email=giftcard_email,
                giftcard_recipient=giftcard_recipient,
                giftcard_gifter=giftcard_gifter
            )

    return render_template("giftcard.html")


@app.route('/cart', methods=["POST", "GET"])
def cart():
    if request.method == 'POST':
        cart_country = request.form.get('cart_country')
        cart_cardfullname = request.form.get('cart_cardfullname')
        cart_cardnumber = request.form.get('cart_cardnumber')
        cart_cardcsc = request.form.get('cart_cardcsc')
        cart_expirydate = request.form.get('cart_expirydate')

        if not (cart_country and cart_cardfullname and cart_cardnumber and cart_cardcsc and cart_expirydate):
            flash("All fields are required!", "error")
        else:
            cart = Cart(cart_country, cart_cardfullname, cart_cardnumber, cart_cardcsc, cart_expirydate)
            db.session.add(cart)
            db.session.commit()
            flash("Item Purchased", "message")

            content = "{giftcard_value}{giftcard_firstname}{giftcard_lastname}{giftcard_email}{giftcard_recipient}{giftcard_gifter} "
            send_email(giftcard_recipient, content, object)
            return redirect(url_for('thankyou'))

    return render_template("cart.html")


@app.route('/thankyou')
def thankyou():
    return render_template("thankyou.html")

    #return render_template("cart.html", cart_giftcard=cart_giftcard)



@app.route("/admin", methods=["GET"])
@require_login("admin")
def admin_page():
    user = db.session.execute(select(User).where(User.user_id == session.get("user_id"))).first()[0]
    current_user = user.email
    return render_template("admin.html", current_user=current_user)


@app.route('/delivery', methods=["POST", "GET"])
def delivery():
    if request.method == 'POST':
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        order_details = request.form.get('order_details')
        specifications = request.form.get('specifications')

        delivery = Order(name, phone_number, order_details, specifications)
        db.session.add(delivery)
        db.session.commit()
        flash("Added to cart", "message")

        return render_template(
            "delivery_cart.html",
            name=name,
            phone_number=phone_number,
            order_details=order_details,
            specifications=specifications,
        )

    return render_template("delivery.html")


@app.route("/admin/tables", methods=["GET"])
@require_login("admin")
def admin_tables():
    statement = select(Table)
    rows = db.session.execute(statement)
    tables = [row[0] for row in rows]

    return render_template("admintables.html", tables=tables)


@app.route("/admin/users", methods=["GET"])
@require_login("admin")
def admin_users():
    users = [row[0] for row in db.session.execute(select(User))]

    return render_template("admin_users.html", users=users)


@app.route("/admin/contact", methods=["GET"])
@require_login("admin")
def admin_contact():
    contacts = [row[0] for row in db.session.execute(select(Complaint).where(Complaint.resolved == False))]

    return render_template("admincontact.html", contacts=contacts)

@app.route("/api/update_layout", methods=["POST"])
@require_login("admin")
def update_layout():
    for table in request.form:
        capacity = int(request.form[table])
        statment = (
            update(Table)
            .where(Table.table_id == int(table))
            .values(capacity=capacity)
        )

        db.session.execute(statment)
    db.session.commit()

    return redirect(url_for("admin_tables"))

@app.route("/api/resolve_complaint/<complaint_id>", methods=["POST"])
@require_login("admin")
def resolve_complaint(complaint_id):
    complaint = db.session.execute(select(Complaint).where(Complaint.id == complaint_id)).first()[0]
    complaint.resolved = True
    db.session.commit()

    return redirect(url_for("admin_contact"))


@app.route("/api/delete_complaint/<complaint_id>", methods=["POST"])
@require_login("admin")
def delete_complaint(complaint_id):
    complaint = db.session.execute(select(Complaint).where(Complaint.id == complaint_id)).first()[0]
    db.session.delete(complaint)
    db.session.commit()

    return redirect(url_for("admin_contact"))

@app.route("/api/update_user/<user_id>", methods=["POST"])
@require_login("admin")
def update_user(user_id):
    row = db.session.execute(select(User).where(User.user_id == user_id)).first()

    if not row:
        flash("Could not delete user", "error")
        return redirect(url_for("admin_users"))

    user = row[0]

    user_type = request.form.get("user_type")
    if not user_type:
        flash("Something went wrong", "error")
        return redirect(url_for("admin_users"))

    user.user_type = user_type
    db.session.commit()

    flash("User updated", "message")
    return redirect(url_for("admin_users"))


@app.route("/api/delete_user/<user_id>", methods=["POST"])
@require_login("admin")
def delete_user(user_id):
    row = db.session.execute(select(User).where(User.user_id == user_id)).first()

    if not row:
        flash("Could not delete user", "error")
        return redirect(url_for("admin_users"))

    user = row[0]
    db.session.delete(user)
    db.session.commit()

    flash("User deleted", "message")
    return redirect(url_for("admin_users"))