import numpy as np
import random
import math
import time
from config.settings import *

class Wind:
    def __init__(self):
        self.base_direction = np.array(WIND_DIRECTION)
        self.current_direction = self.base_direction.copy()
        self.strength = WIND_STRENGTH
        self.turbulence = 0.1
        self.last_update = time.time()
        
    def update(self):
        current_time = time.time()
        dt = current_time - self.last_update
        
        # Update wind direction with some turbulence
        self.current_direction += np.array([
            random.uniform(-self.turbulence, self.turbulence),
            random.uniform(-self.turbulence/2, self.turbulence/2),
            random.uniform(-self.turbulence, self.turbulence)
        ]) * dt
        
        # Normalize direction
        norm = np.linalg.norm(self.current_direction)
        if norm > 0:
            self.current_direction /= norm
            
        # Gradually return to base direction
        self.current_direction = self.current_direction * 0.95 + self.base_direction * 0.05
        
        # Update wind strength
        self.strength = WIND_STRENGTH + math.sin(current_time) * 0.3
        
        self.last_update = current_time
        
    def get_force(self, position, particle_size):
        # Wind gets stronger with height
        height_factor = 1.0 + position[1] * 0.1
        
        # Add some local turbulence based on position
        turbulence = np.array([
            math.sin(position[0] * 0.5) * 0.1,
            math.cos(position[1] * 0.5) * 0.05,
            math.sin(position[2] * 0.5) * 0.1
        ])
        
        # Smaller particles are more affected by wind
        size_factor = 1.0 / (particle_size * 2)
        
        return (self.current_direction + turbulence) * self.strength * height_factor * size_factor 