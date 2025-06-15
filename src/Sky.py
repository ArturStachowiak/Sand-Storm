import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from src.consts import *

"""
This is a class describing the sky.
It is used to:
- draw the sky
- update the sky colors
- draw the sky gradient
- draw the sun
- draw the sun glow effect
"""
class Sky:
    def __init__(self):
        self.sun_position = np.array([-5.0, 15.0, -15.0])
        self.sun_radius = 1.0
        self.sun_color = (1.0, 0.7, 0.3, 1.0)  # Orange color for sun
        
        # Initialize sky colors
        self.sky_color = list(SKY_COLOR)
        self.sunset_color = list(SUNSET_COLOR)
        self.horizon_color = list(HORIZON_COLOR)
        
    def update_colors(self, b):
        """Update sky colors based on RGB values (0-255)"""
        # Convert from 0-255 to 0-1 range
        r = 30 / 255.0
        g = 10 / 255.0
        b = b / 255.0
        
        # Update main sky color
        self.sky_color = [r, g, b]
        
        # Update sunset and horizon colors based on sky color
        self.sunset_color = [min(1.0, r + 0.7), min(1.0, g + 0.2), min(1.0, b - 0.2)]
        self.horizon_color = [min(1.0, r + 0.8), min(1.0, g + 0.4), min(1.0, b - 0.1)]
        
    def draw(self):
        # Draw sky gradient
        glBegin(GL_QUADS)
        
        # Back wall (sky gradient)
        # Top of sky
        glColor3f(*self.sky_color)
        glVertex3f(-20, 20, -20)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 0, -20)
        glVertex3f(-20, 0, -20)
        
        # Middle of sky (sunset colors)
        glColor3f(*self.sunset_color)
        glVertex3f(-20, 0, -20)
        glVertex3f(20, 0, -20)
        glVertex3f(20, -2, -20)
        glVertex3f(-20, -2, -20)
        
        # Left wall
        glColor3f(*self.sky_color)
        glVertex3f(-20, 20, -20)
        glVertex3f(-20, 20, 20)
        glVertex3f(-20, 0, 20)
        glVertex3f(-20, 0, -20)
        
        glColor3f(*self.sunset_color)
        glVertex3f(-20, 0, -20)
        glVertex3f(-20, 0, 20)
        glVertex3f(-20, -2, 20)
        glVertex3f(-20, -2, -20)
        
        # Right wall
        glColor3f(*self.sky_color)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 20, 20)
        glVertex3f(20, 0, 20)
        glVertex3f(20, 0, -20)
        
        glColor3f(*self.sunset_color)
        glVertex3f(20, 0, -20)
        glVertex3f(20, 0, 20)
        glVertex3f(20, -2, 20)
        glVertex3f(20, -2, -20)
        
        # Top wall (ceiling)
        glColor3f(*self.sky_color)
        glVertex3f(-20, 20, -20)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 20, 20)
        glVertex3f(-20, 20, 20)
        
        # Bottom wall (floor sky reflection)
        glColor3f(*self.horizon_color)
        glVertex3f(-20, -2, -20)
        glVertex3f(20, -2, -20)
        glVertex3f(20, -2, 20)
        glVertex3f(-20, -2, 20)
        
        glEnd()
        
        # Draw sun
        glPushMatrix()
        glTranslatef(self.sun_position[0], self.sun_position[1], self.sun_position[2])
        
        # Sun glow effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # Draw multiple spheres for glow effect
        for i in range(3):
            scale = 1.0 + i * 0.3
            alpha = 0.3 - i * 0.1
            glColor4f(self.sun_color[0], self.sun_color[1], self.sun_color[2], alpha)
            quad = gluNewQuadric()
            gluSphere(quad, self.sun_radius * scale, 32, 32)
        
        glDisable(GL_BLEND)
        glPopMatrix() 