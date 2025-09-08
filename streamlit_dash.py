import streamlit as st
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import pandas as pd
import seaborn as sns
from PIL import Image
from io import BytesIO
import requests
import datetime as dt
import pybaseball as pyb

# Import your custom modules
from constants import *
from config import *
from plotting import plot_headshot, plot_player_bio, plot_team_logo, plot_timeframe, plot_std_stats, plot_percentiles, make_batter_card
from utils import get_headshot, get_player_bio, get_team_logo, get_timeframe, get_savant_color, get_filtered_game_logs
from data_processing import calculate_xBA, calculate_xSLG, calculate_xwOBA, process_game_logs, is_barrel, is_sweet_spot

# Streamlit app configuration
st.set_page_config(
    page_title="Baseball Hitter Cards",
    page_icon="⚾",
    layout="wide"
)

# App title and description
st.title("⚾ Baseball Hitter Cards Generator")
st.markdown("Generate professional baseball player cards with statistics and visualizations")

# Sidebar for inputs
st.sidebar.header("Player Configuration")

# Season selection
season = st.sidebar.selectbox(
    "Select Season",
    options=list(SEASON_DATES.keys()),
    index=len(SEASON_DATES.keys()) - 1  # Default to most recent season
)

# Game type selection
game_type = st.sidebar.selectbox(
    "Game Type",
    options=['R', 'P', 'W'],  # Regular, Playoffs, World Series
    index=0,
    help="R = Regular Season, P = Playoffs, W = World Series"
)

# Player search section
st.sidebar.subheader("Player Search")
col1, col2 = st.sidebar.columns(2)

with col1:
    first_name = st.text_input("First Name", placeholder="e.g., Aaron")

with col2:
    last_name = st.text_input("Last Name", placeholder="e.g., Judge")

# Date range selection
st.sidebar.subheader("Date Range")
start_date = st.sidebar.date_input(
    "Start Date",
    value=dt.datetime.strptime(SEASON_DATES[season]['REG_START'], '%Y-%m-%d').date(),
    min_value=dt.datetime.strptime(SEASON_DATES[season]['REG_START'], '%Y-%m-%d').date(),
    max_value=dt.datetime.strptime(SEASON_DATES[season]['REG_END'], '%Y-%m-%d').date()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=dt.datetime.strptime(SEASON_DATES[season]['REG_END'], '%Y-%m-%d').date(),
    min_value=dt.datetime.strptime(SEASON_DATES[season]['REG_START'], '%Y-%m-%d').date(),
    max_value=dt.datetime.strptime(SEASON_DATES[season]['REG_END'], '%Y-%m-%d').date()
)

# Convert dates to string format
start = start_date.strftime('%Y-%m-%d')
end = end_date.strftime('%Y-%m-%d')

# Main content area
if first_name and last_name:
    try:
        # Player lookup
        with st.spinner(f"Looking up {first_name} {last_name}..."):
            player_lookup = pyb.playerid_lookup(last_name, first_name)
            
        if len(player_lookup) == 0:
            st.error(f"No player found with name: {first_name} {last_name}")
        elif len(player_lookup) == 1:
            # Single player found
            player_id = player_lookup['key_mlbam'].iloc[0]
            player_name = f"{player_lookup['name_first'].iloc[0]} {player_lookup['name_last'].iloc[0]}"
            
            st.success(f"Player found: {player_name}")
            
            # Generate card button
            if st.button("Generate Player Card", type="primary"):
                try:
                    with st.spinner("Generating player card..."):
                        # Generate the player card
                        card_fig = make_batter_card(
                            player_id=player_id,
                            start_date=start,
                            end_date=end,
                            game_type=game_type,
                            season=season
                        )
                        
                        # Display the card
                        st.pyplot(card_fig)
                        
                        # Option to save the card
                        st.markdown("---")
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            if st.button("Save Card as PNG"):
                                filename = f"{player_name.replace(' ', '_')}_{season}_card.png"
                                card_fig.savefig(filename, dpi=300, bbox_inches='tight')
                                st.success(f"Card saved as {filename}")
                        
                        with col2:
                            # Create download button
                            buf = BytesIO()
                            card_fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                            buf.seek(0)
                            
                            st.download_button(
                                label="Download Card",
                                data=buf.getvalue(),
                                file_name=f"{player_name.replace(' ', '_')}_{season}_card.png",
                                mime="image/png"
                            )
                
                except Exception as e:
                    st.error(f"Error generating player card: {str(e)}")
                    st.error("Please check that all required data files and functions are available.")
        
        else:
            # Multiple players found
            st.warning(f"Multiple players found with name: {first_name} {last_name}")
            st.write("Please select the correct player:")
            
            # Create a selection dataframe
            display_df = player_lookup[['name_first', 'name_last', 'mlb_played_first', 'mlb_played_last']].copy()
            display_df['Years Active'] = display_df['mlb_played_first'].astype(str) + ' - ' + display_df['mlb_played_last'].astype(str)
            display_df['Full Name'] = display_df['name_first'] + ' ' + display_df['name_last']
            
            # Player selection
            selected_player = st.selectbox(
                "Select Player:",
                options=range(len(display_df)),
                format_func=lambda x: f"{display_df.iloc[x]['Full Name']} ({display_df.iloc[x]['Years Active']})"
            )
            
            if st.button("Generate Card for Selected Player", type="primary"):
                player_id = player_lookup.iloc[selected_player]['key_mlbam']
                player_name = f"{player_lookup.iloc[selected_player]['name_first']} {player_lookup.iloc[selected_player]['name_last']}"
                
                try:
                    with st.spinner("Generating player card..."):
                        card_fig = make_batter_card(
                            player_id=player_id,
                            start_date=start,
                            end_date=end,
                            game_type=game_type,
                            season=season
                        )
                        
                        st.pyplot(card_fig)
                        
                        # Download option
                        buf = BytesIO()
                        card_fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                        buf.seek(0)
                        
                        st.download_button(
                            label="Download Card",
                            data=buf.getvalue(),
                            file_name=f"{player_name.replace(' ', '_')}_{season}_card.png",
                            mime="image/png"
                        )
                
                except Exception as e:
                    st.error(f"Error generating player card: {str(e)}")
    
    except Exception as e:
        st.error(f"Error looking up player: {str(e)}")
        st.error("Please make sure pybaseball is properly installed and configured.")

else:
    # Instructions when no player is entered
    st.info("👆 Enter a player's first and last name in the sidebar to get started")
    
    st.markdown("### How to use:")
    st.markdown("""
    1. **Enter Player Information**: Type the player's first and last name in the sidebar
    2. **Select Season**: Choose the season you want to analyze
    3. **Choose Game Type**: Regular season, playoffs, or World Series
    4. **Set Date Range**: Adjust the start and end dates if needed
    5. **Generate Card**: Click the generate button to create the player card
    6. **Download**: Save the card as a PNG file
    """)
    
    st.markdown("### Features:")
    st.markdown("""
    - 📊 **Advanced Statistics**: Expected stats, percentiles, and more
    - 🎯 **Visual Analytics**: Charts and graphs for easy interpretation  
    - 📸 **Player Photos**: Automatic headshot integration
    - 🏆 **Team Logos**: Official team branding
    - 📅 **Flexible Timeframes**: Custom date ranges
    - 💾 **Export Options**: Download high-quality PNG files
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and pybaseball")