import numpy as np
import random
from OpenGL.GL import *
from src.consts import *
"""
This is a class describing the ground.
It is used to:
- generate the vertices and colors for the ground
- draw the ground
- get the vertices of the ground
"""
class Ground:
    def __init__(self):
        # various colors of sand
        self.sand_colors = [
            [0.90, 0.85, 0.65],  
            [0.75, 0.55, 0.35],  
            [0.65, 0.60, 0.45],  
            [0.85, 0.70, 0.40],  
            [0.70, 0.80, 0.60],  
            [0.80, 0.60, 0.30],  
        ]
        
        
        self.vertices = []
        self.colors = []
        self.indices = []
        
        size = TERRAIN_SIZE 
        resolution = TERRAIN_RESOLUTION // 2  
        
        #generating the ground
        for i in range(resolution):
            for j in range(resolution):
                
                x = (i / resolution - 0.5) * size
                z = (j / resolution - 0.5) * size
                y = -TERRAIN_HEIGHT * 0.5  # Położenie pod terenem
                
                #adding the vertices
                self.vertices.extend([x, y, z])
                
                # generating the colors with random variation
                base_color = random.choice(self.sand_colors)
                variation = random.uniform(-0.2, 0.2)
                
                color = [
                    base_color[0] + variation,
                    base_color[1] + variation,
                    base_color[2] + variation,
                    1.0
                ]
                
                # reducing color values
                color = [max(0, min(1, c)) for c in color]
                self.colors.extend(color)
        
        # generating the indices for the triangles
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                v0 = i * resolution + j
                v1 = v0 + 1
                v2 = (i + 1) * resolution + j
                v3 = v2 + 1
                
                self.indices.extend([v0, v1, v2])
                self.indices.extend([v1, v3, v2])
        
        # converting to numpy arrays
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)
        
        # Creating vao, vbo, cbo and ibo - they are used to draw the ground
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.cbo = glGenBuffers(1)
        self.ibo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        
        # vertices buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        # colors buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)
        
        # indices buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        glBindVertexArray(0)
    
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def get_vertices(self):
        """Returns the vertices array of the ground."""
        return self.vertices 