import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

auth = Blueprint('auth', __name__)


@auth.route('/user/<username>')
def user(username):
    return render_template("user.html", username=username)


# Form class
class SignUpForm(FlaskForm):
    name = StringField("Please confirm your preferred username", validators=[DataRequired()])
    submit = SubmitField("Submit")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    username = None
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.name.data
        form.name.date = ""
        flash(f"Sign Up Success, thanks {username}.")
    return render_template('sign_up.html', username=username, form=form)
