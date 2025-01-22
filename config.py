# Display settings

import matplotlib as mpl
import seaborn as sns

# Display dimensions
FIGURE_DIMENSIONS = (8.5, 11)  # inches
IMAGE_DPI = 300

# Font properties
FONT_FAMILY = 'DejaVu Sans'
FONT_PROPERTIES = {
    'general': {'family': FONT_FAMILY, 'size': 12},
    'title': {'family': FONT_FAMILY, 'size': 20},
    'axes': {'family': FONT_FAMILY, 'size': 16}
}

# Seaborn theme settings
sns.set_theme(
    style='whitegrid',
    palette='deep',
    font=FONT_FAMILY,
    font_scale=1.5,
    color_codes=True,
    rc=None
)

