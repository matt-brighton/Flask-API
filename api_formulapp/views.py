import json
import logging
import requests
from flask import render_template, Blueprint, request

views = Blueprint('views', __name__)

API_BASE_URL = 'http://ergast.com/api/f1/'


def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise


@views.route('/', methods=['GET'])
def index():
    try:
        season_race_data = get_data_from_api(
            API_BASE_URL + '2024.json?limit=1000')
        total_seasons_data = get_data_from_api(
            API_BASE_URL + 'seasons.json?limit=1000')
        driver_data = get_data_from_api(
            API_BASE_URL + 'drivers.json?limit=10000'
        )

        season_year = season_race_data['MRData']['RaceTable']['season']
        total_races = season_race_data['MRData']['total']

        drivers = []
        for driver in driver_data['MRData']['DriverTable']['Drivers']:
            given_name = driver['givenName']
            family_name = driver['familyName']
            date_of_birth = driver['dateOfBirth']
            nationality = driver['nationality']

            drivers.append({
                'given_name': given_name,
                'family_name': family_name,
                'date_of_birth': date_of_birth,
                'nationality': nationality
            })

        years = [{'seasons': season['season']}
                 for season in total_seasons_data['MRData']['SeasonTable']['Seasons']]

        races = []
        for race in season_race_data['MRData']['RaceTable']['Races']:
            round_number = race['round']
            race_name = race['raceName']
            circuit_name = race['Circuit']['circuitName']
            country = race['Circuit']['Location']['country']
            locality = race['Circuit']['Location']['locality']
            race_date = race['date']

            races.append({
                'round_number': round_number,
                'race_name': race_name,
                'circuit_name': circuit_name,
                'country': country,
                'locality': locality,
                'race_date': race_date
            })

        return render_template('index.html', season_year=season_year, total_races=total_races, races=races, years=years, drivers=drivers)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))


@views.route('/get_all_drivers', methods=['GET'])
def get_all_drivers():
    try:
        driver_data = get_data_from_api(
            API_BASE_URL + 'drivers.json?limit=10000'
        )

        drivers1 = []
        for driver in driver_data['MRData']['DriverTable']['Drivers']:
            given_name = driver['givenName']
            family_name = driver['familyName']
            date_of_birth = driver['dateOfBirth']
            nationality = driver['nationality']

            drivers1.append({
                'given_name': given_name,
                'family_name': family_name,
                'date_of_birth': date_of_birth,
                'nationality': nationality
            })

        return render_template('drivers.html', drivers=drivers1)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))
