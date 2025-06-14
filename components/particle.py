import numpy as np
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from config.settings import *

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
        transparency = random.uniform(0.5, 1.0)
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
        glEnable(GL_NORMALIZE)
        
        # Set up light
        light_pos = [0, 10, 0, 1]  # Pozycja światła
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])  # Światło otoczenia
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.7, 1.0])  # Światło rozproszone (lekko żółtawe)
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 0.9, 1.0])  # Światło odbite (lekko żółtawe)
        
        # Set material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Draw particle
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        # Disable effects
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_COLOR_MATERIAL)
        glDisable(GL_NORMALIZE)
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