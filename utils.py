import requests
import pandas as pd
import pybaseball as pyb
from datetime import datetime as dt
from constants import *
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from dateutil.relativedelta import relativedelta


def get_headshot(player_id: int) -> Image:
    """
    Fetches the player's headshot image from the URL.

    Args:
    - player_id (int): The unique player ID.

    Returns:
    - Image: The player's headshot image as a PIL Image object.
    """
     # Construct the URL to fetch player headshot
    url = f'https://img.mlbstatic.com/mlb-photos/image/'\
        f'upload/d_people:generic:headshot:67:current.png/'\
        f'w_640,q_auto:best/v1/people/{player_id}/headshot/silo/current.png'

    # Send a GET request to the URL
    response = requests.get(url)
    
    # Ensure the request was successful
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        return img
    else:
        raise ValueError(f"Failed to fetch headshot for player ID {player_id}")

def get_player_bio(player_id: str) -> dict:
    """
    Fetch player bio data from MLB API.

    Args:
    - player_id (str): The unique player ID.

    Returns:
    - dict: A dictionary containing the player bio information.
    """
    try:
        # Construct the URL to fetch player bio
        url = f'https://statsapi.mlb.com/api/v1/people?'\
              f'personIds={player_id}&hydrate=currentTeam'

        # Send the GET request to fetch the data
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

        # Parse the JSON response
        data = response.json()

        # Check if the response contains the expected data
        if 'people' not in data or not data['people']:
            raise ValueError(f"No player data found for ID {player_id}")

        # Extract player information
        player_info = data['people'][0]
        primary_position = player_info.get('primaryPosition', {}).get('abbreviation', 'N/A')
        player_name = player_info.get('fullName', 'N/A')
        team = player_info.get('currentTeam', {}).get('name', 'N/A')
        batting_hand = player_info.get('batSide', {}).get('code', 'N/A')
        throwing_hand = player_info.get('pitchHand', {}).get('code', 'N/A')
        height = player_info.get('height', 'N/A')
        weight = player_info.get('weight', 'N/A')
        dob = player_info.get('birthDate', '1900-01-01')

        # Calculate age
        dob = dt.strptime(dob, '%Y-%m-%d')
        today = dt.today()
        age_years = relativedelta(today, dob).years
        last_birthday = dt(today.year, dob.month, dob.day)
        if last_birthday > today:
            last_birthday = dt(today.year - 1, dob.month, dob.day)
        days_since_birthday = (today - last_birthday).days

        age = f"{age_years}.{days_since_birthday:03d}"

        # Return the player bio information
        return {
            "primary_position": primary_position,
            "player_name": player_name,
            "team": team,
            "batting_hand": batting_hand,
            "throwing_hand": throwing_hand,
            "height": height,
            "weight": weight,
            "age": age
        }

    except requests.exceptions.RequestException as e:
        print(f"Error with the request: {e}")
    except ValueError as e:
        print(f"Error processing player data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None  # Return None if any error occurred

def get_team_logo(player_id: str) -> Image:
    """
    Fetches the logo of a player's current MLB team.

    Args:
        player_id (str): The player's MLB ID.

    Returns:
        Image: The team's logo image (PIL Image) if successful, or None if there's an error.
    """
    try:
        # Fetch player data
        url = f"https://statsapi.mlb.com/api/v1/people?personIds={player_id}&hydrate=currentTeam"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Get team abbreviation from player data
        team_link = data['people'][0].get('currentTeam', {}).get('link', None)
        if not team_link:
            raise ValueError("Team link not found for player.")

        team_url = f"https://statsapi.mlb.com{team_link}"
        team_response = requests.get(team_url)
        team_response.raise_for_status()  # Raise an error for bad responses
        team_data = team_response.json()

        team_abbreviation = team_data['teams'][0].get('abbreviation', None)
        if not team_abbreviation:
            raise ValueError("Team abbreviation not found.")

        # Get the logo URL from the MLB_TEAM_LOGOS mapping
        logo_url = MLB_TEAM_LOGOS.get(team_abbreviation)
        if not logo_url:
            raise ValueError(f"Logo URL not found for team: {team_abbreviation}")

        # Fetch and return the team logo
        logo_response = requests.get(logo_url)
        logo_response.raise_for_status()  # Raise an error for bad responses
        img = Image.open(BytesIO(logo_response.content))
        return img

    except Exception as e:
        print(f"An error occurred while fetching the team logo: {e}")
        return None  # Return None if there's an error
    
def get_timeframe(game_type: str = None, start_date: str = None, end_date: str = None, season: int = 2024):
    """
    Generates the timeframe label based on the provided inputs.
    Args:
        game_type (str): The type of game.
        start_date (str): The start date of the timeframe.
        end_date (str): The end date of the timeframe.
        season (int): The season year.
    Returns:
        str: The formatted timeframe label.
    """
    if game_type == "P":
        return f"{season} Postseason"
    elif game_type == "D":
        return f"{season} Division Series"
    elif game_type == "L":
        return f"{season} League Championship"
    elif game_type == "W":
        return f"{season} World Series"
    elif game_type == "S":
        return f"{season} Spring Training"
    elif game_type == "1H":
        return f"{season} Pre All-Star"
    elif game_type == "2H":
        return f"{season} Post All-Star"
    elif (game_type == "R" and 
          start_date == str(SEASON_DATES[season]['REG_START']).strip() 
          and end_date == str(SEASON_DATES[season]['REG_END']).strip()):  
        return f"{season} Regular Season"
    elif start_date is not None and end_date is not None:
        try:
            start = dt.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
            end = dt.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")
            return f"{start} - {end}"
        except ValueError:
            return "Invalid date format"
    else:
        return "Timeframe not specified"
    
def get_filtered_game_logs(player_id: int, start_date: str = None, end_date: str = None, season: int = 2024, game_type: str = 'R'):
    """
    Fetches and filters game logs for a player based on optional date ranges.
    
    Args:
        player_id (int): The player's MLB ID.
        start_date (str): Start date in "YYYY-MM-DD" format. Optional.
        end_date (str): End date in "YYYY-MM-DD" format. Optional.
        season (int): The season year.
        
    Returns:
        pd.DataFrame: A DataFrame containing the filtered game logs.
    """
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
    params = {
        "stats": "gameLog", 
        "season": season, 
        "group": "hitting",
        "gameType": game_type
    }
    
    # Fetch game logs from the API
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch game logs for player ID {player_id}: {response.text}")
    
    # Parse the response JSON
    data = response.json()
    try:
        game_logs = data["stats"][0]["splits"]
    except (IndexError, KeyError):
        raise ValueError(f"No game logs found for player ID {player_id}")    
    
    # Collect rows in a list
    rows = []
    
    for game in game_logs:
        stats = game["stat"]
        rows.append({
            'Date': game['date'],
            'G': stats.get('gamesPlayed', 0),
            'PA': stats.get('plateAppearances', 0),
            'AB': stats.get('atBats', 0),
            'H': stats.get('hits', 0),
            '2B': stats.get('doubles', 0),
            '3B': stats.get('triples', 0),
            'HR': stats.get('homeRuns', 0),
            'R': stats.get('runs', 0),
            'RBI': stats.get('rbi', 0),
            'IBB': stats.get('intentionalWalks', 0),
            'BB': stats.get('baseOnBalls', 0),
            'SO': stats.get('strikeOuts', 0),
            'HBP': stats.get('hitByPitch', 0),
            'SB': stats.get('stolenBases', 0),
            'CS': stats.get('caughtStealing', 0),
            'SF': stats.get('sacFlies', 0)
        })
    
    # Create DataFrame from rows
    game_logs_df = pd.DataFrame(rows)
    
    # Filter game logs by date range
    game_logs_df['Date'] = pd.to_datetime(game_logs_df['Date'])
    filtered_logs = game_logs_df[(game_logs_df['Date'] >= start_date) & (game_logs_df['Date'] <= end_date)]
    
    return filtered_logs

def get_savant_data(player_id: int, start_dt: str, end_dt: str) -> pd.DataFrame:
    """
    Fetch raw hitter data using pybaseball.

    Args:
    - player_id (int): The unique player ID.
    - start_dt (str): The start date in "YYYY-MM-DD" format.
    - end_dt (str): The end date in "YYYY-MM-DD" format.

    Returns:
    - pd.DataFrame: A DataFrame containing the raw hitter data.

    """
    # Later rework to download data faster (concurrent requests)

    return pyb.statcast_batter(start_dt, end_dt, player_id=player_id)

def get_savant_color(pct: float) -> tuple:
    """Get Baseball Savant style color for percentile"""
    if pct <= 50:
        t = pct / 50
        return tuple(
            PERCENTILE_COLORS['blue'][i] + 
            (PERCENTILE_COLORS['gray'][i] - PERCENTILE_COLORS['blue'][i]) * t 
            for i in range(3)
        )
    else:
        t = (pct - 50) / 50
        return tuple(
            PERCENTILE_COLORS['gray'][i] + 
            (PERCENTILE_COLORS['red'][i] - PERCENTILE_COLORS['gray'][i]) * t 
            for i in range(3)
        )