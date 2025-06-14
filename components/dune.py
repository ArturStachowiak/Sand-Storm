import math
import random
from opensimplex import OpenSimplex

class Dune:
    def __init__(self, x, z, height, width):
        self.x = x
        self.z = z
        self.height = height
        self.width = width
        # Add noise generator for more realistic dune shapes
        self.noise_gen = OpenSimplex(seed=random.randint(1, 1000))

    def get_height_at(self, x, z):
        # Calculate distance from dune center
        dx = x - self.x
        dz = z - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Create a more realistic dune shape with noise
        if distance < self.width:
            # Base dune shape using a smoother function
            base_height = self.height * math.exp(-(distance / (self.width * 0.6)) ** 2)
            
            # Add noise for more natural appearance
            noise_x = (x + self.x) * 0.3
            noise_z = (z + self.z) * 0.3
            noise_factor = self.noise_gen.noise2(noise_x, noise_z) * 0.3
            
            # Add directional variation (dunes are often asymmetric)
            direction_factor = 1.0 + (dx / self.width) * 0.2
            
            # Combine all factors for realistic dune shape
            final_height = base_height * (1.0 + noise_factor) * direction_factor
            
            # Ensure height is positive and within reasonable bounds
            return max(0, min(self.height * 1.5, final_height))
        return 0 