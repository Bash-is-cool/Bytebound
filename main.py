import math
import pygame
import os
import sys
import random
import tkinter as tk
import time
from interpreter import TokenInterpreter

# =============================================================================
# INITIALIZATION
# =============================================================================
pygame.init()
pygame.key.set_repeat(400, 35)

# =============================================================================
# CONFIGURATION  —  tweak these
# =============================================================================
root = tk.Tk()
root.withdraw()  # Hide the root window

width = root.winfo_screenwidth()
height = root.winfo_screenheight()

WINDOW_W = int(width)
WINDOW_H = int(height)
TILE_SIZE = 50  # pixels per map tile
TARGET_FPS = 30  # ms delay per frame (33 ≈ 30 fps)

# --- SIDEBAR INTERPOLATION CALCULATIONS ---
SIDEBAR_W = WINDOW_W // 6
GAME_VIEW_W = WINDOW_W - SIDEBAR_W

# Tile codes — possibly will extend (e.g. 2 = water, 3 = lava)
TILE_SAND = 0
TILE_WALL = 1

# Action progress threshold — how long a hold-action takes (in progress points)
ACTION_THRESHOLD = 600

# =============================================================================
# ASSETS  —  replace paths with your own sprites
# =============================================================================

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Tile images
tile_imgs = {
    TILE_SAND: pygame.transform.scale(pygame.image.load(resource_path("res/tiles/Sand.png")), (TILE_SIZE, TILE_SIZE)),
    TILE_WALL: pygame.transform.scale(pygame.image.load(resource_path("res/tiles/Wall.png")), (TILE_SIZE, TILE_SIZE)),
}

# Player animation frames: {direction + frame_index: Surface}
player_sprites = {
    "right1": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/player/Jawa_1.png")), (80, 80)),
    "right2": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/player/Jawa_2.png")), (80, 80)),
    "left1": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/player/Jawa_3.png")), (80, 80)),
    "left2": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/player/Jawa_4.png")), (80, 80)),
}

# Enemy animation frames
enemy_sprites = {
    "right1": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/Jawa_5.png")), (80, 80)),
    "right2": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/Jawa_6.png")), (80, 80)),
    "left1": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/Jawa_7.png")), (80, 80)),
    "left2": pygame.transform.scale(pygame.image.load(resource_path("res/sprites/Jawa_8.png")), (80, 80)),
}

# Item images (index 0–3 used by item "type" field)
item_imgs = [
    pygame.transform.scale(pygame.image.load(resource_path("res/items/Scrap_0.png")), (100, 100)),
    pygame.transform.scale(pygame.image.load(resource_path("res/items/Scrap_1.png")), (100, 100)),
    pygame.transform.scale(pygame.image.load(resource_path("res/items/Scrap_2.png")), (100, 100)),
    pygame.transform.scale(pygame.image.load(resource_path("res/items/Scrap_3.png")), (100, 100)),
]

# =============================================================================
# MAP  —  0 = passable, 1 = wall; rows = Y, columns = X
# =============================================================================

# =============================================================================
# MAP  —  0 = passable, 1 = wall; rows = Y, columns = X
# =============================================================================

# =============================================================================
# MAP  —  0 = passable, 1 = wall; rows = Y, columns = X
# =============================================================================

tile_maps = [
    # Map 0
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 0
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 1
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 2 
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 3
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 4
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 5
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 6
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 7
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 8 
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 9  <-- Spawn (2, 9)
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 10
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 11
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 12
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 13
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 14
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 15
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 16
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 17
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]   # 18
    ],
    # Map 1
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 2
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 3
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 4
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 5
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 6
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 7
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 8
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Map 9
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
    ],
    # Map 10
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
    ]
]

map = 0

tile_map = tile_maps[map]

tile_img_map = [
    [tile_imgs[code] for code in row]
    for row in tile_map
]

player_map_coords = [
    (2, 9),  # Map 0
    (2, 9),  # Map 1
    (2, 9),  # Map 2
    (2, 9),  # Map 3
    (2, 9),  # Map 4
    (2, 9),  # Map 5
    (2, 9),  # Map 6
    (2, 9),  # Map 7
    (2, 9),  # Map 8
    (13, 9),  # Map 9
    (13, 9)  # Map 10
]

# =============================================================================
# WORLD / CAMERA
# =============================================================================

world_w = len(tile_map[0]) * TILE_SIZE
world_h = len(tile_map) * TILE_SIZE
camera_x = 0
camera_y = 0


# =============================================================================
# UTILITY
# =============================================================================

def clamp(value, low, high):
    return max(low, min(value, high))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# =============================================================================
# ACTION LOGIC
# =============================================================================

# (action, direction, frames to hold)
actions = [
    # # Navigate out of the central spawn chamber safely into the top corridor
    # ("walk", "up", 32),

    # # Take the long hall to the left wing
    # ("walk", "left", 52),

    # # Head down through the left-most vertical shaft
    # ("walk", "down", 59),

    # # Trek across the expansive bottom corridor
    # ("walk", "right", 79),

    # # Move up into the right-side structural loop
    # ("walk", "up", 39),

    # # Shift over into the final descent column
    # ("walk", "right", 20),

    # # Head down to the exit vector
    # ("walk", "down", 39),

    # # Dash to the bottom-right escape!
    # ("walk", "right", 15)
]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# =============================================================================
# CHARACTER CLASS
# =============================================================================

class Character:
    def __init__(self, tx, ty, hitbox_w, hitbox_h, is_enemy, sprites,
                 attack_power, speed, num_items, total_health,
                 destroy_power=0, build_power=0):
        self.is_enemy = is_enemy
        self.x           = tx * TILE_SIZE + (TILE_SIZE // 2)
        self.y           = ty * TILE_SIZE + (TILE_SIZE // 2)
        self.HITBOX_W = hitbox_w
        self.HITBOX_H = hitbox_h

        # Sprites and animation
        self.sprites = sprites
        self.img = sprites["right1"]
        self.facing = "right"
        self.stride = 0  # accumulates distance; resets every 6 units
        self.walk_frame = 0  # cycles 0→1 for two-frame walk animation

        # Combat
        self.attack_power = attack_power
        self.attack_cooldown = 0
        self.speed = speed

        # Tile interaction
        self.action_tile = None  # (tx, ty) of targeted tile
        self.action_type = None  # "build" or "destroy"
        self.action_progress = 0  # 0 – ACTION_THRESHOLD

        # Inventory  —  each item is a (type_index, visual_offset) tuple
        self.num_items = num_items
        self.items = [(random.randint(0, 3), random.randint(0, 3))
                      for _ in range(num_items)]

        # Health
        self.total_health = total_health
        self.health = total_health

        # Interaction powers
        self.destroy_power = destroy_power
        self.build_power = build_power

        # Enemy carry state (one item max; enemy stops looting after picking one up)
        self.carrying_item = 0
        self.has_looted = False

    # ── Tile helpers ──────────────────────────────────────────────────────────

    def get_tile_at_grid(self, tx, ty):
        if tx < 0 or ty < 0 or ty >= len(tile_map) or tx >= len(tile_map[0]):
            return -1
        return tile_map[ty][tx]

    def set_tile(self, tx, ty, code):
        tile_map[ty][tx] = code
        tile_img_map[ty][tx] = tile_imgs[code]

    def get_adjacent_tiles(self, px, py):
        tx = int(px / TILE_SIZE)
        ty = int(py / TILE_SIZE)
        return [(tx - 1, ty), (tx + 1, ty), (tx, ty - 1), (tx, ty + 1)]

    # ── Collision helpers ─────────────────────────────────────────────────────

    def get_hitbox(self, px, py):
        hx = int(px) - self.HITBOX_W // 2
        hy = int(py) + self.img.get_height() // 2 - self.HITBOX_H
        return pygame.Rect(hx, hy, self.HITBOX_W, self.HITBOX_H)

    def hits_wall(self, px, py):
        rect = self.get_hitbox(px, py)
        for ty in range(rect.top // TILE_SIZE, (rect.bottom - 1) // TILE_SIZE + 1):
            for tx in range(rect.left // TILE_SIZE, (rect.right - 1) // TILE_SIZE + 1):
                if self.get_tile_at_grid(tx, ty) == TILE_WALL:
                    return True
        return False

    def check_player_contact(self, player):
        if not self.get_hitbox(self.x, self.y).colliderect(
                player.get_hitbox(player.x, player.y)):
            return

        if player.num_items > 0 and self.carrying_item == 0 and not self.has_looted:
            player.items.pop()
            player.num_items -= 1
            self.carrying_item = 1
            self.has_looted = True
        else:
            if self.attack_cooldown == 0:
                player.health = max(0, player.health - self.attack_power)
                self.attack_cooldown = 20

    def check_ground_item_pickup(self, ground_items):
        if self.has_looted:
            return

        my_rect = self.get_hitbox(self.x, self.y)
        for item in ground_items[:]:
            if my_rect.colliderect(pygame.Rect(item["x"] - 18, item["y"] - 18, 36, 36)):
                ground_items.remove(item)
                self.carrying_item = 1
                self.has_looted = True
                return

    def drop_item(self, ground_items):
        if self.carrying_item > 0:
            ground_items.append({
                "x": int(self.x),
                "y": int(self.y),
                "item": (random.randint(0, 3), random.randint(0, 3)),
            })
            self.carrying_item = 0

    # ── Movement ──────────────────────────────────────────────────────────────

    def move(self, direction=None, player=None, escape=False):
        global camera_x, camera_y

        if direction is None:
            direction = self._ai_direction(player, escape)
            if direction is None:
                return

        dx, dy = direction

        if dx != 0 and dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx, dy = dx / length, dy / length

        half_w = self.img.get_width() // 2
        half_h = self.img.get_height() // 2

        def try_step(sdx, sdy):
            nx = clamp(self.x + sdx * self.speed, half_w, world_w - half_w)
            ny = clamp(self.y + sdy * self.speed, half_h, world_h - half_h)
            moved = False
            if not self.hits_wall(nx, self.y):
                self.x, moved = nx, True
            if not self.hits_wall(self.x, ny):
                self.y, moved = ny, True
            return moved

        moved = try_step(dx, dy)

        # Enemies try each axis independently for smoother corner navigation
        if self.is_enemy and not moved:
            if abs(dx) >= abs(dy):
                try_step(dx, 0)
                try_step(0, dy)
            else:
                try_step(0, dy)
                try_step(dx, 0)

        # Camera tracking (player only) - adjusted tracking boundaries to match 5/6 game view width
        if not self.is_enemy:
            camera_x = clamp(self.x - GAME_VIEW_W // 2, 0, world_w - GAME_VIEW_W)
            camera_y = clamp(self.y - WINDOW_H // 2, 0, world_h - WINDOW_H)

        # Facing and walk animation
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

        if dx != 0 or dy != 0:
            self.stride += abs(dx) + abs(dy) + 1
            if self.stride >= 6:
                self.stride = 0
                self.walk_frame = (self.walk_frame + 1) % 2
        else:
            self.stride = 0
            self.walk_frame = 0

        self.img = self.sprites[f"{self.facing}{self.walk_frame + 1}"]

    def _ai_direction(self, player, escape):
        if player is None:
            return None
        dx = player.x - self.x
        dy = player.y - self.y
        if escape:
            dx, dy = -dx, -dy
        dist = math.hypot(dx, dy)
        return (0, 0) if dist == 0 else (dx / dist, dy / dist)


# =============================================================================
# SIDEBAR TEXT ENGINE & INTERPRETER COMPONENT
# =============================================================================
class FileInterpreter:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.Font(None, 20)
        self.line_height = 25

        self.BG_COLOR = pygame.Color(20, 20, 25)
        self.TEXT_COLOR = pygame.Color(230, 230, 230)
        self.OUTPUT_COLOR = pygame.Color(100, 200, 255)
        self.CURSOR_COLOR = pygame.Color(255, 165, 0)
        self.DIVIDER_COLOR = pygame.Color(60, 60, 70)
        self.UI_TEXT_COLOR = pygame.Color(120, 120, 130)

        self.BTN_DEFAULT = pygame.Color(46, 117, 89)
        self.BTN_HOVER = pygame.Color(60, 153, 116)
        self.BTN_TEXT = pygame.Color(245, 245, 245)

        self.run_btn_rect = pygame.Rect(180, 8, 55, 22)
        self.is_btn_hovered = False

        self.file_lines = [""]
        self.cursor_row = 0
        self.cursor_col = 0

        self.output_history = ["--- Interpreter Output Window ---", "Press F5 to execute script."]

        self.cursor_visible = True
        self.last_cursor_toggle = time.time()
        self.cursor_interval = 0.5

        self.scroll_x = 0          
        self.padding_left = 20     
        self.max_text_width = self.width - 40 
        
        self.is_dragging_scrollbar = False
        self.scrollbar_y = self.height - 15
        self.scrollbar_height = 8

    # Place this method code block right inside your master Game Class wrapper or main loop runner:
    def execute_user_script(self):
        interpreter = TokenInterpreter()
        global actions # Point this straight to your main action loop tuple list array
        
        # 1. Capture snapshots of live state positions across game classes
        current_tx = int(player.x / TILE_SIZE)
        current_ty = int(player.y / TILE_SIZE)
        
        # 2. Build the state mapping dictionary 
        # These match the variable names typed in the text editor
        live_environment_snapshot = {
            "west":  "wall" if player.get_tile_at_grid(current_tx - 1, current_ty) == 1 else "sand",
            "east":  "wall" if player.get_tile_at_grid(current_tx + 1, current_ty) == 1 else "sand",
            "north": "wall" if player.get_tile_at_grid(current_tx, current_ty - 1) == 1 else "sand",
            "south": "wall" if player.get_tile_at_grid(current_tx, current_ty + 1) == 1 else "sand",
            "items": player.num_items,
            "hp":    player.health,
            "wall":  "wall", # Maps string literal tokens for evaluation comparisons
            "sand":  "sand"
        }
        
        # 3. Clear action queue arrays before loading new injected logic routines
        actions.clear()
        
        # 4. Feed your editor lines straight into the engine row by row
        # (Assuming text input strings are saved inside sidebar.file_lines)
        for script_line in sidebar.file_lines:
            interpreter.execute_line(script_line, live_environment_snapshot, actions)
            
        # Flush output statuses back down to the screen console HUD views
        sidebar.output_history = interpreter.output_history

    def handle_keydown(self, event):
        current_line = self.file_lines[self.cursor_row]

        if event.key == pygame.K_F5:
            self.execute_user_script()
        elif event.key == pygame.K_RETURN:
            if len(self.file_lines) >= 30:
                return
            
            left_side = current_line[:self.cursor_col]
            right_side = current_line[self.cursor_col:]
            self.file_lines[self.cursor_row] = left_side
            self.file_lines.insert(self.cursor_row + 1, right_side)
            self.cursor_row += 1
            self.cursor_col = 0
        elif event.key == pygame.K_BACKSPACE:
            if self.cursor_col > 0:
                new_line = current_line[:self.cursor_col - 1] + current_line[self.cursor_col:]
                self.file_lines[self.cursor_row] = new_line
                self.cursor_col -= 1
                self.cursor_visible = True
            elif self.cursor_row > 0:
                prev_line = self.file_lines[self.cursor_row - 1]
                self.cursor_col = len(prev_line)
                self.file_lines[self.cursor_row - 1] = prev_line + current_line
                self.file_lines.pop(self.cursor_row)
                self.cursor_row -= 1
                self.cursor_visible = True
        elif event.key == pygame.K_UP and self.cursor_row > 0:
            self.cursor_row -= 1
            self.cursor_col = min(self.cursor_col, len(self.file_lines[self.cursor_row]))
        elif event.key == pygame.K_DOWN and self.cursor_row < len(self.file_lines) - 1:
            self.cursor_row += 1
            self.cursor_col = min(self.cursor_col, len(self.file_lines[self.cursor_row]))
        elif event.key == pygame.K_LEFT:
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_row > 0:
                self.cursor_row -= 1
                self.cursor_col = len(self.file_lines[self.cursor_row])
        elif event.key == pygame.K_RIGHT:
            if self.cursor_col < len(current_line):
                self.cursor_col += 1
            elif self.cursor_row < len(self.file_lines) - 1:
                self.cursor_row += 1
                self.cursor_col = 0
    
    def update_scroll(self):
        """Forces the view window to follow the cursor's character position."""
        current_line = self.file_lines[self.cursor_row]
        text_before_cursor = current_line[:self.cursor_col]
        cursor_x_offset, _ = self.font.size(text_before_cursor)
        
        # Where the cursor is relative to the text block start
        cursor_pos_in_text = self.padding_left + cursor_x_offset
        
        # If cursor goes off the right edge of the visible window
        if cursor_pos_in_text > (self.scroll_x + self.width - 40):
            self.scroll_x = cursor_pos_in_text - (self.width - 40)
            
        # If cursor goes off the left edge of the visible window
        elif cursor_pos_in_text < (self.scroll_x + self.padding_left):
            self.scroll_x = max(0, cursor_x_offset)
    
    def handle_mouse(self, event):
        """Processes scrollbar dragging and top-bar Run Button actions."""
        mouse_x, mouse_y = event.pos

        # ⬇️ TRACK MOUSE HOVER STATE FOR THE RUN BUTTON ⬇️
        if event.type == pygame.MOUSEMOTION:
            self.is_btn_hovered = self.run_btn_rect.collidepoint(mouse_x, mouse_y)

        # ⬇️ DETECT RUN BUTTON CLICK ⬇️
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.run_btn_rect.collidepoint(mouse_x, mouse_y):
                self.execute_user_script()
                return # Skip checking scrollbar dragging if they hit the button

        # --- Your existing scrollbar dragging logic below ---
        longest_line = max([len(l) for l in self.file_lines], default=0)
        max_line_pixels, _ = self.font.size("M" * longest_line)
        if max_line_pixels <= self.max_text_width:
            self.is_dragging_scrollbar = False
            return
        
        max_scrollable_dist = max_line_pixels - self.max_text_width
        thumb_width = max(20, int((self.max_text_width / max_line_pixels) * self.max_text_width))
        usable_track_width = self.max_text_width - thumb_width

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            thumb_x = self.padding_left + int((self.scroll_x / max_scrollable_dist) * usable_track_width)
            scrollbar_rect = pygame.Rect(thumb_x, self.scrollbar_y - 2, thumb_width, self.scrollbar_height + 4)
            if scrollbar_rect.collidepoint(mouse_x, mouse_y):
                self.is_dragging_scrollbar = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging_scrollbar = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging_scrollbar:
            scroll_pct = max(0.0, min(1.0, (mouse_x - self.padding_left - (thumb_width // 2)) / usable_track_width))
            self.scroll_x = int(scroll_pct * max_scrollable_dist)

    def draw(self, surface):
        surface.fill(self.BG_COLOR)
        current_time = time.time()

        if current_time - self.last_cursor_toggle > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = current_time

        # 1. Render Top Header Label
        editor_lbl = self.font.render("FILE EDITOR (script.txt)", True, self.UI_TEXT_COLOR)
        surface.blit(editor_lbl, (15, 10))

        # ⬇️ 2. RENDER THE INTERACTIVE RUN BUTTON ⬇️
        # Choose dynamic color based on hover state
        btn_color = self.BTN_HOVER if self.is_btn_hovered else self.BTN_DEFAULT
        pygame.draw.rect(surface, btn_color, self.run_btn_rect, border_radius=4)
        
        # Center the text "RUN" directly inside the button box
        btn_text_surf = self.font.render("RUN", True, self.BTN_TEXT)
        text_x = self.run_btn_rect.x + (self.run_btn_rect.width - btn_text_surf.get_width()) // 2
        text_y = self.run_btn_rect.y + (self.run_btn_rect.height - btn_text_surf.get_height()) // 2
        surface.blit(btn_text_surf, (text_x, text_y))

        # 3. Apply Text Area Clip Viewport (Protects top-bar from scrolling text overlapping)
        start_y = 40
        clip_rect = pygame.Rect(self.padding_left, start_y, self.width - 40, self.scrollbar_y - start_y - 5)
        surface.set_clip(clip_rect)

        for i, line in enumerate(self.file_lines):
            line_surface = self.font.render(line, True, self.TEXT_COLOR)
            text_x = self.padding_left - self.scroll_x
            text_y = start_y + (i * self.line_height)
            surface.blit(line_surface, (text_x, text_y))

            if i == self.cursor_row and self.cursor_visible:
                text_before_cursor = line[:self.cursor_col]
                cursor_x_offset, _ = self.font.size(text_before_cursor)
                cursor_x = self.padding_left + cursor_x_offset - self.scroll_x
                pygame.draw.line(surface, self.CURSOR_COLOR, (cursor_x, text_y), (cursor_x, text_y + 18), 2)

        surface.set_clip(None)

        # 3. Dynamic Interactive Scrollbar Render
        longest_line = max([len(l) for l in self.file_lines], default=0)
        max_line_pixels, _ = self.font.size("M" * longest_line)
        
        if max_line_pixels > self.max_text_width:
            # Draw standard track rail backings
            pygame.draw.rect(surface, self.DIVIDER_COLOR, (self.padding_left, self.scrollbar_y, self.max_text_width, self.scrollbar_height), border_radius=4)
            
            # Calculate metrics
            thumb_width = max(20, int((self.max_text_width / max_line_pixels) * self.max_text_width))
            max_scrollable_dist = max_line_pixels - self.max_text_width
            thumb_x = self.padding_left + int((self.scroll_x / max_scrollable_dist) * (self.max_text_width - thumb_width))
            
            # Make the thumb color pop brighter if we are currently holding/dragging it
            thumb_color = self.TEXT_COLOR if self.is_dragging_scrollbar else self.UI_TEXT_COLOR
            
            pygame.draw.rect(surface, thumb_color, (thumb_x, self.scrollbar_y, thumb_width, self.scrollbar_height), border_radius=4)


# =============================================================================
# ENTITY SETUP
# =============================================================================

player = Character(
    tx            = player_map_coords[map][0],
    ty            = player_map_coords[map][1],
    hitbox_w=34,
    hitbox_h=46,
    is_enemy=False,
    sprites=player_sprites,
    attack_power=10,
    speed=10,
    num_items=5,
    total_health=100,
    destroy_power=6,
    build_power=10,
)

def get_adjacent_tile_to_player(cardinal_direction):

    direction_map = {
        "West": 0,
        "East": 1,
        "North": 2,
        "South": 3
    }
    
    if cardinal_direction not in direction_map:
        raise ValueError(f"Invalid direction: {cardinal_direction}. Expected 'North', 'East', 'South', or 'West'.")
    
    hitbox = player.get_hitbox(player.x, player.y)
    adjacent_tiles = player.get_adjacent_tiles(hitbox.centerx, hitbox.centery)
    
    # Retrieve the index from the map
    index = direction_map[cardinal_direction]
    
    target_coords = adjacent_tiles[index]
    return player.get_tile_at_grid(target_coords[0], target_coords[1])



enemies = []  # active enemy list
ground_items = []  # items dropped on the world floor


def spawn_enemy(tx, ty):
    enemies.append(Character(
        tx=tx,
        ty=ty,
        hitbox_w=34,
        hitbox_h=46,
        is_enemy=True,
        sprites=enemy_sprites,
        attack_power=10,
        speed=9,
        num_items=0,
        total_health=40,
        destroy_power=4,
    ))


# =============================================================================
# DISPLAY / HUD SETUP
# =============================================================================
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))

# Position HUD elements relative to the 5/6 Game Canvas frame instead of absolute screen widths
health_bar_rect = pygame.Rect(SIDEBAR_W + (GAME_VIEW_W // 2) - 300, WINDOW_H - 75, 600, 30)
health_fill_rect = pygame.Rect(health_bar_rect)
action_bar_rect = pygame.Rect(SIDEBAR_W + (GAME_VIEW_W // 2) - 300, WINDOW_H - 88, 600, 8)

debug = False
debug_font = pygame.font.SysFont(None, 22)

# Create the left-side editor panel instance
sidebar = FileInterpreter(SIDEBAR_W, WINDOW_H)

# =============================================================================
# GAME LOOP
# =============================================================================
running = True

while running:
    pygame.time.delay(1000 // TARGET_FPS)
    screen.fill((0, 0, 0))

    # ── Action queue ──────────────────────────────────────────────────────────
    directions = {"right": (1, 0), "left": (-1, 0), "up": (0, -1), "down": (0, 1)}

    if actions and actions[0][0] == "walk":
        _, direction, quantity = actions[0]
        player.move(direction=directions.get(direction, (0, 0)))
        if quantity <= 1:
            actions.pop(0)
        else:
            actions[0] = ("walk", direction, quantity - 1)
    elif actions and actions[0][0] in ("build", "destroy"):
        _, direction, hold = actions[0]
        dir_vec = directions.get(direction, (0, 0))
        hb = player.get_hitbox(player.x, player.y)
        if dir_vec == (1, 0):
            tx_raw, ty_raw = (hb.right - 1) // TILE_SIZE + 1, hb.centery // TILE_SIZE
        elif dir_vec == (-1, 0):
            tx_raw, ty_raw = hb.left // TILE_SIZE - 1, hb.centery // TILE_SIZE
        elif dir_vec == (0, 1):
            tx_raw, ty_raw = hb.centerx // TILE_SIZE, (hb.bottom - 1) // TILE_SIZE + 1
        else:
            tx_raw, ty_raw = hb.centerx // TILE_SIZE, hb.top // TILE_SIZE - 1

        if tx_raw < 0 or tx_raw >= len(tile_map[0]) or ty_raw < 0 or ty_raw >= len(tile_map):
            player.action_tile = player.action_type = None
            player.action_progress = 0
            actions.pop(0)
        else:
            tx, ty = tx_raw, ty_raw
            if player.action_tile != (tx, ty):
                player.action_tile = (tx, ty)
                player.action_type = actions[0][0]
                player.action_progress = 0
            if dir_vec[0] > 0:
                player.facing = "right"
            elif dir_vec[0] < 0:
                player.facing = "left"
            player.img = player.sprites[f"{player.facing}1"]
            if hold <= 1:
                player.action_tile = player.action_type = None
                player.action_progress = 0
                actions.pop(0)
            else:
                actions[0] = (actions[0][0], direction, hold - 1)

    # ── Hold-to-act (build / destroy) ─────────────────────────────────────────
    if player.action_tile and actions and actions[0][0] in ("build", "destroy"):
        atx, aty = player.action_tile
        tile_val = player.get_tile_at_grid(atx, aty)

        if player.action_type == "destroy" and tile_val == TILE_WALL:
            player.action_progress = min(ACTION_THRESHOLD,
                                         player.action_progress + player.destroy_power)
            if player.action_progress >= ACTION_THRESHOLD:
                player.set_tile(atx, aty, TILE_SAND)
                player.items.append((random.randint(0, 3), random.randint(0, 3)))
                player.num_items += 1
                player.action_tile = player.action_type = None
                player.action_progress = 0
                actions.pop(0)

        elif player.action_type == "build" and tile_val == TILE_SAND and player.num_items > 0:
            player.action_progress = min(ACTION_THRESHOLD,
                                         player.action_progress + player.build_power)
            if player.action_progress >= ACTION_THRESHOLD:
                player.set_tile(atx, aty, TILE_WALL)
                player.items.pop()
                player.num_items -= 1
                player.action_tile = player.action_type = None
                player.action_progress = 0
                actions.pop(0)
        else:
            player.action_tile = player.action_type = None
            player.action_progress = 0
            actions.pop(0)
    else:
        player.action_progress = max(0, player.action_progress - 8)
        if player.action_progress == 0:
            player.action_tile = player.action_type = None

    # ── Enemy AI ──────────────────────────────────────────────────────────────
    alive = []
    for enemy in enemies:
        if enemy.attack_cooldown > 0:
            enemy.attack_cooldown -= 1

        enemy.check_player_contact(player)
        enemy.check_ground_item_pickup(ground_items)
        enemy.move(player=player, escape=(enemy.carrying_item > 0))

        if enemy.health <= 0:
            enemy.drop_item(ground_items)
        else:
            alive.append(enemy)
    enemies[:] = alive

    # ── Player picks up ground items ──────────────────────────────────────────
    player_rect = player.get_hitbox(player.x, player.y)
    remaining = []
    for item in ground_items:
        if player_rect.colliderect(pygame.Rect(item["x"] - 18, item["y"] - 18, 36, 36)):
            player.items.append(item["item"])
            player.num_items += 1
        else:
            remaining.append(item)
    ground_items[:] = remaining

    # ==========================================================================
    # EVENT DISPATCH
    # ==========================================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.TEXTINPUT:
            # Route text editing keystrokes straight to the editor instance
            curr_line = sidebar.file_lines[sidebar.cursor_row]
            sidebar.file_lines[sidebar.cursor_row] = curr_line[:sidebar.cursor_col] + event.text + curr_line[
                sidebar.cursor_col:]
            sidebar.cursor_col += len(event.text)
            
            sidebar.update_scroll()

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            sidebar.handle_mouse(event)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                debug = not debug
            elif event.key == pygame.K_ESCAPE:
                running = False
            else:
                sidebar.handle_keydown(event)

    # ==========================================================================
    # RENDER PIPELINE
    # ==========================================================================

    game_canvas = screen.subsurface(pygame.Rect(SIDEBAR_W, 0, GAME_VIEW_W, WINDOW_H))
    game_canvas.fill((10, 10, 12))

    # Tilemap
    for row_i, row in enumerate(tile_img_map):
        for col_i, tile_surf in enumerate(row):
            game_canvas.blit(tile_surf, (col_i * TILE_SIZE - camera_x,
                                         row_i * TILE_SIZE - camera_y))

    # Ground items
    for item in ground_items:
        img = item_imgs[item["item"][0]]
        game_canvas.blit(img, (item["x"] - camera_x - img.get_width() // 2,
                               item["y"] - camera_y - img.get_height() // 2))

    # Player
    game_canvas.blit(player.img, (
        player.x - camera_x - player.img.get_width() // 2,
        player.y - camera_y - player.img.get_height() // 2,
    ))

    # Enemies
    for enemy in enemies:
        game_canvas.blit(enemy.img, (
            enemy.x - camera_x - enemy.img.get_width() // 2,
            enemy.y - camera_y - enemy.img.get_height() // 2,
        ))

    # ── Debug overlay (press B) ───────────────────────────────────────────────
    if debug:
        tx = int(player.x / TILE_SIZE)
        ty = int(player.y / TILE_SIZE)

        tile_hl = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(tile_hl, (255, 255, 1, 80), tile_hl.get_rect())
        game_canvas.blit(tile_hl, (tx * TILE_SIZE - camera_x, ty * TILE_SIZE - camera_y))
        pygame.draw.rect(game_canvas, (255, 255, 1),
                         (tx * TILE_SIZE - camera_x, ty * TILE_SIZE - camera_y,
                          TILE_SIZE, TILE_SIZE), 2)

        hitbox = player.get_hitbox(player.x, player.y)
        pygame.draw.rect(game_canvas, (255, 52, 50),
                         (hitbox.x - camera_x, hitbox.y - camera_y,
                          hitbox.width, hitbox.height), 2)
        
        hb = player.get_hitbox(player.x, player.y)
        for ctX, ctY in player.get_adjacent_tiles(hb.centerx, hb.centery):
            tile_val = player.get_tile_at_grid(ctX, ctY)
            tile_rect = pygame.Rect(ctX * TILE_SIZE, ctY * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            blocked = tile_rect.colliderect(player.get_hitbox(player.x, player.y))

            if tile_val == TILE_SAND and player.num_items > 0:
                fill = (255, 50, 50, 50) if blocked else (0, 255, 100, 50)
            elif tile_val == TILE_WALL:
                fill = (255, 165, 0, 50)
            else:
                fill = (100, 100, 100, 30)

            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(overlay, fill, overlay.get_rect())
            game_canvas.blit(overlay, (ctX * TILE_SIZE - camera_x, ctY * TILE_SIZE - camera_y))

        for i, line in enumerate([
            f"pos:    ({int(player.x)}, {int(player.y)})",
            f"tile:   ({tx}, {ty})  val: {player.get_tile_at_grid(tx, ty)}",
            f"camera: ({int(camera_x)}, {int(camera_y)})",
            f"facing: {player.facing}   queue: {actions[0] if actions else 'idle'}",
        ]):
            game_canvas.blit(debug_font.render(line, True, (255, 255, 255)), (8, 8 + i * 20))

    sidebar_canvas = screen.subsurface(pygame.Rect(0, 0, SIDEBAR_W, WINDOW_H))
    sidebar.draw(sidebar_canvas)

    # Render HUD overlays relative to global display coordinate values
    health_fill_rect.width = clamp(
        int(health_bar_rect.width * (player.health / player.total_health)),
        0, health_bar_rect.width,
    )

    hud_bg = pygame.Surface((health_bar_rect.width, health_bar_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(hud_bg, (0, 0, 0, 150), hud_bg.get_rect(), border_radius=10)
    screen.blit(hud_bg, health_bar_rect.topleft)
    pygame.draw.rect(screen, (0, 129, 0), health_fill_rect, border_radius=10)
    pygame.draw.rect(screen, (0, 0, 0), health_bar_rect, width=3, border_radius=10)

    if player.action_progress > 0:
        bar_color = (255, 140, 0) if player.action_type == "build" else (133, 129, 110)
        fill_rect = pygame.Rect(action_bar_rect.x, action_bar_rect.y,
                                int(action_bar_rect.width * player.action_progress / ACTION_THRESHOLD),
                                action_bar_rect.height)
        bar_bg = pygame.Surface((action_bar_rect.width, action_bar_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, (0, 0, 0, 150), bar_bg.get_rect(), border_radius=3)
        screen.blit(bar_bg, action_bar_rect.topleft)
        pygame.draw.rect(screen, bar_color, fill_rect, border_radius=3)
        pygame.draw.rect(screen, (0, 1, 0), action_bar_rect, width=2, border_radius=3)

    # Draw separator line between layout screens
    pygame.draw.line(screen, pygame.Color(60, 60, 70), (SIDEBAR_W, 0), (SIDEBAR_W, WINDOW_H), 3)

    # End condition
    if player.health <= 0:
        running = False

    if player.x > world_w - TILE_SIZE * 3:  # near right edge
        if map + 1 >= len(tile_maps):
            running = False
        else:
            map += 1
            tile_map = tile_maps[map]
            tile_img_map = [[tile_imgs[code] for code in row] for row in tile_map]
            
            # Update world dimensions
            world_w = len(tile_map[0]) * TILE_SIZE
            world_h = len(tile_map) * TILE_SIZE
            
            # Reset player and state
            px, py = player_map_coords[map]
            player.x = px * TILE_SIZE + TILE_SIZE // 2
            player.y = py * TILE_SIZE + TILE_SIZE // 2
            player.health = player.total_health
            
            enemies.clear()
            ground_items.clear()
            actions.clear()
            camera_x = camera_y = 0

    pygame.display.update()

# =============================================================================
# CLEANUP
# =============================================================================
pygame.quit()