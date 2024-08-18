"""
@author ChinaiArman
@version 1.0.0
This script queries the Faceit API for tournament data and saves it to a CSV file.
"""

# IMPORTS
from dotenv import load_dotenv
load_dotenv()
import argparse
import os
import requests
import pandas as pd
from datetime import datetime




# CONSTANTS
API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://open.faceit.com/data/v4/'
MATCH_URI = 'championships/{}/matches'
TOURNAMENT_URI = 'championships/{}'
PARSER = argparse.ArgumentParser(description="Parse tournament ID from CLI arguments.")
MATCH_COLUMNS = ["w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8", "l9"]
TOURNAMENT_COLUMNS = ["tournament_name", "tournament_start", "tournament_region", "prize_pool"]




# FUNCTIONS
def query_api(URI: str, repeat=False, limit=0) -> dict:
    """
    Query the Faceit API with the given URI.

    Args:
        URI (str): The URI to query.

    Returns:
        dict: The response data from the API.
    """
    if repeat:
        response = requests.get(f'{URI}?limit={limit}', headers={'Authorization': f'Bearer {API_KEY}'}).json()
        i = 1
        while len(response["items"]) % limit == 0 and len(response["items"]) != 0:
            offset = i * limit
            new_request = requests.get(f'{URI}?offset={offset}&limit={limit}', headers={'Authorization': f'Bearer {API_KEY}'}).json()
            if len(new_request["items"]) == 0:
                break
            response["items"] += new_request["items"]
            i+=1
        return response
    else:
        return requests.get(URI, headers={'Authorization': f'Bearer {API_KEY}'}).json()


def format_tournament_data_to_csv(tournament_data: dict) -> pd.Series:
    """
    Format the tournament data to a Series.

    Args:
        tournament_data (dict): The tournament data to format.

    Returns:
        pd.Series: The formatted tournament data.
    """
    tournament_name = tournament_data["name"]
    tournament_start = datetime.fromtimestamp(tournament_data["championship_start"]/1000)
    tournament_region = tournament_data["region"]
    prize_pool = tournament_data["total_prizes"]
    return pd.Series({
        "tournament_name": tournament_name,
        "tournament_start": tournament_start,
        "tournament_region": tournament_region,
        "prize_pool": prize_pool
    })
    


def format_match_data_to_csv(match_data: dict) -> pd.DataFrame:
    """
    Format the match data to a DataFrame.

    Args:
        match_data (dict): The match data to format.

    Returns:
        pd.DataFrame: The formatted match data.
    """
    df = pd.DataFrame(columns=MATCH_COLUMNS)
    for match in match_data["items"]:
        try: 
            winner = match["results"]["winner"]
            winners = [player["game_player_name"] for player in match["teams"][winner]["roster"]]
            loser = "faction1" if winner != "faction1" else "faction2"
            losers = [player["game_player_name"] for player in match["teams"][loser]["roster"]]
            winnersSeries = pd.Series({f'w{i+1}': winners[i] for i in range(0, min(9, len(winners)))})
            losersSeries = pd.Series({f'l{i+1}': losers[i] for i in range(0, min(9, len(winners)))})
            match_series = pd.concat([winnersSeries, losersSeries])
            df = pd.concat([df, match_series.to_frame().T], ignore_index=True)
        except Exception as e:
            if match["teams"]["faction2"]["faction_id"] == "bye":
                try:
                    winnersSeries = pd.Series({f'w{i+1}': match["teams"]["faction1"]["roster"][i]["game_player_name"] for i in range(0, min(9, len(match["teams"]["faction1"]["roster"])))})
                    losersSeries = pd.Series({'l1': 'BYE'})
                    match_series = pd.concat([winnersSeries, losersSeries])
                    df = pd.concat([df, match_series.to_frame().T], ignore_index=True)
                except Exception as e:
                    print(e)
            else:
                print(e)
    df = df.fillna('')
    return df

        
        
            
# MAIN
if __name__ == '__main__':
    # Parse CLI Arguments
    PARSER.add_argument('tournament_id', type=str, help='Tournament ID to query.')
    args = PARSER.parse_args()

    # Query API
    df = pd.DataFrame(columns=TOURNAMENT_COLUMNS + MATCH_COLUMNS)
    tournament_data = query_api(BASE_URL + TOURNAMENT_URI.format(args.tournament_id))
    match_data = query_api(BASE_URL + MATCH_URI.format(args.tournament_id), repeat=True, limit=100)

    # Format Data
    formatted_tournament_data = format_tournament_data_to_csv(tournament_data)
    formatted_match_data = format_match_data_to_csv(match_data)
    for _, row in formatted_match_data.iterrows():
        tournament_data = pd.Series(formatted_tournament_data)
        merged_row = pd.concat([tournament_data, row])
        df = pd.concat([df, merged_row.to_frame().T], ignore_index=True)

    # Save Data
    df.to_csv(f'{args.tournament_id}.csv', index=False)
    print(f'Successfully saved data to {args.tournament_id}.csv')
