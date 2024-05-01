import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, InputRequired

auth = Blueprint('auth', __name__)


@auth.route('/user/<username>')
def user(username):
    return render_template("user.html", username=username)


# Form class
class SignUpForm(FlaskForm):
    name = StringField("Please confirm your preferred username", validators=[DataRequired()])
    email = EmailField("Please confirm your email address", validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField("Submit")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    username = None
    email = None
    password = None
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.name.data
        password = form.password.data
        form.name.date = ""
        flash(f"Sign Up Success, thanks {username}")
    return render_template('sign_up.html', username=username, email=email, form=form, password=password)
