import pygame
import random
from config.settings import TERRAIN_SIZE
from core.SandParticle import SandParticle

class SandStorm:
    def __init__(self, position: pygame.Vector3, num_particles: int = 100):
        self.position = position
        self.wind = pygame.Vector3(2.0, 1.2, 0.0)  # Default wind direction (right and slightly up)
        self.particles = []
        self.num_particles = num_particles
        
        # Initialize particles
        self._initialize_particles()

    def _initialize_particles(self):
        """
        Create initial set of particles around the storm's position
        """
        for _ in range(self.num_particles):
            # Random position within a sphere around the storm's position
            offset = pygame.Vector3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ).normalize() * random.uniform(0, 2)
            
            particle_pos = self.position + offset
            self.particles.append(SandParticle(particle_pos))

    def set_wind(self, wind_vector: pygame.Vector3):
        """
        Set the wind direction and strength
        Args:
            wind_vector: Vector3 representing wind direction and magnitude
        """
        self.wind = wind_vector

    def update(self, delta_time: float):
        """
        Update all particles in the storm
        Args:
            delta_time: Time since last update
        """
        particles_to_remove = []
        half_terrain = TERRAIN_SIZE * 1.5 // 2
        
        for particle in self.particles:
            if particle.active:
                particle.update(self.wind, delta_time)
                
                # Check if particle is too far vertically
                if abs(particle.position.y - self.position.y) > half_terrain:
                    particles_to_remove.append(particle)
                    continue
                
                # Handle horizontal wrapping (X and Z coordinates)
                if abs(particle.position.x - self.position.x) > half_terrain:
                    if particle.has_wrapped:
                        # If particle has already wrapped once, remove it
                        particles_to_remove.append(particle)
                    else:
                        # Calculate the offset from the center
                        offset = particle.position.x - self.position.x
                        # Wrap to the opposite side
                        particle.position.x = self.position.x - offset
                        particle.has_wrapped = True
                
                if abs(particle.position.z - self.position.z) > half_terrain:
                    if particle.has_wrapped:
                        # If particle has already wrapped once, remove it
                        particles_to_remove.append(particle)
                    else:
                        # Calculate the offset from the center
                        offset = particle.position.z - self.position.z
                        # Wrap to the opposite side
                        particle.position.z = self.position.z - offset
                        particle.has_wrapped = True
        
        # Remove particles that went too far vertically or hit walls twice
        for particle in particles_to_remove:
            self.particles.remove(particle)
            self.num_particles -= 1

    def draw(self):
        """
        Draw all active particles
        """
        for particle in self.particles:
            if particle.active:
                particle.draw()

    def add_particles(self, num_particles: int, spawn_point: pygame.Vector3 = None):
        """
        Add new particles to the storm
        Args:
            num_particles: Number of particles to add
            spawn_point: Optional Vector3 point where particles should spawn. If None, uses storm's position
        """
        spawn_position = spawn_point if spawn_point is not None else self.position
        
        for _ in range(num_particles):
            offset = pygame.Vector3(
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5)
            ).normalize() * random.uniform(0, 1)
            
            particle_pos = spawn_position + offset
            self.particles.append(SandParticle(particle_pos))
            self.num_particles += 1 