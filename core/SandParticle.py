import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class SandParticle:
    def __init__(self, position: pygame.Vector3):
        self.position = position
        self.velocity = pygame.Vector3(0, 0, 0)
        self.acceleration = pygame.Vector3(0, 0, 0)
        self.mass = 1  # Default mass
        self.active = True  # Whether the particle is still active in the simulation
        self.has_wrapped = False  # Whether the particle has already wrapped around the terrain
        self.gravity = pygame.Vector3(0, -2.0, 0)  # Reduced gravity force

    def update(self, wind: pygame.Vector3, delta_time: float):
        """
        Update particle's position based on wind and other forces
        Args:
            wind: Vector3 representing wind force
            delta_time: Time since last update
        """
        # Add upward component to wind and increase its strength
        wind_with_upward = pygame.Vector3(wind.x * 2.0, wind.y + 1.0, wind.z)  # Increased wind force
        
        # Combine wind and gravity forces
        self.acceleration = (wind_with_upward + self.gravity) / self.mass
        
        # Update velocity with damping
        self.velocity += self.acceleration * delta_time
        self.velocity *= 0.95  # Reduced air resistance for more dynamic movement
        
        # Update position
        self.position += self.velocity * delta_time

    def draw(self):
        """
        Draw the particle in 3D space
        """
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Draw particle as a small sphere with yellow color
        # glColor3f(1.0, 0.8, 0.0)  # Yellow color
        quad = gluNewQuadric()
        gluSphere(quad, 0.01, 8, 8)  # Smaller sphere with radius 0.02
        
        glPopMatrix() 