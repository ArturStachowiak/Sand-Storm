import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np
import math
import time

# Window settings
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Burza Piaskowa"

# Initialize Pygame and OpenGL
pygame.init()
display = (WINDOW_WIDTH, WINDOW_HEIGHT)
pygame.display.set_mode(display, pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption(WINDOW_TITLE)

# Set up the perspective
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, -2.0, -20)

# Global particle size settings
MIN_PARTICLE_SIZE = 0.05
MAX_PARTICLE_SIZE = 0.25
SMALL_PARTICLE_MAX = 0.15
SIZE_CHANGE_SPEED = 0.01

# Particle count settings
MIN_PARTICLES = 500
MAX_PARTICLES = 5000
CURRENT_PARTICLES = 3000

# Sky color settings
SKY_COLOR = [0.1, 0.2, 0.4]  # Default dark blue
SUNSET_COLOR = [0.8, 0.4, 0.2]  # Default orange-red
HORIZON_COLOR = [0.9, 0.6, 0.3]  # Default light orange

# Slider settings
SLIDER_WIDTH = 200
SLIDER_HEIGHT = 20
SLIDER_X = 10
SLIDER_Y = 100
SLIDER_MIN = 0.01
SLIDER_MAX = 0.5
SLIDER_KNOB_SIZE = 20
slider_value = 0.25  # Initial value
slider_dragging = False

# Particle count slider settings
COUNT_SLIDER_X = 10
COUNT_SLIDER_Y = 150
COUNT_SLIDER_MIN = MIN_PARTICLES
COUNT_SLIDER_MAX = MAX_PARTICLES
count_slider_value = CURRENT_PARTICLES
count_slider_dragging = False

# Color slider settings
COLOR_SLIDER_X = 10
COLOR_SLIDER_Y = 200
COLOR_SLIDER_MIN = 0.0
COLOR_SLIDER_MAX = 1.0
color_slider_value = 0.5
color_slider_dragging = False

# Wind settings
WIND_DIRECTION = [0.5, 0.0, 0.0]  # Default wind direction
WIND_STRENGTH = 1.0

# Wind direction slider settings
WIND_SLIDER_X = 10
WIND_SLIDER_Y = 250
WIND_SLIDER_MIN = 0
WIND_SLIDER_MAX = 360
wind_slider_value = 0
wind_slider_dragging = False

# Particle settings
PARTICLES_PER_CLUSTER = 5  # Number of particles in each cluster
CLUSTER_RADIUS = 0.5  # Maximum distance between particles in a cluster

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

# Sky class
class Sky:
    def __init__(self):
        self.time = 0
        self.sun_position = np.array([-5.0, 8.0, -15.0])
        self.sun_radius = 1.0
        self.sun_color = (1.0, 0.7, 0.3, 1.0)  # Orange color for sun
        
    def update(self):
        self.time += 0.001
        
    def draw(self):
        # Draw sky gradient
        glBegin(GL_QUADS)
        # Top of sky
        glColor3f(*SKY_COLOR)
        glVertex3f(-20, 20, -20)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 20, 20)
        glVertex3f(-20, 20, 20)
        
        # Middle of sky (sunset colors)
        glColor3f(*SUNSET_COLOR)
        glVertex3f(-20, 0, -20)
        glVertex3f(20, 0, -20)
        glVertex3f(20, 20, -20)
        glVertex3f(-20, 20, -20)
        
        # Bottom of sky
        glColor3f(*HORIZON_COLOR)
        glVertex3f(-20, -20, -20)
        glVertex3f(20, -20, -20)
        glVertex3f(20, 0, -20)
        glVertex3f(-20, 0, -20)
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

# Wind class to handle dynamic wind
class Wind:
    def __init__(self):
        self.base_direction = np.array(WIND_DIRECTION)
        self.current_direction = self.base_direction.copy()
        self.strength = WIND_STRENGTH
        self.turbulence = 0.1
        self.last_update = time.time()
        
    def update(self):
        current_time = time.time()
        dt = current_time - self.last_update
        
        # Update wind direction with some turbulence
        self.current_direction += np.array([
            random.uniform(-self.turbulence, self.turbulence),
            random.uniform(-self.turbulence/2, self.turbulence/2),
            random.uniform(-self.turbulence, self.turbulence)
        ]) * dt
        
        # Normalize direction
        norm = np.linalg.norm(self.current_direction)
        if norm > 0:
            self.current_direction /= norm
            
        # Gradually return to base direction
        self.current_direction = self.current_direction * 0.95 + self.base_direction * 0.05
        
        # Update wind strength
        self.strength = WIND_STRENGTH + math.sin(current_time) * 0.3
        
        self.last_update = current_time
        
    def get_force(self, position, particle_size):
        # Wind gets stronger with height
        height_factor = 1.0 + position[1] * 0.1
        
        # Add some local turbulence based on position
        turbulence = np.array([
            math.sin(position[0] * 0.5) * 0.1,
            math.cos(position[1] * 0.5) * 0.05,
            math.sin(position[2] * 0.5) * 0.1
        ])
        
        # Smaller particles are more affected by wind
        size_factor = 1.0 / (particle_size * 2)
        
        return (self.current_direction + turbulence) * self.strength * height_factor * size_factor

# Dune class
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

# Create dunes
dunes = [
    Dune(-5, -5, 2, 3),
    Dune(5, -3, 2.5, 4),
    Dune(0, -8, 3, 5),
    Dune(-8, 0, 2, 3),
    Dune(8, 0, 2.5, 4)
]

def get_terrain_height(x, z):
    height = 0
    for dune in dunes:
        height += dune.get_height_at(x, z)
    return height

# Particle class
class Particle:
    def __init__(self, cluster_center=None):
        # If cluster_center is provided, generate particle near it
        if cluster_center is not None:
            # Generate random offset within cluster radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, CLUSTER_RADIUS)
            self.position = np.array([
                cluster_center[0] + distance * math.cos(angle),
                cluster_center[1] + random.uniform(-0.2, 0.2),  # Small vertical variation
                cluster_center[2] + distance * math.sin(angle)
            ])
        else:
            # Original random position generation
            self.position = np.array([
                random.uniform(-10, 10),
                random.uniform(0, 5),
                random.uniform(-10, 10)
            ])
        
        # Generate size with 90% chance of being small
        if random.random() < 0.9:
            self.size = random.uniform(MIN_PARTICLE_SIZE, SMALL_PARTICLE_MAX)
        else:
            self.size = random.uniform(SMALL_PARTICLE_MAX, MAX_PARTICLE_SIZE)
        
        # Initialize velocity
        self.velocity = np.array([0.0, 0.0, 0.0])
        
        # Initialize color with slight variation and random transparency
        base_color = 0.8
        variation = random.uniform(-0.1, 0.1)
        transparency = random.uniform(0.5, 1.0)  # 0.5 = 50% transparent, 1.0 = fully opaque
        self.color = [base_color + variation, base_color + variation, base_color + variation, transparency]
        
        # Initialize rotation
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        
        # Initialize lifetime
        self.lifetime = random.uniform(0.8, 1.2)
        self.age = 0
        
        # Generate random number of vertices (3-6)
        self.num_vertices = random.randint(3, 6)
        
        # Generate irregular polygon vertices
        self.vertices = []
        for i in range(self.num_vertices):
            angle = (2 * math.pi * i / self.num_vertices)
            # Add random variation to radius for irregular shape
            radius = self.size * random.uniform(0.8, 1.2)
            # Add random variation to angle for more irregularity
            angle += random.uniform(-0.2, 0.2)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            self.vertices.append((x, y))

    def reset(self):
        # Reset particle to initial state
        self.position = np.array([
            random.uniform(-10, 10),
            random.uniform(0, 5),
            random.uniform(-10, 10)
        ])
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.age = 0
        self.lifetime = random.uniform(0.8, 1.2)

    def update(self, wind):
        # Get wind force at current position
        wind_force = wind.get_force(self.position, self.size)
        
        # Apply wind force (inversely proportional to mass)
        self.velocity += wind_force * (1.0 / self.size) * 0.01
        
        # Add some random turbulence (more for smaller particles)
        turbulence_scale = 1.0 / (self.size * 2)
        self.velocity += np.array([
            random.uniform(-0.02, 0.02) * turbulence_scale,
            random.uniform(-0.01, 0.01) * turbulence_scale,
            random.uniform(-0.02, 0.02) * turbulence_scale
        ])
        
        # Apply drag force (air resistance) - more for smaller particles
        drag = 0.98 - (self.size * 0.1)
        self.velocity *= drag
        
        # Update position
        self.position += self.velocity
        
        # Decrease lifetime
        self.lifetime -= 1
        
        # Reset particles that go too far or die
        if any(abs(pos) > 15 for pos in self.position) or self.lifetime <= 0:
            self.reset()

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation, 0, 0, 1)
        
        # Draw irregular polygon
        glBegin(GL_POLYGON)
        glColor4f(*self.color)
        for vertex in self.vertices:
            glVertex2f(vertex[0], vertex[1])
        glEnd()
        
        glPopMatrix()

def draw_terrain():
    glBegin(GL_QUADS)
    for x in range(-10, 10):
        for z in range(-10, 10):
            # Get height at each corner of the quad
            h1 = get_terrain_height(x, z)
            h2 = get_terrain_height(x+1, z)
            h3 = get_terrain_height(x+1, z+1)
            h4 = get_terrain_height(x, z+1)
            
            # Set color based on height
            color = 0.5 + h1 * 0.1
            glColor3f(color, color * 0.9, color * 0.8)
            
            # Draw quad
            glVertex3f(x, h1, z)
            glVertex3f(x+1, h2, z)
            glVertex3f(x+1, h3, z+1)
            glVertex3f(x, h4, z+1)
    glEnd()

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

# Create particles, wind and sky
particles = []
# Generate particles in clusters
for _ in range(CURRENT_PARTICLES // PARTICLES_PER_CLUSTER):
    # Generate cluster center
    cluster_center = [
        random.uniform(-10, 10),
        random.uniform(0, 5),
        random.uniform(-10, 10)
    ]
    # Generate particles for this cluster
    for _ in range(PARTICLES_PER_CLUSTER):
        particles.append(Particle(cluster_center))

wind = Wind()
sky = Sky()
slider = Slider(SLIDER_X, SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT, SLIDER_MIN, SLIDER_MAX, slider_value)
count_slider = Slider(COUNT_SLIDER_X, COUNT_SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT, 
                     COUNT_SLIDER_MIN, COUNT_SLIDER_MAX, count_slider_value, True)
color_slider = Slider(COLOR_SLIDER_X, COLOR_SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT,
                     COLOR_SLIDER_MIN, COLOR_SLIDER_MAX, color_slider_value, False, True)
wind_slider = Slider(WIND_SLIDER_X, WIND_SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT,
                    WIND_SLIDER_MIN, WIND_SLIDER_MAX, wind_slider_value, False, False, True)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        # Handle slider events
        slider.handle_event(event)
        count_slider.handle_event(event)
        color_slider.handle_event(event)
        wind_slider.handle_event(event)

    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Update wind and sky
    wind.update()
    sky.update()
    
    # Draw sky first (as background)
    sky.draw()
    
    # Draw terrain
    draw_terrain()
    
    # Update and draw particles
    for particle in particles:
        particle.update(wind)
        particle.draw()
    
    # Rotate the view slightly to show 3D effect
    glRotatef(0.1, 0, 1, 0)
    
    # Draw UI
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display[0], display[1], 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw sliders
    slider.draw()
    count_slider.draw()
    color_slider.draw()
    wind_slider.draw()
    
    # Draw text
    size_text = f"Rozmiar cząsteczek: {MIN_PARTICLE_SIZE:.2f} - {MAX_PARTICLE_SIZE:.2f}"
    count_text = f"Liczba cząsteczek: {CURRENT_PARTICLES}"
    color_text = f"Kolor nieba: {color_slider.value:.2f}"
    wind_text = f"Kierunek wiatru: {wind_slider.value:.0f}°"
    
    draw_text(size_text, 10, 30)
    draw_text("Przeciągnij suwak aby zmienić rozmiar", 10, 70)
    draw_text(count_text, 10, 120)
    draw_text("Przeciągnij suwak aby zmienić liczbę cząsteczek", 10, 160)
    draw_text(color_text, 10, 180)
    draw_text("Przeciągnij suwak aby zmienić kolor nieba", 10, 220)
    draw_text(wind_text, 10, 240)
    draw_text("Przeciągnij suwak aby zmienić kierunek wiatru", 10, 280)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 