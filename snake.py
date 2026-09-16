import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Define grid configurations
CELL_SIZE = 20
GRID_WIDTH = 40
GRID_HEIGHT = 30

# Calculate window size based on grid parameters
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH   # 800 pixels
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT # 600 pixels

# Colors (R, G, B)
COLOR_BG = (15, 15, 15)       # Dark charcoal
COLOR_SNAKE = (46, 204, 113)  # Emerald green
COLOR_FOOD = (231, 76, 60)    # Alizarin red
COLOR_TEXT = (255, 255, 255)  # White

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Set up font for the score
font = pygame.font.SysFont("arial", 25)

def draw_score(score):
    """Renders the current score on the top-left corner."""
    score_surface = font.render(f"Score: {score}", True, COLOR_TEXT)
    screen.blit(score_surface, (10, 10))

def show_game_over_screen(score):
    """Displays a game over message and waits for user choice to restart or quit."""
    screen.fill(COLOR_BG)
    over_font = pygame.font.SysFont("arial", 50)
    sub_font = pygame.font.SysFont("arial", 20)
    
    over_surface = over_font.render("GAME OVER", True, COLOR_FOOD)
    score_surface = sub_font.render(f"Final Score: {score}", True, COLOR_TEXT)
    restart_surface = sub_font.render("Press SPACE to Play Again or ESC to Quit", True, COLOR_TEXT)
    
    # Center text placement
    screen.blit(over_surface, (WINDOW_WIDTH // 2 - over_surface.get_width() // 2, WINDOW_HEIGHT // 3))
    screen.blit(score_surface, (WINDOW_WIDTH // 2 - score_surface.get_width() // 2, WINDOW_HEIGHT // 2))
    screen.blit(restart_surface, (WINDOW_WIDTH // 2 - restart_surface.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    
    pygame.display.flip()
    
    # Wait for user input loop
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False  # Restart game
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    # Snake setup: Start in the middle of the grid
    # The snake is a list of [grid_x, grid_y] coordinate lists
    snake = [
        [GRID_WIDTH // 2, GRID_HEIGHT // 2],
        [GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2],
        [GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2]
    ]
    
    # Initial movement direction: [x, y]
    direction = [1, 0] # Moving Right
    
    # Spawn the first food piece
    food = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
    
    score = 0
    game_speed = 10 # Adjust this to change difficulty (frames per second)

    # Main Game Loop
    running = True
    while running:
        # 1. Handle Events (Input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                # Change direction but prevent reversing directly into oneself
                if event.key == pygame.K_UP and direction != [0, 1]:
                    direction = [0, -1]
                elif event.key == pygame.K_DOWN and direction != [0, -1]:
                    direction = [0, 1]
                elif event.key == pygame.K_LEFT and direction != [1, 0]:
                    direction = [-1, 0]
                elif event.key == pygame.K_RIGHT and direction != [-1, 0]:
                    direction = [1, 0]

        # 2. Update Game State
        # Calculate new head location
        new_head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
        
        # Check Collision: Wall boundaries
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            running = False
            break
            
        # Check Collision: Snake hitting its own body
        if new_head in snake:
            running = False
            break
            
        # Insert the new head to simulate moving forward
        snake.insert(0, new_head)
        
        # Check if snake ate the food
        if new_head == food:
            score += 1
            # Respawn food somewhere not occupied by the snake
            while True:
                food = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
                if food not in snake:
                    break
        else:
            # Remove the tail element if no food was eaten to maintain normal length
            snake.pop()

        # 3. Draw Everything
        screen.fill(COLOR_BG)
        
        # Draw Food
        food_rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, COLOR_FOOD, food_rect)
        
        # Draw Snake
        for segment in snake:
            snake_rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
            pygame.draw.rect(screen, COLOR_SNAKE, snake_rect)
            
        # Draw Score
        draw_score(score)
        
        # Refresh the screen
        pygame.display.flip()
        
        # Control game framerate/speed
        clock.tick(game_speed)

    # Trigger game over handling if loop breaks
    show_game_over_screen(score)

# Loop to restart the game seamlessly
while True:
    main()
