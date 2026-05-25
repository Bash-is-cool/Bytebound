import math
import pygame
import random

# =============================================================================
# INITIALIZATION
# =============================================================================

pygame.init()

# =============================================================================
# CONFIGURATION  —  tweak these
# =============================================================================

WINDOW_W    = 1000
WINDOW_H    = 600
TILE_SIZE   = 50       # pixels per map tile
TARGET_FPS  = 30       # ms delay per frame (33 ≈ 30 fps)

# Tile codes — extend as needed (e.g. 2 = water, 3 = lava)
TILE_SAND = 0
TILE_WALL = 1

# Action progress threshold — how long a hold-action takes (in progress points)
ACTION_THRESHOLD = 600

# =============================================================================
# ASSETS  —  replace paths with your own sprites
# =============================================================================

# Tile images
tile_imgs = {
    TILE_SAND: pygame.transform.scale(pygame.image.load("res\\tiles\Sand.png"), (TILE_SIZE, TILE_SIZE)),
    TILE_WALL: pygame.transform.scale(pygame.image.load("res\\tiles\Wall.png"), (TILE_SIZE, TILE_SIZE)),
}

# Player animation frames: {direction + frame_index: Surface}
player_sprites = {
    "right1": pygame.transform.scale(pygame.image.load("res\sprites\player\Jawa_1.png"), (80, 80)),
    "right2": pygame.transform.scale(pygame.image.load("res\sprites\player\Jawa_2.png"), (80, 80)),
    "left1":  pygame.transform.scale(pygame.image.load("res\sprites\player\Jawa_3.png"), (80, 80)),
    "left2":  pygame.transform.scale(pygame.image.load("res\sprites\player\Jawa_4.png"), (80, 80)),
}

# Enemy animation frames
enemy_sprites = {
    "right1": pygame.transform.scale(pygame.image.load("res\sprites\Jawa_5.png"), (80, 80)),
    "right2": pygame.transform.scale(pygame.image.load("res\sprites\Jawa_6.png"), (80, 80)),
    "left1":  pygame.transform.scale(pygame.image.load("res\sprites\Jawa_7.png"), (80, 80)),
    "left2":  pygame.transform.scale(pygame.image.load("res\sprites\Jawa_8.png"), (80, 80)),
}

# Item images (index 0–3 used by item "type" field)
item_imgs = [
    pygame.transform.scale(pygame.image.load("res\items\Scrap_0.png"), (100, 100)),
    pygame.transform.scale(pygame.image.load("res\items\Scrap_1.png"), (100, 100)),
    pygame.transform.scale(pygame.image.load("res\items\Scrap_2.png"), (100, 100)),
    pygame.transform.scale(pygame.image.load("res\items\Scrap_3.png"), (100, 100)),
]

# =============================================================================
# MAP  —  0 = passable, 1 = wall; rows = Y, columns = X
# =============================================================================

tile_map = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

# Pre-built image lookup so drawing never touches tile_map directly
tile_img_map = [
    [tile_imgs[code] for code in row]
    for row in tile_map
]

# =============================================================================
# WORLD / CAMERA
# =============================================================================

world_w  = len(tile_map[0]) * TILE_SIZE
world_h  = len(tile_map)    * TILE_SIZE
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

# (action, direction, quantity)

actions = []

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# =============================================================================
# CHARACTER CLASS
# =============================================================================

class Character:
    """
    A general-purpose game entity: handles movement, tile interaction,
    inventory, health, animation, and (for enemies) basic AI.

    Both the player and enemy instances use this class; the `is_enemy`
    flag switches between player-controlled and AI-controlled behaviour.

    Customise per-game by adjusting the constructor arguments or subclassing.
    """

    def __init__(self, x, y, hitbox_w, hitbox_h, is_enemy, sprites,
                 attack_power, speed, num_items, total_health,
                 destroy_power=0, build_power=0):
        """
        Parameters
        ----------
        x, y           : Initial world-space position (centre of sprite).
        hitbox_w/h     : Width and height of the collision rectangle.
        is_enemy       : True → AI-controlled; False → player-controlled.
        sprites        : Dict keyed by "right1","right2","left1","left2".
        attack_power   : HP damage dealt per melee hit.
        speed          : Pixels moved per frame.
        num_items      : Starting inventory count.
        total_health   : Maximum HP.
        destroy_power  : Progress points added per frame while destroying a tile.
        build_power    : Progress points added per frame while placing a tile.
        """

        self.is_enemy    = is_enemy
        self.x           = x
        self.y           = y
        self.HITBOX_W    = hitbox_w
        self.HITBOX_H    = hitbox_h

        # Sprites and animation
        self.sprites    = sprites
        self.img        = sprites["right1"]
        self.facing     = "right"
        self.stride     = 0   # accumulates distance; resets every 6 units
        self.walk_frame = 0   # cycles 0→1 for two-frame walk animation

        # Combat
        self.attack_power   = attack_power
        self.attack_cooldown = 0
        self.speed       = speed

        # Tile interaction
        self.action_tile     = None   # (tx, ty) of targeted tile
        self.action_type     = None   # "build" or "destroy"
        self.action_progress = 0      # 0 – ACTION_THRESHOLD

        # Inventory  —  each item is a (type_index, visual_offset) tuple
        self.num_items = num_items
        self.items     = [(random.randint(0, 3), random.randint(0, 3))
                          for _ in range(num_items)]

        # Health
        self.total_health = total_health
        self.health       = total_health

        # Interaction powers
        self.destroy_power = destroy_power
        self.build_power   = build_power

        # Enemy carry state (one item max; enemy stops looting after picking one up)
        self.carrying_item = 0
        self.has_looted    = False

    # ── Tile helpers ──────────────────────────────────────────────────────────

    def get_tile_at_grid(self, tx, ty):
        """Return the tile code at grid (tx, ty), or -1 if out of bounds."""
        if tx < 0 or ty < 0 or ty >= len(tile_map) or tx >= len(tile_map[0]):
            return -1
        return tile_map[ty][tx]

    def set_tile(self, tx, ty, code):
        """Update the data grid and image cache at grid position (tx, ty)."""
        tile_map[ty][tx]     = code
        tile_img_map[ty][tx] = tile_imgs[code]

    def get_adjacent_tiles(self, px, py):
        """
        Return the four grid coords directly adjacent (L/R/U/D) to the tile
        containing world-pixel (px, py). Used for build/destroy targeting.
        """
        tx = int(px / TILE_SIZE)
        ty = int(py / TILE_SIZE)
        return [(tx - 1, ty), (tx + 1, ty), (tx, ty - 1), (tx, ty + 1)]

    # ── Collision helpers ─────────────────────────────────────────────────────

    def get_hitbox(self, px, py):
        """
        Return a pygame.Rect representing the hitbox centred on (px, py).
        Anchored to the bottom of the sprite for ground-aligned feel.
        """
        hx = int(px) - self.HITBOX_W // 2
        hy = int(py) + self.img.get_height() // 2 - self.HITBOX_H
        return pygame.Rect(hx, hy, self.HITBOX_W, self.HITBOX_H)

    def hits_wall(self, px, py):
        """Return True if the hitbox at (px, py) overlaps any wall tile."""
        rect = self.get_hitbox(px, py)
        for ty in range(rect.top // TILE_SIZE, (rect.bottom - 1) // TILE_SIZE + 1):
            for tx in range(rect.left // TILE_SIZE, (rect.right - 1) // TILE_SIZE + 1):
                if self.get_tile_at_grid(tx, ty) == TILE_WALL:
                    return True
        return False

    def check_player_contact(self, player):
        """
        Called each frame for enemy characters.
        Steals one item from the player if they don't already carry one;
        otherwise deals attack_power damage (with cooldown).
        """
        if not self.get_hitbox(self.x, self.y).colliderect(
                player.get_hitbox(player.x, player.y)):
            return

        if player.num_items > 0 and self.carrying_item == 0 and not self.has_looted:
            player.items.pop()
            player.num_items   -= 1
            self.carrying_item  = 1
            self.has_looted     = True
        else:
            if self.attack_cooldown == 0:
                player.health        = max(0, player.health - self.attack_power)
                self.attack_cooldown = 20

    def check_ground_item_pickup(self, ground_items):
        """
        Let the enemy walk over and pick up a dropped world item.
        Enemies that have already looted will ignore all ground items.
        """
        if self.has_looted:
            return

        my_rect = self.get_hitbox(self.x, self.y)
        for item in ground_items[:]:
            if my_rect.colliderect(pygame.Rect(item["x"] - 18, item["y"] - 18, 36, 36)):
                ground_items.remove(item)
                self.carrying_item = 1
                self.has_looted    = True
                return

    def drop_item(self, ground_items):
        """Spawn any carried item as a world drop at this character's position."""
        if self.carrying_item > 0:
            ground_items.append({
                "x":    int(self.x),
                "y":    int(self.y),
                "item": (random.randint(0, 3), random.randint(0, 3)),
            })
            self.carrying_item = 0

    # ── Movement ──────────────────────────────────────────────────────────────

    def move(self, direction=None, player=None, escape=False):
        """
        Move the character by a normalised (dx, dy) direction.

        For enemy characters, pass `player` and omit `direction`; the AI
        will compute the direction automatically.

        Diagonal movement is normalised to constant speed.
        Axis-separated collision allows wall-sliding.
        Camera follows the player character automatically.
        """
        global camera_x, camera_y

        if direction is None:
            direction = self._ai_direction(player, escape)
            if direction is None:
                return

        dx, dy = direction

        if dx != 0 and dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx, dy = dx / length, dy / length

        half_w = self.img.get_width()  // 2
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

        # Camera tracking (player only)
        if not self.is_enemy:
            camera_x = clamp(self.x - WINDOW_W // 2, 0, world_w - WINDOW_W)
            camera_y = clamp(self.y - WINDOW_H // 2, 0, world_h - WINDOW_H)

        # Facing and walk animation
        if   dx > 0: self.facing = "right"
        elif dx < 0: self.facing = "left"

        if dx != 0 or dy != 0:
            self.stride += abs(dx) + abs(dy) + 1
            if self.stride >= 6:
                self.stride     = 0
                self.walk_frame = (self.walk_frame + 1) % 2
        else:
            self.stride     = 0
            self.walk_frame = 0

        self.img = self.sprites[f"{self.facing}{self.walk_frame + 1}"]

    def _ai_direction(self, player, escape):
        """Compute a normalised vector toward (or away from) the player."""
        if player is None:
            return None
        dx = player.x - self.x
        dy = player.y - self.y
        if escape:
            dx, dy = -dx, -dy
        dist = math.hypot(dx, dy)
        return (0, 0) if dist == 0 else (dx / dist, dy / dist)


# =============================================================================
# ENTITY SETUP  —  create player and enemy instances here
# =============================================================================

player = Character(
    x             = WINDOW_W // 2,
    y             = WINDOW_H // 2,
    hitbox_w      = 34,
    hitbox_h      = 46,
    is_enemy      = False,
    sprites       = player_sprites,
    attack_power  = 10,
    speed         = 10,
    num_items     = 5,
    total_health  = 100,
    destroy_power = 6,
    build_power   = 10,
)

enemies       = []   # active enemy list
ground_items  = []   # items dropped on the world floor

### Can be altered if more than one enemy type
def spawn_enemy(x, y):
    """Create one enemy at world position (x, y) and add it to the list."""
    enemies.append(Character(
        x             = x,
        y             = y,
        hitbox_w      = 34,
        hitbox_h      = 46,
        is_enemy      = True,
        sprites       = enemy_sprites,
        attack_power  = 10,
        speed         = 9,
        num_items     = 0,
        total_health  = 40,
        destroy_power = 4,
    ))

# =============================================================================
# DISPLAY / HUD
# =============================================================================

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))

# Health bar (bottom-centre of screen)
health_bar_rect  = pygame.Rect(WINDOW_W // 2 - 300, WINDOW_H - 75, 600, 30)
health_fill_rect = pygame.Rect(health_bar_rect)

# Action-progress bar (just above the health bar)
action_bar_rect  = pygame.Rect(WINDOW_W // 2 - 300, WINDOW_H - 88, 600, 8)

# Debug
debug      = False
debug_font = pygame.font.SysFont(None, 22)

# =============================================================================
# GAME LOOP
# =============================================================================

running = True

while running:
    pygame.time.delay(1000 // TARGET_FPS)
    screen.fill((0, 0, 0))

    # ── Action queue ──────────────────────────────────────────────────────────
    directions = {"right": (1,0), "left": (-1,0), "up": (0,-1), "down": (0,1)}

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
        if   dir_vec == ( 1,  0): tx_raw, ty_raw = (hb.right  - 1) // TILE_SIZE + 1, hb.centery // TILE_SIZE
        elif dir_vec == (-1,  0): tx_raw, ty_raw =  hb.left        // TILE_SIZE - 1,  hb.centery // TILE_SIZE
        elif dir_vec == ( 0,  1): tx_raw, ty_raw =  hb.centerx     // TILE_SIZE,      (hb.bottom - 1) // TILE_SIZE + 1
        else:                     tx_raw, ty_raw =  hb.centerx     // TILE_SIZE,       hb.top    // TILE_SIZE - 1

        if tx_raw < 0 or tx_raw >= len(tile_map[0]) or ty_raw < 0 or ty_raw >= len(tile_map):
            player.action_tile = player.action_type = None
            player.action_progress = 0
            actions.pop(0)
        else:
            tx, ty = tx_raw, ty_raw
            if player.action_tile != (tx, ty):
                player.action_tile     = (tx, ty)
                player.action_type     = actions[0][0]
                player.action_progress = 0
            if dir_vec[0] > 0:   player.facing = "right"
            elif dir_vec[0] < 0: player.facing = "left"
            player.img = player.sprites[f"{player.facing}1"]
            if hold <= 1:
                player.action_tile     = player.action_type = None
                player.action_progress = 0
                actions.pop(0)
            else:
                actions[0] = (actions[0][0], direction, hold - 1)

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                debug = not debug

    # ── Hold-to-act (build / destroy) ─────────────────────────────────────────
    if player.action_tile and actions and actions[0][0] in ("build", "destroy"):
        atx, aty  = player.action_tile
        tile_val  = player.get_tile_at_grid(atx, aty)


        if player.action_type == "destroy" and tile_val == TILE_WALL:
            player.action_progress = min(ACTION_THRESHOLD,
                                         player.action_progress + player.destroy_power)
            if player.action_progress >= ACTION_THRESHOLD:
                player.set_tile(atx, aty, TILE_SAND)
                player.items.append((random.randint(0, 3), random.randint(0, 3)))
                player.num_items  += 1
                player.action_tile = player.action_type = None
                player.action_progress = 0
                actions.pop(0)

        elif player.action_type == "build" and tile_val == TILE_SAND and player.num_items > 0:
            player.action_progress = min(ACTION_THRESHOLD,
                                         player.action_progress + player.build_power)
            if player.action_progress >= ACTION_THRESHOLD:
                player.set_tile(atx, aty, TILE_WALL)
                player.items.pop()
                player.num_items  -= 1
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
    remaining   = []
    for item in ground_items:
        if player_rect.colliderect(pygame.Rect(item["x"] - 18, item["y"] - 18, 36, 36)):
            player.items.append(item["item"])
            player.num_items += 1
        else:
            remaining.append(item)
    ground_items[:] = remaining

    # ==========================================================================
    # DRAW
    # ==========================================================================

    # Tilemap
    for row_i, row in enumerate(tile_img_map):
        for col_i, tile_surf in enumerate(row):
            screen.blit(tile_surf, (col_i * TILE_SIZE - camera_x,
                                    row_i * TILE_SIZE - camera_y))

    # Ground items
    for item in ground_items:
        img = item_imgs[item["item"][0]]
        screen.blit(img, (item["x"] - camera_x - img.get_width()  // 2,
                          item["y"] - camera_y - img.get_height() // 2))

    # Player
    screen.blit(player.img, (
        player.x - camera_x - player.img.get_width()  // 2,
        player.y - camera_y - player.img.get_height() // 2,
    ))

    # Enemies
    for enemy in enemies:
        screen.blit(enemy.img, (
            enemy.x - camera_x - enemy.img.get_width()  // 2,
            enemy.y - camera_y - enemy.img.get_height() // 2,
        ))

    # Tile action highlights
    hb = player.get_hitbox(player.x, player.y)
    for ctX, ctY in player.get_adjacent_tiles(hb.centerx, hb.centery):
        tile_val  = player.get_tile_at_grid(ctX, ctY)
        tile_rect = pygame.Rect(ctX * TILE_SIZE, ctY * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        blocked   = tile_rect.colliderect(player.get_hitbox(player.x, player.y))

        if tile_val == TILE_SAND and player.num_items > 0:
            fill = (255,  50,  50,  50) if blocked else (0, 255, 100, 50)
        elif tile_val == TILE_WALL:
            fill = (255, 165, 0, 50)
        else:
            fill = (100, 100, 100, 30)

        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(overlay, fill, overlay.get_rect())
        screen.blit(overlay, (ctX * TILE_SIZE - camera_x, ctY * TILE_SIZE - camera_y))

    # ── HUD ───────────────────────────────────────────────────────────────────

    health_fill_rect.width = clamp(
        int(health_bar_rect.width * (player.health / player.total_health)),
        0, health_bar_rect.width,
    )

    hud_bg = pygame.Surface((health_bar_rect.width, health_bar_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(hud_bg, (0, 0, 0, 150), hud_bg.get_rect(), border_radius=10)
    screen.blit(hud_bg, health_bar_rect.topleft)
    pygame.draw.rect(screen, (0, 129, 0), health_fill_rect, border_radius=10)
    pygame.draw.rect(screen, (0, 0,   0), health_bar_rect,  width=3, border_radius=10)

    if player.action_progress > 0:
        bar_color = (255, 140, 0) if player.action_type == "build" else (133, 129, 110)
        fill_rect = pygame.Rect(action_bar_rect.x, action_bar_rect.y,
                                int(action_bar_rect.width * player.action_progress / ACTION_THRESHOLD),
                                action_bar_rect.height)
        bar_bg = pygame.Surface((action_bar_rect.width, action_bar_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, (0, 0, 0, 150), bar_bg.get_rect(), border_radius=3)
        screen.blit(bar_bg, action_bar_rect.topleft)
        pygame.draw.rect(screen, bar_color,  fill_rect,        border_radius=3)
        pygame.draw.rect(screen, (0, 1, 0),  action_bar_rect,  width=2, border_radius=3)

    # ── Debug overlay (press B) ───────────────────────────────────────────────
    if debug:
        tx = int(player.x / TILE_SIZE)
        ty = int(player.y / TILE_SIZE)

        tile_hl = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(tile_hl, (255, 255, 1, 80), tile_hl.get_rect())
        screen.blit(tile_hl, (tx * TILE_SIZE - camera_x, ty * TILE_SIZE - camera_y))
        pygame.draw.rect(screen, (255, 255, 1),
                         (tx * TILE_SIZE - camera_x, ty * TILE_SIZE - camera_y,
                          TILE_SIZE, TILE_SIZE), 2)

        hitbox = player.get_hitbox(player.x, player.y)
        pygame.draw.rect(screen, (255, 52, 50),
                         (hitbox.x - camera_x, hitbox.y - camera_y,
                          hitbox.width, hitbox.height), 2)

        for i, line in enumerate([
            f"pos:    ({int(player.x)}, {int(player.y)})",
            f"tile:   ({tx}, {ty})  val: {player.get_tile_at_grid(tx, ty)}",
            f"camera: ({int(camera_x)}, {int(camera_y)})",
            f"facing: {player.facing}   queue: {actions[0] if actions else 'idle'}",
        ]):
            screen.blit(debug_font.render(line, True, (255, 255, 255)), (8, 8 + i * 20))

    # ── End condition — replace with your own win/lose logic ──────────────────
    if player.health <= 0:
        running = False

    pygame.display.update()

# =============================================================================
# CLEANUP
# =============================================================================

pygame.quit()