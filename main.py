"""
Jawa Survival - A Pygame Wave Defense Game
===========================================
Player controls a Jawa character on a sandy desert map, scrapping walls for
resources, building new ones for defense, and fighting off waves of enemy
Jawas (Darth Jawas) using a blaster.

Controls:
    WASD / Arrow Keys   - Move player
    Left Click          - Shoot blast (blaster mode) or interact with tiles (build/scrap mode)
    SPACE               - Toggle blaster / build+scrap mode
    B                   - Toggle debug overlay

Author: [Your Name]
Course: Advanced Computer Science
"""

import math
import sys
import pygame
import random
import os

# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

pygame.init()

# Window dimensions in pixels
width = 1000
height = 600
screen = pygame.display.set_mode((width, height))

# Semi-transparent surface used for blast glow effects (SRCALPHA supports per-pixel alpha)
glow_surf = pygame.Surface((width, height), pygame.SRCALPHA)

# Tile size: each map cell is rendered as a pixel_size x pixel_size square
pixel_size = 50

# ─────────────────────────────────────────────────────────────────────────────
# DEBUG SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

debug = False                               # Toggle with B key at runtime
debug_font = pygame.font.SysFont(None, 22)  # Small font for debug overlay text
wave_font  = pygame.font.SysFont(None, 34)  # Larger font for wave label (top-left HUD)

# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND / TILEMAP
# ─────────────────────────────────────────────────────────────────────────────

# Off-screen anchor point (not actively used for rendering but kept for reference)
bg = (-pixel_size, -pixel_size)

# Load and scale tile images to match pixel_size
# pygame.transform.scale resizes the surface to the given (width, height)
sand_img = pygame.transform.scale(pygame.image.load("Sand.png"), (pixel_size, pixel_size))
wall_img = pygame.transform.scale(pygame.image.load("Wall.png"), (pixel_size, pixel_size))

# 2D grid representing the map layout.
# 0 = sand (walkable), 1 = wall (solid / destructible / buildable)
# Rows = Y axis, Columns = X axis. Index as background_code[row][col].
background_code = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

# Pre-build a parallel 2D array of tile images so we don't look up the image
# every frame — we index directly into background_imgs during drawing.
background_imgs = [
    [sand_img if code == 0 else wall_img for code in row]
    for row in background_code
]

# ─────────────────────────────────────────────────────────────────────────────
# WORLD / CAMERA
# ─────────────────────────────────────────────────────────────────────────────

# Total world dimensions in pixels (derived from the tile grid)
world_w = len(background_code[0]) * pixel_size   # columns * tile size
world_h = len(background_code)    * pixel_size   # rows    * tile size

# Camera offset: how many pixels the world is shifted left/up relative to screen origin
camera_x = 0
camera_y = 0


# ─────────────────────────────────────────────────────────────────────────────
# JAWA CLASS
# ─────────────────────────────────────────────────────────────────────────────

class Jawa:
    """
    Represents any character in the game — both the player and enemy Darth Jawas.
    The `darth` flag distinguishes enemy behaviour from player behaviour.

    Key responsibilities:
    - Movement with wall collision
    - Hitbox calculation and collision queries (player, blast, dropped scrap)
    - Tile interaction (read / write background_code)
    - Blast projectile logic (shoot & hit-wall checks)
    - Walking animation via sprite cycling
    """

    def __init__(self, x, y, HITBOX_W, HITBOX_H, darth, sprites,
                 attack_power, speed, num_scraps, total_health, scrap_power,
                 build_power=0, blast_speed=0, blast_radius=0,
                 SHOOT_COOLDOWN_MAX=0, BLAST_TRAIL=0):
        """
        Parameters
        ----------
        x, y              : Initial world-space position (centre of sprite)
        HITBOX_W/H        : Width and height of the collision rectangle
        darth             : True for enemy AI; False for player
        sprites           : Dict with keys "right1","right2","left1","left2"
        attack_power      : HP damage dealt per hit to the opposing side
        speed             : Pixels moved per frame
        num_scraps        : Starting scrap count
        total_health      : Maximum HP
        scrap_power       : Progress points added per frame while scrapping a wall
        build_power       : Progress points added per frame while building a wall
        blast_speed       : Pixels a projectile travels per frame
        blast_radius      : (Reserved for future area-of-effect logic)
        SHOOT_COOLDOWN_MAX: Frames between shots
        BLAST_TRAIL       : Number of frames to extend the visual trail behind a blast
        """
        self.darth = darth

        # Position in world space (pixels)
        self.x = x
        self.y = y
        self.HITBOX_W = HITBOX_W
        self.HITBOX_H = HITBOX_H

        # Sprite management
        self.sprites = sprites
        self.img = sprites["right1"]  # default facing direction

        # Combat stats
        self.is_attacking   = False
        self.attack_power   = attack_power
        self.speed          = speed
        self.attack_cooldown = 0

        # Tile interaction state
        self.action_tile     = None   # (tx, ty) of the tile being worked on
        self.action_type     = None   # 'build' or 'scrap'
        self.action_progress = 0      # 0–600; completes at 600

        # Inventory
        self.num_scraps = num_scraps
        # Each scrap is a (type, visual_offset) tuple; type selects which image to draw
        self.scraps = [(random.randint(0, 3), random.randint(0, 3)) for _ in range(num_scraps)]

        # Health
        self.total_health = total_health
        self.health = self.total_health

        # Walking animation counters
        self.stride     = 0           # accumulates movement distance; resets every 6 units
        self.walk_speed = 0           # cycles 0→1 to select sprite frame
        self.facing     = "right"

        # Scrap / build speeds
        self.scrap_power = scrap_power
        self.build_power = build_power

        # Enemy carry state
        self.carrying_scrap = 0       # 1 if the enemy holds a stolen/looted scrap
        self.stole_scrap    = False   # prevents stealing more than once per encounter
        self.has_looted     = False   # Darth-only: stops picking up further scraps

        # Blaster state
        self.blaster_mode     = False
        self.blasts           = []    # list of {"x", "y", "vx", "vy"} dicts
        self.blast_speed      = blast_speed
        self.blast_radius     = blast_radius
        self.shoot_cooldown   = 0
        self.SHOOT_COOLDOWN_MAX = SHOOT_COOLDOWN_MAX
        self.BLAST_TRAIL      = BLAST_TRAIL

    # ── Tile helpers ──────────────────────────────────────────────────────────

    def getTileXY(self, tx, ty):
        """Return the tile code at grid position (tx, ty), or -1 if out of bounds."""
        if tx < 0 or ty < 0 or ty >= len(background_code) or tx >= len(background_code[0]):
            return -1
        return background_code[ty][tx]

    def getTile(self, px, py):
        """Return the tile code at world-pixel position (px, py)."""
        return self.getTileXY(int(px / pixel_size), int(py / pixel_size))

    def setTile(self, px, py, tile_code):
        """
        Update both the data grid and the image cache for the tile at world-pixel (px, py).
        tile_code: 0 = sand, 1 = wall
        """
        tx = int(px / pixel_size)
        ty = int(py / pixel_size)
        background_code[ty][tx] = tile_code
        background_imgs[ty][tx] = sand_img if tile_code == 0 else wall_img

    # ── Collision helpers ─────────────────────────────────────────────────────

    def get_hitbox_rect(self, px, py):
        """
        Build a pygame.Rect for the character's hitbox centred on (px, py).
        The hitbox is positioned at the bottom of the sprite for better
        ground-aligned feel — it sits at the feet, not the top of the image.
        """
        hitbox_x = int(px) - self.HITBOX_W // 2
        hitbox_y = int(py) + self.img.get_height() // 2 - self.HITBOX_H
        return pygame.Rect(hitbox_x, hitbox_y, self.HITBOX_W, self.HITBOX_H)

    def collides_with_wall(self, px, py):
        """
        Return True if the hitbox at (px, py) overlaps any wall tile.
        Checks every tile the four corners of the hitbox touch.
        """
        rect = self.get_hitbox_rect(px, py)
        left_tile   = rect.left   // pixel_size
        right_tile  = rect.right  // pixel_size
        top_tile    = rect.top    // pixel_size
        bottom_tile = rect.bottom // pixel_size
        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                if self.getTileXY(tx, ty) == 1:
                    return True
        return False

    def collides_with_player(self):
        """
        Called each frame for enemy Jawas.
        - If the player carries scraps and the enemy has none, steal one scrap.
        - Otherwise deal attack_power damage to the player (with cooldown).
        """
        global player, dropped_scraps

        my_rect     = self.get_hitbox_rect(self.x, self.y)
        player_rect = player.get_hitbox_rect(player.x, player.y)

        if not my_rect.colliderect(player_rect):
            return   # No contact — nothing to do

        # Steal a scrap if conditions allow
        if player.num_scraps > 0 and self.carrying_scrap == 0 and not self.stole_scrap:
            stolen = player.scraps.pop()
            player.num_scraps -= 1
            self.carrying_scrap = 1
            self.stole_scrap    = True
            if self.darth:
                self.has_looted = True
        else:
            # Deal melee damage with a per-enemy cooldown so hits aren't instant-death
            if self.attack_cooldown == 0:
                player.health      = max(0, player.health - self.attack_power)
                self.attack_cooldown = 20  # ~0.6 s at 30 ms delay

    def collides_with_blast(self):
        """
        Check if any of the player's active blasts hit this enemy.
        Removes spent blasts from the global list and deducts health.
        """
        global player

        my_rect          = self.get_hitbox_rect(self.x, self.y)
        remaining_blasts = []

        for b in player.blasts:
            bx = int(b["x"])
            by = int(b["y"])
            # Small collision box around the blast tip
            blast_rect = pygame.Rect(bx - 4, by - 4, 8, 8)

            if my_rect.colliderect(blast_rect):
                self.health -= player.attack_power  # consume the blast
            else:
                remaining_blasts.append(b)          # blast survives

        player.blasts = remaining_blasts

    def collides_with_dropped_scrap(self):
        """
        Let the enemy pick up a scrap that was dropped on the ground.
        Darth Jawas that have already looted once will skip this.
        """
        global dropped_scraps

        if self.darth and self.has_looted:
            return   # already carrying loot — no need to pick up more

        my_rect = self.get_hitbox_rect(self.x, self.y)
        for item in dropped_scraps[:]:
            scrap_rect = pygame.Rect(item["x"] - 18, item["y"] - 18, 36, 36)
            if my_rect.colliderect(scrap_rect):
                dropped_scraps.remove(item)
                self.carrying_scrap = 1
                if self.darth:
                    self.has_looted = True
                return

    def blast_hits_wall(self, bx, by, vx=0, vy=0):
        """
        Return True if the blast at (bx, by) is inside a wall or outside the world.
        Samples three points along the velocity vector (tip, mid, tail) to avoid
        fast blasts tunnelling through thin walls.
        """
        for t in (0, 0.5, 1.0):
            cx = bx - vx * t
            cy = by - vy * t
            if cx < 0 or cy < 0 or cx >= world_w or cy >= world_h:
                return True
            if self.getTile(cx, cy) == 1:
                return True
        return False

    def get_cardinal_tiles(self, px, py):
        """
        Return the four grid coordinates directly adjacent (left, right, up, down)
        to the tile that contains world-pixel (px, py).
        Used to highlight and select tiles for build/scrap actions.
        """
        tx = int(px / pixel_size)
        ty = int(py / pixel_size)
        return [(tx - 1, ty), (tx + 1, ty), (tx, ty - 1), (tx, ty + 1)]

    # ── Movement ──────────────────────────────────────────────────────────────

    def move(self, xy=None, escape=False):
        """
        Move the character by a normalised direction vector (dx, dy).

        If xy is None this Jawa is an enemy and enemy_move() is called to
        compute the desired direction automatically.

        Diagonal movement is normalised to prevent faster diagonal speed.
        Axis-separated collision lets characters slide along walls rather
        than stopping dead.

        For the player, the camera is also updated here.
        """
        global width, height, world_w, world_h, camera_x, camera_y

        if xy is None:
            xy = self.enemy_move(escape=escape)
            if xy is None:
                return

        dx, dy = xy

        # Normalise diagonal movement so speed stays consistent
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        half_w = self.img.get_width()  // 2
        half_h = self.img.get_height() // 2

        def apply_step(step_dx, step_dy):
            """Attempt to move by (step_dx, step_dy) and return whether movement occurred."""
            new_x = self.x + step_dx * self.speed
            new_y = self.y + step_dy * self.speed

            # Clamp to world bounds so the character can't walk off the edge
            new_x = clamp(new_x, half_w, world_w - half_w)
            new_y = clamp(new_y, half_h, world_h - half_h)

            moved = False
            if not self.collides_with_wall(new_x, self.y):
                self.x, moved = new_x, True
            if not self.collides_with_wall(self.x, new_y):
                self.y, moved = new_y, True
            return moved

        moved = apply_step(dx, dy)

        # Extra wall-slide logic for enemy only: try each axis independently
        # so Darth Jawas can navigate around corners more intelligently
        if self.darth and not moved:
            if abs(dx) > abs(dy):
                apply_step(dx, 0)
                apply_step(0, dy)
            else:
                apply_step(0, dy)
                apply_step(dx, 0)

        # Keep the camera centred on the player
        if not self.darth:
            camera_x = clamp(self.x - width  // 2, 0, world_w - width)
            camera_y = clamp(self.y - height // 2, 0, world_h - height)

        # Determine if the character actually moved this frame
        moving = dx != 0 or dy != 0

        # Update facing direction
        if   dx > 0: self.facing = "right"
        elif dx < 0: self.facing = "left"

        # Advance walking animation; cycle between frame 1 and 2 every 6 stride units
        if moving:
            self.stride += abs(dx) + abs(dy) + 1
            if self.stride >= 6:
                self.stride     = 0
                self.walk_speed = (self.walk_speed + 1) % 2
        else:
            self.stride     = 0
            self.walk_speed = 0

        self.img = self.sprites[f"{self.facing}{self.walk_speed + 1}"]

    def enemy_move(self, escape=False):
        """
        Compute a normalised direction vector toward (or away from) the player.

        escape=True : enemy flees (e.g. after stealing a scrap)
        escape=False: enemy chases the player
        """
        dx = player.x - self.x
        dy = player.y - self.y

        if escape:
            dx, dy = -dx, -dy  # reverse direction to flee

        dist = math.hypot(dx, dy)
        if dist == 0:
            return (0, 0)

        return (dx / dist, dy / dist)

    def drop_scrap(self):
        """Drop any carried scrap as a world item when the enemy dies."""
        global dropped_scraps

        if self.carrying_scrap > 0:
            dropped_scraps.append({
                "x":    int(self.x),
                "y":    int(self.y),
                "scrap": (random.randint(0, 3), random.randint(0, 3))
            })
            self.carrying_scrap = 0


# ─────────────────────────────────────────────────────────────────────────────
# PLAYER SETUP
# ─────────────────────────────────────────────────────────────────────────────

# Load all four player animation frames (right-walk 1&2, left-walk 1&2)
player_sprites = {
    "right1": pygame.transform.scale(pygame.image.load("Jawa_1.png"), (80, 80)),
    "right2": pygame.transform.scale(pygame.image.load("Jawa_2.png"), (80, 80)),
    "left1":  pygame.transform.scale(pygame.image.load("Jawa_3.png"), (80, 80)),
    "left2":  pygame.transform.scale(pygame.image.load("Jawa_4.png"), (80, 80)),
}

# Spawn player near the centre of the screen, with a starter scrap count of 5.
# Parameters: x, y, hitbox_w, hitbox_h, darth, sprites,
#             attack_power, speed, num_scraps, total_health, scrap_power,
#             build_power, blast_speed, blast_radius, shoot_cooldown, blast_trail
player = Jawa(width // 2, height // 2, 34, 46, False, player_sprites, 10, 10, 5, 100, 6, 10, 24, 8, 12, 1)

# ─────────────────────────────────────────────────────────────────────────────
# ENEMY SETUP
# ─────────────────────────────────────────────────────────────────────────────

# Enemy sprites (darker variant of the Jawa spritesheet)
darth_sprites = {
    "right1": pygame.transform.scale(pygame.image.load("Jawa_5.png"), (80, 80)),
    "right2": pygame.transform.scale(pygame.image.load("Jawa_6.png"), (80, 80)),
    "left1":  pygame.transform.scale(pygame.image.load("Jawa_7.png"), (80, 80)),
    "left2":  pygame.transform.scale(pygame.image.load("Jawa_8.png"), (80, 80)),
}

darth_jawas   = []   # active enemy list; rebuilt each frame after deaths
dropped_scraps = []  # world-space scrap items that can be picked up

def spawn_darth_jawa(x, y):
    """Create one enemy Jawa and add it to the active enemy list."""
    darth_jawas.append(
        Jawa(x, y, 34, 46, True, darth_sprites, 10, 9, 0, 4, 4)
    )

# ─────────────────────────────────────────────────────────────────────────────
# WAVE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

wave               = 1    # current wave number (displayed in HUD)
wave_spawn_remaining = 0  # enemies still to be spawned this wave
wave_spawn_timer   = 0    # counts up; spawns an enemy every wave_spawn_delay frames
wave_spawn_delay   = 35   # frames between individual enemy spawns (~1 s at 30 ms delay)

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def clamp(value, low, high):
    """Clamp value to the inclusive range [low, high]."""
    return max(low, min(value, high))

def spawn_enemy_for_wave():
    """
    Spawn one enemy at a random position along the world border.
    Enemies always enter from one of the four edges so the player
    has a moment to react rather than them appearing on top of the player.
    """
    margin = 70  # keep spawns away from the absolute corner pixels
    side   = random.randint(0, 3)  # 0=left, 1=right, 2=top, 3=bottom

    if   side == 0: x, y = margin,           random.randint(margin, world_h - margin)
    elif side == 1: x, y = world_w - margin,  random.randint(margin, world_h - margin)
    elif side == 2: x, y = random.randint(margin, world_w - margin), margin
    else:           x, y = random.randint(margin, world_w - margin), world_h - margin

    spawn_darth_jawa(x, y)

def start_next_wave():
    """
    Begin a new wave by calculating how many enemies to spawn.
    Wave N spawns (2 + N*2) enemies, increasing the challenge each round.
    """
    global wave_spawn_remaining, wave_spawn_timer, wave
    wave_spawn_remaining = 2 + wave * 2
    wave_spawn_timer     = 0

# ─────────────────────────────────────────────────────────────────────────────
# HUD RECTANGLES
# ─────────────────────────────────────────────────────────────────────────────

# Health bar — centred at bottom of the screen
health_bar        = pygame.Rect(width // 2 - 300, height - 75, 600, 30)
moving_health_bar = pygame.Rect(health_bar.x, health_bar.y, health_bar.width, health_bar.height)

# Action / cooldown bar — thin strip just above the health bar
scrap_bar        = pygame.Rect(width // 2 - 300, height - 88, 600, 8)
moving_scrap_bar = pygame.Rect(scrap_bar.x, scrap_bar.y, scrap_bar.width, scrap_bar.height)

# ─────────────────────────────────────────────────────────────────────────────
# SCRAP IMAGES (four visual variants)
# ─────────────────────────────────────────────────────────────────────────────

scrap_img_0 = pygame.transform.scale(pygame.image.load("Scrap_0.png"), (100, 100))
scrap_img_1 = pygame.transform.scale(pygame.image.load("Scrap_1.png"), (100, 100))
scrap_img_2 = pygame.transform.scale(pygame.image.load("Scrap_2.png"), (100, 100))
scrap_img_3 = pygame.transform.scale(pygame.image.load("Scrap_3.png"), (100, 100))


# ─────────────────────────────────────────────────────────────────────────────
# GAME LOOP
# ─────────────────────────────────────────────────────────────────────────────

running = True
start_next_wave()   # kick off wave 1

while running:
    pygame.time.delay(30)       # ~33 FPS cap; keeps CPU usage reasonable
    screen.fill((0, 0, 0))      # clear screen to black before drawing

    # ── Input: determine this frame's movement direction ──────────────────────
    tile = player.getTile(player.x, player.y)  # tile the player is standing on

    keys = pygame.key.get_pressed()  # snapshot of all keyboard state
    dx, dy = 0, 0

    if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
    if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += 1

    player.move((dx, dy))

    # ── Event handling ────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Left mouse button pressed
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if player.blaster_mode:
                # Fire a blast toward the mouse cursor (if cooldown has elapsed)
                if player.shoot_cooldown == 0:
                    mx, my   = event.pos
                    world_mx = mx + camera_x   # convert screen → world coordinates
                    world_my = my + camera_y
                    angle    = math.atan2(world_my - player.y, world_mx - player.x)
                    player.blasts.append({
                        "x":  float(player.x),
                        "y":  float(player.y),
                        "vx": math.cos(angle) * player.blast_speed,
                        "vy": math.sin(angle) * player.blast_speed,
                    })
                    player.shoot_cooldown = player.SHOOT_COOLDOWN_MAX
            else:
                # Build/scrap mode: select an adjacent tile for interaction
                mx, my      = event.pos
                clicked_tx  = int((mx + camera_x) / pixel_size)
                clicked_ty  = int((my + camera_y) / pixel_size)

                if (clicked_tx, clicked_ty) in player.get_cardinal_tiles(player.x, player.y):
                    tile_val  = player.getTileXY(clicked_tx, clicked_ty)
                    wall_rect = pygame.Rect(clicked_tx * pixel_size, clicked_ty * pixel_size, pixel_size, pixel_size)

                    if tile_val == 0 and player.num_scraps > 0 and \
                       not wall_rect.colliderect(player.get_hitbox_rect(player.x, player.y)):
                        # Sand tile + player has scraps → begin building a wall
                        player.action_tile     = (clicked_tx, clicked_ty)
                        player.action_type     = 'build'
                        player.action_progress = 0
                    elif tile_val == 1:
                        # Wall tile → begin scrapping it for resources
                        player.action_tile     = (clicked_tx, clicked_ty)
                        player.action_type     = 'scrap'
                        player.action_progress = 0

        # Left mouse button released — cancel any in-progress action
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not player.blaster_mode:
            player.action_tile     = None
            player.action_type     = None
            player.action_progress = 0

        # Key press events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:     debug = not debug                       # toggle debug overlay
            if event.key == pygame.K_SPACE: player.blaster_mode = not player.blaster_mode  # toggle mode

    # ── Action progress (hold-to-build / hold-to-scrap) ───────────────────────
    if player.action_tile and pygame.mouse.get_pressed()[0]:
        atx, aty = player.action_tile

        # Abort if the target tile is no longer adjacent (player moved away)
        if (atx, aty) in player.get_cardinal_tiles(player.x, player.y):
            tile_val = player.getTileXY(atx, aty)

            if player.action_type == 'scrap' and tile_val == 1:
                # Increment progress; complete at 600 progress points
                player.action_progress = min(600, player.action_progress + player.scrap_power)
                if player.action_progress >= 600:
                    player.setTile(atx * pixel_size, aty * pixel_size, 0)  # remove wall
                    player.scraps.append((random.randint(0, 3), random.randint(0, 3)))
                    player.num_scraps += 1
                    # Reset action state
                    player.action_tile     = None
                    player.action_type     = None
                    player.action_progress = 0

            elif player.action_type == 'build' and tile_val == 0 and player.num_scraps > 0:
                wall_rect = pygame.Rect(atx * pixel_size, aty * pixel_size, pixel_size, pixel_size)
                if not wall_rect.colliderect(player.get_hitbox_rect(player.x, player.y)):
                    player.action_progress = min(600, player.action_progress + player.build_power)
                    if player.action_progress >= 600:
                        player.setTile(atx * pixel_size, aty * pixel_size, 1)  # place wall
                        player.scraps.pop()
                        player.num_scraps -= 1
                        player.action_tile     = None
                        player.action_type     = None
                        player.action_progress = 0
                else:
                    # Player walked into the target tile; cancel
                    player.action_tile     = None
                    player.action_type     = None
                    player.action_progress = 0
            else:
                # Tile changed under the cursor (e.g. wall was already destroyed)
                player.action_tile     = None
                player.action_type     = None
                player.action_progress = 0
    else:
        # Mouse released — slowly decay progress so it doesn't reset instantly
        player.action_progress = max(0, player.action_progress - 8)
        if player.action_progress == 0:
            player.action_tile = None
            player.action_type = None

    # ── Blast movement ────────────────────────────────────────────────────────
    if player.shoot_cooldown > 0:
        player.shoot_cooldown -= 1   # count down between shots

    alive_blasts = []
    for b in player.blasts:
        b["x"] += b["vx"]
        b["y"] += b["vy"]
        # Discard blasts that hit a wall or left the world boundary
        if not player.blast_hits_wall(b["x"], b["y"], b["vx"], b["vy"]):
            alive_blasts.append(b)
    player.blasts = alive_blasts

    # ── Enemy update (per-frame AI) ───────────────────────────────────────────
    alive_enemies = []
    for enemy in darth_jawas:
        if enemy.attack_cooldown > 0:
            enemy.attack_cooldown -= 1  # cool down between melee hits

        enemy.collides_with_blast()         # take damage from player blasts
        enemy.collides_with_player()        # deal damage to / steal from player
        enemy.collides_with_dropped_scrap() # pick up scraps on the ground

        # Flee if carrying loot; otherwise chase the player
        enemy.move(escape=(enemy.carrying_scrap > 0))

        if enemy.health <= 0:
            enemy.drop_scrap()   # leave any held scrap on death
        else:
            alive_enemies.append(enemy)

    darth_jawas = alive_enemies  # discard dead enemies

    # ── Wave progression ──────────────────────────────────────────────────────
    if len(darth_jawas) == 0 and wave_spawn_remaining == 0:
        # All enemies defeated and none left to spawn → advance wave
        wave += 1
        start_next_wave()

    if wave_spawn_remaining > 0:
        wave_spawn_timer += 1
        if wave_spawn_timer >= wave_spawn_delay:
            wave_spawn_timer = 0
            spawn_enemy_for_wave()
            wave_spawn_remaining -= 1

    # ── Player picks up dropped scraps ────────────────────────────────────────
    player_rect = player.get_hitbox_rect(player.x, player.y)
    new_drops   = []
    for item in dropped_scraps:
        scrap_rect = pygame.Rect(item["x"] - 18, item["y"] - 18, 36, 36)
        if player_rect.colliderect(scrap_rect):
            player.scraps.append(item["scrap"])
            player.num_scraps += 1
        else:
            new_drops.append(item)
    dropped_scraps = new_drops

    # ─────────────────────────────────────────────────────────────────────────
    # DRAWING
    # ─────────────────────────────────────────────────────────────────────────

    # Draw tilemap — iterate rows then columns, offset by camera
    for i, row in enumerate(background_imgs):
        for j, bg_tile in enumerate(row):
            screen.blit(bg_tile, (j * pixel_size - camera_x, i * pixel_size - camera_y))

    # Draw dropped scraps
    for item in dropped_scraps:
        scrap = item["scrap"]
        img   = [scrap_img_0, scrap_img_1, scrap_img_2, scrap_img_3][scrap[0]]
        screen.blit(img, (item["x"] - camera_x - img.get_width()  // 2,
                          item["y"] - camera_y - img.get_height() // 2))

    # Draw player blasts with a layered glow effect
    # Layer 1: wide soft glow on the SRCALPHA surface (blended over the scene)
    # Layer 2: brighter inner beam on the SRCALPHA surface
    # Layer 3: sharp bright core drawn directly on screen
    if player.blasts:
        glow_surf.fill((0, 0, 0, 0))   # clear last frame's glow
        for b in player.blasts:
            hx = int(b["x"] - camera_x)
            hy = int(b["y"] - camera_y)
            tx = int(b["x"] - b["vx"] * player.BLAST_TRAIL - camera_x)
            ty = int(b["y"] - b["vy"] * player.BLAST_TRAIL - camera_y)
            pygame.draw.line(glow_surf, (255,   0,  0,  80), (tx, ty), (hx, hy), 7)  # wide red glow
            pygame.draw.line(glow_surf, (255,  50, 80, 130), (tx, ty), (hx, hy), 4)  # mid core
        screen.blit(glow_surf, (0, 0))  # blend glow onto the screen

        for b in player.blasts:   # draw the sharp white-pink centre on top
            hx = int(b["x"] - camera_x)
            hy = int(b["y"] - camera_y)
            tx = int(b["x"] - b["vx"] * player.BLAST_TRAIL - camera_x)
            ty = int(b["y"] - b["vy"] * player.BLAST_TRAIL - camera_y)
            pygame.draw.line(screen, (255, 200, 220), (tx, ty), (hx, hy), 2)

    # Draw player sprite (centred on world position, offset by camera)
    screen.blit(player.img, (
        player.x - camera_x - player.img.get_width()  // 2,
        player.y - camera_y - player.img.get_height() // 2
    ))

    # Draw all living enemy sprites
    for enemy in darth_jawas:
        screen.blit(enemy.img, (
            enemy.x - camera_x - enemy.img.get_width()  // 2,
            enemy.y - camera_y - enemy.img.get_height() // 2
        ))

    # Draw tile highlight overlay for adjacent tiles (build/scrap mode only)
    mx, my   = pygame.mouse.get_pos()
    hov_tx   = int((mx + camera_x) / pixel_size)
    hov_ty   = int((my + camera_y) / pixel_size)

    if not player.blaster_mode:
        for ctX, ctY in player.get_cardinal_tiles(player.x, player.y):
            tile_val  = player.getTileXY(ctX, ctY)
            wall_rect = pygame.Rect(ctX * pixel_size, ctY * pixel_size, pixel_size, pixel_size)
            blocked   = wall_rect.colliderect(player.get_hitbox_rect(player.x, player.y))

            # Choose highlight colour based on tile type and whether action is possible
            if tile_val == 0 and player.num_scraps > 0:
                fill_color   = (255,  50,  50,  50) if blocked else (0, 255, 100,  50)
                border_color = (255,  50,  50)       if blocked else (0, 255, 100)
            elif tile_val == 1:
                fill_color,   border_color = (255, 165,   0, 50), (255, 165, 0)
            else:
                fill_color,   border_color = (100, 100, 100, 30), (100, 100, 100)

            # Blit semi-transparent fill using SRCALPHA surface
            hs = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
            pygame.draw.rect(hs, fill_color, hs.get_rect())
            screen.blit(hs, (ctX * pixel_size - camera_x, ctY * pixel_size - camera_y))

            # Draw border only on the tile the mouse is hovering over
            if (hov_tx, hov_ty) == (ctX, ctY):
                pygame.draw.rect(screen, border_color,
                                 (ctX * pixel_size - camera_x, ctY * pixel_size - camera_y,
                                  pixel_size, pixel_size), 3)

    # ── HUD ───────────────────────────────────────────────────────────────────

    # Health bar: scale width proportionally to current HP
    moving_health_bar.width = clamp(
        int(health_bar.width * (player.health / player.total_health)),
        0, health_bar.width
    )

    # Semi-transparent background, green fill, black border
    health_bg = pygame.Surface((health_bar.width, health_bar.height), pygame.SRCALPHA)
    pygame.draw.rect(health_bg, (0, 0, 0, 150), health_bg.get_rect(), border_radius=10)
    screen.blit(health_bg, health_bar.topleft)
    pygame.draw.rect(screen, (0, 129, 0), moving_health_bar, border_radius=10)
    pygame.draw.rect(screen, (0, 0,   0), health_bar, width=3, border_radius=10)

    # Action / cooldown bar (shown above the health bar)
    if player.blaster_mode and player.shoot_cooldown > 0:
        # Blue bar drains as the shot cooldown counts down
        cooldown_fill_w = int((player.shoot_cooldown / player.SHOOT_COOLDOWN_MAX) * scrap_bar.width)
        cooldown_fill   = pygame.Rect(scrap_bar.x, scrap_bar.y, cooldown_fill_w, scrap_bar.height)
        bar_bg = pygame.Surface((scrap_bar.width, scrap_bar.height), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, (0, 0, 0, 150), bar_bg.get_rect(), border_radius=3)
        screen.blit(bar_bg, scrap_bar.topleft)
        pygame.draw.line(screen, (0, 80, 180),
                         (scrap_bar.x, scrap_bar.y + scrap_bar.height // 2),
                         (scrap_bar.x + cooldown_fill_w, scrap_bar.y + scrap_bar.height // 2), 1)
        pygame.draw.rect(screen, (0, 80, 180), cooldown_fill, border_radius=3)
        pygame.draw.rect(screen, (0, 0, 0),    scrap_bar, width=2, border_radius=3)

    elif player.action_progress > 0:
        # Orange (build) or grey (scrap) bar shows hold-action progress
        bar_color      = (255, 140, 0) if player.action_type == 'build' else (133, 129, 110)
        action_bar_fill = pygame.Rect(scrap_bar.x, scrap_bar.y, player.action_progress, scrap_bar.height)
        bar_bg = pygame.Surface((scrap_bar.width, scrap_bar.height), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, (0, 0, 0, 150), bar_bg.get_rect(), border_radius=3)
        screen.blit(bar_bg, scrap_bar.topleft)
        pygame.draw.rect(screen, bar_color,  action_bar_fill, border_radius=3)
        pygame.draw.rect(screen, (0, 1, 0),  scrap_bar, width=2, border_radius=3)

    # Draw scrap inventory — small overlapping icons at the right edge of the HUD
    for i, scrap in enumerate(player.scraps):
        img = [scrap_img_0, scrap_img_1, scrap_img_2, scrap_img_3][scrap[0]]
        screen.blit(img, (
            width // 2 + 325 + scrap[1] * 7,
            health_bar.bottom + health_bar.height - img.get_height() - i * 9
        ))

    # Wave counter (top-left)
    wave_label = wave_font.render(f"Wave {wave}", True, (255, 255, 255))
    screen.blit(wave_label, (20, 20))

    # ── Debug overlay (press B to toggle) ────────────────────────────────────
    if debug:
        tx = int(player.x / pixel_size)
        ty = int(player.y / pixel_size)

        # Yellow highlight on the player's current tile
        tile_surf = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
        pygame.draw.rect(tile_surf, (255, 255, 1, 80), tile_surf.get_rect())
        screen.blit(tile_surf, (tx * pixel_size - camera_x, ty * pixel_size - camera_y))
        pygame.draw.rect(screen, (255, 255, 1),
                         (tx * pixel_size - camera_x, ty * pixel_size - camera_y, pixel_size, pixel_size), 2)

        # Red player hitbox outline
        hitbox = player.get_hitbox_rect(player.x, player.y)
        pygame.draw.rect(screen, (255, 52, 50),
                         (hitbox.x - camera_x, hitbox.y - camera_y, hitbox.width, hitbox.height), 2)

        # Text info panel
        debug_lines = [
            f"pos: ({int(player.x)}, {int(player.y)})",
            f"tile: ({tx}, {ty})  val: {player.getTileXY(tx, ty)}",
            f"mouse tile: ({hov_tx}, {hov_ty})  val: {player.getTileXY(hov_tx, hov_ty)}",
            f"camera: ({int(camera_x)}, {int(camera_y)})",
            "mode: " + ("blaster" if player.blaster_mode else "scrapy"),
            f"facing: {player.facing}  dx:{dx:.2f} dy:{dy:.2f}",
            f"scraps: {player.num_scraps}",
        ]
        for i, line in enumerate(debug_lines):
            surf = debug_font.render(line, True, (255, 255, 255))
            screen.blit(surf, (8, 8 + i * 20))

    if moving_health_bar.width <= 0:
        running = False

    pygame.display.update()  # push the completed frame to the screen

# ─────────────────────────────────────────────────────────────────────────────
# CLEANUP
# ─────────────────────────────────────────────────────────────────────────────

pygame.quit()