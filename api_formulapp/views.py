import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime

views = Blueprint('views', __name__)

ERGAST_API_BASE_URL = 'http://ergast.com/api/f1/'
current_year = datetime.now().year


def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)['MRData']
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise

def get_season_data(season_year):
    season_race_data = get_data_from_api(f"{ERGAST_API_BASE_URL}{season_year}.json?limit=1000")
    drivers_standings = get_data_from_api(f"{ERGAST_API_BASE_URL}{season_year}/driverStandings.json?limit=10000")
    constructors_standings = get_data_from_api(f"{ERGAST_API_BASE_URL}{season_year}/constructorStandings.json?limit=10000")
    race_results = get_data_from_api(f"{ERGAST_API_BASE_URL}{season_year}/results.json?limit=1000000")
    return {
        'season_year': season_race_data['RaceTable']['season'],
        'total_races': season_race_data['total'],
        'drivers_standings': drivers_standings['StandingsTable'],
        'constructors_standings': constructors_standings['StandingsTable'],
        'race_results': race_results['RaceTable']
    }

def get_all_seasons_data():
    all_seasons_data = get_data_from_api(f"{ERGAST_API_BASE_URL}seasons.json?limit=1000")
    return [{'seasons': season['season']} for season in all_seasons_data['SeasonTable']['Seasons']]


@views.route('/', methods=['GET'])
def index():
    try:
        current_season_data = get_season_data(current_year)
        all_season_years = get_all_seasons_data()
        return render_template('index.html', years=all_season_years, user=current_user, **current_season_data)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/get_selected_season', methods=['POST'])
def get_selected_season():
    try:
        selected_season_year = request.form.get('season_selection')
        selected_season_data = get_season_data(selected_season_year)
        all_season_years = get_all_seasons_data()
        return render_template('index.html', years=all_season_years, user=current_user, **selected_season_data)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/quiz_me', methods=['POST', 'GET'])
def quiz_me():
    quiz_selected_year = request.form.get('quiz_selected_year') if request.method == 'POST' else request.args.get('quiz_selected_year')
    try:
        all_season_years = get_all_seasons_data()
        return render_template('quiz.html', quiz_selected_year=quiz_selected_year, years=all_season_years, user=current_user)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/submit_form', methods=['POST'])
def submit_form():
    input_year = request.form.get('input_year')
    quiz_selected_year = request.form.get('quiz_selected_year')

    if input_year == quiz_selected_year:
        flash("Correct!", category='success')
    else:
        flash("Incorrect. Please try again.", category='error')

    return redirect(url_for('views.quiz_me', quiz_selected_year=quiz_selected_year))
