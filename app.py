from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm
import sqlite3
from datetime import datetime

from forms import LoginForm
from flask_login import login_user, login_required, logout_user, current_user

from apptst import scrape_jumia

import requests
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Users.db"
app.config["SECRET_KEY"] = "0000" 

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
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
    user_income = current_user.income
    if user_income is None:
        user_income = 0

    # Calculer les dépenses totales
    total_spent = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(quantity * pricePerUnit) FROM purchase WHERE user_id = ?
    ''', (current_user.id,))
    result = cursor.fetchone()
    if result and result[0]:
        total_spent = result[0]

    remaining = user_income - total_spent
    percent_used = (total_spent / user_income) * 100 if user_income > 0 else 0
    percent_display = min(percent_used, 100)

    # 🔁 Récupérer tous les objectifs de l’utilisateur
    cursor.execute('''
        SELECT * FROM goal WHERE user_id = ? ORDER BY goalId DESC
    ''', (current_user.id,))
    goals = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           user_income=user_income,
                           total_spent=total_spent,
                           remaining=remaining,
                           percent_used=percent_display,
                           real_percent_used=percent_used,
                           goals=goals)


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].replace(' ', '+')

    jumia = scrape_jumia(query)

    # Construction HTML
    html = "<h2>Résultats Jumia :</h2><ul>"
    for r in jumia:
        html += f"<li>{r}</li>"
    html += "</ul>"
    return html

@app.route("/market")
def market():
    return render_template('market.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

def get_db_connection():
    conn = sqlite3.connect('Users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/history')
def history():
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    conn = get_db_connection()
    achats = conn.execute('''
        SELECT * FROM purchase
        WHERE user_id = ?
        AND strftime('%m', dateOfPurchase) = ?
        AND strftime('%Y', dateOfPurchase) = ?
    ''', (current_user.id, f'{current_month:02d}', str(current_year))).fetchall()
    conn.close()

    return render_template('hist.html', achats=achats)

@app.route("/add-goal", methods=["GET"])
@login_required
def add_goal():
    # Liste prédéfinie de produits disponibles
    products = [
        {"name": "ps5", "price": 6000},
        {"name": "iphone15", "price": 10000},
        {"name": "xboxseriesx", "price": 6000},
        {"name": "airpods", "price": 500},
        {"name": "velo", "price": 1500},
    ]
    return render_template("add_goal.html", products=products)

@app.route("/add-goal", methods=["POST"])
@login_required
def save_goal():
    from datetime import datetime

    product = request.form.get("product")
    startedAt = datetime.today().strftime('%Y-%m-%d')

    product_prices = {
        "ps5": 6000,
        "iphone15": 10000,
        "xboxseriesx": 6000,
        "airpods": 500,
        "velo": 1500
    }

    outcome = product_prices.get(product)

    if outcome is None:
        flash("Produit inconnu ou invalide", "error")
        return redirect(url_for("add_goal"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # cursor.execute('DELETE FROM goal WHERE user_id = ?', (current_user.id,))

    # Ajouter un nouvel objectif en plus des autres
    cursor.execute('''
        INSERT INTO goal (goalNature, startedAt, endedAt, outcome, user_id)
        VALUES (?, ?, NULL, ?, ?)
    ''', (product, startedAt, outcome, current_user.id))
    conn.commit()
    conn.close()

    flash("Objectif ajouté avec succès !", "success")
    return redirect(url_for("dashboard"))


@app.route('/reset_expenses', methods=['POST'])
def reset_expenses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM purchase WHERE user_id = ?', (current_user.id,))
    conn.commit()
    conn.close()

    flash('Vos dépenses ont été réinitialisées avec succès.', 'success')
    return redirect(url_for('history'))


@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if request.method == 'POST':
        productName = request.form['productName']
        quantity = int(request.form['quantity'])
        pricePerUnit = float(request.form['pricePerUnit'])
        dateOfPurchase = request.form['dateOfPurchase']
        vendor = request.form['vendor']
        user_id = current_user.id

        conn = sqlite3.connect('Users.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO purchase (productName, quantity, pricePerUnit, dateOfPurchase, vendor, user_id, product_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (productName, quantity, pricePerUnit, dateOfPurchase, vendor, user_id, 1))

        conn.commit()
        conn.close()

        flash('Achat enregistré avec succès!', 'success')
        return redirect(url_for('expenses'))

    return render_template('expenses.html')

@app.route("/delete-goal/<int:goal_id>", methods=["POST"])
@login_required
def delete_specific_goal(goal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM goal WHERE goalId = ? AND user_id = ?', (goal_id, current_user.id))
    conn.commit()
    conn.close()

    flash("Objectif supprimé.", "info")
    return redirect(url_for("dashboard"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.run(debug=True)