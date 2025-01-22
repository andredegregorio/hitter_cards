import pandas as pd
import numpy as np
from constants import BIP_EVENTS, SWING_CODE, WHIFF_CODE
from utils import get_filtered_game_logs

def calculate_xBA(df):
    '''
    Calculate expected batting average (xBA) for a given DataFrame of Statcast data.

    Args:
    - df (pd.DataFrame): A DataFrame containing Statcast data.

    Returns:
    - float: The expected batting average (xBA) for the given data.
    '''
    df = df.copy()

    # Filter balls in play (valid BIP events) where xBA is available
    balls_in_play = df[(df['events'].isin(BIP_EVENTS)) &  ~df['estimated_ba_using_speedangle'].isnull()]
    
    # Sum xBA for balls in play
    xBA_bip = balls_in_play['estimated_ba_using_speedangle'].sum() 
    
    # Count strikeouts (including strikeout_double_play)
    strikeouts = len(df[df['events'] == 'strikeout']) + len(df[df['events'] == 'strikeout_double_play'])

    # Total plate appearances (BIP + K)
    total_ab = len(balls_in_play) + strikeouts

    # Calculate xBA
    xBA = xBA_bip / total_ab if total_ab > 0 else 0

    return xBA

def calculate_xOBP(df):  # fix later, add IBB
    '''
    Calculate expected on-base percentage (xOBP) for a given DataFrame of Statcast data.

    Args:
    - df (pd.DataFrame): A DataFrame containing Statcast data.

    Returns:
    - float: The expected on-base percentage (xOBP) for the given data.
    '''
    df = df.copy()
    
    # Filter balls in play (valid BIP events) where xBA is available
    balls_in_play = df[(df['events'].isin(BIP_EVENTS)) & ~df['estimated_ba_using_speedangle'].isnull()]
    
    # Sum xHits for balls in play
    xHits = balls_in_play['estimated_ba_using_speedangle'].sum() 
    
    # Count strikeouts (including strikeout_double_play)
    strikeouts = len(df[df['events'] == 'strikeout']) + len(df[df['events'] == 'strikeout_double_play'])

    # Total at-bats (BIP + K)
    total_ab = len(balls_in_play) + strikeouts

    # Walks and hit by pitch
    walks = len(df[df['events'] == 'walk']) ## + intenional_walks
    hit_by_pitch = len(df[df['events'] == 'hit_by_pitch'])

    # Sacrifice flies
    sac_flies = len(df[df['events'] == 'sac_fly'])

    # Numerator: Expected hits + walks + HBP
    numerator = xHits + walks + hit_by_pitch

    # Denominator: Total at-bats + walks + HBP + sacrifice flies
    denominator = total_ab + walks + hit_by_pitch + sac_flies

    # Calculate xOBP
    xOBP = numerator / denominator if denominator > 0 else 0

    return xOBP

def calculate_xSLG(df):
    '''
    Calculate expected slugging percentage (xSLG) for a given DataFrame of Statcast data.

    Args:
    - df (pd.DataFrame): A DataFrame containing Statcast data.
    
    Returns:
    - float: The expected slugging percentage (xSLG) for the given data.
    '''
    df = df.copy()

    # Filter balls in play (valid BIP events) where xSLG is available
    balls_in_play = df[(df['events'].isin(BIP_EVENTS)) & ~df['estimated_slg_using_speedangle'].isnull()]
    
    # Sum xSLG for balls in play
    xSLG_bip = balls_in_play['estimated_slg_using_speedangle'].sum()
    
    # Count strikeouts (including strikeout_double_play)
    strikeouts = len(df[df['events'] == 'strikeout']) + len(df[df['events'] == 'strikeout_double_play'])

    # Total plate appearances (BIP + K)
    total_ab = len(balls_in_play) + strikeouts

    # Calculate xSLG
    xSLG = xSLG_bip / total_ab if total_ab > 0 else 0
    return xSLG

def calculate_xwOBA(df):
    '''
    Calculate expected weighted on-base average (xwOBA) for a given DataFrame of Statcast data.

    Args:
    - df (pd.DataFrame): A DataFrame containing Statcast data.

    Returns:
    - float: The expected weighted on-base average (xwOBA) for the given data.
    '''
    df = df.copy()

    # Define weights for walks and hit-by-pitch
    w_bb = 0.69  # Weight for walks (BB)
    w_hbp = 0.72  # Weight for hit by pitch (HBP)

    # Find sacrifice flies (SF) 
    sf = len(df[df['events'] == 'sac_fly'])
    
    # Filter for events with estimated wOBA using speedangle
    balls_in_play = df[(df['events'].isin(BIP_EVENTS)) & ~df['estimated_woba_using_speedangle'].isnull()]
    
    # Calculate the sum of estimated wOBA for valid BIP events
    xwoba_bip = balls_in_play['estimated_woba_using_speedangle'].sum()

    # Count strikeouts (including strikeout_double_play)
    strikeouts = len(df[df['events'] == 'strikeout']) + len(df[df['events'] == 'strikeout_double_play'])
    
    # Count walks (BB) and hit-by-pitch (HBP)
    bb = len(df[df['events'] == 'walk'])
    hbp = len(df[df['events'] == 'hit_by_pitch'])
    
    # Sum the contributions from BB and HBP to the numerator
    xwoba_numerator = (w_bb * bb) + (w_hbp * hbp) + xwoba_bip
    
    # Count total plate appearances (PA) (including BB, HBP, strikeouts, and BIP events)
    total_ab = len(balls_in_play) + strikeouts
    total_pa = total_ab + bb + sf + hbp
    
    # Calculate xwOBA
    xwOBA = xwoba_numerator / total_pa if total_pa > 0 else 0

    return xwOBA

def process_game_logs(df):
    """
    Processes game logs for a player and returns stat totals.
    
    Args:
        df (pd.DataFrame): A DataFrame containing game logs for a player.
        
    Returns:
        pd.DataFrame: A DataFrame containing the stat totals.
    """
    
    # Convert all columns to numeric
    df = df.apply(pd.to_numeric)
    
    # Initialize dictionary to hold stat totals
    stat_totals = {
        'G': df['G'].sum(), 'PA': df['PA'].sum(), 'AB': df['AB'].sum(), 'R': df['R'].sum(), 
        'H': df['H'].sum(), '2B': df['2B'].sum(), '3B': df['3B'].sum(),'HR': df['HR'].sum(),
        'RBI': df['RBI'].sum(),'HBP': df['HBP'].sum(),'IBB': df['IBB'].sum(), 'BB': df['BB'].sum(),
        'SO': df['SO'].sum(),'SB': df['SB'].sum(), 'CS': df['CS'].sum()
    }
    
    # Manually calculate AVG, OBP, SLG, and OPS
    stat_totals['AVG'] = stat_totals['H'] / stat_totals['AB'] if stat_totals['AB'] > 0 else 0
    stat_totals['OBP'] = (stat_totals['H'] + stat_totals['BB'] + stat_totals['HBP']) / (stat_totals['PA']) if stat_totals['PA'] > 0 else 0
    singles = stat_totals['H'] - stat_totals['2B'] - stat_totals['3B'] - stat_totals['HR']
    total_bases = singles + (2 * stat_totals['2B']) + (3 * stat_totals['3B']) + (4 * stat_totals['HR'])
    stat_totals['SLG'] = total_bases / stat_totals['AB'] if stat_totals['AB'] > 0 else 0
    stat_totals['OPS'] = stat_totals['OBP'] + stat_totals['SLG']
    stat_totals['K%'] = (stat_totals['SO'] / stat_totals['PA']) * 100 if stat_totals['PA'] > 0 else 0
    stat_totals['BB%'] = (stat_totals['BB'] / stat_totals['PA']) * 100 if stat_totals['PA'] > 0 else 0

    # Keep counting stats the same, AVG, OBP, SLG and OPS to 3 decimal places, K% and BB% to 1 decimal place
    for key, value in stat_totals.items():
        if key in ['AVG', 'OBP', 'SLG', 'OPS']:
            stat_totals[key] = f"{value:.3f}".lstrip('0')  # Remove leading zero
        elif key in ['K%', 'BB%']:
            stat_totals[key] = round(value, 1)
        else:
            stat_totals[key] = int(value)
            
    # Convert to DataFrame with one row
    stat_totals_df = pd.DataFrame([stat_totals])

    return stat_totals_df

def process_hitter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw Savant data and calculate advanced stats.

    Args:
    - df (pd.DataFrame): A DataFrame containing raw Savant data.

    Returns:
    - pd.DataFrame: A DataFrame containing cleaned stats for the hitter.
    """

    # Add derived columns
    df['ball_in_play'] = df['events'].isin(BIP_EVENTS)
    df['swing'] = df['description'].isin(SWING_CODE)
    df['whiff'] = df['description'].isin(WHIFF_CODE)
    df['in_zone'] = df['zone'] < 10
    df['out_zone'] = df['zone'] > 10
    df['chase'] = df['out_zone'] & df['swing']
    df['hard_hit'] = (df['launch_speed'] >= 95) & (df['ball_in_play'])
    df['ev90'] = df.loc[df['events'].isin(BIP_EVENTS), 'launch_speed'].quantile(0.9)
    df['max_ev'] = df.loc[df['events'].isin(BIP_EVENTS), 'launch_speed'].max()
    df['barrel'] = df.apply(lambda x: is_barrel(x['launch_speed'], x['launch_angle']), axis=1)
    df['sweet_spot'] = df['launch_angle'].apply(is_sweet_spot) & df['ball_in_play']

    # Calculate advanced stats
    zone_swing_rate = df[df['in_zone']]['swing'].mean()
    out_of_zone_swing_rate = df[df['out_zone']]['swing'].mean()
    whiff_rate = df['whiff'].sum() / df['swing'].sum()
    hard_hit_rate = df['hard_hit'].sum() / df['ball_in_play'].sum()
    barrel_rate = df[df['ball_in_play']]['barrel'].mean()
    sweet_spot_rate = df[df['ball_in_play']]['sweet_spot'].mean()

    # Advanced metrics
    xBA = calculate_xBA(df)
    xSLG = calculate_xSLG(df)
    xwOBA = calculate_xwOBA(df)

    # Assemble stats
    stats = {
        "Z-O Swing%": 100 * (zone_swing_rate - out_of_zone_swing_rate),
        "O-Swing%": out_of_zone_swing_rate * 100,
        "Z-Swing%": zone_swing_rate * 100,
        "Z-O Swing%": 100 * (zone_swing_rate - out_of_zone_swing_rate),
        "Whiff%": whiff_rate * 100,
        #"Max EV": df['max_ev'].values[0],
        "Sweet Spot%": sweet_spot_rate * 100,
        "Hard Hit%": hard_hit_rate * 100,
        "Barrel%": barrel_rate * 100,
        "EV90": df['ev90'].values[0],
        "xSLG": xSLG,
        "xBA": xBA,
        "xwOBA": xwOBA,
    }

    return pd.DataFrame([stats])
    
def is_sweet_spot(launch_angle) -> bool:
    '''
    Determine if a given launch angle is in the "sweet spot" range.

    Args:
    - launch_angle (float): The launch angle of the batted ball.

    Returns:
    - bool: True if the launch angle is in the "sweet spot" range, False otherwise.
    '''
    return 8 <= launch_angle < 32

def is_barrel(launch_speed, launch_angle) -> bool:
    '''
    Determine if a batted ball is a "barrel" based on launch speed and angle.

    Args:
    - launch_speed (float): The launch speed of the batted ball.
    - launch_angle (float): The launch angle of the batted ball.

    Returns:
    - bool: True if the batted ball is a "barrel", False otherwise.
    '''
    if launch_speed < 97.5:
        return False  # Below the minimum speed
    
    # Define bounds for specific launch speeds
    if 97.5 <= launch_speed < 98.5:
        lower_bound, upper_bound = 26, 30
    elif 98.5 <= launch_speed < 99.5:
        lower_bound, upper_bound = 25, 31
    elif 99.5 <= launch_speed < 100.5:
        lower_bound, upper_bound = 24, 33
    elif 100.5 <= launch_speed < 101.5:
        lower_bound, upper_bound = 23, 35
    elif 101.5 <= launch_speed < 102.5:
        lower_bound, upper_bound = 22, 36
    elif 102.5 <= launch_speed < 103.5:
        lower_bound, upper_bound = 21, 37
    elif 103.5 <= launch_speed < 104.5:
        lower_bound, upper_bound = 20, 38
    elif 104.5 <= launch_speed < 105.5:
        lower_bound, upper_bound = 19, 39
    elif 105.5 <= launch_speed < 106.5:
        lower_bound, upper_bound = 18, 40
    elif 106.5 <= launch_speed < 107.5:
        lower_bound, upper_bound = 17, 41
    elif 107.5 <= launch_speed < 108.5:
        lower_bound, upper_bound = 16, 42
    elif 108.5 <= launch_speed < 109.5:
        lower_bound, upper_bound = 15, 43
    elif 109.5 <= launch_speed < 110.5:
        lower_bound, upper_bound = 14, 44
    elif 110.5 <= launch_speed < 111.5:
        lower_bound, upper_bound = 13, 45
    elif 111.5 <= launch_speed < 112.5:
        lower_bound, upper_bound = 12, 46
    elif 112.5 <= launch_speed < 113.5:
        lower_bound, upper_bound = 11, 47
    elif 113.5 <= launch_speed < 114.5:
        lower_bound, upper_bound = 10, 48
    elif 114.5 <= launch_speed < 115.5:
        lower_bound, upper_bound = 9, 49
    elif launch_speed >= 115.5:
        lower_bound, upper_bound = 8, 50
    else:
        return False  # Catch unexpected cases
    
    # Ensure strict bounds
    return lower_bound <= launch_angle <= upper_bound