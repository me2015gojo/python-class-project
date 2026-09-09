import os
import json
import time
import socket
import threading
import hashlib
import secrets

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import (
    DirectFrame, DirectButton, DirectEntry, DirectLabel
)
from direct.task import Task
from panda3d.core import (
    AmbientLight, DirectionalLight, Vec3, Vec4,
    CardMaker, TextNode, Fog, WindowProperties
)

# ============================================================
# THE FALLEN NIGHT
# VOIDCLIPS STUDIOS
# by AMV STUDIOS
#
# Single-file development build:
# - 3D Panda3D client
# - Local account database
# - Automatic session login
# - Element selection
# - Character customization foundation
# - Built-in multiplayer server
#
# IMPORTANT:
# A public Chennai server still needs a VPS/cloud machine in
# Chennai and its public IP/domain. The code cannot create
# Internet hosting by itself.
# ============================================================

GAME_NAME = "THE FALLEN NIGHT"
STUDIO_NAME = "VOIDCLIPS STUDIOS"
CREDIT = "by AMV STUDIOS"

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 25565

ACCOUNT_FILE = "fallen_night_accounts.json"
SESSION_FILE = "fallen_night_session.json"

WORLD_SIZE = 300


# ============================================================
# DATABASE
# ============================================================

def load_json(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(filename, data):
    temp = filename + ".tmp"

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    os.replace(temp, filename)


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()


def create_password_hash(password):
    salt = secrets.token_hex(16)
    hashed = password_hash(password, salt)
    return salt, hashed


# ============================================================
# SERVER
# ============================================================

class GameServer:
    """
    Lightweight development server.

    The server keeps REAL connected clients only.
    There are no fake/random players.
    """

    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port

        self.running = False
        self.clients = {}
        self.lock = threading.Lock()

        self.accounts = load_json(ACCOUNT_FILE, {})

    def start(self):
        if self.running:
            return

        self.running = True

        thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        thread.start()

        print()
        print("=" * 60)
        print("THE FALLEN NIGHT SERVER")
        print("=" * 60)
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print("Region target: Chennai, Tamil Nadu, India")
        print("Server started.")
        print("=" * 60)
        print()

    def run(self):
        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        try:
            server_socket.bind(
                (self.host, self.port)
            )

            server_socket.listen(50)

            server_socket.settimeout(1.0)

            while self.running:
                try:
                    connection, address = server_socket.accept()

                except socket.timeout:
                    continue

                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(connection, address),
                    daemon=True
                )

                client_thread.start()

        except OSError as error:
            print("SERVER ERROR:", error)

        finally:
            server_socket.close()

    def send(self, connection, message):
        try:
            connection.sendall(
                (message + "\n").encode("utf-8")
            )
        except Exception:
            pass

    def handle_client(self, connection, address):
        username = None

        try:
            self.send(
                connection,
                "WELCOME|THE_FALLEN_NIGHT"
            )

            while self.running:
                data = connection.recv(4096)

                if not data:
                    break

                messages = data.decode(
                    "utf-8",
                    errors="ignore"
                ).splitlines()

                for message in messages:
                    self.process_message(
                        connection,
                        address,
                        message
                    )

        except Exception:
            pass

        finally:
            if username:
                with self.lock:
                    self.clients.pop(username, None)

            try:
                connection.close()
            except Exception:
                pass

    def process_message(
        self,
        connection,
        address,
        message
    ):
        parts = message.split("|")

        if not parts:
            return

        command = parts[0]

        # ----------------------------------------------------
        # PING
        # ----------------------------------------------------

        if command == "PING":
            self.send(connection, "PONG")
            return

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        if command == "LOGIN" and len(parts) >= 3:

            username = parts[1].strip()
            password = parts[2]

            account = self.accounts.get(username)

            if not account:
                self.send(
                    connection,
                    "LOGIN_FAIL|Account does not exist"
                )
                return

            salt = account["salt"]

            hashed = password_hash(
                password,
                salt
            )

            if hashed != account["password"]:
                self.send(
                    connection,
                    "LOGIN_FAIL|Incorrect password"
                )
                return

            with self.lock:
                self.clients[username] = {
                    "connection": connection,
                    "address": address,
                    "x": account.get("x", 0),
                    "y": account.get("y", 0),
                    "z": account.get("z", 0)
                }

            self.send(
                connection,
                "LOGIN_OK|" + json.dumps({
                    "username": username,
                    "element": account.get(
                        "element",
                        "Fire"
                    ),
                    "level": account.get(
                        "level",
                        1
                    ),
                    "gold": account.get(
                        "gold",
                        100
                    ),
                    "skin": account.get(
                        "skin",
                        0
                    )
                })
            )

            self.broadcast_players()
            return

        # ----------------------------------------------------
        # REGISTER
        # ----------------------------------------------------

        if command == "REGISTER" and len(parts) >= 3:

            username = parts[1].strip()
            password = parts[2]

            if len(username) < 3:
                self.send(
                    connection,
                    "REGISTER_FAIL|Username too short"
                )
                return

            if len(username) > 20:
                self.send(
                    connection,
                    "REGISTER_FAIL|Username too long"
                )
                return

            if len(password) < 6:
                self.send(
                    connection,
                    "REGISTER_FAIL|Password must be 6+ characters"
                )
                return

            if username in self.accounts:
                self.send(
                    connection,
                    "REGISTER_FAIL|Username already exists"
                )
                return

            salt, hashed = create_password_hash(
                password
            )

            self.accounts[username] = {
                "password": hashed,
                "salt": salt,
                "element": "Fire",
                "level": 1,
                "gold": 100,
                "skin": 0,
                "x": 0,
                "y": 0,
                "z": 0,
                "inventory": {
                    "Wood": 0,
                    "Stone": 0,
                    "Iron": 0,
                    "Crystal": 0
                }
            }

            save_json(
                ACCOUNT_FILE,
                self.accounts
            )

            self.send(
                connection,
                "REGISTER_OK"
            )

            return

        # ----------------------------------------------------
        # CHAT
        # ----------------------------------------------------

        if command == "CHAT" and len(parts) >= 3:

            username = parts[1]
            text = "|".join(parts[2:])

            if len(text) > 200:
                text = text[:200]

            self.broadcast(
                "CHAT|" +
                username +
                "|" +
                text
            )

            return

        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

        if command == "POSITION" and len(parts) >= 5:

            username = parts[1]

            try:
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4])
            except ValueError:
                return

            with self.lock:
                if username in self.clients:

                    self.clients[username]["x"] = x
                    self.clients[username]["y"] = y
                    self.clients[username]["z"] = z

            self.broadcast_players()

    def broadcast(self, message):
        dead = []

        with self.lock:
            clients = list(
                self.clients.items()
            )

        for username, info in clients:
            try:
                info["connection"].sendall(
                    (message + "\n").encode("utf-8")
                )
            except Exception:
                dead.append(username)

        if dead:
            with self.lock:
                for username in dead:
                    self.clients.pop(
                        username,
                        None
                    )

    def broadcast_players(self):
        players = []

        with self.lock:
            for username, data in self.clients.items():
                players.append({
                    "username": username,
                    "x": data["x"],
                    "y": data["y"],
                    "z": data["z"]
                })

        self.broadcast(
            "PLAYERS|" +
            json.dumps(players)
        )


# ============================================================
# 3D WORLD
# ============================================================

class WorldBuilder:

    def __init__(self, app):
        self.app = app

        self.make_lighting()
        self.make_ground()
        self.make_trees()
        self.make_mountains()

    def make_lighting(self):
        ambient = AmbientLight(
            "ambient"
        )

        ambient.setColor(
            Vec4(
                0.35,
                0.38,
                0.48,
                1
            )
        )

        ambient_np = self.app.render.attachNewNode(
            ambient
        )

        self.app.render.setLight(
            ambient_np
        )

        sun = DirectionalLight(
            "sun"
        )

        sun.setColor(
            Vec4(
                0.9,
                0.82,
                0.65,
                1
            )
        )

        sun_np = self.app.render.attachNewNode(
            sun
        )

        sun_np.setHpr(
            -35,
            -50,
            0
        )

        self.app.render.setLight(
            sun_np
        )

    def make_ground(self):
        cm = CardMaker(
            "ground"
        )

        cm.setFrame(
            -WORLD_SIZE,
            WORLD_SIZE,
            -WORLD_SIZE,
            WORLD_SIZE
        )

        ground = self.app.render.attachNewNode(
            cm.generate()
        )

        ground.setP(-90)

        ground.setColor(
            0.08,
            0.28,
            0.12,
            1
        )

    def make_tree(self, x, y):
        trunk = self.app.loader.loadModel(
            "models/box"
        )

        trunk.reparentTo(
            self.app.render
        )

        trunk.setScale(
            1.2,
            1.2,
            5
        )

        trunk.setPos(
            x,
            y,
            2.5
        )

        trunk.setColor(
            0.30,
            0.16,
            0.07,
            1
        )

        leaves = self.app.loader.loadModel(
            "models/box"
        )

        leaves.reparentTo(
            self.app.render
        )

        leaves.setScale(
            5,
            5,
            5
        )

        leaves.setPos(
            x,
            y,
            9
        )

        leaves.setColor(
            0.05,
            0.30,
            0.10,
            1
        )

    def make_trees(self):
        positions = [
            (-90, -80),
            (-55, -35),
            (-100, 30),
            (-65, 75),
            (80, 70),
            (110, 20),
            (90, -45),
            (55, -90),
            (-125, -5),
            (125, 95)
        ]

        for x, y in positions:
            self.make_tree(x, y)

    def make_mountains(self):
        # Simple placeholder mountains.
        # Replace with proper 3D assets later.
        positions = [
            (-120, 120),
            (0, 140),
            (120, 120)
        ]

        for x, y in positions:

            mountain = self.app.loader.loadModel(
                "models/box"
            )

            mountain.reparentTo(
                self.app.render
            )

            mountain.setScale(
                30,
                30,
                18
            )

            mountain.setPos(
                x,
                y,
                18
            )

            mountain.setColor(
                0.12,
                0.14,
                0.18,
                1
            )


# ============================================================
# PLAYER 3D MODEL
# ============================================================

class PlayerModel:

    def __init__(
        self,
        app,
        username,
        x=0,
        y=0,
        z=0
    ):
        self.app = app
        self.username = username

        self.node = (
            self.app.loader.loadModel(
                "models/box"
            )
        )

        self.node.reparentTo(
            self.app.render
        )

        self.node.setScale(
            1.2,
            1.2,
            2.5
        )

        self.node.setPos(
            x,
            y,
            z + 2.5
        )

        self.node.setColor(
            0.2,
            0.4,
            0.8,
            1
        )

    def set_position(self, x, y, z):
        self.node.setPos(
            x,
            y,
            z + 2.5
        )

    def remove(self):
        self.node.removeNode()


# ============================================================
# UI
# ============================================================

class FallenNight(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        props = WindowProperties()
        props.setTitle(
            "The Fallen Night"
        )

        self.win.requestProperties(
            props
        )

        self.disableMouse()

        self.accounts = load_json(
            ACCOUNT_FILE,
            {}
        )

        self.server = GameServer()
        self.server.start()

        self.current_username = None
        self.current_element = "Fire"
        self.current_level = 1
        self.current_gold = 100
        self.current_skin = 0

        self.scene_objects = []
        self.remote_players = {}

        self.ui = []

        self.show_splash()

    # --------------------------------------------------------
    # UI HELPERS
    # --------------------------------------------------------

    def clear_ui(self):
        for item in self.ui:
            try:
                item.destroy()
            except Exception:
                pass

        self.ui.clear()

    def label(
        self,
        text,
        x,
        y,
        scale=0.06,
        color=(1, 1, 1, 1)
    ):
        item = DirectLabel(
            text=text,
            scale=scale,
            text_fg=Vec4(*color),
            frameColor=(0, 0, 0, 0),
            pos=(x, 0, y)
        )

        self.ui.append(item)
        return item

    def button(
        self,
        text,
        x,
        y,
        command,
        width=0.16
    ):
        item = DirectButton(
            text=text,
            scale=0.055,
            text_fg=Vec4(
                1,
                1,
                1,
                1
            ),
            frameColor=(
                0.12,
                0.10,
                0.22,
                0.95
            ),
            frameSize=(
                -width,
                width,
                -0.6,
                0.6
            ),
            pos=(x, 0, y),
            command=command
        )

        self.ui.append(item)
        return item

    # --------------------------------------------------------
    # SPLASH
    # --------------------------------------------------------

    def show_splash(self):
        self.clear_ui()

        DirectFrame(
            frameColor=(0.015, 0.01, 0.025, 1),
            frameSize=(-2, 2, -1, 1)
        )

        self.label(
            STUDIO_NAME,
            0,
            0.15,
            0.12,
            (0.55, 0.15, 1, 1)
        )

        self.label(
            CREDIT,
            0,
            -0.02,
            0.055,
            (0.8, 0.8, 0.85, 1)
        )

        self.label(
            "LOADING...",
            0,
            -0.25,
            0.045,
            (0.7, 0.7, 0.75, 1)
        )

        self.splash_start = time.time()

        self.taskMgr.doMethodLater(
            2.5,
            self.finish_splash,
            "finishSplash"
        )

    def finish_splash(self, task):
        self.show_login()
        return Task.done

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    def show_login(self):
        self.clear_ui()

        self.label(
            GAME_NAME,
            0,
            0.65,
            0.105,
            (0.65, 0.20, 1, 1)
        )

        self.label(
            "RISE. FIGHT. SURVIVE.",
            0,
            0.52,
            0.045,
            (0.8, 0.8, 0.9, 1)
        )

        self.label(
            "Username",
            -0.28,
            0.31,
            0.045
        )

        self.username_entry = DirectEntry(
            scale=0.055,
            width=16,
            numLines=1,
            initialText="",
            focus=0,
            pos=(-0.28, 0, 0.20),
            frameColor=(
                0.05,
                0.06,
                0.10,
                1
            ),
            text_fg=Vec4(
                1,
                1,
                1,
                1
            )
        )

        self.ui.append(
            self.username_entry
        )

        self.label(
            "Password",
            -0.28,
            0.08,
            0.045
        )

        self.password_entry = DirectEntry(
            scale=0.055,
            width=16,
            numLines=1,
            obscured=1,
            initialText="",
            focus=0,
            pos=(-0.28, 0, -0.03),
            frameColor=(
                0.05,
                0.06,
                0.10,
                1
            ),
            text_fg=Vec4(
                1,
                1,
                1,
                1
            )
        )

        self.ui.append(
            self.password_entry
        )

        self.button(
            "LOGIN",
            -0.15,
            -0.30,
            self.login
        )

        self.button(
            "CREATE ACCOUNT",
            0.22,
            -0.30,
            self.register
        )

        self.label(
            "Click an input box and type.",
            0,
            -0.58,
            0.035,
            (0.5, 0.5, 0.58, 1)
        )

        # Try automatic login.
        self.taskMgr.doMethodLater(
            0.2,
            self.try_auto_login,
            "autoLogin"
        )

    # --------------------------------------------------------
    # AUTO LOGIN
    # --------------------------------------------------------

    def try_auto_login(self, task):
        session = load_json(
            SESSION_FILE,
            {}
        )

        username = session.get(
            "username"
        )

        token = session.get(
            "token"
        )

        if (
            username
            and token
            and username in self.accounts
        ):
            account = self.accounts[username]

            if account.get(
                "session_token"
            ) == token:

                self.load_account(
                    username,
                    account
                )

        return Task.done

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if len(username) < 3:
            self.show_message(
                "Username must contain at least 3 characters."
            )
            return

        if len(password) < 6:
            self.show_message(
                "Password must contain at least 6 characters."
            )
            return

        if username in self.accounts:
            self.show_message(
                "That username already exists."
            )
            return

        salt, hashed = create_password_hash(
            password
        )

        token = secrets.token_urlsafe(32)

        self.accounts[username] = {
            "password": hashed,
            "salt": salt,
            "session_token": token,
            "element": "Fire",
            "level": 1,
            "gold": 100,
            "skin": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "inventory": {
                "Wood": 0,
                "Stone": 0,
                "Iron": 0,
                "Crystal": 0
            }
        }

        save_json(
            ACCOUNT_FILE,
            self.accounts
        )

        self.show_message(
            "Account created. Logging in..."
        )

        self.load_account(
            username,
            self.accounts[username]
        )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        account = self.accounts.get(
            username
        )

        if not account:
            self.show_message(
                "Account not found."
            )
            return

        hashed = password_hash(
            password,
            account["salt"]
        )

        if hashed != account["password"]:
            self.show_message(
                "Incorrect password."
            )
            return

        token = secrets.token_urlsafe(32)

        account["session_token"] = token

        save_json(
            ACCOUNT_FILE,
            self.accounts
        )

        save_json(
            SESSION_FILE,
            {
                "username": username,
                "token": token
            }
        )

        self.load_account(
            username,
            account
        )

    # --------------------------------------------------------
    # ACCOUNT LOADING
    # --------------------------------------------------------

    def load_account(
        self,
        username,
        account
    ):
        self.current_username = username

        self.current_element = account.get(
            "element",
            "Fire"
        )

        self.current_level = account.get(
            "level",
            1
        )

        self.current_gold = account.get(
            "gold",
            100
        )

        self.current_skin = account.get(
            "skin",
            0
        )

        self.show_element_select()

    # --------------------------------------------------------
    # ELEMENT SELECT
    # --------------------------------------------------------

    def show_element_select(self):
        self.clear_ui()

        self.label(
            "CHOOSE YOUR ELEMENT",
            0,
            0.65,
            0.09,
            (0.65, 0.20, 1, 1)
        )

        elements = [
            ("FIRE", "Fire"),
            ("WATER", "Water"),
            ("EARTH", "Earth"),
            ("AIR", "Air"),
            ("VOID", "Void")
        ]

        positions = [
            (-0.55, 0.20),
            (-0.28, 0.20),
            (0, 0.20),
            (0.28, 0.20),
            (0.55, 0.20)
        ]

        for (name, element), (
            x,
            y
        ) in zip(elements, positions):

            self.button(
                name,
                x,
                y,
                lambda e=element:
                    self.choose_element(e),
                0.11
            )

        self.label(
            "Your choice is saved to your account.",
            0,
            -0.05,
            0.04,
            (0.55, 0.55, 0.65, 1)
        )

        self.button(
            "ENTER THE FALLEN REALM",
            0,
            -0.40,
            self.enter_world,
            0.25
        )

    def choose_element(self, element):
        self.current_element = element

        if self.current_username in self.accounts:
            self.accounts[
                self.current_username
            ]["element"] = element

            save_json(
                ACCOUNT_FILE,
                self.accounts
            )

        self.show_message(
            f"Element selected: {element}"
        )

    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    def show_message(self, message):
        self.label(
            message,
            0,
            -0.70,
            0.035,
            (1, 0.75, 0.25, 1)
        )

    # --------------------------------------------------------
    # WORLD
    # --------------------------------------------------------

    def enter_world(self):
        self.clear_ui()

        self.world = WorldBuilder(
            self
        )

        account = self.accounts.get(
            self.current_username,
            {}
        )

        x = account.get(
            "x",
            0
        )

        y = account.get(
            "y",
            0
        )

        z = account.get(
            "z",
            0
        )

        self.local_player = PlayerModel(
            self,
            self.current_username,
            x,
            y,
            z
        )

        self.camera.setPos(
            x,
            y - 18,
            z + 10
        )

        self.camera.lookAt(
            self.local_player.node
        )

        self.label(
            GAME_NAME,
            -1.25,
            0.88,
            0.055,
            (0.65, 0.20, 1, 1)
        )

        self.label(
            f"Player: {self.current_username}",
            -1.25,
            0.79,
            0.04
        )

        self.label(
            f"Element: {self.current_element}",
            -1.25,
            0.72,
            0.04
        )

        self.label(
            "WASD = Move    E = Gather    F = Attack    Enter = Chat",
            0,
            -0.91,
            0.035,
            (0.7, 0.7, 0.78, 1)
        )

        self.chat_entry = DirectEntry(
            scale=0.045,
            width=30,
            numLines=1,
            initialText="",
            focus=0,
            pos=(-0.55, 0, -0.78),
            frameColor=(
                0.03,
                0.04,
                0.07,
                0.9
            )
        )

        self.ui.append(
            self.chat_entry
        )

        self.taskMgr.add(
            self.world_update,
            "worldUpdate"
        )

        self.accept(
            "enter",
            self.send_chat
        )

        self.accept(
            "escape",
            self.show_pause
        )

    # --------------------------------------------------------
    # CHAT
    # --------------------------------------------------------

    def send_chat(self):
        text = self.chat_entry.get().strip()

        if not text:
            return

        print(
            f"[CHAT] {self.current_username}: {text}"
        )

        self.chat_entry.enterText("")

        # Development placeholder.
        # A network client can send:
        #
        # CHAT|username|message
        #
        # to the server here.

    # --------------------------------------------------------
    # PAUSE
    # --------------------------------------------------------

    def show_pause(self):
        self.label(
            "PAUSED",
            0,
            0,
            0.10,
            (1, 1, 1, 1)
        )

    # --------------------------------------------------------
    # WORLD UPDATE
    # --------------------------------------------------------

    def world_update(self, task):

        if not hasattr(
            self,
            "local_player"
        ):
            return Task.cont

        dt = globalClock.getDt()

        speed = 15 * dt

        if self.mouseWatcherNode.hasMouse():

            keys = self.mouseWatcherNode

        # Panda3D key state.
        # Use built-in key polling.
        if self.is_key_down("w"):
            self.local_player.node.setY(
                self.local_player.node,
                speed
            )

        if self.is_key_down("s"):
            self.local_player.node.setY(
                self.local_player.node,
                -speed
            )

        if self.is_key_down("a"):
            self.local_player.node.setX(
                self.local_player.node,
                -speed
            )

        if self.is_key_down("d"):
            self.local_player.node.setX(
                self.local_player.node,
                speed
            )

        pos = self.local_player.node.getPos()

        pos.x = max(
            -WORLD_SIZE,
            min(WORLD_SIZE, pos.x)
        )

        pos.y = max(
            -WORLD_SIZE,
            min(WORLD_SIZE, pos.y)
        )

        self.local_player.node.setPos(
            pos
        )

        self.camera.setPos(
            pos.x,
            pos.y - 18,
            pos.z + 10
        )

        self.camera.lookAt(
            self.local_player.node
        )

        # Save player position.
        account = self.accounts.get(
            self.current_username
        )

        if account:
            account["x"] = pos.x
            account["y"] = pos.y
            account["z"] = pos.z

            account["element"] = (
                self.current_element
            )

            account["level"] = (
                self.current_level
            )

            account["gold"] = (
                self.current_gold
            )

            account["skin"] = (
                self.current_skin
            )

        return Task.cont

    def is_key_down(self, key):
        return self.mouseWatcherNode.is_button_down(
            ord(key)
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    # Server starts automatically.
    # Client starts immediately afterwards.

    game = FallenNight()

    game.run()
