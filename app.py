import os
import datetime

from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_bcrypt import Bcrypt
from static.python.utils.json import editweight, loadprizes

load_dotenv(os.path.abspath('.env'))

uri = os.environ.get('DATABASE_URL')
secret_key = os.environ.get('CLIENT_SECRET')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

ENV = os.environ.get('ENV')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SECRET_KEY'] = secret_key

if ENV == 'dev':
    app.debug = True
else:
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
lm = LoginManager(app)
bc = Bcrypt(app)


class Broadcaster(db.Model):
    __tablename__ = 'broadcaster'
    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.String(25), unique=True, nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    prizes = db.relationship("Prize", backref="broadcaster")
    lists = db.relationship("List", backref="broadcaster")


class List(db.Model):
    __tablename__ = 'list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    created_by = db.Column(db.String(25))
    is_active = db.Column(db.Boolean, default=True)
    broadcaster_id = db.Column(db.Integer, db.ForeignKey('broadcaster.id'))


class Prize(db.Model):
    __tablename__ = 'prize'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    prize = db.Column(db.String(255))
    date = db.Column(db.Date, default=datetime.utcnow)
    broadcaster_id = db.Column(db.Integer, db.ForeignKey('broadcaster.id'))
    checkAlert = db.Column(db.Boolean, default=False)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user:
            if bc.check_password_hash(user.password, request.form['password']):
                login_user(user)
                return redirect('/prizes')
    else:
        return render_template("login.html")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route("/", methods=["GET"])
def home():
    prizes = Prize.query.order_by(Prize.id.desc()).filter(
        db.extract('month', Prize.date) == datetime.today().month).all()
    return render_template("table.html", headings=("Name", "Prize", "Date"), prizes=prizes)


@app.route("/prizes", methods=["GET", "POST"])
@login_required
def prizes():
    if request.method == "POST":
        id = request.form["id"]
        weight = request.form["weight"]
        editweight('emerok1', id, weight)
        return redirect('/prizes')
    else:
        prizes = loadprizes('emerok1')
        return render_template("prizes.html", headings=("Prize", "Weight"), prizes=prizes)


@app.route("/prizes/overlay", methods=["GET"])
def overlay():
    return render_template("overlay.html")


@app.route('/api/prizes')
def api_prizes():
    prizes = Prize.query.order_by(Prize.id.asc()).where(
        Prize.checkAlert == False).first()
    try:
        return jsonify({'id': prizes.id, 'prize': prizes.prize})
    except:
        return jsonify(None)


@app.route('/update/prizes/<int:id>', methods=['POST'])
def update_prizes(id):
    Prize.query.filter_by(id=id).update({Prize.checkAlert: True})
    db.session.commit()
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
