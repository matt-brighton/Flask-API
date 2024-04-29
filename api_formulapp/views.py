import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify, flash, redirect, url_for

views = Blueprint('views', __name__)

ERGAST_API_BASE_URL = 'http://ergast.com/api/f1/'


def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)['MRData']
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise


@views.route('/', methods=['GET'])
def index():
    try:
        current_season_race_data = get_data_from_api(
            ERGAST_API_BASE_URL + '2024.json?limit=1000')
        all_seasons_data = get_data_from_api(
            ERGAST_API_BASE_URL + 'seasons.json?limit=1000')
        drivers_top_3 = get_data_from_api(
            ERGAST_API_BASE_URL + '2024/driverStandings.json?limit=100000')
        constructor_top_3 = get_data_from_api(
            ERGAST_API_BASE_URL + '2024/constructorStandings.json?limit=10000')
        race_results = get_data_from_api(
            ERGAST_API_BASE_URL + '2024/results.json?limit=1000000')

        season_year = current_season_race_data['RaceTable']['season']
        total_races = current_season_race_data['total']

        all_season_years = [{'seasons': season['season']}
                            for season in all_seasons_data['SeasonTable']['Seasons']]
        drivers_top_3 = drivers_top_3['StandingsTable']
        constructor_top_3 = constructor_top_3['StandingsTable']
        race_results = race_results['RaceTable']
        return render_template('index.html', season_year=season_year, total_races=total_races, years=all_season_years,
                               drivers_top_3=drivers_top_3, constructor_top_3=constructor_top_3,
                               race_results=race_results)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/get_selected_season', methods=['POST'])
def get_selected_season():
    if request.method == 'POST':
        try:
            selected_season_year = request.form.get('season_selection')
            selected_season_race_data = get_data_from_api(
                ERGAST_API_BASE_URL + selected_season_year + '.json?limit=1000')
            total_seasons_data = get_data_from_api(
                ERGAST_API_BASE_URL + 'seasons.json?limit=1000')
            drivers_top_3 = get_data_from_api(
                ERGAST_API_BASE_URL + selected_season_year + '/driverStandings.json?limit=10000')
            constructor_top_3 = get_data_from_api(
                ERGAST_API_BASE_URL + selected_season_year + '/constructorStandings.json?limit=10000')
            race_results = get_data_from_api(
                ERGAST_API_BASE_URL + selected_season_year + '/results.json?limit=1000000')

            season_year = selected_season_race_data['RaceTable']['season']
            total_races = selected_season_race_data['total']
            years = [{'seasons': season['season']}
                     for season in total_seasons_data['SeasonTable']['Seasons']]
            drivers_top_3 = drivers_top_3['StandingsTable']
            constructor_top_3 = constructor_top_3['StandingsTable']
            race_results = race_results['RaceTable']

            return render_template('index.html', season_year=season_year, total_races=total_races, years=years,
                                   drivers_top_3=drivers_top_3, constructor_top_3=constructor_top_3,
                                   race_results=race_results)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return render_template('error.html', error_message=str(e))


@views.route('/quiz_me', methods=['POST', 'GET'])
def quiz_me():
    if request.method == 'POST':
        try:
            quiz_selected_year = request.form.get('quiz_selection')
            total_seasons_data = get_data_from_api(
                ERGAST_API_BASE_URL + 'seasons.json?limit=1000')

            years = [{'seasons': season['season']}
                     for season in total_seasons_data['SeasonTable']['Seasons']]

            return render_template('quiz.html', quiz_selected_year=quiz_selected_year, years=years)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return render_template('error.html', error_message=str(e))
    else:
        try:
            total_seasons_data = get_data_from_api(
                ERGAST_API_BASE_URL + 'seasons.json?limit=1000')

            years = [{'seasons': season['season']}
                     for season in total_seasons_data['SeasonTable']['Seasons']]

            return render_template('quiz.html', years=years)
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

    return redirect(url_for('views.quiz_me'))
