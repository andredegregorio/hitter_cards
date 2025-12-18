"""
Generate league-wide statistics CSVs for percentile calculations.
Creates clean2024.csv and clean2025.csv in the data/ folder.
"""

import pandas as pd
import numpy as np
import pybaseball as pyb
from tqdm import tqdm
from data_processing import process_hitter_data
from utils import get_savant_data
from constants import SEASON_DATES

def calculate_custom_stats(player_id, start_date, end_date):
    """
    Calculate custom stats not available in Fangraphs leaderboards.
    
    Args:
        player_id (int): MLB player ID
        start_date (str): Start date
        end_date (str): End date
        
    Returns:
        dict: Custom stats (Pulled FB%, EV90, Bat Speed, Sweet Spot%)
    """
    try:
        # Fetch raw Statcast data
        raw_data = get_savant_data(player_id, start_date, end_date)
        
        if raw_data is None or len(raw_data) == 0:
            return None
        
        # Filter for balls in play
        from constants import BIP_EVENTS
        bip_data = raw_data[raw_data['events'].isin(BIP_EVENTS)].copy()
        
        if len(bip_data) == 0:
            return None
        
        # Calculate Pulled FB%
        bip_data['pulled_fly'] = (
            ((bip_data['hc_x'] > 125) & (bip_data['stand'] == 'R')) |
            ((bip_data['hc_x'] < 125) & (bip_data['stand'] == 'L'))
        ) & (bip_data['launch_angle'] >= 25) & (bip_data['launch_angle'] <= 50)
        
        pulled_fb_rate = bip_data['pulled_fly'].mean() * 100 if len(bip_data) > 0 else 0
        
        # Calculate EV90
        ev90 = bip_data['launch_speed'].quantile(0.9) if len(bip_data) > 0 else 0
        
        # Calculate Sweet Spot%
        bip_data['sweet_spot'] = (bip_data['launch_angle'] >= 8) & (bip_data['launch_angle'] < 32)
        sweet_spot_rate = bip_data['sweet_spot'].mean() * 100 if len(bip_data) > 0 else 0
        
        # Calculate Bat Speed (2024+ only)
        bat_speed = raw_data['bat_speed'].mean() if 'bat_speed' in raw_data.columns and raw_data['bat_speed'].notna().sum() > 0 else 0
        
        return {
            'Pulled FB%': pulled_fb_rate,
            'EV90': ev90,
            'Sweet Spot%': sweet_spot_rate,
            'Bat Speed': bat_speed
        }
        
    except Exception as e:
        return None

def generate_league_stats(season):
    """
    Generate league-wide statistics for a given season.
    
    Args:
        season (int): The season year (2024 or 2025)
    
    Returns:
        pd.DataFrame: DataFrame with all players' stats
    """
    print(f"\n{'='*60}")
    print(f"Generating league stats for {season}")
    print(f"{'='*60}\n")
    
    # Get date range for the season
    start_date = SEASON_DATES[season]['REG_START']
    end_date = SEASON_DATES[season]['REG_END']
    
    print(f"Date range: {start_date} to {end_date}")
    
    # Step 1: Get Fangraphs leaderboard (has most stats)
    print("\nFetching Fangraphs leaderboard...")
    fg_stats = pyb.batting_stats(season, qual=340)
    print(f"Found {len(fg_stats)} qualified players")
    
    # Step 2: Select only the columns we need from Fangraphs
    fg_columns = [
        'IDfg', 'Name', 'Team', 'PA',
        'wOBA', 'xwOBA', 'xBA', 'xSLG',
        'Barrel%', 'HardHit%',
        'O-Contact%', 'Z-Contact%',
        'O-Swing%', 'Z-Swing%',
        'SwStr%'  # Will rename to Whiff%
    ]
    
    league_df = fg_stats[fg_columns].copy()
    
    # Rename SwStr% to Whiff%
    league_df = league_df.rename(columns={'SwStr%': 'Whiff%'})
    
    # Calculate Z-O Swing% from existing columns
    league_df['Z-O Swing%'] = league_df['Z-Swing%'] - league_df['O-Swing%']
    
    # Step 3: Convert Fangraphs IDs to MLB IDs for Statcast lookup
    print("\nConverting Fangraphs IDs to MLB IDs...")
    mlb_ids = []
    
    for idx, row in tqdm(league_df.iterrows(), total=len(league_df), desc="ID conversion"):
        fg_id = row['IDfg']
        try:
            id_map = pyb.playerid_reverse_lookup([fg_id], key_type='fangraphs')
            if not id_map.empty and 'key_mlbam' in id_map.columns:
                mlb_id = id_map['key_mlbam'].iloc[0]
                if pd.notna(mlb_id):
                    mlb_ids.append(int(mlb_id))
                else:
                    mlb_ids.append(None)
            else:
                mlb_ids.append(None)
        except:
            mlb_ids.append(None)
    
    league_df['player_id'] = mlb_ids
    
    # Remove players without MLB IDs
    league_df = league_df[league_df['player_id'].notna()].copy()
    print(f"Successfully mapped {len(league_df)} players to MLB IDs")
    
    # Step 4: Calculate custom stats from Statcast
    print("\nCalculating custom stats from Statcast...")
    custom_stats_list = []
    failed_count = 0
    
    for idx, row in tqdm(league_df.iterrows(), total=len(league_df), desc="Processing players"):
        player_id = int(row['player_id'])
        custom_stats = calculate_custom_stats(player_id, start_date, end_date)
        
        if custom_stats is None:
            failed_count += 1
            custom_stats = {
                'Pulled FB%': 0,
                'EV90': 0,
                'Sweet Spot%': 0,
                'Bat Speed': 0
            }
        
        custom_stats_list.append(custom_stats)
    
    # Step 5: Merge custom stats with Fangraphs stats
    custom_df = pd.DataFrame(custom_stats_list)
    league_df = pd.concat([league_df.reset_index(drop=True), custom_df], axis=1)
    
    # Step 6: Split Name into first_name and last_name
    league_df['first_name'] = league_df['Name'].apply(lambda x: x.split()[0] if ' ' in x else x)
    league_df['last_name'] = league_df['Name'].apply(lambda x: x.split()[-1] if ' ' in x else '')
    
    # Add year column
    league_df['year'] = season
    
    # Step 7: Reorder columns
    id_cols = ['last_name', 'first_name', 'player_id', 'year', 'PA']
    stat_cols = [col for col in league_df.columns if col not in id_cols + ['IDfg', 'Name', 'Team']]
    league_df = league_df[id_cols + stat_cols]
    
    print(f"\nFinal dataset: {len(league_df)} players")
    if failed_count > 0:
        print(f"Warning: {failed_count} players had missing Statcast data (filled with zeros)")
    
    return league_df

def main():
    """Main function to generate CSVs for both seasons."""
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    # Generate stats for each season
    for season in [2024, 2025]:
        try:
            # Generate the stats
            league_stats = generate_league_stats(season)
            
            # Save to CSV
            output_file = f'data/clean{season}.csv'
            league_stats.to_csv(output_file, index=False)
            
            print(f"\n✅ Successfully saved {output_file}")
            print(f"   Shape: {league_stats.shape}")
            print(f"   Columns: {list(league_stats.columns)}")
            
        except Exception as e:
            print(f"\n❌ Error processing {season}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("League stats generation complete!")
    print("="*60)

if __name__ == "__main__":
    main()