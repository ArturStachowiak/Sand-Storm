import pygame
import math
import numpy as np

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
        self.position = pygame.Vector3(0, 15, 20)  # Adjusted position for better centering
        
        # Kąty rotacji kamery
        self.yaw = 0.0    # Obrót wokół osi Y
        self.pitch = 0.0  # Obrót wokół osi X
        
        self.move_speed = 0.1
        self.rotate_speed = 2.0
        self.mouse_sensitivity = 0.1
        
        # Inicjalizacja macierzy widoku
        self.update_view_matrix()

    def update_view_matrix(self):
        # Tworzenie macierzy rotacji
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        
        # Macierz rotacji wokół osi Y (yaw)
        cos_yaw = math.cos(yaw_rad)
        sin_yaw = math.sin(yaw_rad)
        
        # Macierz rotacji wokół osi X (pitch)
        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)
        
        # Łączenie rotacji
        self.view_matrix = np.matrix([
            [cos_yaw, sin_yaw * sin_pitch, sin_yaw * cos_pitch, 0],
            [0, cos_pitch, -sin_pitch, 0],
            [-sin_yaw, cos_yaw * sin_pitch, cos_yaw * cos_pitch, 0],
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

    def update(self):
        key = pygame.key.get_pressed()
        
        # Obsługa myszy
        if not pygame.mouse.get_visible():  # jeśli kursor jest "złapany"
            mouse_pos = pygame.mouse.get_pos()
            screen = pygame.display.get_surface()
            center_x = screen.get_width() // 2
            center_y = screen.get_height() // 2
            
            # Oblicz różnicę od środka ekranu
            dx = mouse_pos[0] - center_x
            dy = mouse_pos[1] - center_y
            
            if dx != 0 or dy != 0:
                # Obrót kamery
                self.yaw -= dx * self.mouse_sensitivity
                self.pitch -= dy * self.mouse_sensitivity
                
                # Ograniczenie kąta pitch
                self.pitch = max(-89.0, min(89.0, self.pitch))
                
                # Przywróć kursor do środka
                pygame.mouse.set_pos(center_x, center_y)
        
        # Oblicz wektory kierunkowe kamery w przestrzeni świata
        forward = pygame.Vector3(
            self.view_matrix[0, 2],
            self.view_matrix[1, 2],
            self.view_matrix[2, 2]
        )
        right = pygame.Vector3(
            self.view_matrix[0, 0],
            self.view_matrix[1, 0],
            self.view_matrix[2, 0]
        )
        
        # Ruch do przodu/tyłu
        if key[pygame.K_w]:
            self.position -= forward * self.move_speed
        if key[pygame.K_s]:
            self.position += forward * self.move_speed
            
        # Ruch w lewo/prawo
        if key[pygame.K_a]:
            self.position -= right * self.move_speed
        if key[pygame.K_d]:
            self.position += right * self.move_speed
            
        # Ruch w górę/dół
        if key[pygame.K_SPACE]:
            self.position += pygame.Vector3(0, 1, 0) * self.move_speed
        if key[pygame.K_LSHIFT]:
            self.position -= pygame.Vector3(0, 1, 0) * self.move_speed
            
        # Rotacja wokół osi Y (yaw)
        if key[pygame.K_q]:
            self.yaw += self.rotate_speed
        if key[pygame.K_e]:
            self.yaw -= self.rotate_speed
            
        self.update_view_matrix()

    def get_VM(self):
        return self.view_matrix

    def get_PPM(self):
        return self.PPM

    def get_position(self):
        return self.position