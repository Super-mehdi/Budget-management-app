from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo,InputRequired
from wtforms import IntegerField

class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    login = StringField("Username", validators=[DataRequired(), Length(min=4, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    country = StringField("Country")
    city = StringField("City")
    currencyPreference=StringField("currencyPreference")
    income=IntegerField("Monthly Income",validators=[InputRequired()], render_kw={"placeholder": "Enter whole numbers only"})


class LoginForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])  # Changed from username to login
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")