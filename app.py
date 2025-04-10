from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#users' registration route
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm

from forms import LoginForm
from flask_login import login_user

from flask_login import login_required

from flask_login import logout_user

#Configuration
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Users.db"
app.config["SECRET_KEY"] = "0000" 

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login" 
#Database definition
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    income = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(30), nullable=True)
    ready = db.Column(db.Boolean, default=False)
    currencyPreference = db.Column(db.String(5), default="USD")
    
    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy=True)
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)
    messages = db.relationship('Message', backref='user', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)
    priorityLevel = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Product(db.Model):
    productId = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    # Relationships
    purchases = db.relationship('Purchase', backref='product', lazy=True)
    prizes = db.relationship('Prize', backref='product', lazy=True)

class Purchase(db.Model):
    purchaseId = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    pricePerUnit = db.Column(db.Float, nullable=False)
    dateOfPurchase = db.Column(db.Date, default=datetime.utcnow)
    vendor = db.Column(db.String(20), nullable=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.productId'), nullable=False)

class Goal(db.Model):
    goalId = db.Column(db.Integer, primary_key=True)
    goalNature = db.Column(db.String(20), nullable=False)
    startedAt = db.Column(db.Date, default=datetime.utcnow)
    endedAt = db.Column(db.Date, nullable=True)
    outcome = db.Column(db.Boolean, default=False)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    budget = db.relationship('Budget', backref='goal', lazy=True, uselist=False)
    prize = db.relationship('Prize', backref='goal', lazy=True, uselist=False)
    savings = db.relationship('Saving', backref='goal', lazy=True, uselist=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goalId = db.Column(db.Integer, db.ForeignKey('goal.goalId'), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)

class Prize(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goalId = db.Column(db.Integer, db.ForeignKey('goal.goalId'), unique=True, nullable=False)
    productName = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.productId'), nullable=False)

class Saving(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goalId = db.Column(db.Integer, db.ForeignKey('goal.goalId'), unique=True, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

class Message(db.Model):
    messageId = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

"""if __name__ == '__main__':
    with app.app_context():  # <-- THIS IS THE CRUCIAL PART
        db.create_all()
    app.run(debug=True)"""

with app.app_context():
    db.create_all()

#Database creation 
#db.create_all()

@app.route("/")
def home():
    return redirect(url_for('login'))

"""#users' registration route
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm"""



#users'login route
"""from forms import LoginForm
from flask_login import login_user"""
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template("login.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data,
            login=form.login.data,
            email=form.email.data,
            password=hashed_password,
            country=form.country.data,
            city=form.city.data,
            income=form.income.data,
            currencyPreference=form.currencyPreference.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", form=form)


#from flask_login import login_required

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


#from flask_login import logout_user

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.run(debug=True)