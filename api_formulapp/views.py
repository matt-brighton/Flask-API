from flask import render_template, Blueprint
import requests
from flask import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def index():
    season_race_data = requests.get('http://ergast.com/api/f1/2024.json?limit=1000')
    total_seasons_data = requests.get('http://ergast.com/api/f1/seasons.json?limit=1000')
    season_race_data_json = json.loads(season_race_data.content)
    total_seasons_data_json = json.loads(total_seasons_data.content)
    season_year = season_race_data_json['MRData']['RaceTable']['season']
    total_races = season_race_data_json['MRData']['total']
    all_seasons = []
    races = []     

    for seasons in total_seasons_data_json['MRData']['SeasonTable']['Seasons']:
        all_season_year = seasons['season']
        
        all_seasons.append({
        'seasons': all_season_year
        })
    
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
        
        print(all_seasons)

    return render_template('index.html', season_year=season_year, total_races=total_races, races=races, seasons=all_seasons)
