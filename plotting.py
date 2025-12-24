from utils import *
from data_processing import *
from constants import PERCENTILE_COLORS
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from scipy.stats import percentileofscore
import numpy as np
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec


def plot_headshot(player_id: int, ax: plt.Axes):
    """
    Fetches and plots the player's headshot image on the given axes.

    Args:
    - player_id (int): The unique player ID.
    - ax (plt.Axes): The Matplotlib axes on which to plot the image.
    """
    # Get the headshot image using the player ID
    img = get_headshot(player_id)
    
    # Plot the image on the provided axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.imshow(img, extent=[0, 1, 0, 1], origin='upper')
    ax.axis('off')

def plot_player_bio(player_id: str, ax: plt.Axes):
    """
    Fetches player bio data and plots it on the given axes.
    
    Args:
    - player_id (str): The unique player ID.
    - ax (plt.Axes): The Matplotlib axes on which to plot the bio information.
    """
    # Get player bio data
    player_data = get_player_bio(player_id)

    # Plot player bio data - INCREASED SIZES
    ax.text(0.5, 0.65, f'{player_data["primary_position"]} {player_data["player_name"]}',
            va='bottom', ha='center', fontsize=65, fontweight='bold')
    ax.text(0.5, 0.325, f'{player_data["team"]}', va='bottom', ha='center', fontsize=42)
    ax.text(0.5, 0, f'B/T: {player_data["batting_hand"]}/{player_data["throwing_hand"]} | {player_data["height"]}/{player_data["weight"]} | Age: {player_data["age"]}',
            va='bottom', ha='center', fontsize=40)
    
    ax.axis('off')

def plot_team_logo(player_id: str, ax: plt.Axes):
    """
    Fetches and displays the logo of a player's current MLB team on a given Matplotlib axis.

    Args:
        player_id (str): The player's MLB ID.
        ax (plt.Axes): Matplotlib axis to display the logo on.
    """
    # Get the team logo
    img = get_team_logo(player_id)
    
    if img:
        # Plot the team logo if it was successfully fetched
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.imshow(img, extent=[0, 1, 0, 1], origin='upper')
        ax.axis('off')  # Disable the axis for a clean look
    else:
        print("Failed to fetch team logo.")

def plot_timeframe(game_type: str = None, start_date: str = None, end_date: str = None, 
                   season: int = 2024, ax: plt.Axes = None):
    """
    Plots the timeframe label on the given Axes.

    Args:
        game_type (str): The type of game (e.g., 'regular', 'postseason').
        start_date (str): The start date of the timeframe.
        end_date (str): The end date of the timeframe.
        season (int): The season of the timeframe.
        ax (plt.Axes): The Matplotlib axes on which to plot the label.
    """
    # Generate the timeframe label
    timeframe_label = get_timeframe(game_type, start_date, end_date, season)

    # Plot the label
    ax.text(
        0.5, 0.5, timeframe_label,
        ha='center', va='center', fontsize=38,
    )
    ax.axis('off')

def plot_std_stats(player_id, start_dt, end_dt, season, ax, game_type = 'R'):
    """
    Plots a table of selected stats from the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the stats.
        ax (matplotlib.axes.Axes): Axis to plot the table on.
        stats_to_plot (list): List of stats to include in the table.
        
    Returns:
        matplotlib.axes.Axes: The axis with the plotted table.
    """
    # Define stats to plot
    stats_to_plot = ['PA', 'R', 'HR', 'RBI', 'SB','AVG', 'OBP', 'SLG', 'OPS', 'K%', 'BB%']

    # Get game logs
    data = get_filtered_game_logs(player_id, start_dt, end_dt, season, game_type)

    # Process game logs
    df = process_game_logs(data)

    # Filter DataFrame
    df = df[stats_to_plot]
    
    # Create table
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', bbox=[0.0, 0.0, 1.0, 1.0])
    
    # Set font size - INCREASED
    table.set_fontsize(32)
    table.auto_set_font_size(False)
    
    # Make column headers bold
    for i, cell in table.get_celld().items():
        if i[0] == 0:
            cell.set_text_props(weight='bold')
    
    # Hide the axes
    ax.axis('off')
    
    return ax

def plot_percentiles(player_id: int, start_dt: str, end_dt: str, season: int, ax: plt.Axes, pitcher_hand: str = None):
    """
    Plot percentile bars for a player's stats.
    
    Args:
        player_id: MLB player ID
        start_dt: Start date
        end_dt: End date
        season: Season year
        ax: Matplotlib axis to plot on
        pitcher_hand: 'L' for vs LHP, 'R' for vs RHP, None for all pitchers
    """
    # Fetch and process player data
    raw_data = get_savant_data(player_id, start_dt, end_dt)
    processed_data = process_hitter_data(raw_data, pitcher_hand=pitcher_hand)

    # Convert processed data to a dictionary for percentile calculation
    player_stats = processed_data.iloc[0].to_dict()

    # Define metrics in display order (top to bottom on card)
    # Bat Speed between Hard Hit% and Sweet Spot%
    # Z-Contact%, O-Contact% at the bottom
    metrics = ['xwOBA', 'xBA', 'xSLG', 'EV90', 'Barrel%', 'Hard Hit%', 
               'Bat Speed', 'Sweet Spot%', 'Whiff%', 'Z-Swing%', 'O-Swing%', 
               'Z-O Swing%', 'Z-Contact%', 'O-Contact%']
    
    # Reverse so xwOBA appears at TOP (highest y position)
    metrics = metrics[::-1]

    # Define metrics where lower is better
    lower_is_better = ['Whiff%', 'O-Swing%']
    
    # Metrics that might be stored as decimals in league CSV but percentages in player stats
    pct_metrics = ['Whiff%', 'Z-Swing%', 'O-Swing%', 'Z-O Swing%', 'Z-Contact%', 'O-Contact%', 
                   'Barrel%', 'Hard Hit%', 'Sweet Spot%', 'Pulled FB%']
    
    # Load league stats
    league_stats = pd.read_csv(f'data/clean{season}.csv')

    # Calculate percentiles
    percentiles = {}
    for metric in metrics:
        if metric not in league_stats.columns:
            percentiles[metric] = 50  # Default to 50th percentile if missing
            continue
        
        league_values = league_stats[metric].copy()
        
        # Check if league values are in decimal form (max < 1.5) while player values are percentages
        # If so, multiply league values by 100 to match
        if metric in pct_metrics and league_values.max() < 1.5:
            league_values = league_values * 100

        # Calculate raw percentile
        raw_percentile = percentileofscore(league_values, player_stats[metric], kind='mean')
        adjusted_percentile = max(1, raw_percentile)  # Ensure at least 1st percentile

        # Adjust for "lower is better" metrics
        if metric in lower_is_better:
            adjusted_percentile = max(1, 100 - adjusted_percentile)
        percentiles[metric] = adjusted_percentile

    y_pos = np.arange(len(metrics))
    
    # Settings
    BAR_HEIGHT = 0.65
    CIRCLE_SIZE = 1800

    # Plot bars and circles
    for i, metric in enumerate(metrics):
        pct = percentiles[metric]
        value = player_stats[metric]
        color = get_savant_color(pct)

        # Background gray bar
        ax.barh(i, 100, color=PERCENTILE_COLORS['gray'], height=BAR_HEIGHT/4, zorder=1)
        
        # Colored percentile bar
        ax.barh(i, pct, color=color, height=BAR_HEIGHT, zorder=2)
        
        # Circle using scatter (stays circular!)
        ax.scatter(pct, i, s=CIRCLE_SIZE, c=[color], 
                   edgecolors='white', linewidths=3, zorder=3)
        
        # Percentile text
        ax.text(pct, i, f'{int(pct)}', 
                ha='center', va='center',
                color='white', 
                fontsize=25,
                fontweight='bold',
                zorder=4)
        
        # Value text
        value_text = (f'{value:.3f}'[1:] if metric in ['xBA', 'xSLG', 'xwOBA'] and value < 1
                    else f'{value:.3f}' if metric in ['xBA', 'xSLG', 'xwOBA']
                    else f'{value:.1f}' if metric in ['EV90', 'Bat Speed']
                    else f'{value:.1f}%')
        ax.text(105, i, value_text,
                ha='left', va='center',
                fontsize=28)
    
    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics, fontsize=28, ha='right')
    ax.set_xlim(-10, 120)
    for label in ax.get_yticklabels():
        label.set_x(.07)
    ax.set_xlabel("")
    ax.grid(False)
    ax.set_xticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    return ax

def plot_percentiles_mirror(player_id: int, start_dt: str, end_dt: str, season: int, ax: plt.Axes):
    """
    Plot mirrored percentile bars for platoon splits.
    LHP bars go LEFT, RHP bars go RIGHT, labels on LEFT side.
    
    ADJUSTMENT GUIDE:
    -----------------
    - LABEL_X: Position of metric labels (more negative = further left)
    - CENTER_X: Where bars meet in the middle (increase to shift bars right)
    - CIRCLE_SIZE: Size of circles in points^2 (scatter marker size)
    - BAR_HEIGHT: Height of bars (increase for thicker bars)
    - LABEL_FONTSIZE: Size of metric label text
    - CIRCLE_FONTSIZE: Size of percentile number inside circles
    - VALUE_FONTSIZE: Size of stat values on edges
    """
    # Fetch and process player data for both splits
    raw_data = get_savant_data(player_id, start_dt, end_dt)
    lhp_data = process_hitter_data(raw_data, pitcher_hand='L')
    rhp_data = process_hitter_data(raw_data, pitcher_hand='R')

    lhp_stats = lhp_data.iloc[0].to_dict()
    rhp_stats = rhp_data.iloc[0].to_dict()

    # Define metrics in display order (top to bottom on card)
    metrics = ['xwOBA', 'xBA', 'xSLG', 'EV90', 'Barrel%', 'Hard Hit%', 
               'Bat Speed', 'Sweet Spot%', 'Whiff%', 'Z-Swing%', 'O-Swing%', 
               'Z-O Swing%', 'Z-Contact%', 'O-Contact%']
    
    # Reverse so xwOBA appears at TOP
    metrics = metrics[::-1]

    lower_is_better = ['Whiff%', 'O-Swing%']
    
    pct_metrics = ['Whiff%', 'Z-Swing%', 'O-Swing%', 'Z-O Swing%', 'Z-Contact%', 'O-Contact%', 
                   'Barrel%', 'Hard Hit%', 'Sweet Spot%', 'Pulled FB%']
    
    league_stats = pd.read_csv(f'data/clean{season}.csv')

    # Calculate percentiles for both splits
    lhp_pcts = {}
    rhp_pcts = {}
    for metric in metrics:
        if metric not in league_stats.columns:
            lhp_pcts[metric] = 50
            rhp_pcts[metric] = 50
            continue
        
        league_values = league_stats[metric].copy()
        
        if metric in pct_metrics and league_values.max() < 1.5:
            league_values = league_values * 100

        # LHP percentile
        raw_pct = percentileofscore(league_values, lhp_stats[metric], kind='mean')
        adj_pct = max(1, raw_pct)
        if metric in lower_is_better:
            adj_pct = max(1, 100 - adj_pct)
        lhp_pcts[metric] = adj_pct

        # RHP percentile
        raw_pct = percentileofscore(league_values, rhp_stats[metric], kind='mean')
        adj_pct = max(1, raw_pct)
        if metric in lower_is_better:
            adj_pct = max(1, 100 - adj_pct)
        rhp_pcts[metric] = adj_pct

    # ============================================================
    # ADJUSTMENT VARIABLES - CHANGE THESE TO TWEAK LAYOUT
    # ============================================================
    CENTER_X = 50            # Center point where LHP/RHP bars meet (and where labels go)
    BAR_GAP = 20             # Gap between center and where bars start (white space for labels)
    BAR_HEIGHT = 0.7        # Height of bars (y-axis units)
    CIRCLE_SIZE = 1800       # Circle size in points^2 (for scatter marker)
    LABEL_FONTSIZE = 26      # Metric label font size
    CIRCLE_FONTSIZE = 24     # Percentile number font size
    VALUE_FONTSIZE = 28      # Stat value font size (increased)
    LHP_VALUE_X = -80       # LHP value x position (far left)
    RHP_VALUE_X = 180        # RHP value x position (far right)
    XLIM_LEFT = -85         # Left boundary of plot
    XLIM_RIGHT = 185         # Right boundary of plot
    # ============================================================

    for i, metric in enumerate(metrics):
        lhp_pct = lhp_pcts[metric]
        rhp_pct = rhp_pcts[metric]
        lhp_val = lhp_stats[metric]
        rhp_val = rhp_stats[metric]
        lhp_color = get_savant_color(lhp_pct)
        rhp_color = get_savant_color(rhp_pct)

        # Background gray bars (both directions from center, with gap)
        ax.barh(i, -100, left=CENTER_X - BAR_GAP, color=PERCENTILE_COLORS['gray'], height=BAR_HEIGHT/4, zorder=1)
        ax.barh(i, 100, left=CENTER_X + BAR_GAP, color=PERCENTILE_COLORS['gray'], height=BAR_HEIGHT/4, zorder=1)
        
        # LHP bar (goes LEFT from center with gap)
        ax.barh(i, -lhp_pct, left=CENTER_X - BAR_GAP, color=lhp_color, height=BAR_HEIGHT, zorder=2)
        
        # RHP bar (goes RIGHT from center with gap)
        ax.barh(i, rhp_pct, left=CENTER_X + BAR_GAP, color=rhp_color, height=BAR_HEIGHT, zorder=2)
        
        # LHP circle using scatter (stays circular!)
        ax.scatter(CENTER_X - BAR_GAP - lhp_pct, i, s=CIRCLE_SIZE, c=[lhp_color], 
                   edgecolors='white', linewidths=3, zorder=3)
        ax.text(CENTER_X - BAR_GAP - lhp_pct, i, f'{int(lhp_pct)}', 
                ha='center', va='center',
                color='white', fontsize=CIRCLE_FONTSIZE, fontweight='bold', zorder=4)
        
        # RHP circle using scatter (stays circular!)
        ax.scatter(CENTER_X + BAR_GAP + rhp_pct, i, s=CIRCLE_SIZE, c=[rhp_color], 
                   edgecolors='white', linewidths=3, zorder=3)
        ax.text(CENTER_X + BAR_GAP + rhp_pct, i, f'{int(rhp_pct)}', 
                ha='center', va='center',
                color='white', fontsize=CIRCLE_FONTSIZE, fontweight='bold', zorder=4)
        
        # Value texts
        lhp_value_text = (f'{lhp_val:.3f}'[1:] if metric in ['xBA', 'xSLG', 'xwOBA'] and lhp_val < 1
                         else f'{lhp_val:.3f}' if metric in ['xBA', 'xSLG', 'xwOBA']
                         else f'{lhp_val:.1f}' if metric in ['EV90', 'Bat Speed']
                         else f'{lhp_val:.1f}%')
        rhp_value_text = (f'{rhp_val:.3f}'[1:] if metric in ['xBA', 'xSLG', 'xwOBA'] and rhp_val < 1
                         else f'{rhp_val:.3f}' if metric in ['xBA', 'xSLG', 'xwOBA']
                         else f'{rhp_val:.1f}' if metric in ['EV90', 'Bat Speed']
                         else f'{rhp_val:.1f}%')
        
        # LHP value on far LEFT, RHP value on far RIGHT (mirrored columns)
        ax.text(LHP_VALUE_X, i, lhp_value_text, ha='right', va='center', fontsize=VALUE_FONTSIZE)
        ax.text(RHP_VALUE_X, i, rhp_value_text, ha='left', va='center', fontsize=VALUE_FONTSIZE)
        
        # Metric label in CENTER (between the two bar sections)
        ax.text(CENTER_X, i, metric, ha='center', va='center', fontsize=LABEL_FONTSIZE, zorder=5)
    
    # Styling
    ax.set_yticks([])
    ax.set_xlim(XLIM_LEFT, XLIM_RIGHT)
    ax.set_ylim(-0.5, len(metrics) - 0.5)
    ax.set_xlabel("")
    ax.grid(False)
    ax.set_xticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    return ax

def make_batter_card(player_id, game_type=None, start_date=None, end_date=None, season=2024, split_type=None):
    """
    Create a batter card with optional splits.
    
    Args:
        player_id: MLB player ID
        game_type: Game type filter ('R' for regular, etc.)
        start_date: Start date (defaults to season start if None)
        end_date: End date (defaults to season end if None)
        season: Season year
        split_type: Type of split to display:
            - None: Standard card (no split)
            - 'platoon': Split by pitcher handedness (vs LHP | vs RHP)
    """
    # Set default dates if not provided
    from constants import SEASON_DATES
    if start_date is None:
        start_date = SEASON_DATES[season]['REG_START']
    if end_date is None:
        end_date = SEASON_DATES[season]['REG_END']
    
    if split_type == 'platoon':
        # ===== PLATOON LAYOUT (mirrored butterfly chart) =====
        fig = plt.figure(figsize=(24, 24))  # Taller figure
        
        # height_ratios: [header, headshot/bio, timeframe, stats_table, savant x3, footer]
        # width_ratios: reduced outer margins (0.5 instead of 2) for more plot space
        gs = gridspec.GridSpec(8, 8,
                            height_ratios=[1, 8, 2, 5, 10, 10, 10, 1],
                            width_ratios=[0.1, 16, 16, 16, 16, 16, 16, 0.1])
        
        # Header elements
        ax_headshot = fig.add_subplot(gs[1, 0:3])
        ax_bio = fig.add_subplot(gs[1, 1:7])
        ax_logo = fig.add_subplot(gs[1, 5:9])
        ax_timeframe = fig.add_subplot(gs[2, 1:7])
        ax_player_stats = fig.add_subplot(gs[3, 1:7])
        
        # Single mirrored savant plot
        ax_savant = fig.add_subplot(gs[4:7, 1:7])
        
        ax_text = fig.add_subplot(gs[7, 5])
        
        # Border axes
        ax_footer = fig.add_subplot(gs[-1, 1:7])
        ax_header = fig.add_subplot(gs[0, 1:7])
        ax_left = fig.add_subplot(gs[:, 0])
        ax_right = fig.add_subplot(gs[:, -1])
        
        for ax in [ax_footer, ax_header, ax_left, ax_right]:
            ax.axis('off')
        
        # Plot header elements
        plot_headshot(player_id, ax_headshot)
        plot_player_bio(player_id, ax_bio)
        plot_team_logo(player_id, ax_logo)
        plot_timeframe(game_type=game_type, start_date=start_date, end_date=end_date, season=season, ax=ax_timeframe)
        plot_std_stats(player_id, start_dt=start_date, end_dt=end_date, season=season, ax=ax_player_stats, game_type=game_type)
        
        # Plot mirrored percentiles
        plot_percentiles_mirror(player_id=player_id, start_dt=start_date, end_dt=end_date, season=season, ax=ax_savant)
        
        # Add "vs LHP" and "vs RHP" labels above the chart
        # CENTER_X is 50, BAR_GAP is 8, so LHP centers around -8, RHP centers around 108
        num_metrics = 14
        ax_savant.text(-15, num_metrics - 0.3, 
                       'vs LHP', ha='center', va='bottom', fontsize=34, fontweight='bold')
        ax_savant.text(115, num_metrics - 0.3, 
                       'vs RHP', ha='center', va='bottom', fontsize=34, fontweight='bold')
        
    else:
        # ===== STANDARD LAYOUT (original) =====
        fig = plt.figure(figsize=(20, 24))  # Taller figure
        
        # height_ratios: [header, headshot/bio, timeframe, stats_table, savant x3, footer]
        # width_ratios: reduced outer margins (0.5 instead of 2) for more plot space
        gs = gridspec.GridSpec(8, 8,
                            height_ratios=[1, 6, 2, 5, 10, 10, 10, 1],
                            width_ratios=[0.1,16, 16, 16, 16, 16, 16, 0.1])

        ax_headshot = fig.add_subplot(gs[1, 0:3])
        ax_bio = fig.add_subplot(gs[1, 1:7])
        ax_logo = fig.add_subplot(gs[1, 5:9])
        ax_timeframe = fig.add_subplot(gs[2, 1:7])
        ax_player_stats = fig.add_subplot(gs[3, 1:7])
        ax_savant = fig.add_subplot(gs[4:7, 1:7])
        ax_text = fig.add_subplot(gs[7, 5])
        
        # Border axes
        ax_footer = fig.add_subplot(gs[-1, 1:7])
        ax_header = fig.add_subplot(gs[0, 1:7])
        ax_left = fig.add_subplot(gs[:, 0])
        ax_right = fig.add_subplot(gs[:, -1])

        for ax in [ax_footer, ax_header, ax_left, ax_right]:
            ax.axis('off')
        
        # Plot elements
        plot_headshot(player_id, ax_headshot)
        plot_player_bio(player_id, ax_bio)
        plot_team_logo(player_id, ax_logo)
        plot_timeframe(game_type=game_type, start_date=start_date, end_date=end_date, season=season, ax=ax_timeframe)
        plot_std_stats(player_id, start_dt=start_date, end_dt=end_date, season=season, ax=ax_player_stats, game_type=game_type)
        
        # Plot percentiles (no split)
        plot_percentiles(player_id=player_id, start_dt=start_date, end_dt=end_date, season=season, ax=ax_savant)
        ax_savant.set_anchor('E')

    # X handle
    ax_text.text(0, 0, "X: @DeGregorioAndre", ha='center', va='center', fontsize=35)
    ax_text.axis('off')

    plt.tight_layout()
    plt.show()