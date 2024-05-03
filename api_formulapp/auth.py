import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, InputRequired
from .models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from api_formulapp.views import ERGAST_API_BASE_URL, get_data_from_api

auth = Blueprint('auth', __name__)

# Sign Up Form class
class SignUpForm(FlaskForm):
    name = StringField("Please confirm your preferred username",
                       validators=[DataRequired()])
    email = EmailField("Please confirm your email address",
                       validators=[DataRequired()])
    password = PasswordField('New Password', validators=[
                             DataRequired(), EqualTo('confirm', message='Passwords must match')])
    favourite_team = SelectField("Who is your favourite team?", choices=[], validators=[DataRequired()])
    favourite_driver = SelectField("Who is your favourite driver?", choices=[], validators=[DataRequired()])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Submit")
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        data = get_data_from_api(ERGAST_API_BASE_URL + 'constructors.json?limit=1')
        constructor_list = data.get('MRData', {}).get('ConstructorTable', {}).get('Constructors', {})
        self.favourite_team.choices = [(constructor['constructorId'], constructor['name']) for constructor in constructor_list]




@auth.route('/user')
@ login_required
def user():
    if request.method == 'GET':
        return render_template("user.html", current_user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.index'))



@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = None
        email = None
        password = None
        favourite_team = None
        favourite_driver = None
        user = Users.query.filter_by(email=email).first()
        form = SignUpForm(request.form)

        
        if form.validate_on_submit():
            email = form.email.data
            username = form.name.data
            password = form.password.data
            favourite_team = form.favourite_team.data
            favourite_driver = form.favourite_driver.data
            form.name.data = ""
            if user:
                flash("email already exists", category='error')
            else:
                new_user = Users(email=email, username=username, password=generate_password_hash(
                    password, method='sha256'), favourite_team=favourite_team, favourite_driver=favourite_driver)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash(f"Sign Up Success, thanks {username}")
                login_user(new_user, remember=True)

            except Exception as exception:
                db.session.rollback()
                flash(f"Sign Up Failure: {str(exception)}", category="error")
    # return render_template('sign_up.html', username=username, email=email, form=form, password=password, user=current_user)
        return redirect(url_for('auth.user', current_user=current_user))
    else:
        username = None
        email = None
        password = None
        user = Users.query.filter_by(email=email).first()
        form = SignUpForm()
        return render_template('sign_up.html', username=username, email=email, form=form, password=password, user=current_user)
