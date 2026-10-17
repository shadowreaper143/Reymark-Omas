import os
import random
import pygame


class Background:
    """Loads assets/images/background.png and draws it behind the game.

    If the image is missing or cannot be loaded, a simple animated-looking
    starfield is drawn instead, so the game can still start.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = None

        # entities/background.py -> project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(
            base_dir, "assets", "images", "background.png"
        )

        # Also allow launching the game from a different working directory.
        candidates = [
            image_path,
            os.path.join("assets", "images", "background.png"),
        ]

        for path in candidates:
            if not os.path.isfile(path):
                continue
            try:
                loaded = pygame.image.load(path)
                try:
                    loaded = loaded.convert()
                except pygame.error:
                    # convert() needs a display mode; keep the loaded surface
                    # if Background is initialized before display setup.
                    pass
                self.image = pygame.transform.smoothscale(
                    loaded, (self.width, self.height)
                )
                break
            except (pygame.error, OSError) as error:
                print(f"Background image could not be loaded ({path}): {error}")

        self.stars = []
        for _ in range(100):
            self.stars.append([
                random.randrange(max(1, self.width)),
                random.randrange(max(1, self.height)),
                random.choice((1, 1, 1, 2)),
                random.choice((25, 40, 65, 90))
            ])

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, (0, 0))
            return

        # Fallback background when background.png is absent.
        screen.fill((5, 7, 24))
        for y in range(0, self.height, max(1, self.height // 12)):
            shade = min(32, 9 + (y * 20 // max(1, self.height)))
            pygame.draw.line(
                screen, (shade, shade + 2, min(50, shade + 18)),
                (0, y), (self.width, y)
            )

        for x, y, radius, brightness in self.stars:
            pygame.draw.circle(
                screen,
                (brightness, brightness, min(255, brightness + 25)),
                (x, y),
                radius
            )
