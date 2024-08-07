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
from api_formulapp.views import ERGAST_API_BASE_URL, get_ergast_data
from datetime import datetime

auth = Blueprint('auth', __name__)

# FORMS
class SignUpForm(FlaskForm):
    name = StringField("Please confirm your preferred username",
                       validators=[DataRequired()])
    email = EmailField("Please confirm your email address",
                       validators=[DataRequired()])
    password = PasswordField('New Password', validators=[
                             DataRequired(), EqualTo('confirm', message='Passwords must match')])
    favourite_team = SelectField(
        "Who is your favourite team?", choices=[], validators=[DataRequired()])
    favourite_driver = SelectField(
        "Who is your favourite driver?", choices=[], validators=[DataRequired()])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        constructor_data = get_ergast_data(
            ERGAST_API_BASE_URL + 'constructors.json?limit=10000')
        driver_data = get_ergast_data(
            ERGAST_API_BASE_URL + 'drivers.json?limit=10000')
        constructor_list = constructor_data.get(
            'ConstructorTable', {}).get('Constructors', [])
        self.favourite_team.choices = [
            (constructor['constructorId'], constructor['name']) for constructor in constructor_list]
        driver_list = driver_data.get('DriverTable', {}).get('Drivers', [])
        self.favourite_driver.choices = [(
            driver['driverId'], f"{driver['givenName']} {driver['familyName']}") for driver in driver_list]

# ROUTES
@ auth.route('/user')
def user():
    if request.method == 'GET':
        # Fetch regular race data
        favourite_driver_data = get_ergast_data(
            ERGAST_API_BASE_URL + 'drivers/' + current_user.favourite_driver + '/results.json?limit=10000000000')
        races = favourite_driver_data['RaceTable']['Races']

        get_driver_names = get_ergast_data(
            ERGAST_API_BASE_URL + 'drivers/' + current_user.favourite_driver + '.json')
        driver_first_name = get_driver_names['DriverTable']['Drivers'][0]['givenName']
        driver_surname = get_driver_names['DriverTable']['Drivers'][0]['familyName']
        dob = get_driver_names['DriverTable']['Drivers'][0]['dateOfBirth']
        dob = datetime.strptime(dob, '%Y-%m-%d').strftime('%d/%m/%Y')
        nationality = get_driver_names['DriverTable']['Drivers'][0]['nationality']
        driver_number = get_driver_names['DriverTable']['Drivers'][0]['permanentNumber']
        wiki = get_driver_names['DriverTable']['Drivers'][0]['url']

        get_constructor_names = get_ergast_data(
            ERGAST_API_BASE_URL + 'constructors/' + current_user.favourite_team + '.json')
        constructor_name = get_constructor_names['ConstructorTable']['Constructors'][0]['name']
        constructor_nationality = get_constructor_names[
            'ConstructorTable']['Constructors'][0]['nationality']
        constructor_wiki = get_constructor_names['ConstructorTable']['Constructors'][0]['url']

        # Fetch sprint race data
        favourite_driver_sprint_data = get_ergast_data(
            ERGAST_API_BASE_URL + 'drivers/' + current_user.favourite_driver + '/sprint.json?limit=10000000000')
        sprint_races = favourite_driver_sprint_data['RaceTable']['Races']

        favourite_driver_standings = get_ergast_data(
            ERGAST_API_BASE_URL + 'drivers/' + current_user.favourite_driver + '/driverstandings.json?limit=10000000000')
        standings = favourite_driver_standings['StandingsTable']['StandingsLists']

        season_data = {}
        
        total_wins = 0
        sprint_wins = 0
        driver_championships = 0
        
        for race in races:
            season = race['season']
            if season not in season_data:
                season_data[season] = {
                    'total_races': 0,
                    'races_finished': 0,
                    'total_grid_positions': 0,
                    'total_finishing_positions': 0,
                    'total_points': 0,
                    'total_sprint_races': 0,
                    'total_sprint_points': 0,
                    'final_position': None,
                    'constructor': None,
                    'wins': 0,
                    'sprint_wins': 0
                }
            season_data[season]['total_races'] += 1
            

            for result in race['Results']:
                if result['status'] in ['Finished', '+1 Lap', '+2 Laps']:
                    season_data[season]['races_finished'] += 1
                    if result['grid'].isdigit():
                        season_data[season]['total_grid_positions'] += float(
                            result['grid'])
                    if result['position'].isdigit():
                        season_data[season]['total_finishing_positions'] += float(
                            result['position'])
                    season_data[season]['total_points'] += float(
                        result['points'])
                    if result['position'] == '1':
                        season_data[season]['wins'] += 1
                        total_wins += 1

        # Process sprint race data
        for sprint_race in sprint_races:
            season = sprint_race['season']
            if season in season_data:
                season_data[season]['total_sprint_races'] += 1
                for sprint_result in sprint_race['SprintResults']:
                    season_data[season]['total_sprint_points'] += float(
                        sprint_result['points'])
                    if sprint_result['position'] == '1':
                        season_data[season]['sprint_wins'] += 1
                        sprint_wins += 1

        # Calculate season-wise averages
        for season, data in season_data.items():
            total_races = data['total_races'] + data['total_sprint_races']
            total_points = data['total_points'] + data['total_sprint_points']
            if data['races_finished'] > 0:
                data['average_grid_position'] = data['total_grid_positions'] / \
                    data['races_finished']
                data['average_finishing_position'] = data['total_finishing_positions'] / \
                    data['races_finished']
                data['average_points'] = total_points / total_races
            else:
                data['average_grid_position'] = 0
                data['average_finishing_position'] = 0
                data['average_points'] = 0

        for standing in standings:
            season = standing['season']
            if season in season_data and 'DriverStandings' in standing and standing['DriverStandings']:
                season_data[season]['final_position'] = int(
                    standing['DriverStandings'][0]['position'])
                if standing['DriverStandings'][0]['position'] == '1': driver_championships +=1
                if 'Constructors' in standing['DriverStandings'][0]:
                    season_data[season]['constructor'] = str(
                        standing['DriverStandings'][0]['Constructors'][0]['name'])
                else:
                    season_data[season]['constructor'] = 'Unknown'
        
        return render_template('user.html', season_data=season_data, driver_first_name=driver_first_name, driver_surname=driver_surname, 
                               dob=dob, nationality=nationality, driver_number=driver_number, wiki=wiki, constructor_name=constructor_name, 
                               constructor_nationality=constructor_nationality, constructor_wiki=constructor_wiki, total_wins=total_wins, sprint_wins=sprint_wins, driver_championships=driver_championships)

@ auth.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for('views.index'))

@ auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        username = form.name.data
        password = form.password.data
        favourite_team = form.favourite_team.data
        favourite_driver = form.favourite_driver.data

        user = Users.query.filter_by(email=email).first()

        if user:
            flash("Email already exists", category='error')
        else:
            new_user = Users(email=email, username=username, password=generate_password_hash(password, method='sha256'),
                             favourite_team=favourite_team, favourite_driver=favourite_driver)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash(f"Sign Up Success, thanks {username}")
                login_user(new_user, remember=True)
                return redirect(url_for('auth.user'))
            except Exception as e:
                db.session.rollback()
                flash(f"Sign Up Failure: {str(e)}", category="error")

    return render_template('sign_up.html', form=form)
