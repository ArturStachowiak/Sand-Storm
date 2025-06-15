import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

class SandParticle:
    def __init__(self, position: pygame.Vector3, size: float):
        self.position = position
        self.velocity = pygame.Vector3(0, 0, 0)
        self.acceleration = pygame.Vector3(0, 0, 0)
        self.mass = 1  # Default mass
        self.active = True  # Whether the particle is still active in the simulation
        self.has_wrapped = False  # Whether the particle has already wrapped around the terrain
        self.lifetime = 0  # Current lifetime of the particle
        
        # Losowy rozmiar cząsteczki (bardziej realistyczny)
        self.size = size * random.uniform(3, 10)  # Zwiększony rozmiar
        self.color = (1.0, random.uniform(0.4, 0.78), 0.26, random.uniform(0.7, 1.0))
        # Losowy kolor - pomarańczowy, żółty lub szary

        
        # Losowa rotacja dla bardziej realistycznego wyglądu
        self.rotation_x = random.uniform(0, 360)
        self.rotation_y = random.uniform(0, 360)
        self.rotation_z = random.uniform(0, 360)
        self.rotation_speed_x = random.uniform(-5, 5)
        self.rotation_speed_y = random.uniform(-5, 5)
        self.rotation_speed_z = random.uniform(-5, 5)

    def update(self, wind: pygame.Vector3, delta_time: float, mass: float = 1.0):
        """
        Update particle's position based on wind and other forces
        Args:
            wind: Vector3 representing wind force
            delta_time: Time since last update
            mass: Particle mass affecting its movement
        """
        self.mass = mass*math.sqrt(self.size)*2
        
        # Zwiększona siła wiatru dla szybszego ruchu
        r = random.uniform(-5, 5)
        wind_with_upward = pygame.Vector3(wind.x * 4.0, wind.y + r, wind.z + r)
        
        # Apply wind force with mass consideration
        self.acceleration = wind_with_upward / self.mass
        
        # Update velocity with damping (mniej tłumienia dla szybszego ruchu)
        self.velocity += self.acceleration * delta_time
        self.velocity *= 0.98  # Mniej tłumienia powietrza
        
        # Update position
        self.position += self.velocity * delta_time
        
        # Update rotations
        self.rotation_x += self.rotation_speed_x * delta_time * 15
        self.rotation_y += self.rotation_speed_y * delta_time * 15
        self.rotation_z += self.rotation_speed_z * delta_time * 15
        
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
        
        # Apply random rotations
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set color with transparency
        glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        
        # Draw particle as a small sphere with random size
        quad = gluNewQuadric()
        gluSphere(quad, self.size, 6, 6)  # Mniej segmentów dla bardziej chropowatego wyglądu
        
        # Disable blending
        glDisable(GL_BLEND)
        
        glPopMatrix() 