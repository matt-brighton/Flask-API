import json
import logging
import requests
from flask import render_template, Blueprint

views = Blueprint('views', __name__)

API_BASE_URL = 'http://ergast.com/api/f1/'


def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise  # Propagate the exception for the caller to handle


@views.route('/', methods=['GET'])
def index():
    try:
        season_race_data_json = get_data_from_api(
            API_BASE_URL + '2024.json?limit=1000')
        total_seasons_data_json = get_data_from_api(
            API_BASE_URL + 'seasons.json?limit=1000')

        season_year = season_race_data_json['MRData']['RaceTable']['season']
        total_races = season_race_data_json['MRData']['total']

        all_seasons = [{'seasons': season['season']}
                       for season in total_seasons_data_json['MRData']['SeasonTable']['Seasons']]

        races = []
        for race in season_race_data_json['MRData']['RaceTable']['Races']:
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

        return render_template('index.html', season_year=season_year, total_races=total_races, races=races, seasons=all_seasons)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message=str(e))
