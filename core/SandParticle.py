import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class SandParticle:
    def __init__(self, position: pygame.Vector3):
        self.position = position
        self.velocity = pygame.Vector3(0, 0, 0)
        self.acceleration = pygame.Vector3(0, 0, 0)
        self.mass = 1.0  # Default mass
        self.active = True  # Whether the particle is still active in the simulation

    def update(self, wind: pygame.Vector3, delta_time: float):
        """
        Update particle's position based on wind and other forces
        Args:
            wind: Vector3 representing wind force
            delta_time: Time since last update
        """
        # Apply wind force
        self.acceleration = wind / self.mass
        
        # Update velocity
        self.velocity += self.acceleration * delta_time
        
        # Update position
        self.position += self.velocity * delta_time

    def draw(self):
        """
        Draw the particle in 3D space
        """
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Draw particle as a small sphere with yellow color
        glColor3f(1.0, 0.8, 0.0)  # Yellow color
        quad = gluNewQuadric()
        gluSphere(quad, 0.02, 8, 8)  # Smaller sphere with radius 0.02
        
        glPopMatrix() 