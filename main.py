import pygame

from managers.database import DatabaseManager
from managers.game_manager import GameManager


# ============================================================
# INITIALIZE PYGAME
# ============================================================

pygame.init()

try:
    pygame.mixer.init()
except Exception:
    print("Audio initialization failed.")


# ============================================================
# SCREEN
# ============================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    "Space Invaders"
)


# ============================================================
# DATABASE
# ============================================================

database = DatabaseManager()

if not database.initialize_database():
    print("WARNING: Database initialization failed.")


# ============================================================
# GAME MANAGER
# ============================================================

database = DatabaseManager()

game_manager = GameManager(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    database
)


# ============================================================
# CLOCK
# ============================================================

clock = pygame.time.Clock()


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    events = pygame.event.get()

    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    for event in events:

        if event.type == pygame.QUIT:
            running = False

    # --------------------------------------------------------
    # GAME MANAGER
    # --------------------------------------------------------

    game_manager.update(events)

    game_manager.draw()

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    pygame.display.flip()

    clock.tick(60)


# ============================================================
# CLEANUP
# ============================================================

pygame.quit()