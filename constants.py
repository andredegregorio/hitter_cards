# Season info
CURRENT_SEASON = 2024

# Opening and closing dates for each season
SEASON_DATES = {
    2025: {
        'REG_START': '2025-03-27',
        'REG_END': '2025-09-28',
        'POST_START': '2025-09-30',
        'POST_END': '2025-11-10',
        'SPRING_START': '2025-02-10',
        'SPRING_END': '2025-03-26',
        'FH_START': '2025-03-27',
        'FH_END': '2025-07-13',
        'SH_START': '2025-07-17',
        'SH_END': '2025-09-28'
    },
    2024: {
        'REG_START': '2024-03-28',
        'REG_END': '2024-09-30',
        'POST_START': '2024-10-01',
        'POST_END': '2024-11-10',
        'SPRING_START': '2024-02-10',
        'SPRING_END': '2024-03-27',
        'FH_START': '2024-03-28',
        'FH_END': '2024-07-14',
        'SH_START': '2024-07-18',
        'SH_END': '2024-09-30'
    },
    2023: {
        'REG_START': '2023-03-30',
        'REG_END': '2023-10-01',
        'POST_START': '2023-10-03',
        'POST_END': '2023-11-10',
        'SPRING_START': '2023-02-10',
        'SPRING_END': '2023-03-28',
        'FH_START': '2023-03-30',
        'FH_END': '2023-07-09',
        'SH_START': '2023-07-13',
        'SH_END': '2023-10-01'
    },
    2022: {
        'REG_START': '2022-04-07',
        'REG_END': '2022-10-05',
        'POST_START': '2022-10-06',
        'POST_END': '2022-11-15',
        'SPRING_START': '2022-02-23',
        'SPRING_END': '2022-04-06',
        'FH_START': '2022-04-07',
        'FH_END': '2022-07-14',
        'SH_START': '2022-07-18',
        'SH_END': '2022-10-05'
    },
    2021: {
        'REG_START': '2021-04-01',
        'REG_END': '2021-10-03',
        'POST_START': '2021-10-04',
        'POST_END': '2021-11-15',
        'SPRING_START': '2021-02-23',
        'SPRING_END': '2021-03-31',
        'FH_START': '2021-04-01',
        'FH_END': '2021-07-11',
        'SH_START': '2021-07-15',
        'SH_END': '2021-10-03'
    },
    2020: {
        'REG_START': '2020-07-23',
        'REG_END': '2020-09-27',
        'POST_START': '2020-09-28',
        'POST_END': '2020-11-10',
        'SPRING_START': '2020-02-23',
        'SPRING_END': '2020-07-22'
    },
    2019: {
        'REG_START': '2019-03-28',
        'REG_END': '2019-09-29',
        'POST_START': '2019-10-01',
        'POST_END': '2019-11-01',
        'SPRING_START': '2019-02-23',
        'SPRING_END': '2019-03-27',
        'FH_START': '2019-03-28',
        'FH_END': '2019-07-07',
        'SH_START': '2019-07-11',
        'SH_END': '2019-09-29'
    },
    2018: {
        'REG_START': '2018-03-29',
        'REG_END': '2018-10-01',
        'POST_START': '2018-10-02',
        'POST_END': '2018-11-15',
        'SPRING_START': '2018-02-23',
        'SPRING_END': '2018-03-28',
        'FH_START': '2018-03-29',
        'FH_END': '2018-07-15',
        'SH_START': '2018-07-19',
        'SH_END': '2018-10-01'
    },
    2017: {
        'REG_START': '2017-04-02',
        'REG_END': '2017-10-01',
        'POST_START': '2017-10-02',
        'POST_END': '2017-11-10',
        'SPRING_START': '2017-02-23',
        'SPRING_END': '2017-04-01',
        'FH_START': '2017-04-02',
        'FH_END': '2017-07-09',
        'SH_START': '2017-07-13',
        'SH_END': '2017-10-01'
    }
}


# API endpoints
MLB_API_URL = 'https://statsapi.mlb.com/api/v1/people'
FANGRAPHS_API_URL = 'https://www.fangraphs.com/leaders.aspx'
SAVANT_API_URL = 'https://baseballsavant.mlb.com/api'

# Events
BIP_EVENTS = [
    'field_out', 'single', 'double', 'triple', 'home_run', 'field_error', 
    'force_out', 'grounded_into_double_play', 'triple_play', 'fielders_choice', 'fielders_choice_out',
    'sac_fly_double_play', 'sac_bunt_double_play', 'double_play', 'sac_fly', 'sac_bunt'
]
SWING_CODE = ['foul', 'hit_into_play', 'swinging_strike', 'foul_tip', 'swinging_strike_blocked', 'foul_bunt']
WHIFF_CODE = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked']

# Baseball Savant percentile colors (RGB values)
PERCENTILE_COLORS = {
    'blue': (50/255, 90/255, 161/255),   # #325aa1 (1st percentile)
    'gray': (180/255, 207/255, 209/255), # #b4cfd1 (50th percentile)
    'red': (216/255, 33/255, 41/255)     # #d82129 (100th percentile)
}

# Team primary colors
TEAM_COLORS = {
    '109': '#A71930',  # ARI
    '144': '#CE1141',  # ATL
    '110': '#DF4601',  # BAL
}




# API endpoints
MLB_API_URL = 'https://statsapi.mlb.com/api/v1/people'
FANGRAPHS_API_URL = 'https://www.fangraphs.com/leaders.aspx'
SAVANT_API_URL = 'https://baseballsavant.mlb.com/api'

# Events
BIP_EVENTS = [
    'field_out', 'single', 'double', 'triple', 'home_run', 'field_error', 
    'force_out', 'grounded_into_double_play', 'triple_play', 'fielders_choice', 'fielders_choice_out',
    'sac_fly_double_play', 'sac_bunt_double_play', 'double_play', 'sac_fly', 'sac_bunt'
    ]
SWING_CODE = ['foul', 'hit_into_play', 'swinging_strike', 'foul_tip', 'swinging_strike_blocked', 'foul_bunt']
WHIFF_CODE = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked']

# Baseball Savant percentile colors (RGB values)
PERCENTILE_COLORS = {
    'blue': (50/255, 90/255, 161/255),   # #325aa1 (1st percentile)
    'gray': (180/255, 207/255, 209/255), # #b4cfd1 (50th percentile)
    'red': (216/255, 33/255, 41/255)     # #d82129 (100th percentile)
}
# Team primary colors
TEAM_COLORS = {
    '109': '#A71930',  # ARI
    '144': '#CE1141',  # ATL
    '110': '#DF4601',  # BAL
    '111': '#BD3039',  # BOS
    '112': '#0E3386',  # CHC
    '145': '#27251F',  # CWS
    '113': '#C6011F',  # CIN
    '114': '#00385D',  # CLE
    '115': '#333366',  # COL
    '116': '#0C2340',  # DET
    '117': '#EB6E1F',  # HOU
    '118': '#004687',  # KC
    '108': '#BA0021',  # LAA
    '119': '#005A9C',  # LAD
    '146': '#00A3E0',  # MIA
    '158': '#12284B',  # MIL
    '142': '#002B5C',  # MIN
    '121': '#002D72',  # NYM
    '147': '#003087',  # NYY
    '133': '#003831',  # OAK
    '143': '#E81828',  # PHI
    '134': '#27251F',  # PIT
    '135': '#2F241D',  # SD
    '137': '#FD5A1E',  # SF
    '136': '#0C2C56',  # SEA
    '138': '#C41E3A',  # STL
    '139': '#092C5C',  # TB
    '140': '#003278',  # TEX
    '141': '#134A8E',  # TOR
    '120': '#AB0003'   # WSH
}

# MLB Team Logo ESPN URLs
MLB_TEAM_LOGOS = {
    "AZ": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/ari.png&h=500&w=500",
    "ATL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/atl.png&h=500&w=500",
    "BAL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bal.png&h=500&w=500",
    "BOS": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bos.png&h=500&w=500",
    "CHC": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chc.png&h=500&w=500",
    "CWS": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chw.png&h=500&w=500",
    "CIN": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cin.png&h=500&w=500",
    "CLE": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cle.png&h=500&w=500",
    "COL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/col.png&h=500&w=500",
    "DET": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/det.png&h=500&w=500",
    "HOU": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/hou.png&h=500&w=500",
    "KC": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/kc.png&h=500&w=500",
    "LAA": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/laa.png&h=500&w=500",
    "LAD": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/lad.png&h=500&w=500",
    "MIA": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mia.png&h=500&w=500",
    "MIL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mil.png&h=500&w=500",
    "MIN": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/min.png&h=500&w=500",
    "NYM": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nym.png&h=500&w=500",
    "NYY": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nyy.png&h=500&w=500",
    "OAK": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/oak.png&h=500&w=500",
    "PHI": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/phi.png&h=500&w=500",
    "PIT": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/pit.png&h=500&w=500",
    "SD": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sd.png&h=500&w=500",
    "SF": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sf.png&h=500&w=500",
    "SEA": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sea.png&h=500&w=500",
    "STL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/stl.png&h=500&w=500",
    "TB": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tb.png&h=500&w=500",
    "TEX": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tex.png&h=500&w=500",
    "TOR": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tor.png&h=500&w=500",
    "WSH": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/wsh.png&h=500&w=500"
}

# Dropped columns for savant pitch-by-pitch data
droppable = [
    'release_pos_x','release_pos_z','player_name','batter','pitcher',
    'spin_dir','spin_rate_deprecated','break_angle_deprecated',
    'break_length_deprecated','stand','home_team','away_team','pfx_x','pfx_z',
    'on_3b','on_2b','on_1b','outs_when_up','inning','inning_topbot',
    'tfs_deprecated','tfs_zulu_deprecated','umpire','fielder_2','fielder_3','fielder_4',
    'fielder_5','fielder_6','fielder_7','fielder_8','fielder_9',
    'age_pit_legacy','age_bat_legacy','age_pit', 'age_bat',
    'n_thruorder_pitcher', 'n_priorpa_thisgame_player_at_bat',
    'pitcher_days_since_prev_game', 'batter_days_since_prev_game',
    'pitcher_days_until_next_game', 'batter_days_until_next_game',
    'api_break_z_with_gravity', 'api_break_x_arm', 'api_break_x_batter_in','arm_angle',
    'home_score_diff','home_win_exp', 'bat_win_exp', 'of_fielding_alignment','spin_axis',
    'delta_home_win_exp', 'delta_run_exp', 'if_fielding_alignment','of_fielding_alignment',
    'delta_pitcher_run_exp','bat_score_diff', 'bat_score', 'fld_score', 
    'post_away_score','post_home_score','post_bat_score','post_fld_score','home_score',
    'away_score', 'balls', 'strikes', 'game_year', 'release_extension', 'release_spin_rate',
    'ax', 'ay', 'az', 'vx0', 'vy0', 'vz0', 'hyper_speed'
]