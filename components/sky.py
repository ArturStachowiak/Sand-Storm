import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from config.settings import *

class Sky:
    def __init__(self):
        self.sun_position = np.array([-5.0, 15.0, -15.0])
        self.sun_radius = 1.0
        self.sun_color = (1.0, 0.7, 0.3, 1.0)  # Orange color for sun
        
    def draw(self):
        # Draw sky gradient
        glBegin(GL_QUADS)
        
        # Back wall (sky gradient)
        # Top of sky
        glColor3f(*SKY_COLOR)
        glVertex3f(-20, 20, -20)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 0, -20)
        glVertex3f(-20, 0, -20)
        
        # Middle of sky (sunset colors)
        glColor3f(*SUNSET_COLOR)
        glVertex3f(-20, 0, -20)
        glVertex3f(20, 0, -20)
        glVertex3f(20, -2, -20)
        glVertex3f(-20, -2, -20)
        
        # Left wall
        glColor3f(*SKY_COLOR)
        glVertex3f(-20, 20, -20)
        glVertex3f(-20, 20, 20)
        glVertex3f(-20, 0, 20)
        glVertex3f(-20, 0, -20)
        
        glColor3f(*SUNSET_COLOR)
        glVertex3f(-20, 0, -20)
        glVertex3f(-20, 0, 20)
        glVertex3f(-20, -2, 20)
        glVertex3f(-20, -2, -20)
        
        # Right wall
        glColor3f(*SKY_COLOR)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 20, 20)
        glVertex3f(20, 0, 20)
        glVertex3f(20, 0, -20)
        
        glColor3f(*SUNSET_COLOR)
        glVertex3f(20, 0, -20)
        glVertex3f(20, 0, 20)
        glVertex3f(20, -2, 20)
        glVertex3f(20, -2, -20)
        
        # Top wall (ceiling)
        glColor3f(*SKY_COLOR)
        glVertex3f(-20, 20, -20)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 20, 20)
        glVertex3f(-20, 20, 20)
        
        # Bottom wall (floor sky reflection)
        glColor3f(*HORIZON_COLOR)
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