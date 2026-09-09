import pygame
import sys
import random
import math
import json
import os
import hashlib

# ============================================================
# VOIDCLIPS BETA 2
# Open World Dragon Slayer RPG
# ============================================================

pygame.init()
pygame.font.init()

WIDTH = 1100
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VoidClips Beta 2")
clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

COLOR_BG = (12, 16, 25)
COLOR_PANEL = (27, 33, 46)
COLOR_PANEL2 = (38, 45, 60)

COLOR_TEXT = (240, 243, 250)
COLOR_MUTED = (150, 160, 180)

COLOR_GOLD = (240, 185, 55)
COLOR_RED = (220, 60, 65)
COLOR_GREEN = (70, 200, 105)
COLOR_BLUE = (65, 130, 235)
COLOR_PURPLE = (150, 80, 220)
COLOR_CYAN = (60, 205, 220)
COLOR_ORANGE = (240, 120, 45)

COLOR_GRASS = (45, 100, 58)
COLOR_GRASS2 = (52, 115, 64)
COLOR_WATER = (30, 80, 130)
COLOR_ROCK = (90, 90, 100)
COLOR_TREE = (35, 80, 42)

ELEMENT_COLORS = {
    "Fire": (235, 75, 40),
    "Water": (50, 135, 230),
    "Earth": (80, 170, 90),
    "Air": (150, 210, 235),
    "Void": (145, 65, 205)
}

# ============================================================
# FONTS
# ============================================================

def font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)

FONT_TITLE = font(42, True)
FONT_BIG = font(30, True)
FONT_MED = font(22, True)
FONT = font(18)
FONT_SMALL = font(15)
FONT_TINY = font(13)

# ============================================================
# UTILITIES
# ============================================================

def draw_text(surface, text, x, y, color=COLOR_TEXT, f=FONT, center=False):
    img = f.render(str(text), True, color)

    if center:
        rect = img.get_rect(center=(x, y))
    else:
        rect = img.get_rect(topleft=(x, y))

    surface.blit(img, rect)
    return rect


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def distance(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
# ACCOUNT SYSTEM
# ============================================================

ACCOUNT_FILE = "voidclips_accounts.json"


def load_accounts():
    if not os.path.exists(ACCOUNT_FILE):
        return {}

    try:
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_accounts(accounts):
    try:
        with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=4)
    except Exception as e:
        print("Could not save accounts:", e)


# ============================================================
# BUTTON
# ============================================================

class Button:
    def __init__(self, rect, text, color=COLOR_PANEL2, hover=COLOR_BLUE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()

        color = self.hover if self.rect.collidepoint(mouse) else self.color

        pygame.draw.rect(
            surface,
            color,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            surface,
            (80, 90, 110),
            self.rect,
            2,
            border_radius=8
        )

        draw_text(
            surface,
            self.text,
            self.rect.centerx,
            self.rect.centery,
            WHITE,
            FONT,
            True
        )

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ============================================================
# TEXT INPUT
# ============================================================

class TextInput:
    def __init__(self, rect, placeholder="", password=False):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.password = password
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_RETURN:
                self.active = False

            else:
                if len(self.text) < 24:
                    if event.unicode.isprintable():
                        self.text += event.unicode

    def draw(self, surface):
        color = COLOR_BLUE if self.active else (70, 78, 95)

        pygame.draw.rect(
            surface,
            (18, 22, 31),
            self.rect,
            border_radius=7
        )

        pygame.draw.rect(
            surface,
            color,
            self.rect,
            2,
            border_radius=7
        )

        if self.text:
            display = "*" * len(self.text) if self.password else self.text
            draw_text(surface, display, self.rect.x + 12,
                      self.rect.y + 10, WHITE, FONT)
        else:
            draw_text(
                surface,
                self.placeholder,
                self.rect.x + 12,
                self.rect.y + 10,
                COLOR_MUTED,
                FONT
            )


# ============================================================
# PLAYER
# ============================================================

class Player:
    def __init__(self, username, element="Fire"):
        self.username = username
        self.element = element

        self.x = 1800
        self.y = 1400

        self.speed = 4

        self.max_hp = 100
        self.hp = 100

        self.level = 1
        self.xp = 0
        self.gold = 100

        self.attack_power = 14

        self.skin = 0
        self.hair = 0
        self.armor = "Cloth"

        self.inventory = {
            "Wood": 0,
            "Stone": 0,
            "Iron": 0,
            "Crystal": 0,
            "Dragon Scale": 0,
            "Potion": 3
        }

        self.equipment = {
            "Helmet": None,
            "Chest": "Cloth",
            "Legs": "Cloth",
            "Weapon": "Rusty Sword"
        }

        self.cooldown = 0

    def xp_needed(self):
        return self.level * 100

    def add_xp(self, amount):
        self.xp += amount

        while self.xp >= self.xp_needed():
            self.xp -= self.xp_needed()
            self.level += 1
            self.max_hp += 20
            self.hp = self.max_hp
            self.attack_power += 3

    def attack(self):
        return random.randint(
            self.attack_power - 3,
            self.attack_power + 5
        )

    def use_potion(self):
        if self.inventory["Potion"] > 0 and self.hp < self.max_hp:
            self.inventory["Potion"] -= 1
            self.hp = min(self.max_hp, self.hp + 40)
            return True
        return False


# ============================================================
# RESOURCE
# ============================================================

class Resource:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y

        self.radius = 18

        self.collected = False
        self.respawn = 0

    def update(self):
        if self.collected:
            self.respawn -= 1

            if self.respawn <= 0:
                self.collected = False

    def collect(self, player):
        if self.collected:
            return False

        if distance(
            player.x,
            player.y,
            self.x,
            self.y
        ) < 45:

            player.inventory[self.kind] += 1

            self.collected = True
            self.respawn = FPS * 15

            return True

        return False

    def draw(self, surface, camera_x, camera_y):
        if self.collected:
            return

        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        colors = {
            "Wood": (130, 80, 40),
            "Stone": (130, 130, 140),
            "Iron": (170, 170, 180),
            "Crystal": (100, 210, 255),
            "Dragon Scale": (180, 70, 220)
        }

        color = colors.get(self.kind, WHITE)

        pygame.draw.circle(
            surface,
            color,
            (sx, sy),
            self.radius
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (sx, sy),
            self.radius,
            2
        )

        draw_text(
            surface,
            self.kind,
            sx,
            sy + 25,
            COLOR_TEXT,
            FONT_TINY,
            True
        )


# ============================================================
# NPC
# ============================================================

class NPC:
    def __init__(self, name, x, y, role):
        self.name = name
        self.x = x
        self.y = y
        self.role = role

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        pygame.draw.circle(
            surface,
            COLOR_GOLD,
            (sx, sy - 20),
            13
        )

        pygame.draw.rect(
            surface,
            COLOR_PURPLE,
            (sx - 15, sy - 7, 30, 35),
            border_radius=7
        )

        draw_text(
            surface,
            self.name,
            sx,
            sy - 48,
            WHITE,
            FONT_TINY,
            True
        )

        draw_text(
            surface,
            self.role,
            sx,
            sy + 35,
            COLOR_GOLD,
            FONT_TINY,
            True
        )


# ============================================================
# OTHER PLAYERS
# ============================================================

class WorldPlayer:
    def __init__(self, username, x, y, element):
        self.username = username
        self.x = x
        self.y = y
        self.element = element

        self.hp = 100
        self.max_hp = 100

        self.level = random.randint(1, 15)

        self.attack_timer = random.randint(0, 300)

    def update(self, world):
        self.attack_timer -= 1

        if self.attack_timer <= 0:
            self.attack_timer = random.randint(180, 500)

            self.x += random.randint(-120, 120)
            self.y += random.randint(-120, 120)

            self.x = clamp(self.x, 200, world.world_width - 200)
            self.y = clamp(self.y, 200, world.world_height - 200)

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        color = ELEMENT_COLORS.get(
            self.element,
            COLOR_BLUE
        )

        pygame.draw.circle(
            surface,
            color,
            (sx, sy - 20),
            13
        )

        pygame.draw.rect(
            surface,
            (75, 80, 95),
            (sx - 14, sy - 7, 28, 36),
            border_radius=6
        )

        pygame.draw.rect(
            surface,
            color,
            (sx - 14, sy - 7, 28, 8)
        )

        draw_text(
            surface,
            self.username,
            sx,
            sy - 50,
            WHITE,
            FONT_TINY,
            True
        )

        # HP bar
        pygame.draw.rect(
            surface,
            (60, 20, 25),
            (sx - 25, sy - 38, 50, 5)
        )

        pygame.draw.rect(
            surface,
            COLOR_GREEN,
            (
                sx - 25,
                sy - 38,
                int(50 * self.hp / self.max_hp),
                5
            )
        )


# ============================================================
# WORLD
# ============================================================

class World:
    def __init__(self):
        self.world_width = 3600
        self.world_height = 2800

        self.resources = []
        self.npcs = []
        self.other_players = []

        self.generate()

    def generate(self):
        random.seed(7)

        resource_types = [
            "Wood",
            "Stone",
            "Iron",
            "Crystal"
        ]

        for _ in range(150):
            kind = random.choice(resource_types)

            x = random.randint(
                100,
                self.world_width - 100
            )

            y = random.randint(
                100,
                self.world_height - 100
            )

            self.resources.append(
                Resource(kind, x, y)
            )

        # Rare dragon scales
        for _ in range(12):
            self.resources.append(
                Resource(
                    "Dragon Scale",
                    random.randint(200, self.world_width - 200),
                    random.randint(200, self.world_height - 200)
                )
            )

        self.npcs = [
            NPC("Elder", 1800, 1300, "Quest Giver"),
            NPC("Blacksmith", 1950, 1350, "Crafting"),
            NPC("Merchant", 1650, 1350, "Shop"),
            NPC("Mage", 1850, 1500, "Magic")
        ]

        names = [
            "DragonKnight",
            "ShadowX",
            "VoidWalker",
            "FireLord",
            "CrystalFox",
            "Knight_77",
            "Rogue",
            "StormBorn"
        ]

        elements = [
            "Fire",
            "Water",
            "Earth",
            "Air",
            "Void"
        ]

        for i in range(12):
            self.other_players.append(
                WorldPlayer(
                    random.choice(names) + str(i),
                    random.randint(400, self.world_width - 400),
                    random.randint(400, self.world_height - 400),
                    random.choice(elements)
                )
            )

    def update(self):
        for resource in self.resources:
            resource.update()

        for player in self.other_players:
            player.update(self)

    def draw(self, surface, camera_x, camera_y):
        # Grass
        surface.fill(COLOR_GRASS)

        tile = 80

        start_x = int(camera_x // tile) * tile
        start_y = int(camera_y // tile) * tile

        for x in range(start_x, int(camera_x + WIDTH) + tile, tile):
            for y in range(start_y, int(camera_y + HEIGHT) + tile, tile):

                sx = int(x - camera_x)
                sy = int(y - camera_y)

                pygame.draw.rect(
                    surface,
                    COLOR_GRASS2,
                    (sx, sy, tile - 2, tile - 2)
                )

        # Water lake
        lake = pygame.Rect(
            500 - camera_x,
            400 - camera_y,
            700,
            400
        )

        pygame.draw.ellipse(
            surface,
            COLOR_WATER,
            lake
        )

        # Town
        town = pygame.Rect(
            1450 - camera_x,
            1050 - camera_y,
            700,
            600
        )

        pygame.draw.rect(
            surface,
            (95, 70, 50),
            town,
            border_radius=25
        )

        draw_text(
            surface,
            "VOIDHAVEN",
            1800 - camera_x,
            1080 - camera_y,
            COLOR_GOLD,
            FONT_BIG,
            True
        )

        # Roads
        pygame.draw.rect(
            surface,
            (155, 125, 80),
            (0 - camera_x, 1370 - camera_y,
             self.world_width, 80)
        )

        pygame.draw.rect(
            surface,
            (155, 125, 80),
            (1760 - camera_x, 0 - camera_y,
             80, self.world_height)
        )

        for resource in self.resources:
            resource.draw(
                surface,
                camera_x,
                camera_y
            )

        for npc in self.npcs:
            npc.draw(
                surface,
                camera_x,
                camera_y
            )

        for player in self.other_players:
            player.draw(
                surface,
                camera_x,
                camera_y
            )


# ============================================================
# CHAT
# ============================================================

class Chat:
    def __init__(self):
        self.messages = [
            ("SERVER", "Welcome to VoidHaven!")
        ]

        self.input = ""
        self.active = False

    def add(self, username, message):
        self.messages.append(
            (username, message)
        )

        if len(self.messages) > 7:
            self.messages.pop(0)

    def handle_event(self, event, username):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(
                20,
                HEIGHT - 85,
                430,
                45
            ).collidepoint(event.pos):
                self.active = True

        if event.type == pygame.KEYDOWN and self.active:

            if event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]

            elif event.key == pygame.K_RETURN:
                if self.input.strip():
                    self.add(
                        username,
                        self.input.strip()
                    )

                self.input = ""
                self.active = False

            else:
                if len(self.input) < 70:
                    if event.unicode.isprintable():
                        self.input += event.unicode

    def draw(self, surface):
        panel = pygame.Rect(
            15,
            HEIGHT - 180,
            455,
            165
        )

        pygame.draw.rect(
            surface,
            (18, 22, 30),
            panel,
            border_radius=10
        )

        pygame.draw.rect(
            surface,
            (70, 80, 100),
            panel,
            2,
            border_radius=10
        )

        y = HEIGHT - 170

        for username, message in self.messages:
            draw_text(
                surface,
                f"{username}: {message}",
                28,
                y,
                COLOR_TEXT,
                FONT_SMALL
            )

            y += 19

        input_rect = pygame.Rect(
            25,
            HEIGHT - 65,
            430,
            40
        )

        pygame.draw.rect(
            surface,
            (12, 16, 23),
            input_rect,
            border_radius=6
        )

        pygame.draw.rect(
            surface,
            COLOR_BLUE if self.active else (70, 80, 95),
            input_rect,
            2,
            border_radius=6
        )

        display = self.input

        if self.active and not display:
            display = "Type message..."

        draw_text(
            surface,
            display,
            35,
            HEIGHT - 55,
            COLOR_MUTED if not self.input else WHITE,
            FONT_SMALL
        )


# ============================================================
# GAME
# ============================================================

class Game:
    def __init__(self):
        self.running = True

        self.state = "LOGIN"

        self.accounts = load_accounts()

        self.player = None

        self.world = World()

        self.chat = Chat()

        self.notification = ""
        self.notification_timer = 0

        self.selected_enemy = None

        self.craft_menu = False
        self.inventory_menu = False
        self.customize_menu = False

        self.login_username = TextInput(
            (390, 275, 320, 48),
            "Username"
        )

        self.login_password = TextInput(
            (390, 345, 320, 48),
            "Password",
            True
        )

        self.register_mode = False

        self.buttons = {}

    # --------------------------------------------------------
    # NOTIFICATION
    # --------------------------------------------------------

    def notify(self, text):
        self.notification = text
        self.notification_timer = FPS * 3

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    def login(self):
        username = self.login_username.text.strip()
        password = self.login_password.text

        if not username or not password:
            self.notify("Enter username and password.")
            return

        if username not in self.accounts:
            self.notify("Account not found.")
            return

        if self.accounts[username]["password"] != hash_password(password):
            self.notify("Incorrect password.")
            return

        data = self.accounts[username]

        self.player = Player(
            username,
            data.get("element", "Fire")
        )

        self.load_player_data(data)

        self.state = "WORLD"

        self.chat.add(
            "SERVER",
            f"Welcome back, {username}!"
        )

    def register(self):
        username = self.login_username.text.strip()
        password = self.login_password.text

        if len(username) < 3:
            self.notify("Username must be at least 3 characters.")
            return

        if len(password) < 4:
            self.notify("Password must be at least 4 characters.")
            return

        if username in self.accounts:
            self.notify("Username already exists.")
            return

        self.accounts[username] = {
            "password": hash_password(password),
            "element": "Fire",
            "level": 1,
            "gold": 100
        }

        save_accounts(self.accounts)

        self.notify(
            "Account created! You can now log in."
        )

        self.register_mode = False

    def load_player_data(self, data):
        self.player.level = data.get(
            "level",
            1
        )

        self.player.gold = data.get(
            "gold",
            100
        )

        self.player.element = data.get(
            "element",
            "Fire"
        )

    def save_player(self):
        if not self.player:
            return

        username = self.player.username

        if username not in self.accounts:
            self.accounts[username] = {}

        self.accounts[username].update({
            "password": self.accounts[username].get(
                "password",
                ""
            ),
            "element": self.player.element,
            "level": self.player.level,
            "gold": self.player.gold
        })

        save_accounts(self.accounts)

    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------

    def move_player(self):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.player.speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.player.speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.player.speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.player.speed

        if dx and dy:
            dx *= 0.707
            dy *= 0.707

        self.player.x += dx
        self.player.y += dy

        self.player.x = clamp(
            self.player.x,
            40,
            self.world.world_width - 40
        )

        self.player.y = clamp(
            self.player.y,
            40,
            self.world.world_height - 40
        )

    # --------------------------------------------------------
    # COLLECT
    # --------------------------------------------------------

    def collect_resources(self):
        for resource in self.world.resources:
            if resource.collect(self.player):
                self.notify(
                    f"Collected {resource.kind}!"
                )

    # --------------------------------------------------------
    # PVP
    # --------------------------------------------------------

    def find_nearby_player(self):
        closest = None
        closest_distance = 100000

        for other in self.world.other_players:
            d = distance(
                self.player.x,
                self.player.y,
                other.x,
                other.y
            )

            if d < 90 and d < closest_distance:
                closest = other
                closest_distance = d

        return closest

    def attack_player(self):
        enemy = self.find_nearby_player()

        if not enemy:
            self.notify(
                "No player nearby."
            )
            return

        damage = self.player.attack()

        enemy.hp -= damage

        self.chat.add(
            "COMBAT",
            f"You hit {enemy.username} for {damage}!"
        )

        if enemy.hp <= 0:
            reward = random.randint(25, 80)

            self.player.gold += reward
            self.player.add_xp(50)

            enemy.hp = enemy.max_hp

            enemy.x = random.randint(
                300,
                self.world.world_width - 300
            )

            enemy.y = random.randint(
                300,
                self.world.world_height - 300
            )

            self.notify(
                f"Player defeated! +{reward} gold"
            )

    # --------------------------------------------------------
    # CRAFTING
    # --------------------------------------------------------

    def craft(self, item):
        inv = self.player.inventory

        recipes = {
            "Iron Sword": {
                "Iron": 5,
                "Wood": 2
            },
            "Iron Armor": {
                "Iron": 10,
                "Crystal": 2
            },
            "Crystal Armor": {
                "Crystal": 8,
                "Dragon Scale": 2
            },
            "Potion": {
                "Crystal": 1,
                "Wood": 1
            }
        }

        if item not in recipes:
            return

        recipe = recipes[item]

        for material, amount in recipe.items():
            if inv.get(material, 0) < amount:
                self.notify(
                    f"Need more {material}."
                )
                return

        for material, amount in recipe.items():
            inv[material] -= amount

        if item == "Potion":
            inv["Potion"] += 1

        elif item == "Iron Sword":
            self.player.equipment["Weapon"] = item
            self.player.attack_power += 5

        elif item == "Iron Armor":
            self.player.equipment["Chest"] = item
            self.player.max_hp += 25
            self.player.hp = self.player.max_hp

        elif item == "Crystal Armor":
            self.player.equipment["Chest"] = item
            self.player.max_hp += 50
            self.player.hp = self.player.max_hp

        self.notify(
            f"Crafted {item}!"
        )

    # --------------------------------------------------------
    # CUSTOMIZATION
    # --------------------------------------------------------

    def change_skin(self):
        self.player.skin = (
            self.player.skin + 1
        ) % 5

        self.notify(
            f"Skin changed to {self.player.skin + 1}"
        )

    def change_element(self):
        elements = list(ELEMENT_COLORS.keys())

        index = elements.index(
            self.player.element
        )

        index = (
            index + 1
        ) % len(elements)

        self.player.element = elements[index]

        self.notify(
            f"Element changed to {self.player.element}"
        )

    # --------------------------------------------------------
    # DRAW PLAYER
    # --------------------------------------------------------

    def draw_player(self, surface, camera_x, camera_y):
        sx = int(self.player.x - camera_x)
        sy = int(self.player.y - camera_y)

        color = ELEMENT_COLORS.get(
            self.player.element,
            COLOR_BLUE
        )

        skin_colors = [
            (245, 205, 170),
            (190, 130, 90),
            (125, 80, 55),
            (245, 175, 130),
            (95, 60, 45)
        ]

        skin_color = skin_colors[
            self.player.skin
        ]

        # Shadow
        pygame.draw.ellipse(
            surface,
            (20, 30, 20),
            (sx - 20, sy + 20, 40, 12)
        )

        # Body
        pygame.draw.rect(
            surface,
            color,
            (sx - 17, sy - 10, 34, 42),
            border_radius=8
        )

        # Head
        pygame.draw.circle(
            surface,
            skin_color,
            (sx, sy - 25),
            14
        )

        # Armour
        if self.player.armor != "Cloth":
            pygame.draw.rect(
                surface,
                (160, 160, 170),
                (sx - 18, sy - 10, 36, 35),
                3,
                border_radius=7
            )

        # Sword
        pygame.draw.line(
            surface,
            (225, 225, 230),
            (sx + 15, sy),
            (sx + 40, sy - 30),
            5
        )

        # Name
        draw_text(
            surface,
            self.player.username,
            sx,
            sy - 55,
            WHITE,
            FONT_SMALL,
            True
        )

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def draw_hud(self, surface):
        # Top bar
        pygame.draw.rect(
            surface,
            (15, 19, 27),
            (0, 0, WIDTH, 75)
        )

        draw_text(
            surface,
            "VOIDCLIPS",
            20,
            15,
            COLOR_PURPLE,
            FONT_MED
        )

        draw_text(
            surface,
            f"Lv {self.player.level}",
            180,
            18,
            COLOR_GOLD,
            FONT
        )

        # HP
        pygame.draw.rect(
            surface,
            (60, 20, 25),
            (280, 20, 190, 18),
            border_radius=5
        )

        pygame.draw.rect(
            surface,
            COLOR_RED,
            (
                280,
                20,
                int(
                    190 *
                    self.player.hp /
                    self.player.max_hp
                ),
                18
            ),
            border_radius=5
        )

        draw_text(
            surface,
            f"{self.player.hp}/{self.player.max_hp}",
            375,
            29,
            WHITE,
            FONT_TINY,
            True
        )

        draw_text(
            surface,
            f"Gold: {self.player.gold}",
            500,
            18,
            COLOR_GOLD,
            FONT
        )

        draw_text(
            surface,
            f"Element: {self.player.element}",
            650,
            18,
            ELEMENT_COLORS[self.player.element],
            FONT
        )

        draw_text(
            surface,
            "WASD Move | E Collect | F Attack | I Inventory | C Craft | V Customize",
            20,
            55,
            COLOR_MUTED,
            FONT_TINY
        )

    def draw_inventory(self, surface):
        panel = pygame.Rect(
            700,
            100,
            370,
            500
        )

        pygame.draw.rect(
            surface,
            (20, 25, 35),
            panel,
            border_radius=12
        )

        pygame.draw.rect(
            surface,
            COLOR_BLUE,
            panel,
            2,
            border_radius=12
        )

        draw_text(
            surface,
            "INVENTORY",
            725,
            125,
            COLOR_GOLD,
            FONT_BIG
        )

        y = 185

        for item, amount in self.player.inventory.items():
            draw_text(
                surface,
                f"{item}: {amount}",
                735,
                y,
                WHITE,
                FONT
            )

            y += 40

        y += 10

        draw_text(
            surface,
            "EQUIPMENT",
            725,
            y,
            COLOR_CYAN,
            FONT_MED
        )

        y += 45

        for slot, item in self.player.equipment.items():
            draw_text(
                surface,
                f"{slot}: {item}",
                735,
                y,
                COLOR_TEXT,
                FONT_SMALL
            )

            y += 30

    def draw_crafting(self, surface):
        panel = pygame.Rect(
            680,
            90,
            390,
            540
        )

        pygame.draw.rect(
            surface,
            (20, 24, 34),
            panel,
            border_radius=12
        )

        pygame.draw.rect(
            surface,
            COLOR_GOLD,
            panel,
            2,
            border_radius=12
        )

        draw_text(
            surface,
            "CRAFTING",
            710,
            115,
            COLOR_GOLD,
            FONT_BIG
        )

        recipes = [
            ("Iron Sword", "5 Iron + 2 Wood"),
            ("Iron Armor", "10 Iron + 2 Crystal"),
            ("Crystal Armor", "8 Crystal + 2 Dragon Scale"),
            ("Potion", "1 Crystal + 1 Wood")
        ]

        y = 180

        for item, recipe in recipes:
            rect = pygame.Rect(
                705,
                y,
                335,
                70
            )

            pygame.draw.rect(
                surface,
                COLOR_PANEL2,
                rect,
                border_radius=8
            )

            draw_text(
                surface,
                item,
                rect.x + 15,
                rect.y + 10,
                WHITE,
                FONT
            )

            draw_text(
                surface,
                recipe,
                rect.x + 15,
                rect.y + 40,
                COLOR_MUTED,
                FONT_TINY
            )

            y += 85

    def draw_customize(self, surface):
        panel = pygame.Rect(
            700,
            100,
            350,
            450
        )

        pygame.draw.rect(
            surface,
            (20, 24, 34),
            panel,
            border_radius=12
        )

        pygame.draw.rect(
            surface,
            COLOR_PURPLE,
            panel,
            2,
            border_radius=12
        )

        draw_text(
            surface,
            "CHARACTER",
            730,
            130,
            COLOR_PURPLE,
            FONT_BIG
        )

        draw_text(
            surface,
            f"Element: {self.player.element}",
            730,
            195,
            ELEMENT_COLORS[self.player.element],
            FONT
        )

        draw_text(
            surface,
            f"Skin: {self.player.skin + 1}",
            730,
            240,
            WHITE,
            FONT
        )

        draw_text(
            surface,
            f"Weapon: {self.player.equipment['Weapon']}",
            730,
            285,
            WHITE,
            FONT
        )

        draw_text(
            surface,
            f"Armour: {self.player.equipment['Chest']}",
            730,
            330,
            WHITE,
            FONT
        )

        draw_text(
            surface,
            "S = change skin",
            730,
            400,
            COLOR_MUTED,
            FONT_SMALL
        )

        draw_text(
            surface,
            "L = change element",
            730,
            430,
            COLOR_MUTED,
            FONT_SMALL
        )

    # --------------------------------------------------------
    # LOGIN SCREEN
    # --------------------------------------------------------

    def draw_login(self, surface):
        surface.fill(COLOR_BG)

        # Background glow
        for r in range(350, 50, -25):
            alpha_color = (
                20 + int((350 - r) / 8),
                15,
                45 + int((350 - r) / 4)
            )

            pygame.draw.circle(
                surface,
                alpha_color,
                (WIDTH // 2, 220),
                r,
                2
            )

        draw_text(
            surface,
            "VOIDCLIPS",
            WIDTH // 2,
            100,
            COLOR_PURPLE,
            FONT_TITLE,
            True
        )

        draw_text(
            surface,
            "BETA 2",
            WIDTH // 2,
            145,
            COLOR_GOLD,
            FONT_MED,
            True
        )

        draw_text(
            surface,
            "OPEN WORLD DRAGON RPG",
            WIDTH // 2,
            185,
            COLOR_MUTED,
            FONT_SMALL,
            True
        )

        draw_text(
            surface,
            "Username",
            390,
            250,
            COLOR_MUTED,
            FONT_SMALL
        )

        draw_text(
            surface,
            "Password",
            390,
            320,
            COLOR_MUTED,
            FONT_SMALL
        )

        self.login_username.draw(surface)
        self.login_password.draw(surface)

        login_button = Button(
            (390, 420, 150, 48),
            "LOGIN",
            COLOR_PANEL2,
            COLOR_BLUE
        )

        register_button = Button(
            (560, 420, 150, 48),
            "REGISTER",
            COLOR_PANEL2,
            COLOR_PURPLE
        )

        login_button.draw(surface)
        register_button.draw(surface)

        draw_text(
            surface,
            "Click a box and type normally.",
            WIDTH // 2,
            510,
            COLOR_MUTED,
            FONT_SMALL,
            True
        )

        draw_text(
            surface,
            "No server required for this local beta.",
            WIDTH // 2,
            535,
            COLOR_MUTED,
            FONT_TINY,
            True
        )

    # --------------------------------------------------------
    # WORLD RENDER
    # --------------------------------------------------------

    def render_world(self):
        camera_x = self.player.x - WIDTH / 2
        camera_y = self.player.y - HEIGHT / 2

        camera_x = clamp(
            camera_x,
            0,
            self.world.world_width - WIDTH
        )

        camera_y = clamp(
            camera_y,
            0,
            self.world.world_height - HEIGHT
        )

        self.world.draw(
            screen,
            camera_x,
            camera_y
        )

        self.draw_player(
            screen,
            camera_x,
            camera_y
        )

        self.draw_hud(screen)

        self.chat.draw(screen)

        # Nearby player hint
        enemy = self.find_nearby_player()

        if enemy:
            draw_text(
                screen,
                f"F - Attack {enemy.username}",
                WIDTH // 2,
                100,
                COLOR_RED,
                FONT_MED,
                True
            )

        if self.inventory_menu:
            self.draw_inventory(screen)

        if self.craft_menu:
            self.draw_crafting(screen)

        if self.customize_menu:
            self.draw_customize(screen)

        if self.notification_timer > 0:
            pygame.draw.rect(
                screen,
                (15, 20, 30),
                (WIDTH // 2 - 220, HEIGHT - 230, 440, 50),
                border_radius=10
            )

            draw_text(
                screen,
                self.notification,
                WIDTH // 2,
                HEIGHT - 205,
                COLOR_GOLD,
                FONT,
                True
            )

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    def handle_event(self, event):

        if self.state == "LOGIN":

            self.login_username.handle_event(event)
            self.login_password.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    login_rect = pygame.Rect(
                        390,
                        420,
                        150,
                        48
                    )

                    register_rect = pygame.Rect(
                        560,
                        420,
                        150,
                        48
                    )

                    if login_rect.collidepoint(
                        event.pos
                    ):
                        self.login()

                    elif register_rect.collidepoint(
                        event.pos
                    ):
                        if self.register_mode:
                            self.register()
                        else:
                            self.register_mode = True
                            self.notify(
                                "Fill in your details and click REGISTER again."
                            )

            return

        if self.state == "WORLD":

            self.chat.handle_event(
                event,
                self.player.username
            )

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_e:
                    self.collect_resources()

                elif event.key == pygame.K_f:
                    self.attack_player()

                elif event.key == pygame.K_i:
                    self.inventory_menu = not self.inventory_menu
                    self.craft_menu = False
                    self.customize_menu = False

                elif event.key == pygame.K_c:
                    self.craft_menu = not self.craft_menu
                    self.inventory_menu = False
                    self.customize_menu = False

                elif event.key == pygame.K_v:
                    self.customize_menu = not self.customize_menu
                    self.inventory_menu = False
                    self.craft_menu = False

                elif event.key == pygame.K_h:
                    if self.player.use_potion():
                        self.notify(
                            "Potion used!"
                        )
                    else:
                        self.notify(
                            "Cannot use potion."
                        )

                elif event.key == pygame.K_s:
                    if self.customize_menu:
                        self.change_skin()

                elif event.key == pygame.K_l:
                    if self.customize_menu:
                        self.change_element()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    # Craft buttons
                    if self.craft_menu:

                        recipes = [
                            "Iron Sword",
                            "Iron Armor",
                            "Crystal Armor",
                            "Potion"
                        ]

                        for i, item in enumerate(recipes):

                            rect = pygame.Rect(
                                705,
                                180 + i * 85,
                                335,
                                70
                            )

                            if rect.collidepoint(
                                event.pos
                            ):
                                self.craft(item)

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(self):

        if self.state != "WORLD":
            return

        self.move_player()

        self.world.update()

        if self.notification_timer > 0:
            self.notification_timer -= 1

        # Small automatic regen
        if self.player.hp < self.player.max_hp:
            if random.random() < 0.002:
                self.player.hp += 1

        self.save_player()

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    def render(self):

        if self.state == "LOGIN":
            self.draw_login(screen)

        elif self.state == "WORLD":
            self.render_world()

        pygame.display.flip()

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(self):

        while self.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.save_player()
                    self.running = False

                self.handle_event(event)

            self.update()

            self.render()

            clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ============================================================
# START GAME
# ============================================================

if __name__ == "__main__":
    game = Game()
    game.run()
