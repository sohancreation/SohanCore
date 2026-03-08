import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 288
screen_height = 512
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# Load assets (or create simple shapes if assets are unavailable)
# In a real game, you would load images for bird, pipe, background, etc.
# For this example, we use simple colored rectangles

# Colors
white = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
black = (0, 0, 0)

# Bird properties
bird_x = 50
bird_y = screen_height // 2
bird_radius = 15
bird_velocity = 0
gravity = 0.5
flap_strength = -10

# Pipe properties
pipe_width = 70
pipe_gap = 150
pipe_x = screen_width
pipe_height = random.randint(100, screen_height - 250)
pipe_velocity = -3
pipes = []

def create_pipe():
    pipe_height = random.randint(100, screen_height - 250)
    top_pipe = pygame.Rect(screen_width, 0, pipe_width, pipe_height)
    bottom_pipe = pygame.Rect(screen_width, pipe_height + pipe_gap, pipe_width, screen_height - (pipe_height + pipe_gap))
    return top_pipe, bottom_pipe

pipes.append(create_pipe())


# Score
score = 0
font = pygame.font.Font(None, 36)


# Game over flag
game_over = False

# Clock
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird_velocity = flap_strength
            if event.key == pygame.K_SPACE and game_over:
                # Reset game
                game_over = False
                bird_y = screen_height // 2
                bird_velocity = 0
                pipes = []
                pipes.append(create_pipe())
                score = 0


    # Game logic
    if not game_over:
        # Bird movement
        bird_velocity += gravity
        bird_y += bird_velocity

        # Pipe movement and generation
        for i in range(len(pipes)):
            pipes[i][0].x += pipe_velocity
            pipes[i][1].x += pipe_velocity

        if pipes[-1][0].x < screen_width - 200:
            pipes.append(create_pipe())

        if pipes[0][0].x < -pipe_width:
            pipes.pop(0)
            score += 1

        # Collision detection
        bird_rect = pygame.Rect(bird_x - bird_radius, bird_y - bird_radius, bird_radius * 2, bird_radius * 2)
        for pipe_pair in pipes:
            if bird_rect.colliderect(pipe_pair[0]) or bird_rect.colliderect(pipe_pair[1]):
                game_over = True
                break

        # Check for ground or ceiling collision
        if bird_y > screen_height - bird_radius or bird_y < bird_radius:
            game_over = True


    # Drawing
    screen.fill(blue)  # Background

    # Draw bird
    pygame.draw.circle(screen, red, (bird_x, int(bird_y)), bird_radius)

    # Draw pipes
    for pipe_pair in pipes:
        pygame.draw.rect(screen, green, pipe_pair[0])  # Top pipe
        pygame.draw.rect(screen, green, pipe_pair[1])  # Bottom pipe


    # Draw score
    score_text = font.render("Score: " + str(score), True, white)
    screen.blit(score_text, (10, 10))

    # Game over message
    if game_over:
        game_over_text = font.render("Game Over! Press SPACE to restart", True, white)
        text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(game_over_text, text_rect)

    # Update display
    pygame.display.flip()

    # Control frame rate
    clock.tick(30)

# Quit Pygame
pygame.quit()