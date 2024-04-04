import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify

views = Blueprint('views', __name__)

API_BASE_URL = 'http://ergast.com/api/f1/'


def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)['MRData']
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise


def process_drivers(driver_data):
    return [{'given_name': driver['givenName'],
             'family_name': driver['familyName'],
             'date_of_birth': driver['dateOfBirth'],
             'nationality': driver['nationality']} for driver in driver_data['DriverTable']['Drivers']]


def process_races(race_data):
    return [{'round_number': race['round'],
             'race_name': race['raceName'],
             'circuit_name': race['Circuit']['circuitName'],
             'country': race['Circuit']['Location']['country'],
             'locality': race['Circuit']['Location']['locality'],
             'race_date': race['date']} for race in race_data['RaceTable']['Races']]


@views.route('/', methods=['GET'])
def index():
    try:
        season_race_data = get_data_from_api(
            API_BASE_URL + '2024.json?limit=1000')
        total_seasons_data = get_data_from_api(
            API_BASE_URL + 'seasons.json?limit=1000')
        driver_data = get_data_from_api(
            API_BASE_URL + 'drivers.json?limit=10000')

        season_year = season_race_data['RaceTable']['season']
        total_races = season_race_data['total']

        drivers = process_drivers(driver_data)
        years = [{'seasons': season['season']}
                 for season in total_seasons_data['SeasonTable']['Seasons']]
        races = process_races(season_race_data)

        return render_template('index.html', season_year=season_year, total_races=total_races, races=races, years=years, drivers=drivers)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/get_all_drivers', methods=['GET'])
def get_all_drivers():
    try:
        driver_data = get_data_from_api(
            API_BASE_URL + 'drivers.json?limit=10000')
        drivers = process_drivers(driver_data)
        return render_template('drivers.html', drivers=drivers)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/get_selected_season', methods=['POST'])
def get_selected_season():
    if request.method == 'POST':
        try:
            selected_year = request.form.get('season_selection')
            selected_season_race_data = get_data_from_api(
                API_BASE_URL + selected_year + '.json?limit=1000')

            season_year = selected_season_race_data['RaceTable']['season']
            total_races = selected_season_race_data['total']
            races = process_races(selected_season_race_data)

            return jsonify({'races': races, 'season_year': season_year, 'total_races': total_races})

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return render_template('error.html', error_message=str(e))
