from flask import render_template, Blueprint
import requests
from flask import json

views= Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def index():
    json_data = requests.get('http://ergast.com/api/f1/2024.json')
    data = json.loads(json_data.content)
    season = data['MRData']['RaceTable']['season']
    total_races = data['MRData']['total']
    races = []

    for race in data['MRData']['RaceTable']['Races']:
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


    return render_template('index.html', season=season, total_races=total_races, races=races)