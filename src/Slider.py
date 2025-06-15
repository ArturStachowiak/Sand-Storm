import math
import pygame
from OpenGL.GL import *
from src.consts import *

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, is_count_slider=False, is_color_slider=False, is_wind_slider=False, is_sky_rgb=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = 4  # Zmniejszona wysokość toru slidera
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.knob_size = 12  # Zmniejszony rozmiar uchwytu
        self.is_count_slider = is_count_slider
        self.is_color_slider = is_color_slider
        self.is_wind_slider = is_wind_slider
        self.is_sky_rgb = is_sky_rgb
        self.sand_storm = None  # Reference to SandStorm instance
        
    def set_sand_storm(self, sand_storm):
        self.sand_storm = sand_storm
        
    def draw_value_text(self):
        # Create font here instead of in __init__
        font = pygame.font.Font(None, 24)
        
        # Format the value based on slider type
        if self.is_wind_slider:
            value_text = f"{int(self.value)}°"
        else:
            value_text = f"{int(self.value)}"
            
        text_surface = font.render(value_text, True, (0, 0, 0))  # Changed to black color
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width = text_surface.get_width()
        height = text_surface.get_height()
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Position the text to the right of the slider
        glRasterPos2d(self.x + self.width + 10, self.y + (self.height - height) / 2)
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glDisable(GL_BLEND)
        
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
        
        # Draw the numerical value
        self.draw_value_text()
        
        # Draw slider knob last to ensure it's on top
        knob_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        glBegin(GL_QUADS)
        glColor3f(0.4, 0.4, 0.4)  # Jaśniejszy kolor uchwytu
        
        # Dodajemy małe przesunięcie w górę dla lepszej widoczności
        knob_y_offset = 2
        
        # Rysujemy uchwyt wyżej niż tor slidera
        glVertex2f(knob_x - self.knob_size/2, self.y - self.knob_size/2 + knob_y_offset)
        glVertex2f(knob_x + self.knob_size/2, self.y - self.knob_size/2 + knob_y_offset)
        glVertex2f(knob_x + self.knob_size/2, self.y + self.height + self.knob_size/2 + knob_y_offset)
        glVertex2f(knob_x - self.knob_size/2, self.y + self.height + self.knob_size/2 + knob_y_offset)
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
            
            if self.is_count_slider and self.sand_storm:
                # Update particle count in SandStorm
                new_count = int(self.value)
                if len(self.sand_storm.particles) != new_count:
                    self.sand_storm.particles = []
                    for _ in range(new_count):
                        self.sand_storm.add_particles(1, pygame.Vector3(0, 14, 0))
            elif self.is_color_slider and not self.is_sky_rgb:
                # Update sky colors (only for the old color slider, not for RGB sliders)
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

def draw_text(text, x, y, font_size=36):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, (0, 0, 0))  # Changed to black color
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    width = text_surface.get_width()
    height = text_surface.get_height()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glRasterPos2d(x, y)
    glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    glDisable(GL_BLEND) 