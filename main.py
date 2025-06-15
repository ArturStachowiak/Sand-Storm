import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from src.Camera import *
from src.consts import *
from src.SandStorm import SandStorm
from src.Ground import Ground
from src.Terrain import Terrain
from src.Sky import Sky
from src.Slider import Slider, draw_text
import random



# Performance settings
FPS = 60

# Control panel dimensions
PANEL_WIDTH = 300
PANEL_PADDING = 20
SLIDER_WIDTH = 200
SLIDER_HEIGHT = 20

# Calculate dynamic spacing based on screen height
def calculate_spacing():
    screen_height = math.fabs(window_dimensions[3] - window_dimensions[2])
    
    # Calculate spacing as percentages of screen height
    slider_spacing = int(screen_height * 0.06) 
    group_spacing = int(screen_height * 0.22)  
    start_y = int(screen_height * 0.12)  
    
    return slider_spacing, group_spacing, start_y

# Initialize spacing
SLIDER_SPACING, GROUP_SPACING, START_Y = calculate_spacing()

# Initialize sliders
# Wind parameters
wind_slider = Slider(PANEL_PADDING, START_Y, SLIDER_WIDTH, SLIDER_HEIGHT, 0, 360, 0, is_wind_slider=True)
wind_strength_slider = Slider(PANEL_PADDING, START_Y + SLIDER_SPACING, SLIDER_WIDTH, SLIDER_HEIGHT, 0.1, 10.0, 2.0)

# Particle parameters
particle_count_slider = Slider(PANEL_PADDING, START_Y + GROUP_SPACING, SLIDER_WIDTH, SLIDER_HEIGHT, 0, 100000, 1000, is_count_slider=True)
particle_mass_slider = Slider(PANEL_PADDING, START_Y + GROUP_SPACING + SLIDER_SPACING, SLIDER_WIDTH, SLIDER_HEIGHT, 0.1, 2.0, 1.0)
particle_lifetime_slider = Slider(PANEL_PADDING, START_Y + GROUP_SPACING + SLIDER_SPACING * 2, SLIDER_WIDTH, SLIDER_HEIGHT, 1.0, 10.0, 1.0)

# Visual parameters
sky_r_slider = Slider(PANEL_PADDING, START_Y + GROUP_SPACING * 2 + SLIDER_SPACING * 1, SLIDER_WIDTH, SLIDER_HEIGHT, 0, 255, 26, is_sky_rgb=True)  # 0.1 * 255
sky_g_slider = Slider(PANEL_PADDING, START_Y + GROUP_SPACING * 2 + SLIDER_SPACING * 2, SLIDER_WIDTH, SLIDER_HEIGHT, 0, 255, 51, is_sky_rgb=True)  # 0.2 * 255
sky_b_slider = Slider(PANEL_PADDING, START_Y + GROUP_SPACING * 2 + SLIDER_SPACING * 3, SLIDER_WIDTH, SLIDER_HEIGHT, 0, 255, 102, is_sky_rgb=True)  # 0.4 * 255

def draw_control_panel():
    # Disable lighting for UI elements
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Draw white background panel
    glColor3f(1.0, 0.95, 0.9)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(PANEL_WIDTH, 0)
    glVertex2f(PANEL_WIDTH, screen_height)
    glVertex2f(0, screen_height)
    glEnd()

    # Draw group headers and sliders
    # Wind parameters
    glColor3f(0.0, 0.0, 0.0)  # Black color for text
    draw_text("Wind Parameters", PANEL_PADDING, START_Y - 40, font_size=24)
    wind_slider.draw()
    glColor3f(0.0, 0.0, 0.0)  # Reset to black after slider
    draw_text("Wind Direction", PANEL_PADDING, START_Y - 8, font_size=18)
    wind_strength_slider.draw()
    glColor3f(0.0, 0.0, 0.0)  # Reset to black after slider
    draw_text("Wind Strength", PANEL_PADDING, START_Y + SLIDER_SPACING - 8, font_size=18)

    # Particle parameters
    glColor3f(0.0, 0.0, 0.0)  # Black color for text
    draw_text("Particle Parameters", PANEL_PADDING, START_Y + GROUP_SPACING - 40, font_size=24)
    particle_count_slider.draw()
    glColor3f(0.0, 0.0, 0.0)  # Reset to black after slider
    draw_text("Particle Count", PANEL_PADDING, START_Y + GROUP_SPACING - 8, font_size=18)
    particle_mass_slider.draw()
    glColor3f(0.0, 0.0, 0.0)  # Reset to black after slider
    draw_text("Particle Mass", PANEL_PADDING, START_Y + GROUP_SPACING + SLIDER_SPACING  - 8, font_size=18)
    particle_lifetime_slider.draw()
    glColor3f(0.0, 0.0, 0.0)  # Reset to black after slider
    draw_text("Particle Lifetime", PANEL_PADDING, START_Y + GROUP_SPACING + SLIDER_SPACING * 2 - 8, font_size=18)

    # Visual parameters
    glColor3f(0.0, 0.0, 0.0)  # Black color for text
    draw_text("Visual Parameters", PANEL_PADDING, START_Y + GROUP_SPACING * 2, font_size=24)
    
    # Sky color sliders
    sky_r_slider.draw()
    glColor3f(0.0, 0.0, 0.0)
    draw_text(f"Sky Red: {int(sky_r_slider.value)}", PANEL_PADDING, START_Y + GROUP_SPACING * 2 + SLIDER_SPACING * 1 - 8, font_size=18)
    sky_g_slider.draw()
    glColor3f(0.0, 0.0, 0.0)
    draw_text(f"Sky Green: {int(sky_g_slider.value)}", PANEL_PADDING, START_Y + GROUP_SPACING * 2 + SLIDER_SPACING * 2 - 8, font_size=18)
    sky_b_slider.draw()
    glColor3f(0.0, 0.0, 0.0)
    draw_text(f"Sky Blue: {int(sky_b_slider.value)}", PANEL_PADDING, START_Y + GROUP_SPACING * 2 + SLIDER_SPACING * 3 - 8, font_size=18)

    draw_text("Sterowanie:", PANEL_PADDING, 650, font_size=18)
    draw_text("W - Przód", PANEL_PADDING, 670, font_size=18)
    draw_text("A - Lewo", PANEL_PADDING, 690, font_size=18)
    draw_text("S - Tył", PANEL_PADDING, 710, font_size=18)
    draw_text("D - Prawo", PANEL_PADDING, 730, font_size=18)
    draw_text("Q - obrót w lewo", PANEL_PADDING + 100, 670, font_size=18)
    draw_text("E - obrót w prawo", PANEL_PADDING + 100, 690, font_size=18)
    draw_text("Shift - W dół", PANEL_PADDING + 100, 710, font_size=18)
    draw_text("Space - W górę", PANEL_PADDING + 100, 730, font_size=18)
    draw_text("Esc - Wyjście", PANEL_PADDING + 100, 750, font_size=18)
    draw_text("Tab - Pokaż/ukryj kursor", PANEL_PADDING + 100, 770, font_size=18)

    
    # Re-enable lighting and depth testing
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

def set_2d():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, screen_width, screen_height, 0)
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


camera = Camera(60, (screen_width / screen_height), 0.01, 1000.0)

sky = Sky()

sand_storm = SandStorm(pygame.Vector3(0, 14, 0), num_particles=0, max_particles=particle_count_slider.value)

ground = Ground()

terrain = Terrain()

# Main game loop
clock = pygame.time.Clock()
done = False


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
        
        # Handle slider events
        wind_slider.handle_event(event)
        wind_strength_slider.handle_event(event)
        particle_count_slider.handle_event(event)
        particle_mass_slider.handle_event(event)
        particle_lifetime_slider.handle_event(event)
        sky_r_slider.handle_event(event)
        sky_g_slider.handle_event(event)
        sky_b_slider.handle_event(event)
        
        # Update sand storm parameters based on slider values
        angle = math.radians(wind_slider.value)
        wind_direction = pygame.Vector3(math.cos(angle), 0, math.sin(angle)) * wind_strength_slider.value
        sand_storm.set_wind(wind_direction)
        sand_storm.set_max_particles(int(particle_count_slider.value))
        
        # Update all other parameters
        sand_storm.set_parameters(
            wind_strength=wind_strength_slider.value,
            particle_mass=particle_mass_slider.value,
            particle_lifetime=particle_lifetime_slider.value,
        )

    # Clear screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    
    camera.update()

    
    glPushMatrix()
    set_3d()
    
    # Update and draw sand storm with optimized delta time
    dt = min(clock.get_time() / 1000.0, 1/30)  
    sand_storm.update(dt, terrain)
    sand_storm.draw()
    
    # Update sky colors
    sky.update_colors(sky_r_slider.value, sky_g_slider.value, sky_b_slider.value)
    
    # Draw ground and terrain
    sky.draw()
    ground.draw()
    terrain.draw()
    
    glPopMatrix()

    
    set_2d()
    draw_control_panel()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
