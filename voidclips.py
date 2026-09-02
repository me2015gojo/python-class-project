import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.font.init()

# Window Configuration
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dragon Slayer: Elemental Chronicles")
clock = pygame.time.Clock()

# Color Palette
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

# Load Fonts safely
def get_font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)

FONT_TITLE = get_font(32, True)
FONT_SUBTITLE = get_font(18, False)
FONT_MAIN = get_font(20, True)
FONT_BODY = get_font(16, False)

# -------------------------------------------------------------
# GRAPHICS ENGINE (PNG Image Loader & Fallback)
# -------------------------------------------------------------
DRAGON_SPRITES = {}
DRAGON_FILES = {
    "Emerald Hatchling": "dragon1.png",
    "Frost Wyrm": "dragon2.png",
    "Ancient Pyro-Dread": "dragon3.png",
    "Shadow Void Drake": "dragon4.png"
}

# Pre-load and scale images. If an image file isn't found, it defaults to a clean rect.
for name, filename in DRAGON_FILES.items():
    try:
        raw_img = pygame.image.load(filename).convert_alpha()
        DRAGON_SPRITES[name] = pygame.transform.scale(raw_img, (160, 140))
    except pygame.error:
        print(f"Warning: '{filename}' not found in directory. Using procedural fallback.")
        DRAGON_SPRITES[name] = None

def draw_knight_sprite(surface, x, y, element):
    color = COLOR_FIRE if element == "Fire" else COLOR_WATER if element == "Water" else COLOR_EARTH if element == "Earth" else COLOR_AIR
    pygame.draw.rect(surface, (120, 130, 140), (x, y + 20, 50, 50))
    pygame.draw.rect(surface, color, (x - 10, y + 25, 10, 40))
    pygame.draw.rect(surface, (80, 90, 100), (x + 10, y, 30, 25))
    pygame.draw.rect(surface, color, (x + 25, y + 8, 12, 5))
    pygame.draw.line(surface, (200, 200, 210), (x + 45, y + 35), (x + 75, y + 5), 5)

def draw_dragon_sprite(surface, x, y, dragon_name):
    sprite = DRAGON_SPRITES.get(dragon_name)
    if sprite:
        surface.blit(sprite, (x, y))
    else:
        color = COLOR_EARTH if "Emerald" in dragon_name else COLOR_WATER if "Frost" in dragon_name else COLOR_FIRE if "Ancient" in dragon_name else (120, 50, 180)
        pygame.draw.rect(surface, color, (x, y, 140, 110), border_radius=10)
        lbl = FONT_BODY.render("[Missing Image]", True, COLOR_TEXT)
        surface.blit(lbl, (x + 15, y + 45))

# -------------------------------------------------------------
# GAME STATE CLASSES
# -------------------------------------------------------------
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
            self.power_desc = "Deals massive elemental burst damage."
            self.base_damage = 28
        elif self.element == "Water":
            self.power_name = "Aqua Healing"
            self.power_desc = "Strikes enemy and heals your wounds."
            self.base_damage = 16
        elif self.element == "Earth":
            self.power_name = "Granite Shield"
            self.power_desc = "Moderate damage, shields next attack."
            self.base_damage = 14
        elif self.element == "Air":
            self.power_name = "Cyclone Rush"
            self.power_desc = "Fast multi-strike physical assault."
            self.base_damage = 20

    def attack(self):
        return random.randint(10, 16) + (self.level * 2)

    def cast_power(self):
        return self.base_damage + (self.level * 3)

class DragonEnemy:
    def __init__(self, name, element, hp, damage):
        self.name = name
        self.element = element
        self.hp = hp
        self.max_hp = hp
        self.damage = damage

    def attack(self):
        return random.randint(self.damage - 3, self.damage + 3)

class Quest:
    def __init__(self, q_id, desc, name, element, hp, dmg, gold, xp):
        self.q_id = q_id
        self.description = desc
        self.enemy_name = name
        self.enemy_element = element
        self.enemy_hp = hp
        self.enemy_dmg = dmg
        self.reward_gold = gold
        self.reward_xp = xp
        self.is_completed = False

# -------------------------------------------------------------
# ENGINE CONTROLLER
# -------------------------------------------------------------
class GameManager:
    def __init__(self):
        self.state = "STUDIO_INTRO"
        self.intro_timer = 0
        self.player = None
        self.quests = [
            Quest(1, "Slay the Emerald Hatchling in the Valleys.", "Emerald Hatchling", "Earth", 45, 10, 60, 40),
            Quest(2, "Vanquish the Frost Wyrm over the Great Lakes.", "Frost Wyrm", "Water", 80, 15, 120, 60),
            Quest(3, "Exterminate the Ancient Pyro-Dread at Mt. Doom.", "Ancient Pyro-Dread", "Fire", 140, 24, 250, 100),
            Quest(4, "Purge the ultimate Shadow Void Drake from existence.", "Shadow Void Drake", "Void", 220, 32, 500, 200)
        ]
        self.current_quest = None
        self.active_dragon = None
        self.combat_log = "An ominous shadow looms over the kingdom..."
        self.shield_active = False

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                # W, A, S, D Keyboard Input Detection
                if self.state == "CHARACTER_SELECT":
                    if event.key == pygame.K_w: self.start_game("Fire")
                    elif event.key == pygame.K_a: self.start_game("Water")
                    elif event.key == pygame.K_s: self.start_game("Earth")
                    elif event.key == pygame.K_d: self.start_game("Air")
                    
                elif self.state == "TOWN_HUB":
                    available_quests = [q for q in self.quests if not q.is_completed]
                    
                    # W, A, S to pick dynamic bounty list targets
                    if event.key == pygame.K_w and len(available_quests) > 0:
                        self.start_combat(available_quests[0])
                    elif event.key == pygame.K_a and len(available_quests) > 1:
                        self.start_combat(available_quests[1])
                    elif event.key == pygame.K_s and len(available_quests) > 2:
                        self.start_combat(available_quests[2])
                    elif event.key == pygame.K_d:  # D maps directly to resting up at the safe house
                        if self.player.gold >= 25:
                            self.player.gold -= 25
                            self.player.hp = min(self.player.max_hp, self.player.hp + 40)
                            self.combat_log = "Rested at the Inn. Recovered 40 HP!"
                        else:
                            self.combat_log = "Not enough gold to rest!"

                elif self.state == "BATTLE":
                    if event.key == pygame.K_w:   # W -> Basic Sword Attack
                        self.execute_player_turn("attack")
                    elif event.key == pygame.K_a: # A -> Cast Elemental Spell 
                        self.execute_player_turn("skill")
                    elif event.key == pygame.K_s: # S -> Flee combat arena back safely
                        self.state = "TOWN_HUB"
                        self.combat_log = "Fled back safely into the town hub."
                        
                elif self.state in ["GAME_OVER", "VICTORY_SCREEN"]:
                    if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                        self.__init__()
                        self.state = "CHARACTER_SELECT"

    def start_combat(self, quest):
        self.current_quest = quest
        self.active_dragon = DragonEnemy(quest.enemy_name, quest.enemy_element, quest.enemy_hp, quest.enemy_dmg)
        self.combat_log = f"Battle started! You challenge the {quest.enemy_name}."
        self.state = "BATTLE"

    def start_game(self, element):
        self.player = Player("Sir Lancelot", element)
        self.state = "TOWN_HUB"
        self.combat_log = f"Welcome Knight! Elements initialized. Protect the realm."

    def execute_player_turn(self, move_type):
        if not self.active_dragon or self.player.hp <= 0: return

        if move_type == "attack":
            dmg = self.player.attack()
            self.active_dragon.hp -= dmg
            self.combat_log = f"You slash the {self.active_dragon.name} for {dmg} damage!"
        elif move_type == "skill":
            dmg = self.player.cast_power()
            self.active_dragon.hp -= dmg
            self.combat_log = f"Cast {self.player.power_name}! Caused {dmg} burst damage."
            if self.player.element == "Water":
                heal = 15 + (self.player.level * 2)
                self.player.hp = min(self.player.max_hp, self.player.hp + heal)
                self.combat_log += f" Recovered {heal} HP."
            elif self.player.element == "Earth":
                self.shield_active = True

        if self.active_dragon.hp <= 0:
            self.current_quest.is_completed = True
            self.player.gold += self.current_quest.reward_gold
            self.player.xp += self.current_quest.reward_xp
        if self.active_dragon.hp <= 0:
            self.current_quest.is_completed = True
            self.player.gold += self.current_quest.reward_gold
            self.player.xp += self.current_quest.reward_xp
            self.combat_log = f"Victory! Cleared {self.active_dragon.name}. Gained Rewards!"
            
            if self.player.xp >= self.player.level * 60:
                self.player.level += 1
                self.player.max_hp += 20
                self.player.hp = self.player.max_hp
                self.player.setup_element_powers()
            
            if all(q.is_completed for q in self.quests):
                self.state = "VICTORY_SCREEN"
            else:
                self.state = "TOWN_HUB"
            return

        enemy_dmg = self.active_dragon.attack()
        if self.shield_active:
            enemy_dmg = max(2, enemy_dmg - 10)
            self.shield_active = False
            self.combat_log += " Shield mitigated incoming damage."
            
        self.player.hp -= enemy_dmg
        
        if self.player.hp <= 0:
            self.state = "GAME_OVER"

    def update(self):
        if self.state == "STUDIO_INTRO":
            self.intro_timer += 1
            if self.intro_timer > 120:
                self.state = "CHARACTER_SELECT"

    def draw(self):
        screen.fill(COLOR_BG)
        
        if self.state == "STUDIO_INTRO":
            txt1 = FONT_TITLE.render("VOID CLIPS", True, COLOR_FIRE)
            txt2 = FONT_TITLE.render("& AMV STUDIOS", True, COLOR_WATER)
            txt3 = FONT_SUBTITLE.render("Presents a 2D Tactical Adventure...", True, COLOR_TEXT_MUTED)
            screen.blit(txt1, (SCREEN_WIDTH//2 - txt1.get_width()//2, 220))
            screen.blit(txt2, (SCREEN_WIDTH//2 - txt2.get_width()//2, 270))
            screen.blit(txt3, (SCREEN_WIDTH//2 - txt3.get_width()//2, 360))
            
        elif self.state == "CHARACTER_SELECT":
            title = FONT_TITLE.render("SELECT YOUR ELEMENTAL AFFINITY", True, COLOR_TEXT)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))
            
            elements = [
                ("[W] Fire Order", COLOR_FIRE, 150, 200, "Skill: Inferno Strike (Massive Dmg)"),
                ("[A] Water Order", COLOR_WATER, 550, 200, "Skill: Aqua Healing (Dmg + Self Heal)"),
                ("[S] Earth Order", COLOR_EARTH, 150, 360, "Skill: Granite Shield (Dmg + Defense)"),
                ("[D] Air Order", COLOR_AIR, 550, 360, "Skill: Cyclone Rush (Swift High DPS)")
            ]
            for name, color, x, y, desc in elements:
                pygame.draw.rect(screen, COLOR_PANEL, (x, y, 200, 60), border_radius=6)
                pygame.draw.rect(screen, color, (x, y, 200, 60), 2, border_radius=6)
                lbl = FONT_MAIN.render(name, True, color)
                d_lbl = FONT_BODY.render(desc, True, COLOR_TEXT_MUTED)
                screen.blit(lbl, (x + 15, y + 8))
                screen.blit(d_lbl, (x - 20, y + 70))
                
        elif self.state == "TOWN_HUB":
            pygame.draw.rect(screen, COLOR_PANEL, (20, 20, 860, 80), border_radius=8)
            stats_str = f"Knight: {self.player.name} | Level {self.player.level} | HP: {self.player.hp}/{self.player.max_hp} | Gold: {self.player.gold}G"
            screen.blit(get_font(22, True).render(stats_str, True, COLOR_TEXT), (40, 30))
            
            screen.blit(FONT_TITLE.render("Active Bounty Board", True, COLOR_TEXT), (50, 130))
            y_offset = 190
            available_quests = [q for q in self.quests if not q.is_completed]
            
            controls_keys = ["[W]", "[A]", "[S]"]
            for idx, q in enumerate(available_quests[:3]):
                pygame.draw.rect(screen, COLOR_PANEL, (50, y_offset, 520, 45), border_radius=5)
                pygame.draw.rect(screen, COLOR_TEXT_MUTED, (50, y_offset, 520, 45), 1, border_radius=5)
                screen.blit(FONT_MAIN.render(controls_keys[idx], True, COLOR_GOLD), (65, y_offset + 12))
                screen.blit(FONT_BODY.render(q.description, True, COLOR_TEXT), (115, y_offset + 12))
                screen.blit(FONT_BODY.render(f"Reward: {q.reward_gold}G", True, COLOR_GOLD), (440, y_offset + 12))
                y_offset += 55
                
            if len(available_quests) > 3:
                screen.blit(FONT_BODY.render(f"+ {len(available_quests) - 3} more elite bounties locked in queues.", True, COLOR_TEXT_MUTED), (55, y_offset + 5))

            pygame.draw.rect(screen, COLOR_PANEL, (600, 140, 270, 420), border_radius=8)
            screen.blit(FONT_MAIN.render("Local Safety Inn", True, COLOR_TEXT), (620, 160))
            pygame.draw.rect(screen, COLOR_GOLD, (620, 420, 230, 50), border_radius=6)
            screen.blit(FONT_MAIN.render("[D] Rest at Inn (25G)", True, COLOR_BG), (640, 432))
            screen.blit(FONT_BODY.render(f"Status: {self.combat_log}", True, COLOR_TEXT_MUTED), (30, 565))

        elif self.state == "BATTLE":
            screen.blit(FONT_TITLE.render("CRITICAL COMBAT ENCOUNTER", True, COLOR_TEXT), (30, 20))
            
            pygame.draw.rect(screen, COLOR_PANEL, (50, 80, 360, 350), border_radius=10)
            screen.blit(FONT_MAIN.render(f"{self.player.name} (You)", True, COLOR_TEXT), (70, 100))
            draw_knight_sprite(screen, 190, 220, self.player.element)
            pygame.draw.rect(screen, COLOR_HEALTH_BG, (70, 140, 320, 20))
            hp_w = int(320 * (self.player.hp / self.player.max_hp))
            pygame.draw.rect(screen, COLOR_HEALTH, (70, 140, hp_w, 20))
            
            pygame.draw.rect(screen, COLOR_PANEL, (490, 80, 360, 350), border_radius=10)
            screen.blit(FONT_MAIN.render(self.active_dragon.name, True, COLOR_HEALTH), (510, 100))
            draw_dragon_sprite(screen, 590, 200, self.active_dragon.name)
            pygame.draw.rect(screen, COLOR_HEALTH_BG, (510, 140, 320, 20))
            en_hp_w = int(320 * (max(0, self.active_dragon.hp) / self.active_dragon.max_hp))
            pygame.draw.rect(screen, COLOR_HEALTH, (510, 140, en_hp_w, 20))
            
            pygame.draw.rect(screen, COLOR_PANEL, (30, 450, 840, 95), border_radius=8)
            pygame.draw.rect(screen, COLOR_TEXT_MUTED, (50, 480, 180, 50), border_radius=6)
            screen.blit(FONT_MAIN.render("[W] Sword Strike", True, COLOR_BG), (65, 492))
            pygame.draw.rect(screen, COLOR_WATER, (260, 480, 230, 50), border_radius=6)
            screen.blit(FONT_MAIN.render(f"[A] {self.player.power_name}", True, COLOR_BG), (275, 492))
            pygame.draw.rect(screen, COLOR_HEALTH, (520, 480, 160, 50), border_radius=6)
            screen.blit(FONT_MAIN.render("[S] Flee Battle", True, COLOR_TEXT), (545, 492))
            screen.blit(FONT_BODY.render(f"Log: {self.combat_log}", True, COLOR_GOLD), (40, 560))

        elif self.state == "GAME_OVER":
            title = FONT_TITLE.render("THE KNIGHT HAS FALLEN IN BATTLE", True, COLOR_HEALTH)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            pygame.draw.rect(screen, COLOR_TEXT, (330, 420, 240, 50), border_radius=6)
            screen.blit(FONT_MAIN.render("Press any WASD key", True, COLOR_BG), (360, 432))

        elif self.state == "VICTORY_SCREEN":
            title = FONT_TITLE.render("ALL QUESTS COMPLETED!", True, COLOR_EARTH)
            lbl = FONT_MAIN.render("Peace returns to the lands thanks to your blades.", True, COLOR_TEXT)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 160))
            screen.blit(lbl, (SCREEN_WIDTH//2 - lbl.get_width()//2, 230))
            
            credits_1 = FONT_SUBTITLE.render("Production Studio: Void Clips", True, COLOR_FIRE)
            credits_2 = FONT_SUBTITLE.render("Design Suite: AMV Studios", True, COLOR_WATER)
            screen.blit(credits_1, (SCREEN_WIDTH//2 - credits_1.get_width()//2, 310))
            screen.blit(credits_2, (SCREEN_WIDTH//2 - credits_2.get_width()//2, 340))
            
            pygame.draw.rect(screen, COLOR_GOLD, (330, 420, 240, 50), border_radius=6)
            screen.blit(FONT_MAIN.render("Press any WASD key", True, COLOR_BG), (360, 432))

        pygame.display.flip()

def main():
    manager = GameManager()
    while True:
        manager.process_events()
        manager.update()
        manager.draw()
        clock.tick(60)
