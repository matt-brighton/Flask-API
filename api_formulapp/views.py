import json
import logging
import requests
from flask import render_template, Blueprint, request, jsonify

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
        current_season_race_data = get_data_from_api(
            ERGAST_API_BASE_URL + '2024.json?limit=1000')
        all_seasons_data = get_data_from_api(
            ERGAST_API_BASE_URL + 'seasons.json?limit=1000')
        all_drivers_data = get_data_from_api(
            ERGAST_API_BASE_URL + 'drivers.json?limit=10000')
        drivers_top_3 = get_data_from_api(
            ERGAST_API_BASE_URL + '2024/driverStandings.json?limit=3')
        constructor_top_3 = get_data_from_api(
            ERGAST_API_BASE_URL + '2024/constructorStandings.json?limit=3')
        race_results_1st = get_data_from_api(
            ERGAST_API_BASE_URL + '2024/results/1.json?limit=10000')

        season_year = current_season_race_data['RaceTable']['season']
        total_races = current_season_race_data['total']

        drivers = process_drivers(all_drivers_data)
        all_season_years = [{'seasons': season['season']}
                            for season in all_seasons_data['SeasonTable']['Seasons']]
        races = process_races(current_season_race_data)
        drivers_top_3 = drivers_top_3['StandingsTable']
        constructor_top_3 = constructor_top_3['StandingsTable']
        race_results_1st = race_results_1st['RaceTable']
        return render_template('index.html', season_year=season_year, total_races=total_races, races=races, years=all_season_years, drivers=drivers, drivers_top_3=drivers_top_3, constructor_top_3=constructor_top_3, race_results_1st=race_results_1st)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/get_all_drivers', methods=['GET'])
def get_all_drivers():
    try:
        driver_data = get_data_from_api(
            ERGAST_API_BASE_URL + 'drivers.json?limit=10000')
        drivers = process_drivers(driver_data)
        return render_template('drivers.html', drivers=drivers)

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
            driver_data = get_data_from_api(
                ERGAST_API_BASE_URL + 'drivers.json?limit=10000')
            total_seasons_data = get_data_from_api(
                ERGAST_API_BASE_URL + 'seasons.json?limit=1000')
            drivers_top_3 = get_data_from_api(
                ERGAST_API_BASE_URL + selected_season_year + '/driverStandings.json?limit=3')
            constructor_top_3 = get_data_from_api(
                ERGAST_API_BASE_URL + selected_season_year + '/constructorStandings.json?limit=3')
            race_results_1st = get_data_from_api(
                ERGAST_API_BASE_URL + selected_season_year + '/results/1.json?limit=10000')

            season_year = selected_season_race_data['RaceTable']['season']
            total_races = selected_season_race_data['total']
            races = process_races(selected_season_race_data)
            drivers = process_drivers(driver_data)
            years = [{'seasons': season['season']}
                     for season in total_seasons_data['SeasonTable']['Seasons']]
            drivers_top_3 = drivers_top_3['StandingsTable']
            constructor_top_3 = constructor_top_3['StandingsTable']
            race_results_1st = race_results_1st['RaceTable']

            return render_template('index.html', season_year=season_year, total_races=total_races, races=races, years=years, drivers=drivers, drivers_top_3=drivers_top_3, constructor_top_3=constructor_top_3, race_results_1st=race_results_1st)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return render_template('error.html', error_message=str(e))
