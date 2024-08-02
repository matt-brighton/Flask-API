import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta

# GLOBALS
views = Blueprint('views', __name__)
ERGAST_API_BASE_URL = 'http://ergast.com/api/f1/'
current_year = datetime.now().year
OPEN_F1_BASE_URL = 'https://api.openf1.org/v1/'

# METHODS


def get_ergast_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)['MRData']
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise


def get_openf1_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)

    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise


def process_datetime(data):
    for entry in data:
        entry['date'] = datetime.fromisoformat(entry['date'])
        entry['date'] = entry['date'].strftime('%d-%m-%Y @ %H:%M')
    return data


def convert_mins(data):
    for entry in data:
        if entry['lap_duration'] == None or not isinstance(entry['lap_duration'], (int, float)):
            continue
        seconds = entry['lap_duration']
        minutes = int(seconds // 60)
        remainder = seconds % 60
        whole_seconds = int(remainder)
        milliseconds = int((remainder - whole_seconds) * 1000)
        entry['lap_duration'] = f"{minutes:02}:{whole_seconds:02}.{milliseconds:03}"

    return data


def get_season_data(season_year):
    season_race_data = get_ergast_data(
        f"{ERGAST_API_BASE_URL}{season_year}.json?limit=1000")
    drivers_standings = get_ergast_data(
        f"{ERGAST_API_BASE_URL}{season_year}/driverStandings.json?limit=10000")
    constructors_standings = get_ergast_data(
        f"{ERGAST_API_BASE_URL}{season_year}/constructorStandings.json?limit=10000")
    race_results = get_ergast_data(
        f"{ERGAST_API_BASE_URL}{season_year}/results.json?limit=1000000")
    for race in race_results['RaceTable']['Races']:
        original_date = race['date']
        formatted_date = datetime.strptime(
            original_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        race['date'] = formatted_date
    return {
        'season_year': season_race_data['RaceTable']['season'],
        'total_races': season_race_data['total'],
        'drivers_standings': drivers_standings['StandingsTable'],
        'constructors_standings': constructors_standings['StandingsTable'],
        'race_results': race_results['RaceTable']
    }


def get_all_seasons_data():
    all_seasons_data = get_ergast_data(
        f"{ERGAST_API_BASE_URL}seasons.json?limit=1000")
    return [{'seasons': season['season']} for season in all_seasons_data['SeasonTable']['Seasons']]

# ROUTES


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
    quiz_selected_year = request.form.get(
        'quiz_selected_year') if request.method == 'POST' else request.args.get('quiz_selected_year')
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


@views.route('/latest_meeting', methods=["GET"])
def current_grid():
    try:
        drivers_data = get_openf1_data(f"{OPEN_F1_BASE_URL}drivers")
        driver_map = {}
        for driver in drivers_data:
            driver_number = driver['driver_number']
            driver_name = driver['full_name']
            if driver_number not in driver_map:
                driver_map[driver_number] = driver_name
        print(driver_map)
        latest_meeting_session_data = get_openf1_data(
            f"{OPEN_F1_BASE_URL}sessions?session_key=latest")
        latest_meeting_driver_data = get_openf1_data(
            f"{OPEN_F1_BASE_URL}drivers?session_key=latest&driver_number=44")
        latest_meeting_position_data = get_openf1_data(
            f"{OPEN_F1_BASE_URL}position?session_key=latest&driver_number=44")
        latest_meeting_position_data = process_datetime(
            latest_meeting_position_data)
        latest_meeting_position_data = latest_meeting_position_data[-1] if latest_meeting_position_data else None
        latest_meeting_radio_data = get_openf1_data(
            f"{OPEN_F1_BASE_URL}team_radio?session_key=latest&driver_number=44")
        latest_meeting_radio_data = process_datetime(
            latest_meeting_radio_data)
        latest_meeting_lap_data = get_openf1_data(
            f"{OPEN_F1_BASE_URL}laps?session_key=latest&driver_number=44")
        latest_meeting_lap_data = reversed(
            convert_mins(latest_meeting_lap_data))
        return render_template('latest_meeting.html', latest_meeting_session_data=latest_meeting_session_data[0], latest_meeting_driver_data=latest_meeting_driver_data[0],
                                latest_meeting_position_data=latest_meeting_position_data, latest_meeting_radio_data=latest_meeting_radio_data,
                                latest_meeting_lap_data=latest_meeting_lap_data)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))
