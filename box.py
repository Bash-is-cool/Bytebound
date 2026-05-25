import pygame
import math
import cv2
import numpy as np
import random
import string
from Box2D import b2World, b2PolygonShape

# -----------------------------
# SETTINGS
# -----------------------------
PPM = 20.0
TIME_STEP = 1.0 / 60
VEL_ITERS = 6
POS_ITERS = 2

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900

WHITE = (255, 255, 255)
BLUE = (50, 120, 255)
GREEN = (50, 220, 100)
RED = (255, 50, 50)  # Color to visualize accurate debug hitboxes

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Box2D Accurate Letter Physics")

font = pygame.font.SysFont("comic_sans", 3 * int(PPM), bold=True)
clock = pygame.time.Clock()

# -----------------------------
# BOX2D WORLD
# -----------------------------
world = b2World(gravity=(0, -10), doSleep=True)

# Ground
ground = world.CreateStaticBody(
    position=(SCREEN_WIDTH / (2 * PPM), 1),
    shapes=b2PolygonShape(box=(SCREEN_WIDTH / (2 * PPM), 1)),
)

# Walls
left = world.CreateStaticBody(
    position=(0, SCREEN_HEIGHT / (2 * PPM)),
    shapes=b2PolygonShape(box=(1, SCREEN_HEIGHT / (2 * PPM))),
)

right = world.CreateStaticBody(
    position=(SCREEN_WIDTH / PPM, SCREEN_HEIGHT / (2 * PPM)),
    shapes=b2PolygonShape(box=(1, SCREEN_HEIGHT / (2 * PPM))),
)

letters = []

# -----------------------------
# ACCURATE LETTER → MULTI-FIXTURE POLYGON
# -----------------------------
# -----------------------------
# FIXED LETTER → POLYGON FUNCTION
# -----------------------------
def create_letter_body(world, char, x, y):
    surface = font.render(char, True, (255, 255, 255))
    mask = pygame.mask.from_surface(surface)
    outline = mask.outline()

    if len(outline) < 3:
        return None

    pts = np.array(outline, dtype=np.int32)

    epsilon = 2.5 
    approx = cv2.approxPolyDP(pts, epsilon, True)
    verts_raw = approx[:, 0, :]

    w, h = surface.get_width(), surface.get_height()

    vertices = []
    for p in verts_raw:
        vx = (p[0] - w / 2) / PPM
        vy = -(p[1] - h / 2) / PPM
        vertices.append((vx, vy))

    if len(vertices) < 3:
        return None

    body = world.CreateDynamicBody(position=(x, y))

    # Center-fan decomposition
    center_x = sum(v[0] for v in vertices) / len(vertices)
    center_y = sum(v[1] for v in vertices) / len(vertices)
    center = (center_x, center_y)

    for i in range(len(vertices)):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % len(vertices)]
        triangle = [center, v1, v2]
        
        area = (v1[0] - center_x) * (v2[1] - center_y) - (v2[0] - center_x) * (v1[1] - center_y)
        if abs(area) > 0.01:
            if area < 0:
                triangle = [center, v2, v1]
            try:
                body.CreatePolygonFixture(vertices=triangle, density=1.0, friction=0.3)
            except:
                continue

    if len(body.fixtures) == 0:
        world.DestroyBody(body)
        return None

    # !!! CRITICAL ADDITION !!!
    # Force Box2D to align its internal mass center based on the shapes we attached
    body.ResetMassData()

    return body

# -----------------------------
# FIXED DRAW FUNCTION
# -----------------------------
def draw_letter(body, char):
    # 1. Get the real world coordinates of the body's center of mass
    world_center = body.worldCenter
    x = world_center.x * PPM
    y = SCREEN_HEIGHT - (world_center.y * PPM)
    
    # 2. Render and rotate the text surface
    angle_degrees = math.degrees(body.angle)
    text = font.render(char, True, BLUE)
    rotated = pygame.transform.rotate(text, angle_degrees)
    
    # 3. Calculate the local offset between the surface's visual center 
    # and Box2D's physical center of mass
    local_center = body.localCenter
    
    # Rotate the local offset vector to match the body's current orientation
    cos_a = math.cos(body.angle)
    sin_a = math.sin(body.angle)
    
    # Box2D Y goes up, Pygame Y goes down, so negate the Y translation
    rotated_offset_x = (local_center.x * cos_a - local_center.y * sin_a) * PPM
    rotated_offset_y = (local_center.x * sin_a + local_center.y * cos_a) * PPM
    
    # 4. Shift the final blit target to neutralize the offset
    draw_x = x - rotated_offset_x
    draw_y = y + rotated_offset_y

    rect = rotated.get_rect(center=(draw_x, draw_y))
    screen.blit(rotated, rect)

# -----------------------------
# STRING → MULTI-FIXTURE METHOD
# -----------------------------
def create_word_body(world, text_string, x, y):
    if not text_string:
        return None

    # Create a single physical container for the entire word
    body = world.CreateDynamicBody(position=(x, y))

    # We need to measure character dimensions to calculate horizontal offsets
    space_width = font.metrics(" ")[0][4] if font.metrics(" ") else 30
    current_offset_x = 0.0

    # First Pass: Pre-calculate total width to center the word's origin point
    total_width = 0
    for char in text_string:
        if char == " ":
            total_width += space_width
        else:
            char_surface = font.render(char, True, (255, 255, 255))
            total_width += char_surface.get_width()
    
    half_total_width_meters = (total_width / 2) / PPM

    # Second Pass: Trace and attach each letter's fixtures to the body
    for char in text_string:
        if char == " ":
            current_offset_x += space_width / PPM
            continue

        char_surface = font.render(char, True, (255, 255, 255))
        w = char_surface.get_width()
        h = char_surface.get_height()

        mask = pygame.mask.from_surface(char_surface)
        outline = mask.outline()

        if len(outline) < 3:
            current_offset_x += w / PPM
            continue

        pts = np.array(outline, dtype=np.int32)
        epsilon = 2.5
        approx = cv2.approxPolyDP(pts, epsilon, True)
        verts_raw = approx[:, 0, :]

        # Convert raw pixel vertices to Box2D coordinates.
        # Shift each letter horizontally by current_offset_x, 
        # and subtract half_total_width_meters so the entire word rotates around its true center.
        vertices = []
        for p in verts_raw:
            vx = ((p[0] - w / 2) / PPM) + current_offset_x - half_total_width_meters
            vy = -(p[1] - h / 2) / PPM
            vertices.append((vx, vy))

        if len(vertices) >= 3:
            # Triangulate this specific letter
            center_x = sum(v[0] for v in vertices) / len(vertices)
            center_y = sum(v[1] for v in vertices) / len(vertices)
            center = (center_x, center_y)

            for i in range(len(vertices)):
                v1 = vertices[i]
                v2 = vertices[(i + 1) % len(vertices)]
                triangle = [center, v1, v2]
                
                area = (v1[0] - center_x) * (v2[1] - center_y) - (v2[0] - center_x) * (v1[1] - center_y)
                if abs(area) > 0.01:
                    if area < 0:
                        triangle = [center, v2, v1]
                    try:
                        body.CreatePolygonFixture(vertices=triangle, density=1.0, friction=0.3)
                    except:
                        continue

        # Move the cursor forward for the next letter
        current_offset_x += w / PPM

    # Clean up body if no valid letter fixtures were generated
    if len(body.fixtures) == 0:
        world.DestroyBody(body)
        return None

    # Force Box2D to re-balance the center of mass for the combined word
    body.ResetMassData()
    return body
# -----------------------------
# DRAW FUNCTIONS
# -----------------------------
def draw_body_fixtures(body, color):
    """Draws the underlying compound Box2D fixtures for debugging"""
    for fixture in body.fixtures:
        shape = fixture.shape
        verts = [(body.transform * v) * PPM for v in shape.vertices]
        verts = [(v[0], SCREEN_HEIGHT - v[1]) for v in verts]
        pygame.draw.polygon(screen, color, verts, 1) # Wireframe representation

def draw_word(body, text_string):
    # 1. Get the real-world position of the body's origin (0, 0 in local space)
    origin_x = body.position.x * PPM
    origin_y = SCREEN_HEIGHT - (body.position.y * PPM)
    
    angle_degrees = math.degrees(body.angle)
    cos_a = math.cos(body.angle)
    sin_a = math.sin(body.angle)

    # 2. Re-calculate the layout tracking metrics exactly like create_word_body
    space_width = font.metrics(" ")[0][4] if font.metrics(" ") else 30
    current_offset_x = 0.0

    # Calculate total width to find the center-alignment pivot point
    total_width = 0
    for char in text_string:
        if char == " ":
            total_width += space_width
        else:
            char_surface = font.render(char, True, (255, 255, 255))
            total_width += char_surface.get_width()
    
    half_total_width_meters = (total_width / 2) / PPM

    # 3. Step through and draw each character individually based on the physics layout
    for char in text_string:
        if char == " ":
            current_offset_x += space_width / PPM
            continue

        # Render the single isolated character
        char_surface = font.render(char, True, BLUE)
        w = char_surface.get_width()
        h = char_surface.get_height()

        # Find the unrotated local position of this character's center relative to the body's origin
        # This matches the exact math used to position the vertices in create_word_body
        local_char_x = current_offset_x - half_total_width_meters
        local_char_y = 0.0 # Standard flat baseline alignment

        # Rotate this local character vector using Box2D's body angle
        rotated_char_x = (local_char_x * cos_a - local_char_y * sin_a) * PPM
        rotated_char_y = (local_char_x * sin_a + local_char_y * cos_a) * PPM

        # Rotate the individual character's texture
        rotated_surface = pygame.transform.rotate(char_surface, angle_degrees)

        # Calculate the final screen placement position
        draw_x = origin_x + rotated_char_x
        draw_y = origin_y - rotated_char_y

        # Bind the center of the rotated character surface to the calculated position
        rect = rotated_surface.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated_surface, rect)

        # Advance the kerning cursor forward for the next character
        current_offset_x += w / PPM

# -----------------------------
# MAIN LOOP
# -----------------------------
running = True
show_debug_hitboxes = True # Toggle this to see the breakdown triangles!

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

            # In your main loop keypress event:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            word_list = ["PYGAME", "BOX2D", "PHYSICS", "COMIC", "SANS"]
            chosen_word = random.choice(word_list)
            
            body = create_word_body(world, chosen_word, random.uniform(5, 20), 40)
            if body:
                letters.append((body, chosen_word)) # Storing the entire word string now

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ch = random.choice(string.ascii_uppercase)
                body = create_letter_body(world, ch, random.uniform(10, 35), 40)
                if body:
                    letters.append((body, ch))
            if event.key == pygame.K_d:
                show_debug_hitboxes = not show_debug_hitboxes

    world.Step(TIME_STEP, VEL_ITERS, POS_ITERS)
    screen.fill(WHITE)

    # Draw environments
    draw_body_fixtures(ground, GREEN)
    draw_body_fixtures(left, BLUE)
    draw_body_fixtures(right, BLUE)

    for body, ch in letters:
        if body:
            draw_letter(body, ch)
            if show_debug_hitboxes:
                draw_body_fixtures(body, RED)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()