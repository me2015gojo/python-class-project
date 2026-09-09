import pygame
import sys
import random

# =============================================================
# INITIALIZE PYGAME
# =============================================================
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dragon Slayer: Elemental Chronicles")

clock = pygame.time.Clock()

# =============================================================
# COLORS
# =============================================================
COLOR_BG = (20, 24, 30)
COLOR_PANEL = (35, 40, 50)
COLOR_TEXT = (240, 240, 245)
COLOR_TEXT_MUTED = (160, 170, 185)
COLOR_GOLD = (235, 180, 50)

COLOR_HEALTH = (220, 60, 60)
COLOR_HEALTH_BG = (60, 20, 20)

COLOR_FIRE = (230, 80, 40)
COLOR_WATER = (50, 130, 220)
COLOR_EARTH = (70, 160, 90)
COLOR_AIR = (140, 200, 220)
COLOR_VOID = (130, 60, 180)

COLOR_BUTTON = (55, 65, 80)
COLOR_BUTTON_HOVER = (75, 90, 110)

# =============================================================
# FONTS
# =============================================================
def get_font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


FONT_TITLE = get_font(32, True)
FONT_SUBTITLE = get_font(18)
FONT_MAIN = get_font(20, True)
FONT_BODY = get_font(16)
FONT_SMALL = get_font(14)

# =============================================================
# DRAGON SPRITES
# =============================================================
DRAGON_SPRITES = {}

DRAGON_FILES = {
    "Emerald Hatchling": "dragon1.png",
    "Frost Wyrm": "dragon2.png",
    "Ancient Pyro-Dread": "dragon3.png",
    "Shadow Void Drake": "dragon4.png"
}

for name, filename in DRAGON_FILES.items():
    try:
        raw_img = pygame.image.load(filename).convert_alpha()
        DRAGON_SPRITES[name] = pygame.transform.scale(raw_img, (160, 140))
    except (pygame.error, FileNotFoundError):
        print(f"Warning: '{filename}' not found. Using fallback.")
        DRAGON_SPRITES[name] = None


# =============================================================
# GRAPHICS
# =============================================================
def get_element_color(element):
    if element == "Fire":
        return COLOR_FIRE
    elif element == "Water":
        return COLOR_WATER
    elif element == "Earth":
        return COLOR_EARTH
    elif element == "Air":
        return COLOR_AIR
    elif element == "Void":
        return COLOR_VOID

    return COLOR_TEXT


def draw_knight_sprite(surface, x, y, element):
    color = get_element_color(element)

    # Body
    pygame.draw.rect(
        surface,
        (120, 130, 140),
        (x, y + 20, 50, 50)
    )

    # Cape / element effect
    pygame.draw.rect(
        surface,
        color,
        (x - 10, y + 25, 10, 40)
    )

    # Helmet
    pygame.draw.rect(
        surface,
        (80, 90, 100),
        (x + 10, y, 30, 25)
    )

    # Helmet decoration
    pygame.draw.rect(
        surface,
        color,
        (x + 25, y + 8, 12, 5)
    )

    # Sword
    pygame.draw.line(
        surface,
        (220, 220, 230),
        (x + 45, y + 35),
        (x + 75, y + 5),
        5
    )


def draw_dragon_sprite(surface, x, y, dragon_name):
    sprite = DRAGON_SPRITES.get(dragon_name)

    if sprite:
        surface.blit(sprite, (x, y))
        return

    # Fallback dragon
    if "Emerald" in dragon_name:
        color = COLOR_EARTH
    elif "Frost" in dragon_name:
        color = COLOR_WATER
    elif "Ancient" in dragon_name:
        color = COLOR_FIRE
    else:
        color = COLOR_VOID

    pygame.draw.rect(
        surface,
        color,
        (x, y, 160, 120),
        border_radius=15
    )

    # Eyes
    pygame.draw.circle(surface, (255, 255, 255), (x + 45, y + 40), 7)
    pygame.draw.circle(surface, (255, 255, 255), (x + 115, y + 40), 7)

    pygame.draw.circle(surface, (0, 0, 0), (x + 45, y + 40), 3)
    pygame.draw.circle(surface, (0, 0, 0), (x + 115, y + 40), 3)

    # Mouth
    pygame.draw.line(
        surface,
        (30, 30, 30),
        (x + 50, y + 80),
        (x + 110, y + 80),
        5
    )


# =============================================================
# UI HELPERS
# =============================================================
def draw_text(surface, text, font, color, x, y, center=False):
    rendered = font.render(text, True, color)

    if center:
        rect = rendered.get_rect(center=(x, y))
    else:
        rect = rendered.get_rect(topleft=(x, y))

    surface.blit(rendered, rect)
    return rect


def draw_button(surface, rect, text, mouse_pos):
    color = COLOR_BUTTON_HOVER if rect.collidepoint(mouse_pos) else COLOR_BUTTON

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        surface,
        (100, 110, 125),
        rect,
        2,
        border_radius=8
    )

    draw_text(
        surface,
        text,
        FONT_MAIN,
        COLOR_TEXT,
        rect.centerx,
        rect.centery,
        center=True
    )


def draw_health_bar(surface, x, y, width, height, hp, max_hp):
    hp = max(0, hp)

    pygame.draw.rect(
        surface,
        COLOR_HEALTH_BG,
        (x, y, width, height),
        border_radius=5
    )

    if max_hp > 0:
        fill_width = int(width * hp / max_hp)
    else:
        fill_width = 0

    pygame.draw.rect(
        surface,
        COLOR_HEALTH,
        (x, y, fill_width, height),
        border_radius=5
    )

    pygame.draw.rect(
        surface,
        (120, 120, 130),
        (x, y, width, height),
        2,
        border_radius=5
    )


# =============================================================
# PLAYER
# =============================================================
class Player:
    def __init__(self, name, element):
        self.name = name
        self.element = element

        self.hp = 100
        self.max_hp = 100

        self.gold = 0

        self.level = 1
        self.xp = 0

        self.power_name = ""
        self.power_desc = ""
        self.base_damage = 0

        self.setup_element_powers()

    def setup_element_powers(self):
        if self.element == "Fire":
            self.power_name = "Inferno Strike"
            self.power_desc = "A powerful fire attack."
            self.base_damage = 28

        elif self.element == "Water":
            self.power_name = "Aqua Healing"
            self.power_desc = "Deals damage and heals you."
            self.base_damage = 16

        elif self.element == "Earth":
            self.power_name = "Granite Shield"
            self.power_desc = "Deals damage and reduces the next hit."
            self.base_damage = 14

        elif self.element == "Air":
            self.power_name = "Cyclone Rush"
            self.power_desc = "A fast elemental attack."
            self.base_damage = 20

    def attack(self):
        return random.randint(10, 16) + (self.level * 2)

    def cast_power(self):
        return self.base_damage + (self.level * 3)

    def add_xp(self, amount):
        self.xp += amount

        leveled_up = False

        while self.xp >= self.level * 100:
            self.xp -= self.level * 100
            self.level += 1

            self.max_hp += 20
            self.hp = self.max_hp

            leveled_up = True

        return leveled_up


# =============================================================
# DRAGON
# =============================================================
class DragonEnemy:
    def __init__(self, name, element, hp, damage):
        self.name = name
        self.element = element

        self.hp = hp
        self.max_hp = hp

        self.damage = damage

    def attack(self):
        minimum = max(1, self.damage - 3)
        maximum = self.damage + 3

        return random.randint(minimum, maximum)


# =============================================================
# QUEST
# =============================================================
class Quest:
    def __init__(
        self,
        q_id,
        desc,
        name,
        element,
        hp,
        dmg,
        gold,
        xp
    ):
        self.q_id = q_id
        self.description = desc

        self.enemy_name = name
        self.enemy_element = element

        self.enemy_hp = hp
        self.enemy_dmg = dmg

        self.reward_gold = gold
        self.reward_xp = xp

        self.is_completed = False


# =============================================================
# GAME MANAGER
# =============================================================
class GameManager:
    def __init__(self):
        self.state = "STUDIO_INTRO"

        self.intro_timer = 0

        self.player = None

        self.quests = [
            Quest(
                1,
                "Slay the Emerald Hatchling.",
                "Emerald Hatchling",
                "Earth",
                45,
                10,
                60,
                40
            ),

            Quest(
                2,
                "Vanquish the Frost Wyrm.",
                "Frost Wyrm",
                "Water",
                80,
                15,
                120,
                60
            ),

            Quest(
                3,
                "Exterminate the Ancient Pyro-Dread.",
                "Ancient Pyro-Dread",
                "Fire",
                140,
                24,
                250,
                100
            ),

            Quest(
                4,
                "Purge the Shadow Void Drake.",
                "Shadow Void Drake",
                "Void",
                220,
                32,
                500,
                200
            )
        ]

        self.current_quest = None
        self.active_dragon = None

        self.combat_log = "An ominous shadow looms..."

        self.shield_active = False

    # ---------------------------------------------------------
    # START GAME
    # ---------------------------------------------------------
    def start_game(self, element):
        self.player = Player("Slayer", element)

        self.state = "TOWN_HUB"

        self.combat_log = (
            f"Welcome, {element} Knight! "
            "Select a bounty."
        )

    # ---------------------------------------------------------
    # START COMBAT
    # ---------------------------------------------------------
    def start_combat(self, quest):
        self.current_quest = quest

        self.active_dragon = DragonEnemy(
            quest.enemy_name,
            quest.enemy_element,
            quest.enemy_hp,
            quest.enemy_dmg
        )

        self.state = "BATTLE"

        self.shield_active = False

        self.combat_log = (
            f"A wild {quest.enemy_name} appears!"
        )

    # ---------------------------------------------------------
    # PLAYER TURN
    # ---------------------------------------------------------
    def execute_player_turn(self, action):
        if self.state != "BATTLE":
            return

        if not self.active_dragon:
            return

        if action == "attack":

            dmg = self.player.attack()

            self.active_dragon.hp -= dmg

            self.combat_log = (
                f"You strike for {dmg} damage!"
            )

        elif action == "skill":

            dmg = self.player.cast_power()

            self.active_dragon.hp -= dmg

            self.combat_log = (
                f"You unleash {self.player.power_name} "
                f"for {dmg} damage!"
            )

            # Water ability
            if self.player.element == "Water":

                heal = int(dmg * 0.5)

                self.player.hp = min(
                    self.player.max_hp,
                    self.player.hp + heal
                )

                self.combat_log += (
                    f" Healed {heal} HP."
                )

            # Earth ability
            elif self.player.element == "Earth":

                self.shield_active = True

                self.combat_log += (
                    " Shield raised!"
                )

        # Check dragon death
        if self.active_dragon.hp <= 0:
            self.active_dragon.hp = 0
            self.handle_victory()
            return

        # Dragon attacks
        enemy_dmg = self.active_dragon.attack()

        if self.shield_active:

            enemy_dmg = int(enemy_dmg * 0.4)

            self.shield_active = False

            self.combat_log += (
                " Shield absorbed damage."
            )

        self.player.hp -= enemy_dmg

        self.combat_log += (
            f" Dragon hits back for {enemy_dmg}!"
        )

        # Player death
        if self.player.hp <= 0:

            self.player.hp = 0

            self.state = "GAME_OVER"

    # ---------------------------------------------------------
    # VICTORY
    # ---------------------------------------------------------
    def handle_victory(self):

        self.current_quest.is_completed = True

        self.player.gold += self.current_quest.reward_gold

        leveled_up = self.player.add_xp(
            self.current_quest.reward_xp
        )

        if leveled_up:
            self.combat_log = (
                f"Victory! You reached level "
                f"{self.player.level}!"
            )
        else:
            self.combat_log = (
                f"Victory! Claimed "
                f"{self.current_quest.reward_gold} gold."
            )

        if all(q.is_completed for q in self.quests):
            self.state = "VICTORY_SCREEN"
        else:
            self.state = "TOWN_HUB"

    # ---------------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------------
    def process_events(self):

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # -------------------------------------------------
            # Keyboard
            # -------------------------------------------------
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    if self.state in [
                        "TOWN_HUB",
                        "CHARACTER_SELECT"
                    ]:
                        pygame.quit()
                        sys.exit()

                    elif self.state == "BATTLE":
                        self.state = "TOWN_HUB"
                        self.active_dragon = None

                # Character select
                elif self.state == "CHARACTER_SELECT":

                    keys = {
                        pygame.K_1: "Fire",
                        pygame.K_2: "Water",
                        pygame.K_3: "Earth",
                        pygame.K_4: "Air"
                    }

                    if event.key in keys:
                        self.start_game(keys[event.key])

                # Battle keyboard shortcuts
                elif self.state == "BATTLE":

                    if event.key == pygame.K_a:
                        self.execute_player_turn("attack")

                    elif event.key == pygame.K_s:
                        self.execute_player_turn("skill")

                # Restart after game over
                elif self.state == "GAME_OVER":

                    if event.key == pygame.K_r:
                        self.__init__()

            # -------------------------------------------------
            # Mouse
            # -------------------------------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                # Character selection
                if self.state == "CHARACTER_SELECT":

                    buttons = self.get_element_buttons()

                    for element, rect in buttons:

                        if rect.collidepoint(mouse_pos):
                            self.start_game(element)
                            break

                # Town
                elif self.state == "TOWN_HUB":

                    quest_buttons = self.get_quest_buttons()

                    for quest, rect in quest_buttons:

                        if (
                            rect.collidepoint(mouse_pos)
                            and not quest.is_completed
                        ):
                            self.start_combat(quest)
                            break

                # Battle
                elif self.state == "BATTLE":

                    attack_rect = pygame.Rect(
                        200, 500, 200, 55
                    )

                    skill_rect = pygame.Rect(
                        500, 500, 200, 55
                    )

                    if attack_rect.collidepoint(mouse_pos):
                        self.execute_player_turn("attack")

                    elif skill_rect.collidepoint(mouse_pos):
                        self.execute_player_turn("skill")

                # Victory
                elif self.state == "VICTORY_SCREEN":

                    restart_rect = pygame.Rect(
                        325, 470, 250, 55
                    )

                    if restart_rect.collidepoint(mouse_pos):
                        self.__init__()

                # Game over
                elif self.state == "GAME_OVER":

                    restart_rect = pygame.Rect(
                        325, 470, 250, 55
                    )

                    if restart_rect.collidepoint(mouse_pos):
                        self.__init__()

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------
    def update(self):

        if self.state == "STUDIO_INTRO":

            self.intro_timer += 1

            if self.intro_timer > 120:
                self.state = "CHARACTER_SELECT"

    # ---------------------------------------------------------
    # BUTTON DATA
    # ---------------------------------------------------------
    def get_element_buttons(self):

        elements = [
            ("Fire", COLOR_FIRE),
            ("Water", COLOR_WATER),
            ("Earth", COLOR_EARTH),
            ("Air", COLOR_AIR)
        ]

        buttons = []

        start_x = 100
        y = 330

        for i, (element, color) in enumerate(elements):

            rect = pygame.Rect(
                start_x + i * 190,
                y,
                160,
                70
            )

            buttons.append((element, rect))

        return buttons

    def get_quest_buttons(self):

        buttons = []

        x = 70
        y = 170

        for i, quest in enumerate(self.quests):

            rect = pygame.Rect(
                x,
                y + i * 85,
                760,
                65
            )

            buttons.append((quest, rect))

        return buttons

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self):

        screen.fill(COLOR_BG)

        if self.state == "STUDIO_INTRO":
            self.render_intro()

        elif self.state == "CHARACTER_SELECT":
            self.render_character_select()

        elif self.state == "TOWN_HUB":
            self.render_town()

        elif self.state == "BATTLE":
            self.render_battle()

        elif self.state == "GAME_OVER":
            self.render_game_over()

        elif self.state == "VICTORY_SCREEN":
            self.render_victory()

        pygame.display.flip()

    # ---------------------------------------------------------
    # INTRO
    # ---------------------------------------------------------
    def render_intro(self):

        draw_text(
            screen,
            "DRAGON SLAYER",
            FONT_TITLE,
            COLOR_GOLD,
            SCREEN_WIDTH // 2,
            230,
            center=True
        )

        draw_text(
            screen,
            "Elemental Chronicles",
            FONT_SUBTITLE,
            COLOR_TEXT,
            SCREEN_WIDTH // 2,
            275,
            center=True
        )

        draw_text(
            screen,
            "A new legend awakens...",
            FONT_BODY,
            COLOR_TEXT_MUTED,
            SCREEN_WIDTH // 2,
            330,
            center=True
        )

    # ---------------------------------------------------------
    # CHARACTER SELECT
    # ---------------------------------------------------------
    def render_character_select(self):

        draw_text(
            screen,
            "Choose Your Element",
            FONT_TITLE,
            COLOR_GOLD,
            SCREEN_WIDTH // 2,
            90,
            center=True
        )

        draw_text(
            screen,
            "Select an elemental knight",
            FONT_SUBTITLE,
            COLOR_TEXT_MUTED,
            SCREEN_WIDTH // 2,
            130,
            center=True
        )

        descriptions = {
            "Fire": "High damage",
            "Water": "Damage + healing",
            "Earth": "Damage + shield",
            "Air": "Balanced attack"
        }

        buttons = self.get_element_buttons()

        mouse_pos = pygame.mouse.get_pos()

        for element, rect in buttons:

            draw_button(
                screen,
                rect,
                element,
                mouse_pos
            )

            color = get_element_color(element)

            draw_text(
                screen,
                descriptions[element],
                FONT_SMALL,
                color,
                rect.centerx,
                rect.bottom + 15,
                center=True
            )

        draw_text(
            screen,
            "Keyboard: 1 Fire   2 Water   3 Earth   4 Air",
            FONT_SMALL,
            COLOR_TEXT_MUTED,
            SCREEN_WIDTH // 2,
            530,
            center=True
        )

    # ---------------------------------------------------------
    # TOWN HUB
    # ---------------------------------------------------------
    def render_town(self):

        draw_text(
            screen,
            "BOUNTY BOARD",
            FONT_TITLE,
            COLOR_GOLD,
            50,
            30
        )

        # Player information
        draw_text(
            screen,
            f"Knight: {self.player.name}",
            FONT_BODY,
            COLOR_TEXT,
            50,
            80
        )

        draw_text(
            screen,
            f"Element: {self.player.element}",
            FONT_BODY,
            get_element_color(self.player.element),
            250,
            80
        )

        draw_text(
            screen,
            f"Level: {self.player.level}",
            FONT_BODY,
            COLOR_TEXT,
            450,
            80
        )

        draw_text(
            screen,
            f"Gold: {self.player.gold}",
            FONT_BODY,
            COLOR_GOLD,
            650,
            80
        )

        mouse_pos = pygame.mouse.get_pos()

        for quest, rect in self.get_quest_buttons():

            completed = quest.is_completed

            color = (
                (45, 75, 55)
                if completed
                else (
                    COLOR_BUTTON_HOVER
                    if rect.collidepoint(mouse_pos)
                    else COLOR_BUTTON
                )
            )

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=8
            )

            pygame.draw.rect(
                screen,
                (100, 110, 125),
                rect,
                2,
                border_radius=8
            )

            status = "COMPLETED" if completed else "AVAILABLE"

            draw_text(
                screen,
                f"{quest.q_id}. {quest.description}",
                FONT_MAIN,
                COLOR_TEXT,
                rect.x + 15,
                rect.y + 10
            )

            draw_text(
                screen,
                f"HP: {quest.enemy_hp} | "
                f"Damage: {quest.enemy_dmg} | "
                f"Reward: {quest.reward_gold} Gold / "
                f"{quest.reward_xp} XP",
                FONT_SMALL,
                COLOR_TEXT_MUTED,
                rect.x + 15,
                rect.y + 38
            )

            draw_text(
                screen,
                status,
                FONT_SMALL,
                COLOR_GOLD if not completed else COLOR_EARTH,
                rect.right - 120,
                rect.y + 25
            )

        draw_text(
            screen,
            "Click an available bounty to begin.",
            FONT_SMALL,
            COLOR_TEXT_MUTED,
            SCREEN_WIDTH // 2,
            555,
            center=True
        )

    # ---------------------------------------------------------
    # BATTLE
    # ---------------------------------------------------------
    def render_battle(self):

        dragon = self.active_dragon

        # Title
        draw_text(
            screen,
            "BATTLE",
            FONT_TITLE,
            COLOR_GOLD,
            SCREEN_WIDTH // 2,
            35,
            center=True
        )

        # Dragon name
        draw_text(
            screen,
            dragon.name,
            FONT_MAIN,
            get_element_color(dragon.element),
            670,
            105,
            center=True
        )

        # Dragon HP
        draw_health_bar(
            screen,
            570,
            130,
            300,
            25,
            dragon.hp,
            dragon.max_hp
        )

        draw_text(
            screen,
            f"{dragon.hp} / {dragon.max_hp}",
            FONT_SMALL,
            COLOR_TEXT,
            720,
            165,
            center=True
        )

        # Dragon
        draw_dragon_sprite(
            screen,
            590,
            190,
            dragon.name
        )

        # Player
        draw_knight_sprite(
            screen,
            160,
            210,
            self.player.element
        )

        draw_text(
            screen,
            f"{self.player.name} - "
            f"Level {self.player.level}",
            FONT_MAIN,
            get_element_color(self.player.element),
            185,
            310,
            center=True
        )

        # Player HP
        draw_health_bar(
            screen,
            80,
            350,
            280,
            25,
            self.player.hp,
            self.player.max_hp
        )

        draw_text(
            screen,
            f"HP: {self.player.hp} / "
            f"{self.player.max_hp}",
            FONT_SMALL,
            COLOR_TEXT,
            220,
            385,
            center=True
        )

        # Combat log
        pygame.draw.rect(
            screen,
            COLOR_PANEL,
            (70, 410, 760, 70),
            border_radius=8
        )

        draw_text(
            screen,
            self.combat_log,
            FONT_SMALL,
            COLOR_TEXT,
            450,
            445,
            center=True
        )

        # Buttons
        mouse_pos = pygame.mouse.get_pos()

        attack_rect = pygame.Rect(
            200,
            500,
            200,
            55
        )

        skill_rect = pygame.Rect(
            500,
            500,
            200,
            55
        )

        draw_button(
            screen,
            attack_rect,
            "ATTACK [A]",
            mouse_pos
        )

        draw_button(
            screen,
            skill_rect,
            f"{self.player.power_name} [S]",
            mouse_pos
        )

    # ---------------------------------------------------------
    # GAME OVER
    # ---------------------------------------------------------
    def render_game_over(self):

        draw_text(
            screen,
            "GAME OVER",
            FONT_TITLE,
            COLOR_HEALTH,
            SCREEN_WIDTH // 2,
            200,
            center=True
        )

        draw_text(
            screen,
            "The dragon has defeated you.",
            FONT_SUBTITLE,
            COLOR_TEXT,
            SCREEN_WIDTH // 2,
            260,
            center=True
        )

        draw_text(
            screen,
            "Press R or click below to restart.",
            FONT_BODY,
            COLOR_TEXT_MUTED,
            SCREEN_WIDTH // 2,
            310,
            center=True
        )

        mouse_pos = pygame.mouse.get_pos()

        restart_rect = pygame.Rect(
            325,
            400,
            250,
            55
        )

        draw_button(
            screen,
            restart_rect,
            "RESTART",
            mouse_pos
        )

    # ---------------------------------------------------------
    # VICTORY SCREEN
    # ---------------------------------------------------------
    def render_victory(self):

        draw_text(
            screen,
            "DRAGON SLAYER!",
            FONT_TITLE,
            COLOR_GOLD,
            SCREEN_WIDTH // 2,
            180,
            center=True
        )

        draw_text(
            screen,
            "All four dragons have been defeated.",
            FONT_SUBTITLE,
            COLOR_TEXT,
            SCREEN_WIDTH // 2,
            240,
            center=True
        )

        draw_text(
            screen,
            f"Final Level: {self.player.level}",
            FONT_MAIN,
            COLOR_TEXT,
            SCREEN_WIDTH // 2,
            300,
            center=True
        )

        draw_text(
            screen,
            f"Gold Collected: {self.player.gold}",
            FONT_MAIN,
            COLOR_GOLD,
            SCREEN_WIDTH // 2,
            340,
            center=True
        )

        mouse_pos = pygame.mouse.get_pos()

        restart_rect = pygame.Rect(
            325,
            470,
            250,
            55
        )

        draw_button(
            screen,
            restart_rect,
            "PLAY AGAIN",
            mouse_pos
        )


# =============================================================
# MAIN GAME LOOP
# =============================================================
if __name__ == "__main__":

    game = GameManager()

    while True:

        game.process_events()
        game.update()
        game.render()

        clock.tick(60)
