import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# Default colors if settings are not available
DEFAULT_SKY_COLOR = [0.1, 0.2, 0.4]  # Dark blue
DEFAULT_SUNSET_COLOR = [0.8, 0.4, 0.2]  # Orange-red
DEFAULT_HORIZON_COLOR = [0.9, 0.6, 0.3]  # Light orange

class Sky:
    def __init__(self):
        self.sun_position = np.array([-5.0, 15.0, -15.0])
        self.sun_radius = 1.0
        self.sun_color = (1.0, 0.7, 0.3, 1.0)  # Orange color for sun
        
        # Initialize sky colors
        try:
            from config.settings import SKY_COLOR, SUNSET_COLOR, HORIZON_COLOR
            self.sky_color = list(SKY_COLOR)
            self.sunset_color = list(SUNSET_COLOR)
            self.horizon_color = list(HORIZON_COLOR)
        except ImportError:
            self.sky_color = list(DEFAULT_SKY_COLOR)
            self.sunset_color = list(DEFAULT_SUNSET_COLOR)
            self.horizon_color = list(DEFAULT_HORIZON_COLOR) 