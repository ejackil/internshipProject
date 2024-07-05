from sqlalchemy import select, func, text
from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy

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


class Reservation(db.Model):
    __tablename__ = "reservations"
    reservation_id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey("tables.table_id"), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/bookings/<table_id>")
def get_bookings(table_id):
    date = request.args.get("date")

    statement = (select(Reservation.start_time, Reservation.end_time)
                 .where(Reservation.table_id == table_id)
                 .where(func.datediff(Reservation.start_time, date) == 0)
                 )

    reservations = [{"start_time": row[0], "end_time": row[1]}
                    for row in db.session.execute(statement)]

    return list(reservations)
