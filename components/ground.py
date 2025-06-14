import numpy as np
import random
from OpenGL.GL import *
from config.settings import *

class Ground:
    def __init__(self):
        # Bazowe kolory piasku - zredukowana paleta
        self.sand_colors = [
            [0.55, 0.27, 0.07],  # Ciemny brąz
            [0.65, 0.35, 0.15],  # Średni brąz
            [0.75, 0.45, 0.25],  # Jasny brąz
        ]
        
        # Rozmiar podłoża
        size = TERRAIN_SIZE * 1.5
        resolution = TERRAIN_RESOLUTION // 2
        
        # Generowanie wierzchołków i kolorów dla podłoża
        vertices = []
        colors = []
        indexes = []
        
        # Generowanie siatki podłoża
        for i in range(resolution):
            for j in range(resolution):
                # Pozycja wierzchołka - poprawione centrowanie
                x = (i / (resolution - 1) - 0.5) * size
                z = (j / (resolution - 1) - 0.5) * size
                y = -TERRAIN_HEIGHT
                
                vertices.extend([x, y, z])
                
                # Generowanie koloru z mniejszą wariacją
                base_color = random.choice(self.sand_colors)
                variation = random.uniform(-0.1, 0.1)
                
                color = [
                    max(0, min(1, base_color[0] + variation)),
                    max(0, min(1, base_color[1] + variation)),
                    max(0, min(1, base_color[2] + variation)),
                    1.0
                ]
                colors.extend(color)
        
        # Generowanie indeksów dla trójkątów
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                v0 = i * resolution + j
                v1 = v0 + 1
                v2 = (i + 1) * resolution + j
                v3 = v2 + 1
                
                indexes.extend([v0, v1, v2, v1, v3, v2])
        
        # Konwersja na tablice numpy
        self.vertices = np.array(vertices, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)
        self.indexes = np.array(indexes, dtype=np.uint32)
        
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
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indexes.nbytes, self.indexes, GL_STATIC_DRAW)
        
        glBindVertexArray(0)
    
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indexes), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def get_vertices(self):
        """Returns the vertices array of the ground."""
        return self.vertices 