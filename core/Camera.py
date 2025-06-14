import pygame
import math
import numpy as np
from core.Transform import *

class Camera:
    def __init__(self, fovy, aspect, near, far):
        # Macierz projekcji perspektywicznej
        f = 1/math.tan(math.radians(fovy/2))
        a = f/aspect
        b = f
        c = (far + near) / (near - far)
        d = 2 * near * far / (near - far)
        self.PPM = np.matrix([
            [a, 0, 0, 0],
            [0, b, 0, 0],
            [0, 0, c, -1],
            [0, 0, d, 0]
        ])
        
        # Macierz widoku kamery
        self.view_matrix = np.identity(4)
        self.position = pygame.Vector3(0, 0, 5)  # Pozycja początkowa kamery
        
        # Wektory orientacji kamery
        self.forward = pygame.Vector3(0, 0, -1)  # Kierunek "do przodu"
        self.up = pygame.Vector3(0, 1, 0)        # Kierunek "w górę"
        self.right = pygame.Vector3(1, 0, 0)     # Kierunek "w prawo"
        
        self.move_speed = 0.1
        self.rotate_speed = 2.0
        
        # Inicjalizacja macierzy widoku
        self.update_view_matrix()

    def update_view_matrix(self):
        # Normalizacja wektorów
        self.forward = self.forward.normalize()
        self.right = self.right.normalize()
        self.up = self.up.normalize()
        
        # Tworzenie macierzy widoku
        self.view_matrix = np.matrix([
            [self.right.x, self.right.y, self.right.z, 0],
            [self.up.x, self.up.y, self.up.z, 0],
            [self.forward.x, self.forward.y, self.forward.z, 0],
            [0, 0, 0, 1]
        ])
        
        # Dodanie translacji
        T = np.matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-self.position.x, -self.position.y, -self.position.z, 1]
        ])
        
        self.view_matrix = T @ self.view_matrix

    def rotate_yaw(self, angle):
        # Obrót wokół osi Y (yaw)
        rad = math.radians(angle)
        cos = math.cos(rad)
        sin = math.sin(rad)
        
        # Obrót wektorów forward i right
        new_forward = pygame.Vector3(
            self.forward.x * cos - self.forward.z * sin,
            self.forward.y,
            self.forward.x * sin + self.forward.z * cos
        )
        
        new_right = pygame.Vector3(
            self.right.x * cos - self.right.z * sin,
            self.right.y,
            self.right.x * sin + self.right.z * cos
        )
        
        self.forward = new_forward
        self.right = new_right
        self.up = self.forward.cross(self.right)
        self.update_view_matrix()

    def rotate_pitch(self, angle):
        # Obrót wokół osi X (pitch)
        rad = math.radians(angle)
        cos = math.cos(rad)
        sin = math.sin(rad)
        
        # Obrót wektorów forward i up
        new_forward = pygame.Vector3(
            self.forward.x,
            self.forward.y * cos - self.forward.z * sin,
            self.forward.y * sin + self.forward.z * cos
        )
        
        new_up = pygame.Vector3(
            self.up.x,
            self.up.y * cos - self.up.z * sin,
            self.up.y * sin + self.up.z * cos
        )
        
        self.forward = new_forward
        self.up = new_up
        self.right = self.forward.cross(self.up)
        self.update_view_matrix()

    def move_forward(self, amount):
        self.position += self.forward * amount
        self.update_view_matrix()

    def move_right(self, amount):
        self.position += self.right * amount
        self.update_view_matrix()

    def move_up(self, amount):
        self.position += self.up * amount
        self.update_view_matrix()

    def update(self):
        key = pygame.key.get_pressed()
        
        # Ruch do przodu/tyłu
        if key[pygame.K_UP]:
            self.move_forward(self.move_speed)
        if key[pygame.K_DOWN]:
            self.move_forward(-self.move_speed)
            
        # Ruch w lewo/prawo (przesunięcie)
        if key[pygame.K_COMMA]:  # <
            self.move_right(-self.move_speed)
        if key[pygame.K_PERIOD]:  # >
            self.move_right(self.move_speed)
            
        # Ruch w górę/dół
        if key[pygame.K_SPACE]:
            self.move_up(self.move_speed)
        if key[pygame.K_LSHIFT]:
            self.move_up(-self.move_speed)
            
        # Rotacja wokół osi Y (yaw)
        if key[pygame.K_LEFT]:
            self.rotate_yaw(self.rotate_speed)
        if key[pygame.K_RIGHT]:
            self.rotate_yaw(-self.rotate_speed)
            
        # Rotacja wokół osi X (pitch)
        if key[pygame.K_q]:
            self.rotate_pitch(self.rotate_speed)
        if key[pygame.K_e]:
            self.rotate_pitch(-self.rotate_speed)

    def get_VM(self):
        return self.view_matrix

    def get_PPM(self):
        return self.PPM

    def get_position(self):
        return self.position