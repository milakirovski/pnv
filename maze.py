import pygame, sys

# --- CONFIG ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 60
GRID_COLS = 8
GRID_ROWS = 6
STATUS_BAR = 80
FPS = 30

# Colors
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
DARKGRAY = (50, 50, 50)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
ORANGE = (255, 165, 0)

# --- LEVEL ---
LEVEL = [
    "........",
    ".T..T..E",
    "....T...",
    ".TT.....",
    ".S......",
    "........"
]


def parse_level():
    """Parses the string level into coordinates."""
    traps = set()
    start = exitp = None
    for r, row in enumerate(LEVEL):
        for c, ch in enumerate(row):
            if ch == "S": start = (c, r)
            if ch == "E": exitp = (c, r)
            if ch == "T": traps.add((c, r))
    return start, exitp, traps


def grid_origin():
    """Calculates the top-left pixel coordinate to center the grid."""
    w = GRID_COLS * CELL_SIZE
    h = GRID_ROWS * CELL_SIZE
    # Center horizontally, and center vertically in the space BELOW status bar
    return (WINDOW_WIDTH - w) // 2, STATUS_BAR + (WINDOW_HEIGHT - STATUS_BAR - h) // 2


def draw_board(screen, font, player, traps, start, exitp, show_traps, lives, moves, message):
    """Draws the UI, Grid, Player, and special tiles."""
    screen.fill(BLACK)

    # 1. Draw Status Bar Background
    pygame.draw.rect(screen, DARKGRAY, (0, 0, WINDOW_WIDTH, STATUS_BAR))

    # 2. Draw Status Text
    status_text = f"Lives: {lives} | Moves: {moves} | {message}"
    text_surf = font.render(status_text, True, WHITE)
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, STATUS_BAR // 2))
    screen.blit(text_surf, text_rect)

    # 3. Draw Grid
    gx, gy = grid_origin()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            # cell rectangle coords
            x = gx + c * CELL_SIZE
            y = gy + r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Default floor color
            pygame.draw.rect(screen, GRAY, rect)
            # Grid border
            pygame.draw.rect(screen, DARKGRAY, rect, 1)

            # Draw Exit
            if (c, r) == exitp:
                pygame.draw.rect(screen, BLUE, rect)

            # Draw Traps (Only if hidden is False/show_traps is True)
            if (c, r) in traps and show_traps:
                # CHANGE: Instead of a solid rect, draw an "X"
                trap_surf = font.render("X", True, RED)
                # Center the X in the cell rectangle
                trap_rect = trap_surf.get_rect(center=(rect.centerx, rect.centery))
                screen.blit(trap_surf, trap_rect)

            # Draw Player
            if (c, r) == tuple(player):
                # Make player slightly smaller than the cell
                player_rect = pygame.Rect(x + 10, y + 10, CELL_SIZE - 20, CELL_SIZE - 20)
                pygame.draw.rect(screen, GREEN, player_rect)


# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Trap Maze")
    clock = pygame.time.Clock()

    # Font for status bar and map symbols
    # Increased size slightly for better visibility of "X"
    font = pygame.font.SysFont('arial', 32, bold=True)

    # Level Data
    start, exitp, traps = parse_level()

    # Game Variables
    player = list(start)
    lives = 3
    moves = 0
    message = "Showing traps..."
    state = "REVEAL"  # States: REVEAL, PLAY, WIN, LOSE

    # Timer for revealing traps
    reveal_start = pygame.time.get_ticks()
    REVEAL_MS = 3000  # 3 Seconds

    while True:
        clock.tick(FPS)

        # --- Event Handling ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                # Global Keys
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # Restart Key
                if e.key == pygame.K_r:
                    # Reset everything
                    player = list(start)
                    lives = 3
                    moves = 0
                    state = "REVEAL"
                    message = "Showing traps..."
                    reveal_start = pygame.time.get_ticks()

                # Gameplay Inputs (Only allowed in PLAY state)
                if state == "PLAY":
                    dx, dy = 0, 0
                    moved = False

                    if e.key == pygame.K_LEFT:
                        dx = -1; moved = True
                    elif e.key == pygame.K_RIGHT:
                        dx = 1; moved = True
                    elif e.key == pygame.K_UP:
                        dy = -1; moved = True
                    elif e.key == pygame.K_DOWN:
                        dy = 1; moved = True

                    if moved:
                        # Calculate new position
                        nx = player[0] + dx
                        ny = player[1] + dy

                        # Check Bounds
                        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                            # Valid Move logic
                            moves += 1

                            # Check Trap
                            if (nx, ny) in traps:
                                lives -= 1
                                if lives > 0:
                                    message = "HIT A TRAP! Resetting..."
                                    player = list(start)  # Reset to start
                                else:
                                    message = "GAME OVER! (Press R)"
                                    state = "LOSE"
                            # Check Exit
                            elif (nx, ny) == exitp:
                                player = [nx, ny]
                                message = "YOU WON! (Press R)"
                                state = "WIN"
                            # Standard Move
                            else:
                                player = [nx, ny]
                                message = ""  # Clear warnings
                        else:
                            message = "Invalid Move!"

        # --- Game Logic updates (Timer) ---
        show_traps = False  # Default hidden

        if state == "REVEAL":
            show_traps = True
            # Check if 3 seconds (3000ms) have passed
            if pygame.time.get_ticks() - reveal_start >= REVEAL_MS:
                state = "PLAY"
                message = "Go!"

        # Show traps when Game Over to show user where they were
        if state == "LOSE":
            show_traps = True

        # --- Draw ---
        # We pass 'show_traps' into the draw function
        draw_board(screen, font, player, traps, start, exitp, show_traps, lives, moves, message)

        pygame.display.update()


if __name__ == "__main__":
    main()