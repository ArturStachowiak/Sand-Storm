import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import random

class SandParticle:
    def __init__(self, position: pygame.Vector3, size: float):
        self.position = position
        self.velocity = pygame.Vector3(0, 0, 0)
        self.acceleration = pygame.Vector3(0, 0, 0)
        self.mass = 1  # Default mass
        self.active = True  # Whether the particle is still active in the simulation
        self.has_wrapped = False  # Whether the particle has already wrapped around the terrain
        self.lifetime = 0  # Current lifetime of the particle
        self.size = size

    def update(self, wind: pygame.Vector3, delta_time: float, mass: float = 1.0):
        """
        Update particle's position based on wind and other forces
        Args:
            wind: Vector3 representing wind force
            delta_time: Time since last update
            mass: Particle mass affecting its movement
        """
        self.mass = mass
        
        # Add upward component to wind and increase its strength
        r = random.uniform(-3, 3)
        wind_with_upward = pygame.Vector3(wind.x * 2.0, wind.y + r, wind.z + r)
        
        # Apply wind force with mass consideration
        self.acceleration = wind_with_upward / self.mass
        
        # Update velocity with damping
        self.velocity += self.acceleration * delta_time
        self.velocity *= 0.95  # Reduced air resistance for more dynamic movement
        
        # Update position
        self.position += self.velocity * delta_time
        
        # Update lifetime
        self.lifetime += delta_time

    def draw(self, color_value: float = 0.5):
        """
        Draw the particle in 3D space
        Args:
            color_value: Value between 0 and 1 determining particle color
        """
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Calculate color based on color_value
        # Interpolate between yellow (0.0) and orange-red (1.0)
        r = 1.0
        g = 0.8 - (0.8 - 0.4) * color_value
        b = 0.0 + 0.2 * color_value
        
        # Set color
        glColor4f(r, g, b, 1.0)
        
        # Draw particle as a small sphere
        quad = gluNewQuadric()
        gluSphere(quad, 0.15, 8, 8)
        
        glPopMatrix() 