import pygame
import sys
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
PADDLE_SPEED = 8
INITIAL_BALL_SPEED_X = 5
INITIAL_BALL_SPEED_Y = 5
BALL_SIZE = 10
BALL_SPEED_INCREMENT = 0.5 # Speed increment on successful hit
SCORE_TO_WIN = 10

# --- Colors ---
WHITE = (255, 255, 255)
CYAN = (0, 139, 139)


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pygame Pong')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)


class Paddle(pygame.Rect):
    def __init__(self, x, y, width, height, speed):
        super().__init__(x, y, width, height)
        self.speed = speed

    def move(self, direction):
        # Moves the paddle up (direction < 0) or down (direction > 0).
        self.y += self.speed * direction

        # Keep paddle within screen boundaries
        if self.top < 0:
            self.top = 0
        if self.bottom > SCREEN_HEIGHT:
            self.bottom = SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self)

class Ball(pygame.Rect):
    def __init__(self, x, y, size, speed_x, speed_y):
        super().__init__(x, y, size, size)
        self.initial_x = x
        self.initial_y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.current_speed = abs(speed_x) # used for speed increase logic

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def reset(self):
        # Reset ball to center with initial speed.
        self.center = (self.initial_x, self.initial_y)
        # Randomize initial direction slightly
        self.speed_x = INITIAL_BALL_SPEED_X * random.choice([1, -1])
        self.speed_y = INITIAL_BALL_SPEED_Y * random.choice([1, -1])
        self.current_speed = abs(INITIAL_BALL_SPEED_X) # Reset speed multiplier

    def increase_speed(self):
        # Increases the magnitude of the ball's speed.
        self.current_speed += BALL_SPEED_INCREMENT
        # Maintain direction while increasing speed magnitude
        self.speed_x = self.current_speed if self.speed_x > 0 else -self.current_speed
        # Keep Y speed relative to X speed to prevent excessive vertical drift
        # This keeps the overall difficulty manageable as X speed increases
        self.speed_y = (abs(self.speed_y) / abs(self.speed_x)) * abs(self.speed_x)
        if self.speed_y < 0:
            self.speed_y = -abs(self.speed_y)
        else:
            self.speed_y = abs(self.speed_y)


    def draw(self, surface):
        pygame.draw.ellipse(surface, WHITE, self)


# Core Game Logic and Functions
def setup_game():
    # Initializes game objects and variables.
    player_paddle = Paddle(
        20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED
    )
    # The right side is a static "wall" implemented by collision logic

    ball = Ball(
        SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
        BALL_SIZE, INITIAL_BALL_SPEED_X, INITIAL_BALL_SPEED_Y
    )

    game_state = {
        'score': 0,
        'running': True,
        'paused': False,
        'game_over': False
    }

    return player_paddle, ball, game_state


# Collision Handling Function
def check_collisions(ball, paddle, game_state):
    # 1. Wall Collision (Top and Bottom)
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball.speed_y *= -1  # Reverse Y direction

    # 2. Right Boundary (The Wall)
    if ball.right >= SCREEN_WIDTH:
        ball.speed_x *= -1  # Reverse X direction

    # 3. Paddle Collision
    if ball.colliderect(paddle) and ball.speed_x < 0:
        # Check if ball is moving towards the paddle (left)

        # Successful hit!
        game_state['score'] += 1
        ball.increase_speed()
        ball.speed_x *= -1  # Reverse X direction

        # *** Random Y-Axis Adjustment for dynamic movement (Requirement) ***
        # Adjust vertical movement by adding a random value from a chosen range
        random_y_adjust = random.uniform(-2, 2)
        ball.speed_y += random_y_adjust

        # Ensure the ball doesn't go completely flat or vertical too easily
        if abs(ball.speed_y) < 1:
            ball.speed_y = random.choice([-1, 1])

        # Ensure the overall speed is still based on current_speed magnitude
        magnitude = ball.current_speed

        # Recalculate speeds based on new vector
        # This is a bit more complex, a simpler approach is to just apply the change:
        # ball.speed_y += random_y_adjust
        # But we'll stick to the simpler one for this implementation.

    # 4. Game Over Condition (Passes behind the paddle)
    if ball.left <= 0:
        game_state['game_over'] = True
        game_state['running'] = False  # Stop the main loop


# Drawing Function
def draw_elements(surface, paddle, ball, game_state):
    surface.fill(CYAN)

    # center line
    # pygame.draw.aaline(surface, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    paddle.draw(surface)
    ball.draw(surface)

    # score text
    score_surf = font.render("Score: "+ str(game_state['score']), True, WHITE)
    surface.blit(score_surf, (SCREEN_WIDTH // 2 - 20, 10))

    # pause text
    pause_hint_surf = small_font.render("Press P to Pause", True, (255, 255, 0)) # yellow text fot pausing the game
    surface.blit(pause_hint_surf, (600, 10))


# Main Game Loop
def display_message(surface, message, y_pos):
    # text messages Pause, Game Over
    text_surf = small_font.render(message, True, WHITE)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    surface.blit(text_surf, text_rect)


def run_game():
    player_paddle, ball, game_state = setup_game()

    while True:
        # --- 1. Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # P key for Pause/Unpause (Requirement)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if game_state['running'] and not game_state['game_over']:
                        game_state['paused'] = not game_state['paused']

                # R key to Restart from Game Over
                if event.key == pygame.K_r and game_state['game_over']:
                    player_paddle, ball, game_state = setup_game()  # Reset everything
                    game_state['running'] = True  # Start the game loop again

        # --- 2. Game Logic  ---
        if game_state['running'] and not game_state['paused']:
            # Paddle Movement Input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player_paddle.move(-1)  # -1 is up
            if keys[pygame.K_DOWN]:
                player_paddle.move(1)  # 1 is down

            # Ball Movement and Collision
            ball.move()
            check_collisions(ball, player_paddle, game_state)

        # --- 3. Drawing ---
        draw_elements(screen, player_paddle, ball, game_state)

        # --- 4. Special States Display ---
        if game_state['paused']:
            display_message(screen, "PAUSED", SCREEN_HEIGHT // 2 - 50)
            display_message(screen, "Press P to Continue", SCREEN_HEIGHT // 2)

        if game_state['game_over']:
            final_score = game_state['score']
            display_message(screen, "GAME OVER", SCREEN_HEIGHT // 2 - 50)
            display_message(screen, f"Final Score: {final_score}", SCREEN_HEIGHT // 2)
            display_message(screen, "Press R to Restart", SCREEN_HEIGHT // 2 + 50)

        # Update the display
        pygame.display.flip()
        # Cap the frame rate
        clock.tick(60)


# Run the game
if __name__ == '__main__':
    run_game()


