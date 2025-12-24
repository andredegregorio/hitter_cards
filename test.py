import matplotlib
matplotlib.use('TkAgg')  # Force interactive backend

from plotting import make_batter_card

# Generate and display the card
make_batter_card(player_id=592450, season=2024)