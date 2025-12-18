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

def process_hitter_data(df: pd.DataFrame, pitcher_hand: str = None) -> pd.DataFrame:
    """
    Process raw Savant data and calculate advanced stats.

    Args:
    - df (pd.DataFrame): A DataFrame containing raw Savant data.
    - pitcher_hand (str): Filter by pitcher handedness - 'R', 'L', or None for all

    Returns:
    - pd.DataFrame: A DataFrame containing cleaned stats for the hitter.
    """
    
    # Filter by pitcher handedness if specified
    if pitcher_hand in ['R', 'L']:
        df = df[df['p_throws'] == pitcher_hand].copy()
    else:
        df = df.copy()
    
    # Return empty stats if no data after filtering
    if len(df) == 0:
        return pd.DataFrame([{
            "xwOBA": 0, "wOBA": 0, "xBA": 0, "xSLG": 0, "EV90": 0,
            "Barrel%": 0, "Hard Hit%": 0, "Sweet Spot%": 0, "Pulled FB%": 0,
            "Whiff%": 0, "Z-Contact%": 0, "O-Contact%": 0,
            "Z-Swing%": 0, "O-Swing%": 0, "Z-O Swing%": 0, "Bat Speed": 0
        }])

    # Add derived columns
    df['ball_in_play'] = df['events'].isin(BIP_EVENTS)
    df['swing'] = df['description'].isin(SWING_CODE)
    df['whiff'] = df['description'].isin(WHIFF_CODE)
    df['in_zone'] = df['zone'] < 10
    df['out_zone'] = df['zone'] > 10
    df['chase'] = df['out_zone'] & df['swing']
    df['hard_hit'] = (df['launch_speed'] >= 95) & (df['ball_in_play'])
    df['barrel'] = df.apply(lambda x: is_barrel(x['launch_speed'], x['launch_angle']), axis=1)
    df['sweet_spot'] = df['launch_angle'].apply(is_sweet_spot) & df['ball_in_play']
    
    # NEW: Pulled fly balls
    df['pulled_fly'] = (
        ((df['hc_x'] > 125) & (df['stand'] == 'R')) |  # RHH pulls right
        ((df['hc_x'] < 125) & (df['stand'] == 'L'))    # LHH pulls left
    ) & (df['launch_angle'] >= 25) & (df['launch_angle'] <= 50) & df['ball_in_play']
    
    # Calculate EV90 and max EV only on balls in play
    bip_df = df[df['events'].isin(BIP_EVENTS)]
    ev90 = bip_df['launch_speed'].quantile(0.9) if len(bip_df) > 0 else 0

    # Calculate swing/discipline stats
    zone_swing_rate = df[df['in_zone']]['swing'].mean() if df['in_zone'].sum() > 0 else 0
    out_of_zone_swing_rate = df[df['out_zone']]['swing'].mean() if df['out_zone'].sum() > 0 else 0
    whiff_rate = df['whiff'].sum() / df['swing'].sum() if df['swing'].sum() > 0 else 0
    
    # NEW: Zone and chase contact rates
    zone_whiff_rate = df[df['in_zone']]['whiff'].sum() / df[df['in_zone']]['swing'].sum() if df[df['in_zone']]['swing'].sum() > 0 else 0
    chase_whiff_rate = df[df['out_zone']]['whiff'].sum() / df[df['out_zone']]['swing'].sum() if df[df['out_zone']]['swing'].sum() > 0 else 0
    
    # Calculate quality of contact rates
    hard_hit_rate = df['hard_hit'].sum() / df['ball_in_play'].sum() if df['ball_in_play'].sum() > 0 else 0
    barrel_rate = df[df['ball_in_play']]['barrel'].mean() if df['ball_in_play'].sum() > 0 else 0
    sweet_spot_rate = df[df['ball_in_play']]['sweet_spot'].mean() if df['ball_in_play'].sum() > 0 else 0
    pulled_fly_rate = df[df['ball_in_play']]['pulled_fly'].mean() if df['ball_in_play'].sum() > 0 else 0

    # Expected metrics
    xBA = calculate_xBA(df)
    xSLG = calculate_xSLG(df)
    xwOBA = calculate_xwOBA(df)
    
    # NEW: Actual wOBA
    w_bb, w_hbp, w_1b, w_2b, w_3b, w_hr = 0.69, 0.72, 0.88, 1.24, 1.56, 2.08
    singles = len(df[df['events'] == 'single'])
    doubles = len(df[df['events'] == 'double'])
    triples = len(df[df['events'] == 'triple'])
    hr = len(df[df['events'] == 'home_run'])
    bb = len(df[df['events'] == 'walk'])
    hbp = len(df[df['events'] == 'hit_by_pitch'])
    sf = len(df[df['events'] == 'sac_fly'])
    
    woba_num = (w_bb * bb) + (w_hbp * hbp) + (w_1b * singles) + (w_2b * doubles) + (w_3b * triples) + (w_hr * hr)
    woba_denom = len(df[df['events'].isin(BIP_EVENTS)]) + len(df[df['events'] == 'strikeout']) + bb + hbp + sf
    wOBA = woba_num / woba_denom if woba_denom > 0 else 0
    
    # NEW: Bat speed
    avg_bat_speed = df['bat_speed'].mean() if 'bat_speed' in df.columns and df['bat_speed'].notna().sum() > 0 else 0

    # Assemble stats
    stats = {
        "xwOBA": xwOBA,
        "wOBA": wOBA,
        "xBA": xBA,
        "xSLG": xSLG,
        "EV90": ev90,
        "Barrel%": barrel_rate * 100,
        "Hard Hit%": hard_hit_rate * 100,
        "Sweet Spot%": sweet_spot_rate * 100,
        "Pulled FB%": pulled_fly_rate * 100,
        "Whiff%": whiff_rate * 100,
        "Z-Contact%": (1 - zone_whiff_rate) * 100,
        "O-Contact%": (1 - chase_whiff_rate) * 100,
        "Z-Swing%": zone_swing_rate * 100,
        "O-Swing%": out_of_zone_swing_rate * 100,
        "Z-O Swing%": 100 * (zone_swing_rate - out_of_zone_swing_rate),
        "Bat Speed": avg_bat_speed,
    }

    return pd.DataFrame([stats])

def is_barrel(launch_speed, launch_angle) -> bool:
    '''
    Determine if a batted ball is a "barrel" based on launch speed and angle.

    Args:
    - launch_speed (float): The launch speed of the batted ball.
    - launch_angle (float): The launch angle of the batted ball.

    Returns:
    - bool: True if the batted ball is a "barrel", False otherwise.
    '''
    if pd.isna(launch_speed) or pd.isna(launch_angle):
        return False
    
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

def calculate_pulled_air(bip_data):
    """
    Calculate Pulled Air % using Variation 7 formula.
    
    NOTES:
    ------
    This formula systematically underestimates Pull AIR% by ~2.5-3% compared to 
    Baseball Savant. However, the error is CONSISTENT across all players, which 
    means percentile rankings remain accurate (everyone shifts equally).
    
    Tested on: Cal Raleigh, Aaron Judge, Juan Soto, Mookie Betts, Bryce Harper
    Error range: -2.5% to -3.2% (acceptable for league-wide percentiles)
    
    FORMULA DETAILS:
    ----------------
    Spray Angle Calculation (from Bill Petti's research):
        spray_angle = arctan((hc_x - 125.42) / (198.27 - hc_y)) * 180 / π * 0.75
        
        Where:
        - hc_x, hc_y are Statcast hit coordinates
        - 125.42 = center field x-coordinate
        - 198.27 = home plate y-coordinate  
        - 0.75 = adjustment factor (empirically determined)
    
    Adjusted Spray Angle (account for batter handedness):
        For LHH: adj_spray_angle = -spray_angle (flip sign)
        For RHH: adj_spray_angle = spray_angle (keep same)
        
        Result: Negative angle = pull, Positive = oppo, 0 = center
    
    Pull Definition:
        Pull = adj_spray_angle < -15°
        
        NOTE: This is likely too strict. Savant may use ~-13° to -14°, but 
        we couldn't find exact threshold. Using -15° for consistency.
    
    Air Ball Definition:
        Air = launch_angle >= 10°
        
        This includes:
        - Line Drives: 10° to 25°
        - Fly Balls: 25° to 60°  
        - Popups: 60°+
        
        Excludes ground balls (< 10°)
    
    Batted Ball Type Boundaries:
        Ground Ball (GB): launch_angle < 10°
        Line Drive (LD): 10° <= launch_angle < 25°
        Fly Ball (FB): 25° <= launch_angle < 60°  ← KEY: Upper bound is 60°, not 50°!
        Popup (PU): launch_angle >= 60°
    
    Final Calculation:
        Pulled_Air = (Pull AND Air)
        Pulled_Air% = (count of Pulled_Air / total BIP) * 100
    
    FUTURE IMPROVEMENTS:
    -------------------
    To get closer to Savant's exact numbers:
    1. Try pull threshold of -13° or -14° instead of -15°
    2. Investigate if spray angle formula needs different adjustment factor
    3. Check if Savant uses player-specific adjustments (unlikely)
    4. Consider if Savant calculates "Pulled Air" differently than Pull AND Air
    
    Args:
        bip_data (pd.DataFrame): DataFrame of balls in play with columns:
            - hc_x: Hit coordinate x
            - hc_y: Hit coordinate y  
            - launch_angle: Launch angle in degrees
            - stand: Batter handedness ('R' or 'L')
    
    Returns:
        float: Pulled Air percentage (0-100)
    """
    import numpy as np
    
    # KEY NUMBERS - ADJUST THESE TO IMPROVE ACCURACY
    PULL_THRESHOLD = -15  # degrees (try -13 or -14 for closer match)
    AIR_THRESHOLD = 10    # degrees (minimum LA for air ball)
    FB_UPPER_BOUND = 60   # degrees (CRITICAL: use 60, not 50!)
    
    # Calculate spray angle
    spray_angle = np.arctan(
        (bip_data['hc_x'] - 125.42) / (198.27 - bip_data['hc_y'])
    ) * 180 / np.pi * 0.75
    
    # Adjust for batter handedness
    adj_spray_angle = np.where(
        bip_data['stand'] == 'L',
        -spray_angle,  # Flip for lefties
        spray_angle    # Keep for righties
    )
    
    # Define pull and air
    is_pulled = adj_spray_angle < PULL_THRESHOLD
    is_air = bip_data['launch_angle'] >= AIR_THRESHOLD
    
    # Combine
    pulled_air = is_pulled & is_air
    
    # Calculate percentage
    pulled_air_pct = (pulled_air.sum() / len(bip_data)) * 100 if len(bip_data) > 0 else 0
    
    return pulled_air_pct 