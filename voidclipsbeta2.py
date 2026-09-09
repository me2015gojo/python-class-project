import pygame
import socket
import threading
import json
import sys
import os
import math
import random
import time

pygame.init()
pygame.font.init()

# ============================================================
# DRAGON SLAYER ONLINE
# Single-file multiplayer RPG prototype
# ============================================================

WIDTH, HEIGHT = 1280, 720
FPS = 60
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5050
DATA_FILE = "dragon_players.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Slayer Online")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------

BG = (10, 13, 20)
PANEL = (20, 25, 36)
PANEL2 = (28, 34, 48)
WHITE = (240, 243, 250)
MUTED = (145, 155, 175)
GOLD = (239, 184, 67)
RED = (220, 65, 70)
GREEN = (70, 205, 120)
BLUE = (70, 145, 235)
PURPLE = (165, 90, 230)
CYAN = (75, 205, 220)
ORANGE = (235, 120, 45)
DARK = (7, 9, 14)
BLACK = (0, 0, 0)

ELEMENTS = {
    "Fire": (235, 75, 45),
    "Water": (65, 145, 235),
    "Earth": (75, 175, 100),
    "Air": (130, 205, 225),
    "Void": (165, 80, 220)
}

# ---------------- FONTS ----------------

def font(size, bold=False):
    return pygame.font.SysFont("arial", size, bold=bold)

F12 = font(12)
F14 = font(14)
F16 = font(16)
F18 = font(18)
F20 = font(20, True)
F24 = font(24, True)
F30 = font(30, True)
F42 = font(42, True)
F60 = font(60, True)

# ============================================================
# UTILITY
# ============================================================

def clamp(v, a, b):
    return max(a, min(b, v))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def draw_text(surface, text, pos, f=F16, color=WHITE, center=False):
    img = f.render(str(text), True, color)
    rect = img.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(img, rect)
    return rect


def panel(surface, rect, color=PANEL, radius=12, border=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

    if border:
        pygame.draw.rect(surface, border, rect, 2, border_radius=radius)


def button(surface, rect, text, mouse, active=False):
    hover = rect.collidepoint(mouse)
    col = (52, 63, 85) if hover else PANEL2

    if active:
        col = (68, 90, 125)

    pygame.draw.rect(surface, col, rect, border_radius=8)
    pygame.draw.rect(surface, (65, 75, 95), rect, 1, border_radius=8)

    draw_text(surface, text, rect.center, F16, WHITE, True)
    return hover


# ============================================================
# SERVER
# ============================================================

class Server:
    def __init__(self):
        self.players = {}
        self.clients = {}
        self.lock = threading.Lock()
        self.running = True

        self.world_items = [
            {"id": i, "x": random.randint(150, 3000),
             "y": random.randint(150, 2500),
             "type": random.choice(["wood", "ore", "herb"])}
            for i in range(180)
        ]

        self.load_players()

    def load_players(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.players = json.load(f)
            except:
                self.players = {}

    def save_players(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.players, f, indent=2)
        except:
            pass

    def send(self, conn, data):
        try:
            conn.sendall((json.dumps(data) + "\n").encode())
        except:
            pass

    def broadcast(self, data, exclude=None):
        raw = (json.dumps(data) + "\n").encode()

        with self.lock:
            for name, conn in list(self.clients.items()):
                if conn != exclude:
                    try:
                        conn.sendall(raw)
                    except:
                        pass

    def register(self, username, password):
        with self.lock:
            if username in self.players:
                return False, "Username already exists."

            if len(username) < 3:
                return False, "Username must be at least 3 characters."

            if len(password) < 4:
                return False, "Password must be at least 4 characters."

            self.players[username] = {
                "password": password,
                "x": 1500,
                "y": 1250,
                "hp": 100,
                "max_hp": 100,
                "level": 1,
                "xp": 0,
                "gold": 100,
                "element": "Fire",
                "skin": 0,
                "hair": 0,
                "inventory": {
                    "wood": 0,
                    "ore": 0,
                    "herb": 0,
                    "iron_armor": 0,
                    "health_potion": 2
                }
            }

            self.save_players()

        return True, "Account created."

    def login(self, username, password):
        with self.lock:
            p = self.players.get(username)

            if not p:
                return False, "Account not found."

            if p["password"] != password:
                return False, "Incorrect password."

        return True, "Login successful."

    def handle_client(self, conn, address):
        username = None

        try:
            file = conn.makefile("r")

            for line in file:
                if not line.strip():
                    continue

                try:
                    msg = json.loads(line)
                except:
                    continue

                action = msg.get("type")

                if action == "register":
                    ok, text = self.register(
                        msg.get("username", ""),
                        msg.get("password", "")
                    )

                    self.send(conn, {
                        "type": "auth",
                        "success": ok,
                        "message": text
                    })

                elif action == "login":
                    ok, text = self.login(
                        msg.get("username", ""),
                        msg.get("password", "")
                    )

                    if ok:
                        username = msg["username"]

                        with self.lock:
                            self.clients[username] = conn

                    p = self.players.get(username, {})

                    self.send(conn, {
                        "type": "auth",
                        "success": ok,
                        "message": text,
                        "player": p if ok else None
                    })

                    if ok:
                        self.broadcast({
                            "type": "system",
                            "message": f"{username} entered the realm."
                        })

                elif action == "move" and username:
                    with self.lock:
                        p = self.players.get(username)

                        if p:
                            p["x"] = clamp(msg["x"], 80, 2920)
                            p["y"] = clamp(msg["y"], 80, 2420)

                elif action == "chat" and username:
                    text = str(msg.get("message", "")).strip()

                    if text:
                        self.broadcast({
                            "type": "chat",
                            "username": username,
                            "message": text[:120]
                        })

                elif action == "update" and username:
                    with self.lock:
                        if username in self.players:
                            for key in [
                                "x", "y", "hp", "max_hp",
                                "level", "xp", "gold",
                                "element", "skin", "hair",
                                "inventory"
                            ]:
                                if key in msg:
                                    self.players[username][key] = msg[key]

                elif action == "request_world" and username:
                    with self.lock:
                        players = {
                            name: {
                                "x": p["x"],
                                "y": p["y"],
                                "hp": p["hp"],
                                "max_hp": p["max_hp"],
                                "level": p["level"],
                                "element": p["element"],
                                "skin": p.get("skin", 0),
                                "hair": p.get("hair", 0)
                            }
                            for name, p in self.players.items()
                            if name in self.clients
                        }

                    self.send(conn, {
                        "type": "world",
                        "players": players,
                        "resources": self.world_items
                    })

        except Exception:
            pass

        finally:
            if username:
                with self.lock:
                    self.clients.pop(username, None)

                self.broadcast({
                    "type": "system",
                    "message": f"{username} left the realm."
                })

                self.save_players()

            try:
                conn.close()
            except:
                pass

    def run(self):
        print("Dragon Slayer server starting...")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", SERVER_PORT))
        server.listen(20)

        print(f"Server running on port {SERVER_PORT}")

        while self.running:
            try:
                conn, addr = server.accept()

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                )

                thread.start()

            except:
                break


# ============================================================
# NETWORK CLIENT
# ============================================================

class Network:
    def __init__(self):
        self.sock = None
        self.connected = False
        self.incoming = []
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_IP, SERVER_PORT))
            self.connected = True

            threading.Thread(
                target=self.receive,
                daemon=True
            ).start()

            return True
        except:
            return False

    def receive(self):
        buffer = ""

        while self.connected:
            try:
                data = self.sock.recv(4096)

                if not data:
                    break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    try:
                        msg = json.loads(line)

                        with self.lock:
                            self.incoming.append(msg)

                    except:
                        pass

            except:
                break

        self.connected = False

    def send(self, data):
        if not self.connected:
            return

        try:
            self.sock.sendall(
                (json.dumps(data) + "\n").encode()
            )
        except:
            self.connected = False

    def messages(self):
        with self.lock:
            msgs = self.incoming[:]
            self.incoming.clear()

        return msgs


# ============================================================
# PLAYER
# ============================================================

class Player:
    def __init__(self):
        self.username = ""
        self.x = 1500
        self.y = 1250

        self.hp = 100
        self.max_hp = 100

        self.level = 1
        self.xp = 0
        self.gold = 100

        self.element = "Fire"
        self.skin = 0
        self.hair = 0

        self.inventory = {
            "wood": 0,
            "ore": 0,
            "herb": 0,
            "iron_armor": 0,
            "health_potion": 2
        }

        self.attack_cooldown = 0

    def xp_needed(self):
        return 100 + self.level * 75

    def gain_xp(self, amount):
        self.xp += amount

        while self.xp >= self.xp_needed():
            self.xp -= self.xp_needed()
            self.level += 1
            self.max_hp += 20
            self.hp = self.max_hp

    def damage(self):
        return random.randint(
            12 + self.level * 2,
            20 + self.level * 3
        )

    def heal(self):
        if self.inventory["health_potion"] <= 0:
            return False

        self.inventory["health_potion"] -= 1
        self.hp = min(self.max_hp, self.hp + 40)
        return True


# ============================================================
# ENEMIES
# ============================================================

class Enemy:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind

        if kind == "Goblin":
            self.hp = 50
            self.max_hp = 50
            self.damage = 8
            self.color = GREEN

        elif kind == "Wraith":
            self.hp = 80
            self.max_hp = 80
            self.damage = 13
            self.color = PURPLE

        else:
            self.hp = 120
            self.max_hp = 120
            self.damage = 18
            self.color = RED

        self.attack_timer = random.uniform(1, 3)
        self.dead = False

    def update(self, player, dt):
        if self.dead:
            return

        d = distance((self.x, self.y), (player.x, player.y))

        if d < 330:
            if d > 70:
                angle = math.atan2(
                    player.y - self.y,
                    player.x - self.x
                )

                self.x += math.cos(angle) * 35 * dt
                self.y += math.sin(angle) * 35 * dt

            self.attack_timer -= dt

            if d < 70 and self.attack_timer <= 0:
                player.hp -= self.damage
                self.attack_timer = 2


# ============================================================
# GAME
# ============================================================

class Game:
    def __init__(self):
        self.net = Network()
        self.player = Player()

        self.state = "LOGIN"
        self.auth_mode = "login"

        self.username = ""
        self.password = ""
        self.chat_input = ""

        self.active_field = "username"
        self.message = ""

        self.camera_x = 0
        self.camera_y = 0

        self.players = {}
        self.resources = []

        self.enemies = [
            Enemy(800, 800, "Goblin"),
            Enemy(1100, 600, "Goblin"),
            Enemy(1900, 900, "Wraith"),
            Enemy(2300, 1500, "Dragonling"),
            Enemy(700, 1900, "Wraith"),
            Enemy(2500, 500, "Dragonling")
        ]

        self.chat = [
            "Welcome to the realm.",
            "Gather materials and forge your destiny."
        ]

        self.chat_open = False
        self.inventory_open = False
        self.customize_open = False

        self.last_send = 0
        self.time = 0

        self.connecting = False

    # ========================================================
    # NETWORK
    # ========================================================

    def connect(self):
        if self.net.connected:
            return

        self.connecting = True

        if self.net.connect():
            self.message = "Connected to server."
        else:
            self.message = "Could not connect to server."

        self.connecting = False

    def send_auth(self):
        if not self.username or not self.password:
            self.message = "Enter both username and password."
            return

        if not self.net.connected:
            self.connect()

        if not self.net.connected:
            return

        self.net.send({
            "type": self.auth_mode,
            "username": self.username,
            "password": self.password
        })

    # ========================================================
    # INPUT
    # ========================================================

    def input_event(self, event):

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---------------- LOGIN ----------------

        if self.state == "LOGIN":

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                user_box = pygame.Rect(390, 270, 500, 55)
                pass_box = pygame.Rect(390, 350, 500, 55)

                if user_box.collidepoint(mx, my):
                    self.active_field = "username"

                elif pass_box.collidepoint(mx, my):
                    self.active_field = "password"

                login_button = pygame.Rect(390, 440, 240, 55)
                register_button = pygame.Rect(650, 440, 240, 55)

                if login_button.collidepoint(mx, my):
                    self.send_auth()

                elif register_button.collidepoint(mx, my):
                    self.auth_mode = (
                        "register"
                        if self.auth_mode == "login"
                        else "login"
                    )

                    self.message = (
                        "Register mode."
                        if self.auth_mode == "register"
                        else "Login mode."
                    )

                connect_button = pygame.Rect(390, 515, 500, 45)

                if connect_button.collidepoint(mx, my):
                    self.connect()

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_TAB:
                    self.active_field = (
                        "password"
                        if self.active_field == "username"
                        else "username"
                    )

                elif event.key == pygame.K_BACKSPACE:

                    if self.active_field == "username":
                        self.username = self.username[:-1]
                    else:
                        self.password = self.password[:-1]

                elif event.key == pygame.K_RETURN:
                    self.send_auth()

                elif event.unicode.isprintable():

                    if self.active_field == "username":
                        if len(self.username) < 18:
                            self.username += event.unicode

                    else:
                        if len(self.password) < 32:
                            self.password += event.unicode

            return

        # ---------------- WORLD ----------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_i:
                self.inventory_open = not self.inventory_open

            elif event.key == pygame.K_c:
                self.customize_open = not self.customize_open

            elif event.key == pygame.K_RETURN:
                self.chat_open = not self.chat_open

                if not self.chat_open:
                    self.send_chat()

            elif event.key == pygame.K_h:
                if self.player.heal():
                    self.message = "You drank a health potion."

            elif event.key == pygame.K_ESCAPE:
                self.inventory_open = False
                self.customize_open = False
                self.chat_open = False

            elif self.chat_open:

                if event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]

                elif event.key == pygame.K_RETURN:
                    self.send_chat()

                elif event.unicode.isprintable():
                    if len(self.chat_input) < 100:
                        self.chat_input += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = event.pos

            if self.customize_open:
                self.handle_customize_click(mx, my)
                return

            if self.inventory_open:
                self.handle_inventory_click(mx, my)
                return

            if not self.chat_open:
                self.attack(mx, my)

    # ========================================================
    # CHAT
    # ========================================================

    def send_chat(self):
        if self.chat_input.strip():
            self.net.send({
                "type": "chat",
                "message": self.chat_input.strip()
            })

        self.chat_input = ""

    # ========================================================
    # COMBAT
    # ========================================================

    def attack(self, mx, my):
        if self.player.attack_cooldown > 0:
            return

        world_x = mx + self.camera_x
        world_y = my + self.camera_y

        # Enemy attack
        for enemy in self.enemies:

            if enemy.dead:
                continue

            if distance(
                (world_x, world_y),
                (enemy.x, enemy.y)
            ) < 80:

                dmg = self.player.damage()
                enemy.hp -= dmg

                self.message = (
                    f"You hit {enemy.kind} for {dmg}."
                )

                if enemy.hp <= 0:
                    enemy.dead = True
                    self.player.gold += random.randint(10, 35)
                    self.player.gain_xp(random.randint(20, 45))
                    self.message = (
                        f"{enemy.kind} defeated! "
                        f"+XP +Gold"
                    )

                self.player.attack_cooldown = 0.35
                return

        # Player attack
        for name, p in self.players.items():

            if name == self.player.username:
                continue

            if distance(
                (world_x, world_y),
                (p["x"], p["y"])
            ) < 70:

                dmg = self.player.damage()

                self.net.send({
                    "type": "pvp",
                    "target": name,
                    "damage": dmg
                })

                self.message = (
                    f"You attacked {name}!"
                )

                self.player.attack_cooldown = 0.5
                return

    # ========================================================
    # GATHERING
    # ========================================================

    def gather(self):
        for r in self.resources:

            if distance(
                (self.player.x, self.player.y),
                (r["x"], r["y"])
            ) < 65:

                typ = r["type"]

                self.player.inventory[typ] += 1

                self.message = f"Collected {typ}."

                self.resources.remove(r)
                return

    # ========================================================
    # CRAFTING
    # ========================================================

    def craft(self):
        inv = self.player.inventory

        if inv["wood"] >= 5 and inv["ore"] >= 8:

            inv["wood"] -= 5
            inv["ore"] -= 8
            inv["iron_armor"] += 1

            self.player.max_hp += 25
            self.player.hp = self.player.max_hp

            self.message = "Forged Iron Dragon Armour!"

        else:
            self.message = "Need 5 wood and 8 ore."

    # ========================================================
    # CUSTOMIZATION
    # ========================================================

    def handle_customize_click(self, mx, my):

        if pygame.Rect(760, 230, 200, 45).collidepoint(mx, my):
            self.player.skin = (
                self.player.skin + 1
            ) % 5

        if pygame.Rect(760, 290, 200, 45).collidepoint(mx, my):
            self.player.hair = (
                self.player.hair + 1
            ) % 5

        if pygame.Rect(760, 350, 200, 45).collidepoint(mx, my):
            elements = list(ELEMENTS)
            i = elements.index(self.player.element)
            self.player.element = elements[
                (i + 1) % len(elements)
            ]

        if pygame.Rect(760, 430, 200, 50).collidepoint(mx, my):
            self.customize_open = False

    # ========================================================
    # INVENTORY
    # ========================================================

    def handle_inventory_click(self, mx, my):

        if pygame.Rect(
            720, 570, 200, 50
        ).collidepoint(mx, my):
            self.craft()

        if pygame.Rect(
            720, 630, 200, 50
        ).collidepoint(mx, my):
            self.inventory_open = False

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        self.time += dt

        if self.state != "WORLD":
            return

        keys = pygame.key.get_pressed()

        speed = 230

        if keys[pygame.K_LSHIFT]:
            speed = 340

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        if dx or dy:

            length = math.hypot(dx, dy)

            dx /= length
            dy /= length

            self.player.x += dx * speed * dt
            self.player.y += dy * speed * dt

            self.player.x = clamp(
                self.player.x, 70, 2930
            )

            self.player.y = clamp(
                self.player.y, 70, 2430
            )

        self.player.attack_cooldown = max(
            0,
            self.player.attack_cooldown - dt
        )

        for enemy in self.enemies:
            enemy.update(self.player, dt)

        # Gather automatically when pressing E
        if keys[pygame.K_e]:
            self.gather()

        # Network movement
        if time.time() - self.last_send > 0.08:

            self.net.send({
                "type": "move",
                "x": self.player.x,
                "y": self.player.y
            })

            self.last_send = time.time()

        # Camera
        self.camera_x = clamp(
            self.player.x - WIDTH / 2,
            0,
            3000 - WIDTH
        )

        self.camera_y = clamp(
            self.player.y - HEIGHT / 2,
            0,
            2500 - HEIGHT
        )

        # Receive network
        for msg in self.net.messages():
            self.handle_network(msg)

    # ========================================================
    # NETWORK EVENTS
    # ========================================================

    def handle_network(self, msg):

        typ = msg.get("type")

        if typ == "auth":

            self.message = msg.get("message", "")

            if msg.get("success"):

                data = msg.get("player", {})

                self.player.username = self.username

                self.player.x = data.get("x", 1500)
                self.player.y = data.get("y", 1250)

                self.player.hp = data.get("hp", 100)
                self.player.max_hp = data.get("max_hp", 100)
                self.player.level = data.get("level", 1)
                self.player.xp = data.get("xp", 0)
                self.player.gold = data.get("gold", 100)
                self.player.element = data.get(
                    "element", "Fire"
                )

                self.player.skin = data.get("skin", 0)
                self.player.hair = data.get("hair", 0)

                self.player.inventory = data.get(
                    "inventory",
                    self.player.inventory
                )

                self.state = "WORLD"

                self.net.send({
                    "type": "request_world"
                })

        elif typ == "world":

            self.players = msg.get("players", {})
            self.resources = msg.get("resources", [])

        elif typ == "chat":

            self.chat.append(
                f"{msg.get('username', '?')}: "
                f"{msg.get('message', '')}"
            )

            self.chat = self.chat[-8:]

        elif typ == "system":

            self.chat.append(
                "[Realm] " + msg.get("message", "")
            )

            self.chat = self.chat[-8:]

    # ========================================================
    # RENDER WORLD
    # ========================================================

    def render_world(self):

        screen.fill((18, 39, 29))

        # Ground
        pygame.draw.rect(
            screen,
            (26, 62, 42),
            (0, 0, WIDTH, HEIGHT)
        )

        # World grid
        grid = 100

        for x in range(
            int(self.camera_x // grid) * grid,
            int(self.camera_x + WIDTH) + grid,
            grid
        ):
            sx = x - self.camera_x
            pygame.draw.line(
                screen,
                (28, 67, 45),
                (sx, 0),
                (sx, HEIGHT)
            )

        for y in range(
            int(self.camera_y // grid) * grid,
            int(self.camera_y + HEIGHT) + grid,
            grid
        ):
            sy = y - self.camera_y
            pygame.draw.line(
                screen,
                (28, 67, 45),
                (0, sy),
                (WIDTH, sy)
            )

        # River
        river = pygame.Rect(
            1350 - self.camera_x,
            0,
            220,
            HEIGHT
        )

        pygame.draw.rect(
            screen,
            (25, 80, 115),
            river
        )

        # Town
        town_x = 1350 - self.camera_x
        town_y = 1050 - self.camera_y

        pygame.draw.circle(
            screen,
            (90, 75, 55),
            (int(town_x), int(town_y)),
            230
        )

        draw_text(
            screen,
            "EMBERFALL",
            (town_x, town_y - 250),
            F24,
            GOLD,
            True
        )

        # Trees
        random.seed(7)

        for i in range(100):

            x = random.randint(40, 2960)
            y = random.randint(40, 2460)

            sx = x - self.camera_x
            sy = y - self.camera_y

            if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:

                pygame.draw.circle(
                    screen,
                    (18, 90, 48),
                    (int(sx), int(sy)),
                    25
                )

                pygame.draw.rect(
                    screen,
                    (75, 55, 35),
                    (sx - 6, sy + 12, 12, 30)
                )

        # Resources
        for r in self.resources:

            sx = r["x"] - self.camera_x
            sy = r["y"] - self.camera_y

            if r["type"] == "wood":
                col = (115, 75, 38)

            elif r["type"] == "ore":
                col = (125, 135, 155)

            else:
                col = (80, 190, 100)

            pygame.draw.circle(
                screen,
                col,
                (int(sx), int(sy)),
                13
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (int(sx), int(sy)),
                13,
                2
            )

        # Enemies
        for enemy in self.enemies:

            if enemy.dead:
                continue

            sx = enemy.x - self.camera_x
            sy = enemy.y - self.camera_y

            pygame.draw.circle(
                screen,
                enemy.color,
                (int(sx), int(sy)),
                28
            )

            pygame.draw.circle(
                screen,
                BLACK,
                (int(sx), int(sy)),
                28,
                3
            )

            draw_text(
                screen,
                enemy.kind,
                (sx, sy - 50),
                F12,
                WHITE,
                True
            )

            pygame.draw.rect(
                screen,
                (60, 20, 20),
                (sx - 30, sy - 40, 60, 6)
            )

            pygame.draw.rect(
                screen,
                RED,
                (
                    sx - 30,
                    sy - 40,
                    60 * max(
                        0,
                        enemy.hp / enemy.max_hp
                    ),
                    6
                )
            )

        # Other players
        for name, p in self.players.items():

            if name == self.player.username:
                continue

            sx = p["x"] - self.camera_x
            sy = p["y"] - self.camera_y

            self.draw_character(
                sx,
                sy,
                p.get("element", "Fire"),
                p.get("skin", 0),
                p.get("hair", 0)
            )

            draw_text(
                screen,
                f"{name}  Lv.{p.get('level', 1)}",
                (sx, sy - 55),
                F12,
                WHITE,
                True
            )

        # Local player
        self.draw_character(
            self.player.x - self.camera_x,
            self.player.y - self.camera_y,
            self.player.element,
            self.player.skin,
            self.player.hair
        )

        draw_text(
            screen,
            self.player.username,
            (
                self.player.x - self.camera_x,
                self.player.y - 58
            ),
            F12,
            GOLD,
            True
        )

        self.draw_hud()

        if self.inventory_open:
            self.draw_inventory()

        if self.customize_open:
            self.draw_customize()

        if self.chat_open:
            self.draw_chat_box()

    # ========================================================
    # CHARACTER
    # ========================================================

    def draw_character(
        self,
        x,
        y,
        element,
        skin=0,
        hair=0
    ):

        col = ELEMENTS.get(element, WHITE)

        skin_colors = [
            (245, 190, 145),
            (205, 145, 100),
            (170, 105, 70),
            (115, 70, 45),
            (235, 165, 125)
        ]

        skin_col = skin_colors[skin % len(skin_colors)]

        # Shadow
        pygame.draw.ellipse(
            screen,
            (8, 15, 10),
            (x - 25, y + 20, 50, 18)
        )

        # Cape
        pygame.draw.polygon(
            screen,
            col,
            [
                (x - 20, y - 5),
                (x + 22, y - 5),
                (x + 28, y + 40),
                (x - 28, y + 40)
            ]
        )

        # Body armour
        pygame.draw.rect(
            screen,
            (80, 88, 105),
            (x - 18, y, 36, 42),
            border_radius=7
        )

        # Head
        pygame.draw.circle(
            screen,
            skin_col,
            (int(x), int(y - 18)),
            17
        )

        hair_colors = [
            (30, 25, 22),
            (80, 45, 25),
            (170, 120, 45),
            (35, 35, 40),
            (210, 210, 210)
        ]

        hc = hair_colors[hair % len(hair_colors)]

        pygame.draw.arc(
            screen,
            hc,
            (x - 17, y - 34, 34, 30),
            math.pi,
            math.pi * 2,
            7
        )

        # Eyes
        pygame.draw.circle(
            screen,
            BLACK,
            (int(x - 6), int(y - 19)),
            2
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (int(x + 6), int(y - 19)),
            2
        )

        # Weapon
        pygame.draw.line(
            screen,
            (220, 220, 230),
            (x + 20, y + 20),
            (x + 45, y - 15),
            5
        )

    # ========================================================
    # HUD
    # ========================================================

    def draw_hud(self):

        # Top bar
        panel(
            screen,
            pygame.Rect(20, 20, WIDTH - 40, 75),
            (15, 20, 30)
        )

        # HP
        pygame.draw.rect(
            screen,
            (55, 25, 30),
            (40, 48, 270, 18),
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            RED,
            (
                40,
                48,
                270 * clamp(
                    self.player.hp /
                    self.player.max_hp,
                    0,
                    1
                ),
                18
            ),
            border_radius=8
        )

        draw_text(
            screen,
            f"HP {self.player.hp}/{self.player.max_hp}",
            (50, 47),
            F12,
            WHITE
        )

        # XP
        xp_ratio = (
            self.player.xp /
            self.player.xp_needed()
        )

        pygame.draw.rect(
            screen,
            (35, 40, 60),
            (330, 48, 270, 18),
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            BLUE,
            (
                330,
                48,
                270 * xp_ratio,
                18
            ),
            border_radius=8
        )

        draw_text(
            screen,
            f"LEVEL {self.player.level}",
            (340, 47),
            F12,
            WHITE
        )

        draw_text(
            screen,
            f"⚔ {self.player.element}",
            (630, 43),
            F18,
            ELEMENTS[self.player.element]
        )

        draw_text(
            screen,
            f"◆ {self.player.gold}",
            (800, 43),
            F18,
            GOLD
        )

        draw_text(
            screen,
            "WASD Move",
            (WIDTH - 390, 35),
            F12,
            MUTED
        )

        draw_text(
            screen,
            "E Gather   Click Attack   I Inventory   C Customize",
            (WIDTH - 390, 55),
            F12,
            MUTED
        )

        # Bottom message
        panel(
            screen,
            pygame.Rect(
                20,
                HEIGHT - 65,
                620,
                45
            ),
            (15, 20, 28)
        )

        draw_text(
            screen,
            self.message,
            (35, HEIGHT - 53),
            F14,
            WHITE
        )

        # Chat
        panel(
            screen,
            pygame.Rect(
                WIDTH - 350,
                HEIGHT - 210,
                330,
                140
            ),
            (13, 17, 25)
        )

        for i, line in enumerate(
            self.chat[-6:]
        ):
            draw_text(
                screen,
                line[:42],
                (
                    WIDTH - 335,
                    HEIGHT - 195 + i * 20
                ),
                F12,
                MUTED
            )

    # ========================================================
    # INVENTORY
    # ========================================================

    def draw_inventory(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(
            260, 100, 760, 520
        )

        panel(
            screen,
            box,
            (20, 25, 35),
            15,
            (75, 90, 115)
        )

        draw_text(
            screen,
            "INVENTORY",
            (box.x + 30, box.y + 25),
            F30,
            WHITE
        )

        items = [
            ("Wood", "wood"),
            ("Ore", "ore"),
            ("Herbs", "herb"),
            ("Iron Armour", "iron_armor"),
            ("Health Potion", "health_potion")
        ]

        for i, (label, key) in enumerate(items):

            x = box.x + 35 + (i % 3) * 220
            y = box.y + 90 + (i // 3) * 150

            slot = pygame.Rect(
                x, y, 190, 120
            )

            panel(
                screen,
                slot,
                PANEL2,
                10,
                (60, 70, 90)
            )

            draw_text(
                screen,
                label,
                (x + 15, y + 15),
                F16
            )

            draw_text(
                screen,
                f"x {self.player.inventory[key]}",
                (x + 15, y + 50),
                F24,
                GOLD
            )

        craft = pygame.Rect(
            720, 570, 200, 50
        )

        button(
            screen,
            craft,
            "FORGE ARMOUR",
            pygame.mouse.get_pos()
        )

        close = pygame.Rect(
            720, 630, 200, 50
        )

        button(
            screen,
            close,
            "CLOSE",
            pygame.mouse.get_pos()
        )

        draw_text(
            screen,
            "Armour recipe: 5 Wood + 8 Ore",
            (300, 570),
            F14,
            MUTED
        )

    # ========================================================
    # CUSTOMIZATION
    # ========================================================

    def draw_customize(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(
            250, 120, 780, 520
        )

        panel(
            screen,
            box,
            (20, 25, 36),
            15,
            (80, 90, 120)
        )

        draw_text(
            screen,
            "CHARACTER FORGE",
            (box.x + 35, box.y + 25),
            F30,
            WHITE
        )

        # Preview
        pygame.draw.circle(
            screen,
            (35, 42, 55),
            (530, 340),
            150
        )

        self.draw_character(
            530,
            350,
            self.player.element,
            self.player.skin,
            self.player.hair
        )

        draw_text(
            screen,
            self.player.element,
            (530, 480),
            F18,
            ELEMENTS[self.player.element],
            True
        )

        controls = [
            (230, "CHANGE SKIN"),
            (290, "CHANGE HAIR"),
            (350, "CHANGE ELEMENT"),
            (430, "DONE")
        ]

        for y, text in controls:

            r = pygame.Rect(
                760, y, 200, 45
            )

            button(
                screen,
                r,
                text,
                pygame.mouse.get_pos()
            )

    # ========================================================
    # CHAT INPUT
    # ========================================================

    def draw_chat_box(self):

        r = pygame.Rect(
            WIDTH - 370,
            HEIGHT - 70,
            350,
            45
        )

        panel(
            screen,
            r,
            (20, 25, 35),
            8,
            CYAN
        )

        draw_text(
            screen,
            self.chat_input + "|",
            (r.x + 12, r.y + 12),
            F14,
            WHITE
        )

    # ========================================================
    # LOGIN SCREEN
    # ========================================================

    def render_login(self):

        screen.fill(BG)

        # Decorative glow
        for radius in range(300, 50, -15):
            alpha = max(
                0,
                70 - radius // 5
            )

            glow = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                glow,
                (70, 50, 130, alpha),
                (WIDTH // 2, 180),
                radius
            )

            screen.blit(glow, (0, 0))

        draw_text(
            screen,
            "DRAGON SLAYER",
            (WIDTH // 2, 80),
            F60,
            GOLD,
            True
        )

        draw_text(
            screen,
            "ONLINE",
            (WIDTH // 2, 140),
            F30,
            PURPLE,
            True
        )

        draw_text(
            screen,
            "ENTER THE ELEMENTAL CHRONICLES",
            (WIDTH // 2, 185),
            F14,
            MUTED,
            True
        )

        box = pygame.Rect(
            350, 225, 580, 370
        )

        panel(
            screen,
            box,
            (18, 23, 34),
            15,
            (60, 70, 95)
        )

        draw_text(
            screen,
            "LOGIN" if self.auth_mode == "login"
            else "CREATE ACCOUNT",
            (390, 240),
            F24,
            WHITE
        )

        # Username
        user_box = pygame.Rect(
            390, 270, 500, 55
        )

        col = (
            (42, 55, 78)
            if self.active_field == "username"
            else PANEL2
        )

        panel(
            screen,
            user_box,
            col,
            8,
            BLUE if self.active_field == "username"
            else None
        )

        draw_text(
            screen,
            "Username",
            (405, 280),
            F12,
            MUTED
        )

        draw_text(
            screen,
            self.username or "Type your username...",
            (405, 300),
            F16,
            WHITE if self.username else MUTED
        )

        # Password
        pass_box = pygame.Rect(
            390, 350, 500, 55
        )

        col = (
            (42, 55, 78)
            if self.active_field == "password"
            else PANEL2
        )

        panel(
            screen,
            pass_box,
            col,
            8,
            BLUE if self.active_field == "password"
            else None
        )

        draw_text(
            screen,
            "Password",
            (405, 360),
            F12,
            MUTED
        )

        masked = "*" * len(self.password)

        draw_text(
            screen,
            masked or "Type your password...",
            (405, 380),
            F16,
            WHITE if self.password else MUTED
        )

        # Buttons
        login_button = pygame.Rect(
            390, 440, 240, 55
        )

        register_button = pygame.Rect(
            650, 440, 240, 55
        )

        button(
            screen,
            login_button,
            "ENTER REALM"
            if self.auth_mode == "login"
            else "CREATE ACCOUNT",
            pygame.mouse.get_pos()
        )

        button(
            screen,
            register_button,
            "SWITCH MODE",
            pygame.mouse.get_pos()
        )

        connect = pygame.Rect(
            390, 515, 500, 45
        )

        button(
            screen,
            connect,
            "CONNECTED"
            if self.net.connected
            else "CONNECT TO SERVER",
            pygame.mouse.get_pos()
        )

        draw_text(
            screen,
            self.message,
            (WIDTH // 2, 635),
            F14,
            RED if (
                "incorrect" in self.message.lower()
                or "not found" in self.message.lower()
                or "could not" in self.message.lower()
            ) else CYAN,
            True
        )

        draw_text(
            screen,
            "Click a field to type • TAB switches fields • ENTER submits",
            (WIDTH // 2, 680),
            F12,
            MUTED,
            True
        )

    # ========================================================
    # RENDER
    # ========================================================

    def render(self):

        if self.state == "LOGIN":
            self.render_login()

        elif self.state == "WORLD":
            self.render_world()

        pygame.display.flip()


# ============================================================
# MAIN
# ============================================================

def run_server():

    server = Server()

    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped.")


def run_client():

    game = Game()

    # Try connecting immediately
    game.connect()

    running = True

    while running:

        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            game.input_event(event)

        game.update(dt)
        game.render()

    pygame.quit()


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1].lower() == "server":
        run_server()
    else:
        run_client()