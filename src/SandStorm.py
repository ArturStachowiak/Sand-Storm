import pygame
import random
from src.consts import TERRAIN_SIZE
from src.SandParticle import SandParticle

"""
This is a class describing the sandstorm.
It is used to:
- simulate the movement of sand particles in the sandstorm depending on the wind
- draw the sand particles in the sandstorm
- update the sand particles in the sandstorm
- add new particles to the sandstorm
- remove particles that went too far vertically or hit walls twice
- generate new particles from terrain if provided
- update the wind direction and strength
- update the parameters of the sandstorm
- update the particle properties
"""
class SandStorm:
    def __init__(self, position: pygame.Vector3, num_particles: int = 100, max_particles: int = 5000):
        self.position = position
        self.wind = pygame.Vector3(2.0, 1.2, 0.0)  # Default wind direction (right and slightly up)
        self.particles = []
        self.num_particles = num_particles
        
        # Performance settings
        self.MAX_PARTICLES = max_particles
        self.PARTICLES_PER_VERTEX = 2
        self.MAX_VERTICES_PER_FRAME = 30
        self.SAND_GENERATION_INTERVAL = 100
        self.last_sand_generation = pygame.time.get_ticks()
        
        # New parameters
        self.wind_strength = 2.0
        self.wind_turbulence = 0.2
        self.particle_mass = 1.0
        self.particle_lifetime = 5.0
        self.particle_color = 0.5
        self.particle_size = 0.01
        self.sky_intensity = 1.0
        
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

    def set_parameters(self, wind_strength=None, wind_turbulence=None, particle_mass=None, 
                      particle_lifetime=None, particle_color=None, sky_intensity=None, particle_size=None):
        """
        Update storm parameters
        """
        if wind_strength is not None:
            self.wind_strength = wind_strength
            self.MAX_VERTICES_PER_FRAME = round(wind_strength)*30
        if wind_turbulence is not None:
            self.wind_turbulence = wind_turbulence
        if particle_mass is not None:
            self.particle_mass = particle_mass
        if particle_lifetime is not None:
            self.particle_lifetime = particle_lifetime
        if particle_color is not None:
            self.particle_color = particle_color
        if sky_intensity is not None:
            self.sky_intensity = sky_intensity
        if particle_size is not None:
            # Update particle sizes for all particles
            for particle in self.particles:
                if random.random() < 0.9:
                    particle.size = random.uniform(particle_size * 0.2, particle_size * 0.6)
                else:
                    particle.size = random.uniform(particle_size * 0.6, particle_size)

    def update(self, delta_time: float, terrain=None):
        """
        Update all particles in the storm and generate new ones from terrain if provided
        Args:
            delta_time: Time since last update
            terrain: Optional terrain object to generate particles from
        """
        # Update existing particles
        particles_to_remove = set()  # Changed to set for O(1) lookups
        half_terrain = TERRAIN_SIZE // 2
        
        for particle in self.particles:
            if particle.active:
                # Apply wind with turbulence
                wind_with_turbulence = self.wind + pygame.Vector3(
                    random.uniform(-self.wind_turbulence, self.wind_turbulence),
                    random.uniform(-self.wind_turbulence, self.wind_turbulence),
                    random.uniform(-self.wind_turbulence, self.wind_turbulence)
                )
                
                particle.update(wind_with_turbulence, delta_time, self.particle_mass)
                
                # Check if particle is too far vertically
                if abs(particle.position.y - self.position.y) > half_terrain:
                    particles_to_remove.add(particle)
                    continue
                
                # Handle horizontal wrapping (X and Z coordinates)
                if abs(particle.position.x - self.position.x) > half_terrain:
                    if particle.has_wrapped:
                        # If particle has already wrapped once, remove it
                        particles_to_remove.add(particle)
                    else:
                        # Calculate the offset from the center
                        offset = particle.position.x - self.position.x
                        # Wrap to the opposite side
                        particle.position.x = self.position.x - offset
                        particle.has_wrapped = True
                
                if abs(particle.position.z - self.position.z) > half_terrain:
                    if particle.has_wrapped:
                        # If particle has already wrapped once, remove it
                        particles_to_remove.add(particle)
                    else:
                        # Calculate the offset from the center
                        offset = particle.position.z - self.position.z
                        # Wrap to the opposite side
                        particle.position.z = self.position.z - offset
                        particle.has_wrapped = True
        
        # Remove particles that went too far vertically or hit walls twice
        self.particles = [p for p in self.particles if p not in particles_to_remove]
        self.num_particles = len(self.particles)

        # Generate new particles from terrain if provided
        if terrain is not None:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_sand_generation >= self.SAND_GENERATION_INTERVAL:
                terrain_vertices = terrain.get_vertices()
                
                if len(self.particles) < self.MAX_PARTICLES:
                    vertices_to_process = min(self.MAX_VERTICES_PER_FRAME, len(terrain_vertices) // 3)
                    vertex_indices = random.sample(range(0, len(terrain_vertices), 3), vertices_to_process)
                    
                    for i in vertex_indices:
                        if len(self.particles) >= self.MAX_PARTICLES:
                            break
                        x, y, z = terrain_vertices[i:i+3]
                        self.add_particles(self.PARTICLES_PER_VERTEX, pygame.Vector3(x, y, z))
                
                self.last_sand_generation = current_time

    def draw(self):
        """
        Draw all active particles
        """
        for particle in self.particles:
            if particle.active:
                particle.draw(self.particle_color)

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
            self.particles.append(SandParticle(particle_pos, self.particle_size))
            self.num_particles += 1

    def set_max_particles(self, max_particles: int):
        """
        Update the maximum number of particles allowed in the storm
        Args:
            max_particles: New maximum number of particles
        """
        self.MAX_PARTICLES = max_particles
        # Remove excess particles if necessary
        while len(self.particles) > self.MAX_PARTICLES:
            self.particles.pop()
            self.num_particles -= 1

    def update_particle_properties(self,
                                 particle_lifetime=None,
                                 particle_color=None,
                                 particle_size=None):
        if particle_lifetime is not None:
            self.particle_lifetime = particle_lifetime
        if particle_color is not None:
            self.particle_color = particle_color 
        if particle_size is not None:
            self.particle_size = particle_size