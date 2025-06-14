import math

class Dune:
    def __init__(self, x, z, height, width):
        self.x = x
        self.z = z
        self.height = height
        self.width = width

    def get_height_at(self, x, z):
        # Calculate distance from dune center
        dx = x - self.x
        dz = z - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Create a bell-shaped curve for the dune
        if distance < self.width:
            return self.height * math.cos(distance * math.pi / self.width) ** 2
        return 0 