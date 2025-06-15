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
        
        # Losowy rozmiar cząsteczki (bardziej realistyczny)
        if random.random() < 0.8:  # 80% szans na małe cząsteczki
            self.size = random.uniform(MIN_PARTICLE_SIZE * 1.2, SMALL_PARTICLE_MAX * 2.0)  # Zwiększony rozmiar
        else:
            self.size = random.uniform(SMALL_PARTICLE_MAX * 1.5, MAX_PARTICLE_SIZE * 2.5)  # Zwiększony rozmiar
        
        # Initialize velocity
        self.velocity = np.array([0.0, 0.0, 0.0])
        
        # Losowy kolor - pomarańczowy, żółty lub szary
        color_type = random.choice(['orange', 'yellow', 'gray'])
        if color_type == 'orange':
            r = random.uniform(0.8, 1.0)
            g = random.uniform(0.4, 0.7)
            b = random.uniform(0.0, 0.3)
        elif color_type == 'yellow':
            r = random.uniform(0.9, 1.0)
            g = random.uniform(0.7, 0.9)
            b = random.uniform(0.0, 0.2)
        else:  # gray
            r = random.uniform(0.5, 0.8)
            g = random.uniform(0.5, 0.8)
            b = random.uniform(0.5, 0.8)
        
        # Losowa przezroczystość - mniej przezroczyste
        transparency = random.uniform(0.6, 1.0)  # Zwiększona nieprzezroczystość
        
        self.color = [r, g, b, transparency]
        
        # Initialize rotation with more randomness
        self.rotation_x = random.uniform(0, 360)
        self.rotation_y = random.uniform(0, 360)
        self.rotation_z = random.uniform(0, 360)
        self.rotation_speed_x = random.uniform(-4, 4)
        self.rotation_speed_y = random.uniform(-4, 4)
        self.rotation_speed_z = random.uniform(-4, 4)
        
        # Initialize lifetime
        self.lifetime = random.uniform(0.8, 1.2)
        self.age = 0
        
        # Generate 3D sphere mesh
        self.vertices = []
        self.colors = []
        self.indices = []
        
        # Sphere parameters
        radius = self.size
        segments = 6  # Mniej segmentów dla bardziej chropowatego wyglądu
        
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
        
        # Apply random rotations
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)
        
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
        
        # Apply wind force (inversely proportional to mass) - zwiększona siła
        self.velocity += wind_force * (1.0 / self.size) * 0.03  # Zwiększona siła
        
        # Add some random turbulence (more for smaller particles)
        turbulence_scale = 1.0 / (self.size * 2)
        self.velocity += np.array([
            random.uniform(-0.05, 0.05) * turbulence_scale,  # Zwiększona turbulencja
            random.uniform(-0.03, 0.03) * turbulence_scale,
            random.uniform(-0.05, 0.05) * turbulence_scale
        ])
        
        # Apply drag force (air resistance) - mniej tłumienia dla szybszego ruchu
        drag = 0.99 - (self.size * 0.05)  # Mniej tłumienia
        self.velocity *= drag
        
        # Update position
        self.position += self.velocity
        
        # Update rotations
        self.rotation_x += self.rotation_speed_x
        self.rotation_y += self.rotation_speed_y
        self.rotation_z += self.rotation_speed_z
        
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
        
        # Reset rotations
        self.rotation_x = random.uniform(0, 360)
        self.rotation_y = random.uniform(0, 360)
        self.rotation_z = random.uniform(0, 360)
        self.rotation_speed_x = random.uniform(-4, 4)
        self.rotation_speed_y = random.uniform(-4, 4)
        self.rotation_speed_z = random.uniform(-4, 4)
        
        # Update transparency based on current particle count
        self.update_transparency()
    
    def update_transparency(self):
        """Update particle transparency based on current particle count"""
        # Calculate transparency based on total particle count
        particle_count_factor = min(1.0, CURRENT_PARTICLES / 1000.0)  # Normalize to 0-1 range
        base_transparency = 1.0 - (particle_count_factor * 0.7)  # 30% to 100% transparency
        transparency = base_transparency + random.uniform(-0.1, 0.1)  # Add small variation
        transparency = max(0.2, min(1.0, transparency))  # Clamp between 20% and 100%
        
        # Update color with new transparency
        self.color[3] = transparency
        
        # Update the color buffer with new transparency
        for i in range(3, len(self.colors), 4):  # Update alpha channel (every 4th value)
            self.colors[i] = transparency
        
        # Update the color buffer on GPU
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW) 