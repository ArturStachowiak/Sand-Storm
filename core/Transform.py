import pygame
import math
import numpy as np

class Transform:
    def __init__(self):
        self.MVM = np.identity(4)
    def get_MVM(self):
        return self.MVM
    def update_position(self, position):
        self.MVM = self.MVM @ np.matrix([
                                        [1, 0, 0, 0],
                                        [0, 1, 0, 0],
                                        [0, 0, 1, 0],
                                        [position.x, position.y, position.z, 1]
                                        ])
    def update_scale(self, amount: pygame.Vector3):
        self.MVM = self.MVM @ np.matrix([
                                        [amount.x, 0, 0, 0],
                                        [0, amount.y, 0, 0],
                                        [0, 0, amount.z, 0],
                                        [0, 0, 0, 1]
                                        ])
    def rotate_x(self, amount):
        amount = math.radians(amount)
        self.MVM = self.MVM @ np.matrix([
                                        [1, 0, 0, 0],
                                        [0, math.cos(amount), math.sin(amount), 0],
                                        [0, -math.sin(amount), math.cos(amount), 0],
                                        [0, 0, 0, 1]
                                        ])
    def rotate_y(self, amount):
        amount = math.radians(amount)
        self.MVM = self.MVM @ np.matrix([
                                        [math.cos(amount), 0, -math.sin(amount), 0],
                                        [0, 1, 0, 0],
                                        [math.sin(amount), 0, math.cos(amount), 0],
                                        [0, 0, 0, 1]
                                        ])
    def rotate_z(self, amount):
        amount = math.radians(amount)
        self.MVM = self.MVM @ np.matrix([
                                        [math.cos(amount), math.sin(amount), 0, 0],
                                        [-math.sin(amount), math.cos(amount), 0, 0],
                                        [0, 0, 1, 0],
                                        [0, 0, 0, 1]
                                        ])
    def get_position(self):
        return pygame.Vector3(self.MVM[0,3], self.MVM[1,3], self.MVM[2,3])
    def get_scale(self):
        return pygame.Vector3(self.get_MVM()[0,0], self.MVM[1,1], self.MVM[2,2])
    def get_rotation(self):
        rot_matrix = self.MVM[:3, :3]
        yaw = math.atan2(rot_matrix[1, 0], rot_matrix[0, 0])
        pitch = math.atan2(-rot_matrix[2, 0], math.sqrt(rot_matrix[2, 1]**2 + rot_matrix[2, 2]**2))
        roll = math.atan2(rot_matrix[2, 1], rot_matrix[2, 2])
        return (
            math.degrees(roll),
            math.degrees(pitch),
            math.degrees(yaw)
        )