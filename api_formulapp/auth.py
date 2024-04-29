import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

auth = Blueprint('auth', __name__)

@auth.route('/user/<name>')
def user(name):
    return render_template("user.html", name=name)


# Form class
class SignUpForm(FlaskForm):
    name = StringField("Please confirm your name", validators=[DataRequired()])
    submit= SubmitField("Submit")
    
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    name = None
    form = SignUpForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.date = ""
    return render_template('sign_up.html', name=name, form=form)