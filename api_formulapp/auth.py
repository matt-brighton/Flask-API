import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, InputRequired
from .models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/user/<username>')
def user(username):
    return render_template("user.html", username=username)


# Form class
class SignUpForm(FlaskForm):
    name = StringField("Please confirm your preferred username",
                       validators=[DataRequired()])
    email = EmailField("Please confirm your email address",
                       validators=[DataRequired()])
    password = PasswordField('New Password', validators=[
                             DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Submit")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    username = None
    email = None
    password = None
    user = Users.query.filter_by(email=email).first()
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.name.data
        password = form.password.data
        form.name.date = ""
        if user:
            flash("email already exists", category='error')
        else:
            new_user = Users(email=email, username=username, password=generate_password_hash(
                password, method='sha256'))
            try:
                db.session.add(new_user)
                db.session.commit()
                flash(f"Sign Up Success, thanks {username}")

            except Exception as exception:
                db.session.rollback()
                flash(f"Sign Up Failure: {str(exception)}", category="error")
    return render_template('sign_up.html', username=username, email=email, form=form, password=password, user=current_user)
