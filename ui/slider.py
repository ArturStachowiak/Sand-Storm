import pygame
from OpenGL.GL import *

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, is_sky_rgb=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.is_dragging = False
        self.is_sky_rgb = is_sky_rgb
        
    def draw(self):
        # Draw slider track
        glColor3f(0.7, 0.7, 0.7)  # Light gray
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Draw slider knob
        knob_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        glColor3f(0.3, 0.3, 0.3)  # Dark gray
        glBegin(GL_QUADS)
        glVertex2f(knob_x - 5, self.y - 5)
        glVertex2f(knob_x + 5, self.y - 5)
        glVertex2f(knob_x + 5, self.y + self.height + 5)
        glVertex2f(knob_x - 5, self.y + self.height + 5)
        glEnd()
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y <= mouse_y <= self.y + self.height):
                    self.is_dragging = True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.is_dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                # Calculate new value based on mouse position
                relative_x = max(0, min(1, (mouse_x - self.x) / self.width))
                self.value = self.min_val + relative_x * (self.max_val - self.min_val)
                
                # Update sky colors if this is a sky RGB slider
                if self.is_sky_rgb:
                    try:
                        from config.settings import SKY_COLOR
                        # Update the appropriate color component
                        if hasattr(self, 'color_component'):
                            SKY_COLOR[self.color_component] = self.value / 255.0
                    except ImportError:
                        pass  # Ignore if settings are not available 