import pygame
import random

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BYTEBOUND")

clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("consolas", 72)
menu_font = pygame.font.SysFont("consolas", 36)
small_font = pygame.font.SysFont("consolas", 24)

# Colors
BG = (8, 10, 25)
CYAN = (0, 255, 200)
WHITE = (240, 240, 240)
GRAY = (120, 120, 120)

menu = [
    "START GAME",
    "SANDBOX MODE",
    "SETTINGS",
    "EXIT"
]

selected = 0

# Floating particles
particles = []

for _ in range(80):
    particles.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])

running = True

while running:

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(menu)

            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(menu)

            if event.key == pygame.K_RETURN:

                choice = menu[selected]

                if choice == "EXIT":
                    running = False

                print("Selected:", choice)

    # ---------------- DRAW ----------------
    screen.fill(BG)

    # Background particles
    for p in particles:

        pygame.draw.circle(screen, CYAN, (p[0], p[1]), p[2])

        p[1] += 0.3

        if p[1] > HEIGHT:
            p[1] = 0
            p[0] = random.randint(0, WIDTH)

    # Title
    title = title_font.render("BYTEBOUND", True, CYAN)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

    subtitle = small_font.render(
        "TYPE. BUILD. ESCAPE.",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        (WIDTH//2 - subtitle.get_width()//2, 210)
    )

    # Menu
    for i, item in enumerate(menu):

        color = CYAN if i == selected else GRAY

        text = menu_font.render(item, True, color)

        screen.blit(
            text,
            (WIDTH//2 - text.get_width()//2,
             320 + i * 60)
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()