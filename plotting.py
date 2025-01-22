from utils import *
from data_processing import *
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

    # Note: plot_headshot(player_id, plt.gca()) is good for quick plots

def plot_player_bio(player_id: str, ax: plt.Axes):
    """
    Fetches player bio data and plots it on the given axes.
    
    Args:
    - player_id (str): The unique player ID.
    - ax (plt.Axes): The Matplotlib axes on which to plot the bio information.
    """
    # Get player bio data
    player_data = get_player_bio(player_id)

    # Plot player bio data
    ax.text(0.5, 0.65, f'{player_data["primary_position"]} {player_data["player_name"]}',
            va='bottom', ha='center', fontsize=55, fontweight='bold')
    ax.text(0.5, 0.325, f'{player_data["team"]}', va='bottom', ha='center', fontsize=35)
    ax.text(0.5, 0, f'B/T: {player_data["batting_hand"]}/{player_data["throwing_hand"]} | {player_data["height"]}/{player_data["weight"]} | Age: {player_data["age"]}',
            va='bottom', ha='center', fontsize=35)
    
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
        ha='center', va='center', fontsize=40,
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
    
    # Set font size
    table.set_fontsize(25)
    table.auto_set_font_size(False)
    
    # Make column headers bold
    for i, cell in table.get_celld().items():
        if i[0] == 0:
            cell.set_text_props(weight='bold')
    
    # Hide the axes
    ax.axis('off')
    
    return ax

def plot_percentiles(player_id: int, start_dt: str, end_dt: str, season: int, ax: plt.Axes):

    # Fetch and process player data
    raw_data = get_savant_data(player_id, start_dt, end_dt)
    processed_data = process_hitter_data(raw_data)

    # Convert processed data to a dictionary for percentile calculation
    player_stats = processed_data.iloc[0].to_dict()

    metrics = list(player_stats.keys())

    # Define metrics where lower is better
    lower_is_better = ['Whiff%', 'O-Swing%']
    
    # Load league stats
    league_stats = pd.read_csv(f'data/clean{season}.csv')

    # Calculate percentiles
    percentiles = {}
    for metric in metrics:
        if metric not in league_stats.columns:
            continue  # Skip metrics not in league stats

        # Calculate raw percentile
        raw_percentile = percentileofscore(league_stats[metric], player_stats[metric], kind='mean')
        adjusted_percentile = max(1, raw_percentile)  # Ensure at least 1st percentile

        # Adjust for "lower is better" metrics
        if metric in lower_is_better:
            adjusted_percentile = max(1, 100 - adjusted_percentile)  # Ensure minimum is 1
        percentiles[metric] = adjusted_percentile


    y_pos = np.arange(len(metrics))

    # Plot bars and circles
    for i, metric in enumerate(metrics):
        pct = percentiles[metric]
        value = player_stats[metric]
        color = get_savant_color(pct)
        bar_height = 0.85

        # Background gray bar
        ax.barh(i, 100, color=PERCENTILE_COLORS['gray'], height = bar_height/4 , zorder=1)
        
        # Colored percentile bar
        ax.barh(i, pct, color=color, height=bar_height, zorder=2)
        
        # Circle
        ellipse = patches.Ellipse((pct, i), width= bar_height * 6.8,  # not sure why this works
                                  height = bar_height, 
                                facecolor=color, edgecolor = 'white', 
                                linewidth=3, zorder=3)
        ax.add_patch(ellipse)
        
        # Percentile text
        font_size = 22 if pct == 100 else 27  # Adjust font size if percentile is 100
        ax.text(pct, i, f'{int(pct)}', 
                ha='center', va='center_baseline',
                color='white', 
                fontsize= font_size,
                fontweight='bold',
                zorder=4)
        
        # Value text
        value_text = (f'{value:.3f}'[1:] if metric in ['xBA', 'xSLG', 'xwOBA'] and value < 1
                    else f'{value:.3f}' if metric in ['xBA', 'xSLG', 'xwOBA']
                    else f'{value:.1f}' if metric == 'EV90'
                    else f'{value:.1f}%')
        ax.text(103, i, value_text,
                ha='left', va='center',
                fontsize=25)
    
    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics, fontsize=25, ha='right')
    ax.set_xlim(-10, 110)
    for label in ax.get_yticklabels():
        label.set_x(.07)  # Adjust the value as needed
    ax.set_xlabel("")
    ax.grid(False)
    ax.set_xticks([])  # Remove x-axis numbers
    ax.spines['left'].set_visible(False)   # Remove left spine
    ax.spines['right'].set_visible(False)  # Remove right spine
    ax.spines['top'].set_visible(False)    # Remove top spine
    ax.spines['bottom'].set_visible(False) # Remove bottom spine

    return ax

def make_batter_card(player_id, game_type=None, start_date= None, end_date=None, season=2024):
    # Create a figure of size 20x20
    fig = plt.figure(figsize=(20, 20))
    
    # Create a gridspec layout with 8 columns and 6 rows
    gs = gridspec.GridSpec(8, 8,
                        height_ratios=[3,6,3,4,8,8,8,2],
                        width_ratios=[2,16,16,16,16,16,16,2])

    # Define the position of each subplot in the grid
    ax_headshot = fig.add_subplot(gs[1, 0:3])  # Top-left for headshot
    ax_bio = fig.add_subplot(gs[1, 1:7])  # Space for bio
    ax_logo = fig.add_subplot(gs[1, 5:9])  # Top-right for team logo
    ax_timeframe = fig.add_subplot(gs[2, 1:7])  # Timeframe 
    ax_player_stats = fig.add_subplot(gs[3, 1:7])  # Player stats
    ax_savant = fig.add_subplot(gs[4:7, 1:7])  # Savant plot
    ax_text = fig.add_subplot(gs[7, 5])  # Text
    
    # Hide the header, footer, and side borders for now
    ax_footer = fig.add_subplot(gs[-1, 1:7])
    ax_header = fig.add_subplot(gs[0, 1:7])
    ax_left = fig.add_subplot(gs[:, 0])
    ax_right = fig.add_subplot(gs[:, -1])

    # Hide the axes for the borders
    ax_footer.axis('off')
    ax_header.axis('off')
    ax_left.axis('off')
    ax_right.axis('off')
    
    # Plot the headshot, bio, logo (static)
    plot_headshot(player_id, ax_headshot)
    plot_player_bio(player_id, ax_bio)
    plot_team_logo(player_id, ax_logo)

    # Plot the timeframe label based on the game type
    plot_timeframe(game_type=game_type, start_date=start_date, end_date=end_date, season=season, ax=ax_timeframe)    
    
    # Plot player standard stats 
    plot_std_stats(player_id, start_dt=start_date, end_dt=end_date, 
                   season=season, ax = ax_player_stats, game_type=game_type)    
    
    # Plot the Savant plot
    plot_percentiles(player_id=player_id, start_dt=start_date, end_dt=end_date, season=season, ax=ax_savant)
    ax_savant.set_anchor('E')

    # Plot my X handle on the bottom right
    ax_text.text(0, 0, "X: @AndreD_Stats", ha='center', va='center', fontsize=30)
    ax_text.axis('off')

    # Ensure the layout is adjusted properly
    plt.tight_layout()
    # Show the figure
    plt.show()