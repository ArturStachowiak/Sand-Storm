import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from core.Camera import *
from utils.Settings import *
from core.SandStorm import SandStorm

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
    glLoadMatrixf(camera.get_VM())  # Używamy macierzy widoku kamery
    glViewport(0, 0, screen.get_width(), screen.get_height())
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 5, 0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
    glEnable(GL_LIGHT0)

# Initialize Pygame and OpenGL
pygame.init()
screen_width = math.fabs(window_dimensions[1] - window_dimensions[0])
screen_height = math.fabs(window_dimensions[3] - window_dimensions[2])
pygame.display.set_caption('Sand Storm Simulation')
screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)

# Create camera
camera = Camera(60, (screen_width / screen_height), 0.1, 1000.0)

# Create sand storm
sand_storm = SandStorm(pygame.Vector3(0, 0, -5), num_particles=100)

# Timer for continuous sand generation
SAND_GENERATION_INTERVAL = 1000  # milliseconds
last_sand_generation = pygame.time.get_ticks()

# Main game loop
clock = pygame.time.Clock()
fps = 60
done = False

while not done:
    # Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            elif event.key == pygame.K_w:
                # Change wind direction
                sand_storm.set_wind(pygame.Vector3(0, 1, 0))  # Up
            elif event.key == pygame.K_s:
                sand_storm.set_wind(pygame.Vector3(0, -1, 0))  # Down
            elif event.key == pygame.K_a:
                sand_storm.set_wind(pygame.Vector3(-1, 0, 0))  # Left
            elif event.key == pygame.K_d:
                sand_storm.set_wind(pygame.Vector3(1, 0, 0))  # Right

    # Generate new sand particles every second
    current_time = pygame.time.get_ticks()
    if current_time - last_sand_generation >= SAND_GENERATION_INTERVAL:
        sand_storm.add_particles(10)  # Add 10 particles every second
        last_sand_generation = current_time

    # Clear screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Update camera
    camera.update()

    # Set up 3D view
    glPushMatrix()  # Zachowujemy stan macierzy
    set_3d()
    
    # Update and draw sand storm
    dt = clock.get_time() / 1000.0  # Convert to seconds
    sand_storm.update(dt)
    sand_storm.draw()
    
    # Draw coordinate axes for reference
    glBegin(GL_LINES)
    # X axis (red)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(1, 0, 0)
    # Y axis (green)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 1, 0)
    # Z axis (blue)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1)
    glEnd()

    glPopMatrix()  # Przywracamy stan macierzy

    # Set up 2D view (for UI if needed)
    set_2d()

    # Update display
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
