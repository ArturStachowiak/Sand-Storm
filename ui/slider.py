import pygame
from OpenGL.GL import *
from config.settings import *

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, is_count_slider=False, is_color_slider=False, is_wind_slider=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.knob_size = SLIDER_KNOB_SIZE
        self.is_count_slider = is_count_slider
        self.is_color_slider = is_color_slider
        self.is_wind_slider = is_wind_slider
        
    def draw(self):
        # Draw slider track
        glBegin(GL_QUADS)
        if self.is_color_slider:
            # Draw color gradient for color slider
            for i in range(2):
                x = self.x + (self.width * i)
                color = self.get_color_at_position(i)
                glColor3f(*color)
                glVertex2f(x, self.y)
                glVertex2f(x + self.width/2, self.y)
                glVertex2f(x + self.width/2, self.y + self.height)
                glVertex2f(x, self.y + self.height)
        elif self.is_wind_slider:
            # Draw wind direction gradient
            for i in range(4):  # Four segments for different wind directions
                x = self.x + (self.width * i/4)
                color = self.get_wind_color_at_position(i)
                glColor3f(*color)
                glVertex2f(x, self.y)
                glVertex2f(x + self.width/4, self.y)
                glVertex2f(x + self.width/4, self.y + self.height)
                glVertex2f(x, self.y + self.height)
        else:
            glColor3f(0.3, 0.3, 0.3)  # Dark gray track
            glVertex2f(self.x, self.y)
            glVertex2f(self.x + self.width, self.y)
            glVertex2f(self.x + self.width, self.y + self.height)
            glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Draw slider knob
        knob_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        glBegin(GL_QUADS)
        glColor3f(0.7, 0.7, 0.7)  # Light gray knob
        glVertex2f(knob_x - self.knob_size/2, self.y - self.knob_size/2)
        glVertex2f(knob_x + self.knob_size/2, self.y - self.knob_size/2)
        glVertex2f(knob_x + self.knob_size/2, self.y + self.height + self.knob_size/2)
        glVertex2f(knob_x - self.knob_size/2, self.y + self.height + self.knob_size/2)
        glEnd()
        
    def get_color_at_position(self, position):
        if position == 0:
            return [0.1, 0.2, 0.4]  # Dark blue
        else:
            return [0.8, 0.4, 0.2]  # Orange-red
        
    def get_wind_color_at_position(self, position):
        # Colors for different wind directions
        colors = [
            [0.8, 0.2, 0.2],  # Red - North
            [0.2, 0.8, 0.2],  # Green - East
            [0.2, 0.2, 0.8],  # Blue - South
            [0.8, 0.8, 0.2]   # Yellow - West
        ]
        return colors[position]
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            knob_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
            
            # Check if click is on knob
            if (abs(mouse_x - knob_x) < self.knob_size/2 and 
                self.y - self.knob_size/2 <= mouse_y <= self.y + self.height + self.knob_size/2):
                self.dragging = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            # Calculate new value based on mouse position
            self.value = self.min_val + (mouse_x - self.x) / self.width * (self.max_val - self.min_val)
            # Clamp value to valid range
            self.value = max(self.min_val, min(self.max_val, self.value))
            
            if self.is_count_slider:
                # Update particle count
                global CURRENT_PARTICLES, particles
                new_count = int(self.value)
                if new_count != CURRENT_PARTICLES:
                    CURRENT_PARTICLES = new_count
                    particles = [Particle() for _ in range(CURRENT_PARTICLES)]
            elif self.is_color_slider:
                # Update sky colors
                global SKY_COLOR, SUNSET_COLOR, HORIZON_COLOR
                t = self.value
                # Interpolate between dark blue and orange-red
                SKY_COLOR = [
                    0.1 + (0.8 - 0.1) * t,
                    0.2 + (0.4 - 0.2) * t,
                    0.4 + (0.2 - 0.4) * t
                ]
                SUNSET_COLOR = [
                    0.8 + (0.9 - 0.8) * t,
                    0.4 + (0.6 - 0.4) * t,
                    0.2 + (0.3 - 0.2) * t
                ]
                HORIZON_COLOR = [
                    0.9 + (1.0 - 0.9) * t,
                    0.6 + (0.8 - 0.6) * t,
                    0.3 + (0.5 - 0.3) * t
                ]
            elif self.is_wind_slider:
                # Update wind direction
                global WIND_DIRECTION
                angle = math.radians(self.value)
                WIND_DIRECTION = [
                    math.cos(angle) * WIND_STRENGTH,
                    0.0,
                    math.sin(angle) * WIND_STRENGTH
                ]
            else:
                # Update particle sizes
                global MIN_PARTICLE_SIZE, MAX_PARTICLE_SIZE, SMALL_PARTICLE_MAX
                MIN_PARTICLE_SIZE = self.value * 0.2
                MAX_PARTICLE_SIZE = self.value
                SMALL_PARTICLE_MAX = self.value * 0.6

def draw_text(text, x, y):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (255, 255, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    width = text_surface.get_width()
    height = text_surface.get_height()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glRasterPos2d(x, y)
    glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    glDisable(GL_BLEND) 