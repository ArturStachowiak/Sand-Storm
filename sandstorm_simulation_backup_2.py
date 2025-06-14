import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np
import math
import time
import noise
from opensimplex import OpenSimplex

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
MIN_PARTICLES = 100
MAX_PARTICLES = 5000
CURRENT_PARTICLES = 500

# Sky color settings
SKY_COLOR = [0.1, 0.2, 0.4]  # Default dark blue
SUNSET_COLOR = [0.8, 0.4, 0.2]  # Default orange-red
HORIZON_COLOR = [0.9, 0.6, 0.3]  # Default light orange

# Text settings
PARTICLE_SIZE_TEXT = 30
PARTICLE_AMOUNT_TEXT = 130
SKY_COLOR_TEXT = 230
WIND_DIRECTION_TEXT = 330

# Particle size Slider settings
SLIDER_WIDTH = 200
SLIDER_HEIGHT = 20
SLIDER_X = 10
SLIDER_Y = 50
SLIDER_MIN = 0.01
SLIDER_MAX = 0.5
SLIDER_KNOB_SIZE = 20
slider_value = 0.25  # Initial value
slider_dragging = False

# Particle amount slider settings
COUNT_SLIDER_X = 10
COUNT_SLIDER_Y = 150
COUNT_SLIDER_MIN = MIN_PARTICLES
COUNT_SLIDER_MAX = MAX_PARTICLES
count_slider_value = CURRENT_PARTICLES
count_slider_dragging = False

# Sky Color slider settings
COLOR_SLIDER_X = 10
COLOR_SLIDER_Y = 260
COLOR_SLIDER_MIN = 0.0
COLOR_SLIDER_MAX = 1.0
color_slider_value = 0.5
color_slider_dragging = False

# Wind slider direction slider settings
WIND_SLIDER_X = 10
WIND_SLIDER_Y = 370
WIND_SLIDER_MIN = 0
WIND_SLIDER_MAX = 360
wind_slider_value = 0
wind_slider_dragging = False

# Wind settings
WIND_DIRECTION = [0.5, 0.0, 0.0]  # Default wind direction
WIND_STRENGTH = 1.0

# Camera settings
CAMERA_POSITION = [0.0, 2.0, -20.0]  # Initial camera position
CAMERA_ROTATION_Y = 0.0  # Horizontal rotation (left/right)
CAMERA_ROTATION_X = 0.0  # Vertical rotation (up/down)
CAMERA_SPEED = 0.5  # Movement speed
ROTATION_SPEED = 2.0  # Rotation speed
CAMERA_HEIGHT = 2.0  # Height above terrain

# Pendulum camera movement settings
PENDULUM_AMPLITUDE = 45.0  # Maximum rotation angle (degrees)
PENDULUM_SPEED = 0.5  # Speed of pendulum movement
PENDULUM_TIME = 0.0  # Current time for pendulum calculation
PENDULUM_ENABLED = True  # Enable/disable pendulum movement

# Particle settings
PARTICLES_PER_CLUSTER = 5  # Number of particles in each cluster
CLUSTER_RADIUS = 0.5  # Maximum distance between particles in a cluster

# Terrain settings
TERRAIN_SIZE = 20
TERRAIN_RESOLUTION = 50  # Number of vertices per side
TERRAIN_HEIGHT = 2.0
TERRAIN_SCALE = 0.5

# Dune class
class Dune:
    def __init__(self, x, z, height, width):
        self.x = x
        self.z = z
        self.height = height
        self.width = width
        # Add noise generator for more realistic dune shapes
        self.noise_gen = OpenSimplex(seed=random.randint(1, 1000))

    def get_height_at(self, x, z):
        # Calculate distance from dune center
        dx = x - self.x
        dz = z - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Create a more realistic dune shape with noise
        if distance < self.width:
            # Base dune shape using a smoother function
            base_height = self.height * math.exp(-(distance / (self.width * 0.6)) ** 2)
            
            # Add noise for more natural appearance
            noise_x = (x + self.x) * 0.3
            noise_z = (z + self.z) * 0.3
            noise_factor = self.noise_gen.noise2(noise_x, noise_z) * 0.3
            
            # Add directional variation (dunes are often asymmetric)
            direction_factor = 1.0 + (dx / self.width) * 0.2
            
            # Combine all factors for realistic dune shape
            final_height = base_height * (1.0 + noise_factor) * direction_factor
            
            # Ensure height is positive and within reasonable bounds
            return max(0, min(self.height * 1.5, final_height))
        return 0

# Create dunes
dunes = [
    Dune(-5, -5, 2, 3),
    Dune(5, -3, 2.5, 4),
    Dune(0, -8, 3, 5),
    Dune(-8, 0, 2, 3),
    Dune(8, 0, 2.5, 4),
    # Dodanie większej liczby wydm dla bardziej realistycznego krajobrazu
    Dune(-3, 3, 1.8, 2.5),
    Dune(3, 5, 2.2, 3.2),
    Dune(-6, -2, 1.5, 2.8),
    Dune(6, -6, 2.8, 4.5),
    Dune(0, 0, 1.2, 2.0),
    Dune(-2, -7, 2.1, 3.1),
    Dune(4, 2, 1.9, 2.7),
    Dune(-4, 6, 2.3, 3.8),
    Dune(7, 3, 1.7, 2.4),
    Dune(-7, -4, 2.4, 3.6)
]

def get_terrain_height(x, z):
    height = 0
    for dune in dunes:
        height += dune.get_height_at(x, z)
    return height

class Terrain:
    def __init__(self):
        self.vertices = []
        self.indices = []
        self.colors = []
        
        # Initialize noise generator
        noise_gen = OpenSimplex(seed=42)
        
        # Generate height map
        self.height_map = np.zeros((TERRAIN_RESOLUTION, TERRAIN_RESOLUTION))
        for i in range(TERRAIN_RESOLUTION):
            for j in range(TERRAIN_RESOLUTION):
                x = i / TERRAIN_RESOLUTION * TERRAIN_SCALE
                y = j / TERRAIN_RESOLUTION * TERRAIN_SCALE
                
                # Get base terrain height from dunes
                base_height = get_terrain_height(x * TERRAIN_SIZE, y * TERRAIN_SIZE)
                
                # Add noise for more natural terrain variation
                # Large formations
                noise_large = noise_gen.noise2(x, y) * 1.0
                # Medium details
                noise_medium = noise_gen.noise2(x * 3, y * 3) * 0.5
                # Small details
                noise_small = noise_gen.noise2(x * 8, y * 8) * 0.2
                
                # Combine dune height with noise
                height = base_height + noise_large + noise_medium + noise_small
                
                # Add some random variations for more realistic appearance
                if random.random() < 0.05:  # 5% chance for small variations
                    height += random.uniform(-0.5, 0.5)
                
                # Ensure minimum height and smooth transitions
                height = max(0, height)
                
                # Store in height map
                self.height_map[i, j] = height
        
        # Generate vertices and colors
        for i in range(TERRAIN_RESOLUTION):
            for j in range(TERRAIN_RESOLUTION):
                # Calculate position
                x = (i / TERRAIN_RESOLUTION - 0.5) * TERRAIN_SIZE
                z = (j / TERRAIN_RESOLUTION - 0.5) * TERRAIN_SIZE
                y = self.height_map[i, j]
                
                # Add vertex
                self.vertices.extend([x, y, z])
                
                # Calculate color based on height, position and random pattern
                height_factor = (y + TERRAIN_HEIGHT) / (2 * TERRAIN_HEIGHT)
                
                # Bazowe kolory piasku z większym kontrastem i gradientami
                sand_colors = [
                    [0.95, 0.90, 0.70],  # Jasny, ciepły piasek (szczyty)
                    [0.85, 0.75, 0.55],  # Średni, ciepły piasek
                    [0.75, 0.55, 0.35],  # Ciemny, ciepły piasek (doliny)
                    [0.80, 0.65, 0.45],  # Pomarańczowy piasek
                    [0.70, 0.60, 0.40],  # Czerwono-brązowy piasek
                    [0.90, 0.80, 0.60],  # Jasny żółty piasek
                ]
                
                # Wybór bazowego koloru z gradientem wysokości
                if height_factor > 0.7:  # Szczyty wydm
                    base_color = sand_colors[0]  # Jasny piasek
                elif height_factor > 0.4:  # Środkowe części
                    base_color = sand_colors[1]  # Średni piasek
                else:  # Doliny i podstawy
                    base_color = sand_colors[2]  # Ciemny piasek
                
                # Dodanie gradientu wysokości z płynniejszymi przejściami
                height_gradient = height_factor * 0.4  # Zmniejszony wpływ wysokości
                
                # Dodanie losowej wariacji dla naturalności
                variation = random.uniform(-0.15, 0.15)  # Zmniejszona wariacja
                
                # Dodanie gradientu pozycji (wydmy mają różne kolory w różnych miejscach)
                position_factor = (x + z) / (TERRAIN_SIZE * 2)  # Normalizacja pozycji
                position_variation = math.sin(position_factor * math.pi * 2) * 0.1
                
                # Finalny kolor z gradientami
                color = [
                    base_color[0] + height_gradient + variation + position_variation,
                    base_color[1] + height_gradient * 0.8 + variation + position_variation,
                    base_color[2] + height_gradient * 0.6 + variation + position_variation,
                    1.0
                ]
                
                # Ograniczenie wartości kolorów do zakresu [0, 1]
                color = [max(0, min(1, c)) for c in color]
                self.colors.extend(color)
        
        # Generate indices for triangles
        for i in range(TERRAIN_RESOLUTION - 1):
            for j in range(TERRAIN_RESOLUTION - 1):
                # Calculate vertex indices
                v0 = i * TERRAIN_RESOLUTION + j
                v1 = v0 + 1
                v2 = (i + 1) * TERRAIN_RESOLUTION + j
                v3 = v2 + 1
                
                # Add two triangles
                self.indices.extend([v0, v1, v2])
                self.indices.extend([v1, v3, v2])
        
        # Convert to numpy arrays
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)
        
        # Create VAO and VBOs
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # Vertex buffer
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        # Color buffer
        self.cbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)
        
        # Index buffer
        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        glBindVertexArray(0)
    
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

# Create terrain
terrain = Terrain()

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
        glVertex3f(20, -20, -20)
        glVertex3f(-20, -20, -20)
        
        # Left wall
        glColor3f(*SKY_COLOR)
        glVertex3f(-20, 20, -20)
        glVertex3f(-20, 20, 20)
        glVertex3f(-20, 0, 20)
        glVertex3f(-20, 0, -20)
        
        glColor3f(*SUNSET_COLOR)
        glVertex3f(-20, 0, -20)
        glVertex3f(-20, 0, 20)
        glVertex3f(-20, -20, 20)
        glVertex3f(-20, -20, -20)
        
        # Right wall
        glColor3f(*SKY_COLOR)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 20, 20)
        glVertex3f(20, 0, 20)
        glVertex3f(20, 0, -20)
        
        glColor3f(*SUNSET_COLOR)
        glVertex3f(20, 0, -20)
        glVertex3f(20, 0, 20)
        glVertex3f(20, -20, 20)
        glVertex3f(20, -20, -20)
        
        # Top wall (ceiling)
        glColor3f(*SKY_COLOR)
        glVertex3f(-20, 20, -20)
        glVertex3f(20, 20, -20)
        glVertex3f(20, 20, 20)
        glVertex3f(-20, 20, 20)
        
        # Bottom wall (floor sky reflection)
        glColor3f(*HORIZON_COLOR)
        glVertex3f(-20, -20, -20)
        glVertex3f(20, -20, -20)
        glVertex3f(20, -20, 20)
        glVertex3f(-20, -20, 20)
        
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

def get_camera_terrain_height(x, z):
    """Get terrain height at camera position, including terrain mesh"""
    # Get dune height
    dune_height = get_terrain_height(x, z)
    
    # Get terrain mesh height (simplified - using noise)
    noise_gen = OpenSimplex(seed=42)
    terrain_x = (x + TERRAIN_SIZE/2) / TERRAIN_SIZE * TERRAIN_SCALE
    terrain_z = (z + TERRAIN_SIZE/2) / TERRAIN_SIZE * TERRAIN_SCALE
    
    # Calculate terrain height using the same noise function as terrain
    terrain_height = noise_gen.noise2(terrain_x, terrain_z) * 3.0
    terrain_height += noise_gen.noise2(terrain_x * 2, terrain_z * 2) * 1.5
    terrain_height += noise_gen.noise2(terrain_x * 4, terrain_z * 4) * 0.3
    terrain_height *= TERRAIN_HEIGHT * 1.5
    
    return max(dune_height, terrain_height)

def handle_camera_movement():
    """Handle camera movement and rotation based on key presses"""
    global CAMERA_POSITION, CAMERA_ROTATION_Y, CAMERA_ROTATION_X
    
    keys = pygame.key.get_pressed()
    
    # Calculate forward and right vectors based on camera rotation
    forward_x = math.sin(math.radians(CAMERA_ROTATION_Y))
    forward_z = math.cos(math.radians(CAMERA_ROTATION_Y))
    right_x = math.cos(math.radians(CAMERA_ROTATION_Y))
    right_z = -math.sin(math.radians(CAMERA_ROTATION_Y))
    
    # Handle movement
    if keys[pygame.K_w]:  # Forward
        new_x = CAMERA_POSITION[0] + forward_x * CAMERA_SPEED
        new_z = CAMERA_POSITION[2] + forward_z * CAMERA_SPEED
        # Check terrain height at new position
        terrain_height = get_camera_terrain_height(new_x, new_z)
        CAMERA_POSITION[0] = new_x
        CAMERA_POSITION[2] = new_z
        CAMERA_POSITION[1] = terrain_height + CAMERA_HEIGHT
    
    if keys[pygame.K_s]:  # Backward
        new_x = CAMERA_POSITION[0] - forward_x * CAMERA_SPEED
        new_z = CAMERA_POSITION[2] - forward_z * CAMERA_SPEED
        terrain_height = get_camera_terrain_height(new_x, new_z)
        CAMERA_POSITION[0] = new_x
        CAMERA_POSITION[2] = new_z
        CAMERA_POSITION[1] = terrain_height + CAMERA_HEIGHT
    
    if keys[pygame.K_a]:  # Left
        new_x = CAMERA_POSITION[0] - right_x * CAMERA_SPEED
        new_z = CAMERA_POSITION[2] - right_z * CAMERA_SPEED
        terrain_height = get_camera_terrain_height(new_x, new_z)
        CAMERA_POSITION[0] = new_x
        CAMERA_POSITION[2] = new_z
        CAMERA_POSITION[1] = terrain_height + CAMERA_HEIGHT
    
    if keys[pygame.K_d]:  # Right
        new_x = CAMERA_POSITION[0] + right_x * CAMERA_SPEED
        new_z = CAMERA_POSITION[2] + right_z * CAMERA_SPEED
        terrain_height = get_camera_terrain_height(new_x, new_z)
        CAMERA_POSITION[0] = new_x
        CAMERA_POSITION[2] = new_z
        CAMERA_POSITION[1] = terrain_height + CAMERA_HEIGHT
    
    # Handle rotation with mouse
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        mouse_rel = pygame.mouse.get_rel()
        CAMERA_ROTATION_Y += mouse_rel[0] * 0.5
        CAMERA_ROTATION_X -= mouse_rel[1] * 0.5
        
        # Clamp vertical rotation
        CAMERA_ROTATION_X = max(-90, min(90, CAMERA_ROTATION_X))
    
    # Keep camera within bounds
    CAMERA_POSITION[0] = max(-15, min(15, CAMERA_POSITION[0]))
    CAMERA_POSITION[2] = max(-15, min(15, CAMERA_POSITION[2]))

# Particle class
class Particle:
    def __init__(self):
        # Initialize basic properties
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
        transparency = random.uniform(0.9, 1.0)  # Changed from (0.5, 1.0) to (0.9, 1.0) for 0-10% transparency
        self.color = [base_color + variation, base_color + variation, base_color + variation, transparency]
        
        # Initialize rotation
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        
        # Initialize lifetime
        self.lifetime = random.uniform(0.8, 1.2)
        self.age = 0
        
        # Generate 3D sphere mesh
        self.vertices = []
        self.colors = []
        self.indices = []
        
        # Sphere parameters
        radius = self.size
        segments = 8
        
        # Generate sphere vertices
        for i in range(segments + 1):
            lat = np.pi * (-0.5 + float(i) / segments)
            for j in range(segments + 1):
                lon = 2 * np.pi * float(j) / segments
                x = np.cos(lat) * np.cos(lon) * radius
                y = np.cos(lat) * np.sin(lon) * radius
                z = np.sin(lat) * radius
                
                self.vertices.extend([x, y, z])
                self.colors.extend([self.color[0], self.color[1], self.color[2], self.color[3]])
        
        # Generate triangle indices
        for i in range(segments):
            for j in range(segments):
                first = i * (segments + 1) + j
                second = first + segments + 1
                
                self.indices.extend([first, second, first + 1])
                self.indices.extend([second, second + 1, first + 1])
        
        # Convert to numpy arrays
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)
        
        # Create VAO and VBOs
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.cbo = glGenBuffers(1)
        self.ibo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        
        # Vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        # Color buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)
        
        # Index buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        glBindVertexArray(0)
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
        # Enable transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Set up light
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        
        # Draw particle
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        # Disable effects
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_COLOR_MATERIAL)
        glDisable(GL_BLEND)
        
        glPopMatrix()

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
        particles.append(Particle())

wind = Wind()
sky = Sky()
slider = Slider(SLIDER_X, SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT, SLIDER_MIN, SLIDER_MAX, slider_value)
count_slider = Slider(COUNT_SLIDER_X, COUNT_SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT, 
                     COUNT_SLIDER_MIN, COUNT_SLIDER_MAX, count_slider_value, True)
color_slider = Slider(COLOR_SLIDER_X, COLOR_SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT,
                     COLOR_SLIDER_MIN, COLOR_SLIDER_MAX, color_slider_value, False, True)
wind_slider = Slider(WIND_SLIDER_X, WIND_SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT,
                    WIND_SLIDER_MIN, WIND_SLIDER_MAX, wind_slider_value, False, False, True)

# Ground class
class Ground:
    def __init__(self):
        # Bazowe kolory piasku z większym kontrastem
        self.sand_colors = [
            [0.90, 0.85, 0.65],  # Jasny, ciepły piasek
            [0.75, 0.55, 0.35],  # Ciemny, ciepły piasek
            [0.65, 0.60, 0.45],  # Szary piasek
            [0.85, 0.70, 0.40],  # Pomarańczowy piasek
            [0.70, 0.80, 0.60],  # Zielonkawy piasek
            [0.80, 0.60, 0.30],  # Czerwony piasek
        ]
        
        # Generowanie wierzchołków i kolorów dla podłoża
        self.vertices = []
        self.colors = []
        self.indices = []
        
        # Rozmiar podłoża
        size = TERRAIN_SIZE * 1.5  # Nieco większe niż teren
        resolution = TERRAIN_RESOLUTION // 2  # Mniejsza rozdzielczość dla wydajności
        
        # Generowanie siatki podłoża
        for i in range(resolution):
            for j in range(resolution):
                # Pozycja wierzchołka
                x = (i / resolution - 0.5) * size
                z = (j / resolution - 0.5) * size
                y = -TERRAIN_HEIGHT * 0.5  # Położenie pod terenem
                
                # Dodanie wierzchołka
                self.vertices.extend([x, y, z])
                
                # Generowanie koloru z losową wariacją
                base_color = random.choice(self.sand_colors)
                variation = random.uniform(-0.2, 0.2)
                
                # Dodanie wariacji do koloru
                color = [
                    base_color[0] + variation,
                    base_color[1] + variation,
                    base_color[2] + variation,
                    1.0
                ]
                
                # Ograniczenie wartości kolorów
                color = [max(0, min(1, c)) for c in color]
                self.colors.extend(color)
        
        # Generowanie indeksów dla trójkątów
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                v0 = i * resolution + j
                v1 = v0 + 1
                v2 = (i + 1) * resolution + j
                v3 = v2 + 1
                
                self.indices.extend([v0, v1, v2])
                self.indices.extend([v1, v3, v2])
        
        # Konwersja na tablice numpy
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)
        
        # Tworzenie VAO i VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.cbo = glGenBuffers(1)
        self.ibo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        
        # Bufor wierzchołków
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        # Bufor kolorów
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)
        
        # Bufor indeksów
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        glBindVertexArray(0)
    
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

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
    
    # Draw ground first (pod terenem)
    ground = Ground()
    ground.draw()
    
    # Draw terrain
    terrain.draw()
    
    # Update and draw particles
    for particle in particles:
        particle.update(wind)
        particle.draw()
    
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
    
    draw_text(size_text, 0, PARTICLE_SIZE_TEXT)
    
    draw_text(count_text, 0, PARTICLE_AMOUNT_TEXT)
    
    draw_text(color_text, 0, SKY_COLOR_TEXT)
    
    draw_text(wind_text, 0, WIND_DIRECTION_TEXT)
    
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 