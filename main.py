import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from core.Camera import *
from utils.Settings import *
from core.SandStorm import SandStorm
from components.ground import Ground
from components.terrain import Terrain
from components.sky import Sky
import random

# Performance settings
MAX_PARTICLES = 5000  # Increased maximum particles
PARTICLES_PER_VERTEX = 2  # Reduced particles per vertex for better performance
MAX_VERTICES_PER_FRAME = 30  # Reduced vertices per frame
SAND_GENERATION_INTERVAL = 100  # Increased interval between generations
FPS = 60

def set_2d():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(gui_dimensions[0], gui_dimensions[1],
               gui_dimensions[3], gui_dimensions[2])
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glViewport(0, 0, screen.get_width(), screen.get_height())

def set_3d():
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixf(camera.get_PPM())
    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixf(camera.get_VM())
    glViewport(0, 0, screen.get_width(), screen.get_height())
    
    # Enable depth testing and lighting
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    # Optimized lighting settings
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 25, 0, 1))  # Moved light higher
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))  # Reduced ambient
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.6, 0.6, 0.6, 1))  # Adjusted diffuse
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.1, 0.1, 0.1, 1))  # Reduced specular
    glEnable(GL_LIGHT0)
    
    # Optimized material settings
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.03, 0.03, 0.03, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 8.0)

# Initialize Pygame and OpenGL
pygame.init()
screen_width = math.fabs(window_dimensions[1] - window_dimensions[0])
screen_height = math.fabs(window_dimensions[3] - window_dimensions[2])
pygame.display.set_caption('Sand Storm Simulation')
screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)

# Create camera
camera = Camera(60, (screen_width / screen_height), 0.01, 1000.0)

# Create sky
sky = Sky()

# Create sand storm with optimized initial settings
sand_storm = SandStorm(pygame.Vector3(0, 14, 0), num_particles=0)

# Create ground
ground = Ground()

# Create terrain
terrain = Terrain()

# Timer for continuous sand generation
last_sand_generation = pygame.time.get_ticks()

# Main game loop
clock = pygame.time.Clock()
done = False

# Enable mouse capture
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)
pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

while not done:
    # Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
                done = True
            elif event.key == pygame.K_TAB:
                if pygame.mouse.get_visible():
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    pygame.mouse.set_pos(screen_width // 2, screen_height // 2)
                else:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
            elif event.key == pygame.K_UP:
                sand_storm.set_wind(pygame.Vector3(0, 1, 0))
            elif event.key == pygame.K_DOWN:
                sand_storm.set_wind(pygame.Vector3(0, -1, 0))
            elif event.key == pygame.K_LEFT:
                sand_storm.set_wind(pygame.Vector3(-1, 0, 0))
            elif event.key == pygame.K_RIGHT:
                sand_storm.set_wind(pygame.Vector3(1, 0, 0))

    # Optimized particle generation
    current_time = pygame.time.get_ticks()
    if current_time - last_sand_generation >= SAND_GENERATION_INTERVAL:
        terrain_vertices = terrain.get_vertices()
        
        if len(sand_storm.particles) < MAX_PARTICLES:
            vertices_to_process = min(MAX_VERTICES_PER_FRAME, len(terrain_vertices) // 3)
            vertex_indices = random.sample(range(0, len(terrain_vertices), 3), vertices_to_process)
            
            for i in vertex_indices:
                if len(sand_storm.particles) >= MAX_PARTICLES:
                    break
                x, y, z = terrain_vertices[i:i+3]
                sand_storm.add_particles(PARTICLES_PER_VERTEX, pygame.Vector3(x, y, z))
        
        last_sand_generation = current_time

    # Clear screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Update camera
    camera.update()

    # Set up 3D view
    glPushMatrix()
    set_3d()
    
    # Update and draw sky
    sky.update()
    sky.draw()
    
    # Update and draw sand storm with optimized delta time
    dt = min(clock.get_time() / 1000.0, 1/30)  # Cap delta time to prevent large jumps
    sand_storm.update(dt)
    sand_storm.draw()
    
    # Draw ground and terrain
    ground.draw()
    terrain.draw()
    
    # Draw coordinate axes only when needed (commented out for better performance)
    # glDisable(GL_LIGHTING)
    # glBegin(GL_LINES)
    # glColor3f(1, 0, 0)
    # glVertex3f(0, 0, 0)
    # glVertex3f(1, 0, 0)
    # glColor3f(0, 1, 0)
    # glVertex3f(0, 0, 0)
    # glVertex3f(0, 1, 0)
    # glColor3f(0, 0, 1)
    # glVertex3f(0, 0, 0)
    # glVertex3f(0, 0, 1)
    # glEnd()
    # glEnable(GL_LIGHTING)

    glPopMatrix()

    # Set up 2D view
    set_2d()

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
