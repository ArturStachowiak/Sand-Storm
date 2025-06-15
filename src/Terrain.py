import numpy as np
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from opensimplex import OpenSimplex
from src.consts import *

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
                
                # Large formations
                height = noise_gen.noise2(x, y) * 3.0
                # Medium details
                height += noise_gen.noise2(x * 2, y * 2) * 1.5
                # Small details
                height += noise_gen.noise2(x * 4, y * 4) * 0.3
                
                # Dodanie losowych szczytów
                if random.random() < 0.1:  # 10% szans na wyższy szczyt
                    height *= 1.5
                
                # Zwiększenie ogólnej wysokości terenu
                self.height_map[i, j] = height * TERRAIN_HEIGHT * 1.5
        
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
                
                # Bazowe kolory piasku z większym kontrastem
                sand_colors = [
                    [0.90, 0.85, 0.65],  # Jasny, ciepły piasek
                    [0.75, 0.55, 0.35],  # Ciemny, ciepły piasek
                    [0.65, 0.60, 0.45],  # Szary piasek
                    [0.85, 0.70, 0.40],  # Pomarańczowy piasek
                    [0.70, 0.80, 0.60],  # Zielonkawy piasek
                    [0.80, 0.60, 0.30],  # Czerwony piasek
                ]
                
                # Wybór bazowego koloru z losową wariacją
                base_color = random.choice(sand_colors)
                variation = random.uniform(-0.2, 0.2)  # Zwiększona wariacja
                
                # Dodanie gradientu wysokości i losowej wariacji
                color = [
                    base_color[0] + (height_factor * 0.3) + variation,  # Zwiększony wpływ wysokości
                    base_color[1] + (height_factor * 0.25) + variation,
                    base_color[2] + (height_factor * 0.2) + variation,
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
        # Draw terrain
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def get_vertices(self):
        """
        Returns the vertices array of the terrain.
        Each vertex is represented by 3 float values (x, y, z).
        """
        return self.vertices 