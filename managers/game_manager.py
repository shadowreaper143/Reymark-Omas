import pygame
import random
import os
import hashlib
import secrets

from entities.player import Player
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from entities.background  import Background

from config.settings_manager import (
    load_settings,
    save_settings
)


class GameManager:

    # ============================================================
    # INITIALIZE
    # ============================================================

    def __init__(
        self,
        screen,
        screen_width,
        screen_height,
        database
    ):

        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load the scrolling/static game background image once.
        # Background.draw() has a fallback if background.png is missing.
        self.background = Background(screen_width, screen_height)

        # ========================================================
        # DATABASE
        # ========================================================

        self.db = database
        self.db_error = None

        # Prepare MySQL storage for the spaceship shop.
        self.ensure_shop_database()

        # ========================================================
        # AUTHENTICATION
        # ========================================================

        self.player_id = None
        self.player_name = ""
        self.player_email = ""
        self.logged_player = None

        self.auth_mode = "login"

        self.auth_username = ""
        self.auth_email = ""
        self.auth_password = ""
        self.auth_confirm_password = ""

        self.auth_active_field = "username"

        self.auth_message = ""
        self.auth_message_timer = 0
        self.auth_password_hidden = True

        self.auth_username_rect = pygame.Rect(
            screen_width // 2 - 150, 180, 300, 45
        )

        self.auth_email_rect = pygame.Rect(
            screen_width // 2 - 150, 245, 300, 45
        )

        self.auth_password_rect = pygame.Rect(
            screen_width // 2 - 150, 310, 300, 45
        )

        self.auth_confirm_rect = pygame.Rect(
            screen_width // 2 - 150, 375, 300, 45
        )

        self.auth_button_rect = pygame.Rect(
            screen_width // 2 - 150, 450, 300, 50
        )

        self.auth_switch_rect = pygame.Rect(
            screen_width // 2 - 150, 515, 300, 40
        )

        # ========================================================
        # FONTS
        # ========================================================

        self.font = pygame.font.SysFont("Arial", 36)
        self.big_font = pygame.font.SysFont("Arial", 64)
        self.small_font = pygame.font.SysFont("Arial", 22)

        # ========================================================
        # SETTINGS
        # ========================================================

        self.settings = load_settings()

        self.settings.setdefault("audio", {})
        self.settings.setdefault("sound", {})
        self.settings.setdefault("controls", {})
        self.settings.setdefault("player", {})

        # ========================================================
        # MOBILE CONTROLS
        # ========================================================

        self.mobile_controls = self.settings["controls"].get(
            "mobile_controls",
            True
        )

        # ========================================================
        # SOUND
        # ========================================================

        self.sound_volume = float(
            self.settings["audio"].get(
                "sound_volume",
                self.settings["sound"].get("volume", 0.8)
            )
        )

        self.sound_volume = max(
            0.0,
            min(1.0, self.sound_volume)
        )

        self.shoot_sound = None
        self.explosion_sound = None

        self.load_sounds()

        # ========================================================
        # APPLICATION STATE
        # ========================================================

        self.app_state = "auth"

        # Professional home/menu state
        self.home_start_button = pygame.Rect(screen_width // 2 - 130, screen_height - 145, 260, 55)
        self.home_leaderboard_button = pygame.Rect(screen_width // 2 - 220, screen_height - 80, 125, 48)
        self.home_settings_button = pygame.Rect(screen_width // 2 + 95, screen_height - 80, 125, 48)
        self.home_high_score = 0
        self.player_high_score = 0

        # ========================================================
        # SPACESHIP SHOP
        # ========================================================

        self.shop_open = False
        self.shop_message = ""
        self.shop_message_timer = 0
        self.coins = 0
        self.selected_ship = 1
        self.owned_ships = {1}
        self.shop_selected_id = 1
        self.shop_image_cache = {}

        # Spaceship shop images.
        # Ship 2 uses your new character image: ship02.png.
        self.shop_ships = {
            # Original/default playable character. Always available.
            1: {"name": "MY SHIP", "price": 0, "image": "assets/images/ship01.png"},

            # Second shop ship.
            2: {"name": "SHIP 02", "price": 100, "image": "assets/images/ship02.png"},

            # Third shop ship.
            3: {"name": "SHADOW WING", "price": 250, "image": "assets/images/ship3.png"},

            # Fourth shop ship.
            4: {"name": "INFERNO GUARDIAN", "price": 500, "image": "assets/images/ship4.png"}
        }

        self.home_shop_button = pygame.Rect(
            screen_width // 2 - 70, screen_height - 80, 140, 48
        )
        self.shop_left_button = pygame.Rect(
            55, screen_height // 2 - 25, 55, 55
        )
        self.shop_right_button = pygame.Rect(
            screen_width - 110, screen_height // 2 - 25, 55, 55
        )
        self.shop_buy_button = pygame.Rect(
            screen_width // 2 - 115, screen_height - 135, 230, 48
        )
        self.shop_back_button = pygame.Rect(
            screen_width // 2 - 100, screen_height - 75, 200, 48
        )

        self.home_star_positions = []
        for _ in range(70):
            self.home_star_positions.append((random.randrange(screen_width), random.randrange(screen_height), random.choice((1, 1, 2))))

        # ========================================================
        # PAUSE / GAME MENU
        # ========================================================

        self.pause_menu_open = False

        # Main MENU button
        self.menu_button = pygame.Rect(
            screen_width - 150,
            20,
            130,
            45
        )

        self.pause_continue_button = pygame.Rect(
            screen_width // 2 - 120,
            screen_height // 2 - 90,
            240,
            50
        )

        self.pause_settings_button = pygame.Rect(
            screen_width // 2 - 120,
            screen_height // 2 - 25,
            240,
            50
        )

        self.pause_restart_button = pygame.Rect(
            screen_width // 2 - 120,
            screen_height // 2 + 40,
            240,
            50
        )

        # ========================================================
        # SETTINGS SCREEN
        # ========================================================

        self.settings_open = False

        self.settings_back_button = pygame.Rect(
            screen_width // 2 - 100,
            screen_height - 90,
            200,
            50
        )

        self.volume_minus_button = pygame.Rect(
            screen_width // 2 - 160,
            220,
            50,
            50
        )

        self.volume_plus_button = pygame.Rect(
            screen_width // 2 + 110,
            220,
            50,
            50
        )

        self.mobile_toggle_button = pygame.Rect(
            screen_width // 2 - 100,
            320,
            200,
            50
        )

        # ========================================================
        # USERNAME
        # ========================================================

        self.username_input = ""
        self.username_input_active = False

        self.username_box_rect = pygame.Rect(
            screen_width // 2 - 140,
            420,
            210,
            44
        )

        self.username_save_button = pygame.Rect(
            screen_width // 2 + 80,
            420,
            110,
            44
        )

        self.profile_message = None
        self.profile_message_timer = 0

        # ========================================================
        # LOGOUT
        # ========================================================

        self.logout_button = pygame.Rect(
            screen_width // 2 - 100,
            screen_height - 150,
            200,
            50
        )

        self.logout_requested = False

        # ========================================================
        # LEADERBOARD
        # ========================================================

        self.leaderboard_open = False
        self.leaderboard_data = []
        self.leaderboard_error = None

        self.leaderboard_button_rect = pygame.Rect(
            screen_width // 2 - 110,
            screen_height // 2 + 115,
            220,
            50
        )

        self.leaderboard_back_button = pygame.Rect(
            screen_width // 2 - 100,
            screen_height - 90,
            200,
            50
        )

        # ========================================================
        # GAME OVER
        # ========================================================

        self.reload_button_rect = pygame.Rect(
            screen_width // 2 - 100,
            screen_height // 2 + 50,
            200,
            50
        )

        # Return to the home page after Game Over
        self.game_over_home_button = pygame.Rect(
            screen_width // 2 - 110,
            screen_height // 2 + 115,
            220,
            50
        )

        # Separate Game Over leaderboard button so it does not overlap HOME
        self.game_over_leaderboard_button = pygame.Rect(
            screen_width // 2 - 110,
            screen_height // 2 + 180,
            220,
            50
        )

        # ========================================================
        # GAME OBJECTS
        # ========================================================

        self.player = None
        self.buttons = None
        self.bullets = []
        self.enemies = []

        self.score = 0
        self.high_score = 0
        self.stage = 1
        self.spawn_number = 5
        self.weapon_level = 1
        self.fire_cooldown = 0
        self.max_bullets = 8
        self.game_state = "waiting"

        self.player_history = []

        self.timer = 0
        self.state_timer = 0

        self.score_saved = False
        self.live_score_id = None

    # ============================================================
    # SPACESHIP SHOP DATABASE / LOGIC
    # ============================================================

    def ensure_shop_database(self):
        """Create the shop fields/tables while preserving existing players."""
        connection = None
        cursor = None
        try:
            connection = self.db.connect()
            cursor = connection.cursor()

            try:
                cursor.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS coins INT NOT NULL DEFAULT 0")
            except Exception:
                try:
                    cursor.execute("SELECT coins FROM players LIMIT 1")
                except Exception:
                    cursor.execute("ALTER TABLE players ADD COLUMN coins INT NOT NULL DEFAULT 0")

            try:
                cursor.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS selected_ship INT NOT NULL DEFAULT 1")
            except Exception:
                try:
                    cursor.execute("SELECT selected_ship FROM players LIMIT 1")
                except Exception:
                    cursor.execute("ALTER TABLE players ADD COLUMN selected_ship INT NOT NULL DEFAULT 1")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_ships (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT NOT NULL,
                    ship_id INT NOT NULL,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_player_ship (player_id, ship_id),
                    CONSTRAINT fk_player_ships_player
                        FOREIGN KEY (player_id) REFERENCES players(id)
                        ON DELETE CASCADE
                )
            """)
            connection.commit()
        except Exception as error:
            self.db_error = str(error)
            print("Shop database setup warning:", error)
        finally:
            if cursor:
                try: cursor.close()
                except Exception: pass
            if connection:
                try: connection.close()
                except Exception: pass

    def load_shop_data(self):
        self.coins = 0
        self.selected_ship = 1
        self.owned_ships = {1}
        if self.player_id is None:
            return

        connection = None
        cursor = None
        try:
            connection = self.db.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT coins, selected_ship FROM players WHERE id = %s",
                (self.player_id,)
            )
            row = cursor.fetchone() or {}
            self.coins = max(0, int(row.get("coins", 0) or 0))
            self.selected_ship = int(row.get("selected_ship", 1) or 1)
            if self.selected_ship not in self.shop_ships:
                self.selected_ship = 1

            cursor.execute(
                "SELECT ship_id FROM player_ships WHERE player_id = %s",
                (self.player_id,)
            )
            for row in cursor.fetchall() or []:
                ship_id = int(row.get("ship_id", 0) or 0)
                if ship_id in self.shop_ships:
                    self.owned_ships.add(ship_id)

            cursor.execute(
                "INSERT IGNORE INTO player_ships (player_id, ship_id) VALUES (%s, 1)",
                (self.player_id,)
            )
            connection.commit()
        except Exception as error:
            self.db_error = str(error)
            print("Could not load shop data:", error)
        finally:
            if cursor:
                try: cursor.close()
                except Exception: pass
            if connection:
                try: connection.close()
                except Exception: pass

    def add_coins(self, amount):
        amount = max(0, int(amount))
        if amount <= 0 or self.player_id is None:
            return

        self.coins += amount
        connection = None
        cursor = None
        try:
            connection = self.db.connect()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE players SET coins = %s WHERE id = %s",
                (self.coins, self.player_id)
            )
            connection.commit()
        except Exception as error:
            self.db_error = str(error)
            print("Coin save error:", error)
        finally:
            if cursor:
                try: cursor.close()
                except Exception: pass
            if connection:
                try: connection.close()
                except Exception: pass

    def save_shop_selection(self):
        if self.player_id is None:
            return False
        connection = None
        cursor = None
        try:
            connection = self.db.connect()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE players SET selected_ship = %s WHERE id = %s",
                (self.selected_ship, self.player_id)
            )
            connection.commit()
            return True
        except Exception as error:
            self.db_error = str(error)
            print("Selected ship save error:", error)
            return False
        finally:
            if cursor:
                try: cursor.close()
                except Exception: pass
            if connection:
                try: connection.close()
                except Exception: pass

    def select_shop_ship(self, ship_id):
        ship_id = int(ship_id)
        if ship_id not in self.shop_ships:
            return
        if ship_id not in self.owned_ships:
            self.shop_message = "Purchase this ship first."
            self.shop_message_timer = 120
            return
        self.selected_ship = ship_id
        self.save_shop_selection()
        self.shop_message = f"{self.shop_ships[ship_id]['name']} selected!"
        self.shop_message_timer = 120

    def buy_or_select_ship(self):
        ship_id = self.shop_selected_id
        if ship_id in self.owned_ships:
            self.select_shop_ship(ship_id)
            return

        price = self.shop_ships[ship_id]["price"]
        if self.coins < price:
            self.shop_message = f"Not enough coins. Need {price} coins."
            self.shop_message_timer = 150
            return

        connection = None
        cursor = None
        try:
            connection = self.db.connect()
            cursor = connection.cursor()
            new_coins = self.coins - price
            cursor.execute(
                "UPDATE players SET coins = %s, selected_ship = %s WHERE id = %s",
                (new_coins, ship_id, self.player_id)
            )
            cursor.execute(
                "INSERT IGNORE INTO player_ships (player_id, ship_id) VALUES (%s, %s)",
                (self.player_id, ship_id)
            )
            connection.commit()

            self.coins = new_coins
            self.owned_ships.add(ship_id)
            self.selected_ship = ship_id
            self.shop_message = f"{self.shop_ships[ship_id]['name']} purchased!"
            self.shop_message_timer = 150
        except Exception as error:
            self.db_error = str(error)
            self.shop_message = "Purchase failed."
            self.shop_message_timer = 150
            print("Ship purchase error:", error)
        finally:
            if cursor:
                try: cursor.close()
                except Exception: pass
            if connection:
                try: connection.close()
                except Exception: pass

    def get_shop_image(self, ship_id):
        """Load and cache the actual ship image used by the shop."""
        if ship_id in self.shop_image_cache:
            return self.shop_image_cache[ship_id]

        path = self.shop_ships[ship_id]["image"]

        # Try the normal project-relative path first.
        possible_paths = [path]

        # Also try a path relative to game_manager.py. This prevents the
        # shop image from disappearing when the game is launched from a
        # different working directory.
        manager_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(manager_dir, path))

        # Remove duplicates while preserving order.
        checked = []
        for image_path in possible_paths:
            image_path = os.path.normpath(image_path)
            if image_path not in checked:
                checked.append(image_path)

        for image_path in checked:
            if not os.path.isfile(image_path):
                continue

            try:
                image = pygame.image.load(image_path).convert_alpha()

                # Keep the whole ship visible inside the shop card.
                image = pygame.transform.smoothscale(image, (150, 150))
                self.shop_image_cache[ship_id] = image
                return image
            except Exception as error:
                print(f"Shop image load error ({image_path}):", error)

        print(f"Shop image NOT FOUND for {self.shop_ships[ship_id]['name']}: {path}")
        return None

    def apply_selected_ship_to_player(self):
        """Apply the selected shop image to the real player."""
        if not self.player:
            return

        try:
            image = self.get_shop_image(self.selected_ship)
            if image:
                self.player.image = pygame.transform.smoothscale(
                    image,
                    (self.player.width, self.player.height)
                )
        except Exception as error:
            print("Could not apply selected ship:", error)

    # ============================================================
    # SPACESHIP SHOP SCREEN
    # ============================================================

    def draw_shop(self):
        self.screen.fill((7, 9, 25))

        for x, y, size in self.home_star_positions:
            pygame.draw.circle(self.screen, (65, 80, 125), (x, y), size)

        title = self.big_font.render("SPACESHIP SHOP", True, (245, 248, 255))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 25))

        coin_text = self.font.render(f"COINS: {self.coins}", True, (255, 220, 100))
        self.screen.blit(coin_text, (self.screen_width // 2 - coin_text.get_width() // 2, 95))

        ship = self.shop_ships[self.shop_selected_id]
        name = self.font.render(ship["name"], True, (150, 215, 255))
        self.screen.blit(name, (self.screen_width // 2 - name.get_width() // 2, 135))

        panel = pygame.Rect(self.screen_width // 2 - 140, 175, 280, 210)
        pygame.draw.rect(self.screen, (15, 22, 50), panel, border_radius=18)
        pygame.draw.rect(self.screen, (55, 80, 130), panel, width=2, border_radius=18)

        image = self.get_shop_image(self.shop_selected_id)
        if image:
            self.screen.blit(image, image.get_rect(center=panel.center))
        else:
            missing = self.small_font.render(
                ship["image"],
                True,
                (255, 110, 110)
            )
            self.screen.blit(
                missing,
                (panel.centerx - missing.get_width() // 2, panel.centery - 10)
            )
            missing2 = self.small_font.render(
                "IMAGE NOT FOUND",
                True,
                (255, 180, 120)
            )
            self.screen.blit(
                missing2,
                (panel.centerx - missing2.get_width() // 2, panel.centery + 20)
            )

        # Always show your current playable ship on the shop screen so
        # you can immediately see which character is equipped.
        current_label = self.small_font.render(
            "YOUR SHIP",
            True,
            (130, 230, 255)
        )
        self.screen.blit(current_label, (25, 145))

        current_image = self.get_shop_image(self.selected_ship)
        current_panel = pygame.Rect(15, 175, 120, 150)
        pygame.draw.rect(self.screen, (15, 22, 50), current_panel, border_radius=14)
        pygame.draw.rect(self.screen, (70, 180, 220), current_panel, width=2, border_radius=14)
        if current_image:
            current_preview = pygame.transform.smoothscale(current_image, (100, 100))
            self.screen.blit(current_preview, current_preview.get_rect(center=current_panel.center))

        self.draw_button(self.shop_left_button, "<", (55, 85, 145), self.font)
        self.draw_button(self.shop_right_button, ">", (55, 85, 145), self.font)

        price = ship["price"]
        if self.shop_selected_id in self.owned_ships:
            status = "SELECTED" if self.shop_selected_id == self.selected_ship else "OWNED"
            status_color = (80, 220, 130)
            action = "SELECT SHIP"
            action_color = (55, 130, 185)
        else:
            status = f"PRICE: {price} COINS"
            status_color = (255, 210, 100)
            action = "BUY SHIP"
            action_color = (55, 155, 90)

        status_text = self.small_font.render(status, True, status_color)
        self.screen.blit(status_text, (self.screen_width // 2 - status_text.get_width() // 2, 405))
        self.draw_button(self.shop_buy_button, action, action_color, self.small_font)

        if self.shop_message:
            message = self.small_font.render(self.shop_message, True, (255, 220, 120))
            self.screen.blit(message, (self.screen_width // 2 - message.get_width() // 2, 520))

        hint = self.small_font.render("LEFT / RIGHT to browse  •  ENTER to buy/select", True, (125, 135, 160))
        self.screen.blit(hint, (self.screen_width // 2 - hint.get_width() // 2, self.screen_height - 115))
        self.draw_button(self.shop_back_button, "BACK", (70, 70, 105), self.small_font)

    # ============================================================
    # HOME SCREEN
    # ============================================================

    def hash_password(self, password, salt=None):

        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )

        return salt + "$" + password_hash.hex()

    def verify_password(self, password, stored_hash):

        try:

            if "$" not in stored_hash:
                return False

            salt, saved_hash = stored_hash.split("$", 1)

            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                100000
            ).hex()

            return secrets.compare_digest(
                password_hash,
                saved_hash
            )

        except Exception:
            return False

    # ============================================================
    # AUTH MESSAGE
    # ============================================================

    def set_auth_message(self, message):

        self.auth_message = message
        self.auth_message_timer = 180

    # ============================================================
    # REGISTER
    # ============================================================

    def register_account(self):

        username = self.auth_username.strip()
        email = self.auth_email.strip()
        password = self.auth_password
        confirm = self.auth_confirm_password

        if not username:
            self.set_auth_message("Username is required.")
            return False

        if len(username) < 3:
            self.set_auth_message(
                "Username must be at least 3 characters."
            )
            return False

        if not email:
            self.set_auth_message("Email is required.")
            return False

        if not password:
            self.set_auth_message("Password is required.")
            return False

        if len(password) < 6:
            self.set_auth_message(
                "Password must be at least 6 characters."
            )
            return False

        if password != confirm:
            self.set_auth_message(
                "Passwords do not match."
            )
            return False

        password_hash = self.hash_password(password)

        connection = None
        cursor = None

        try:

            connection = self.db.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id
                FROM players
                WHERE username = %s
                """,
                (username,)
            )

            if cursor.fetchone():
                self.set_auth_message(
                    "Username already exists."
                )
                return False

            cursor.execute(
                """
                SELECT id
                FROM players
                WHERE email = %s
                """,
                (email,)
            )

            if cursor.fetchone():
                self.set_auth_message(
                    "Email already exists."
                )
                return False

            cursor.execute(
                """
                INSERT INTO players
                (
                    username,
                    email,
                    password_hash
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    username,
                    email,
                    password_hash
                )
            )

            connection.commit()

            self.auth_username = username
            self.auth_email = ""
            self.auth_password = ""
            self.auth_confirm_password = ""

            self.auth_mode = "login"
            self.auth_active_field = "username"

            self.set_auth_message(
                "Registration successful! Please login."
            )

            return True

        except Exception as error:

            self.db_error = str(error)

            self.set_auth_message(
                "Registration failed."
            )

            print("Registration error:", error)

            return False

        finally:

            if cursor:

                try:
                    cursor.close()
                except Exception:
                    pass

            if connection:

                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # LOGIN
    # ============================================================

    def login_account(self):

        username = self.auth_username.strip()
        password = self.auth_password

        if not username:
            self.set_auth_message(
                "Enter your username."
            )
            return False

        if not password:
            self.set_auth_message(
                "Enter your password."
            )
            return False

        connection = None
        cursor = None

        try:

            connection = self.db.connect()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    coins,
                    selected_ship
                FROM players
                WHERE username = %s
                """,
                (username,)
            )

            player = cursor.fetchone()

            if not player:
                self.set_auth_message(
                    "Invalid username or password."
                )
                return False

            stored_hash = player.get(
                "password_hash"
            )

            if not stored_hash:
                self.set_auth_message(
                    "Account has no password."
                )
                return False

            if not self.verify_password(
                password,
                stored_hash
            ):
                self.set_auth_message(
                    "Invalid username or password."
                )
                return False

            self.logged_player = player
            self.player_id = player["id"]
            self.player_name = player["username"]
            self.player_email = player.get("email") or ""

            self.username_input = self.player_name

            self.load_shop_data()

            self.auth_password = ""
            self.auth_confirm_password = ""

            self.app_state = "home"

            self.player = Player(self.screen_width, self.screen_height)
            self.buttons = MobileButtons(self.screen_width, self.screen_height)
            self.load_home_high_score()
            self.player_high_score = self.get_player_high_score()

            self.settings_open = False
            self.pause_menu_open = False
            self.leaderboard_open = False

            self.logout_requested = False

            # Stay on the home screen after login.
            # The game is started only when START GAME is pressed.
            self.game_state = "waiting"
            self.bullets = []
            self.enemies = []
            self.live_score_id = None

            print(
                "Login successful:",
                self.player_name
            )

            return True

        except Exception as error:

            self.db_error = str(error)

            self.set_auth_message(
                "Database login error."
            )

            print("Login error:", error)

            return False

        finally:

            if cursor:

                try:
                    cursor.close()
                except Exception:
                    pass

            if connection:

                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # AUTH EVENTS
    # ============================================================

    def handle_auth_events(self, events):

        for event in events:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if self.auth_username_rect.collidepoint(
                    event.pos
                ):
                    self.auth_active_field = "username"

                elif (
                    self.auth_mode == "register"
                    and self.auth_email_rect.collidepoint(
                        event.pos
                    )
                ):
                    self.auth_active_field = "email"

                elif self.auth_password_rect.collidepoint(
                    event.pos
                ):
                    self.auth_active_field = "password"

                elif (
                    self.auth_mode == "register"
                    and self.auth_confirm_rect.collidepoint(
                        event.pos
                    )
                ):
                    self.auth_active_field = "confirm"

                elif self.auth_button_rect.collidepoint(
                    event.pos
                ):

                    if self.auth_mode == "login":
                        self.login_account()
                    else:
                        self.register_account()

                elif self.auth_switch_rect.collidepoint(
                    event.pos
                ):

                    if self.auth_mode == "login":
                        self.auth_mode = "register"
                    else:
                        self.auth_mode = "login"

                    self.auth_message = ""
                    self.auth_password = ""
                    self.auth_confirm_password = ""

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    if self.auth_mode == "login":
                        self.login_account()
                    else:
                        self.register_account()

                elif event.key == pygame.K_BACKSPACE:

                    if self.auth_active_field == "username":
                        self.auth_username = self.auth_username[:-1]

                    elif self.auth_active_field == "email":
                        self.auth_email = self.auth_email[:-1]

                    elif self.auth_active_field == "password":
                        self.auth_password = self.auth_password[:-1]

                    elif self.auth_active_field == "confirm":
                        self.auth_confirm_password = (
                            self.auth_confirm_password[:-1]
                        )

                elif event.key == pygame.K_TAB:

                    fields = ["username"]

                    if self.auth_mode == "register":
                        fields.append("email")

                    fields.append("password")

                    if self.auth_mode == "register":
                        fields.append("confirm")

                    try:
                        current_index = fields.index(
                            self.auth_active_field
                        )
                    except ValueError:
                        current_index = 0

                    current_index += 1

                    if current_index >= len(fields):
                        current_index = 0

                    self.auth_active_field = fields[
                        current_index
                    ]

                elif event.key == pygame.K_F2:

                    self.auth_password_hidden = (
                        not self.auth_password_hidden
                    )

                elif event.unicode.isprintable():

                    if self.auth_active_field == "username":

                        if len(self.auth_username) < 50:
                            self.auth_username += event.unicode

                    elif self.auth_active_field == "email":

                        if len(self.auth_email) < 100:
                            self.auth_email += event.unicode

                    elif self.auth_active_field == "password":

                        if len(self.auth_password) < 100:
                            self.auth_password += event.unicode

                    elif self.auth_active_field == "confirm":

                        if len(self.auth_confirm_password) < 100:
                            self.auth_confirm_password += event.unicode

        if self.auth_message_timer > 0:

            self.auth_message_timer -= 1

            if self.auth_message_timer <= 0:
                self.auth_message = ""

    # ============================================================
    # INPUT BOX
    # ============================================================

    def draw_input_box(
        self,
        rect,
        label,
        value,
        active,
        password=False
    ):

        label_text = self.small_font.render(
            label,
            True,
            (220, 220, 220)
        )

        self.screen.blit(
            label_text,
            (rect.x, rect.y - 28)
        )

        box_color = (
            (60, 120, 180)
            if active
            else
            (45, 45, 65)
        )

        pygame.draw.rect(
            self.screen,
            box_color,
            rect,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            (150, 150, 170),
            rect,
            width=2,
            border_radius=8
        )

        display_value = value

        if password and self.auth_password_hidden:
            display_value = "*" * len(value)

        if active:

            if (pygame.time.get_ticks() // 500) % 2 == 0:
                display_value += "|"

        text = self.small_font.render(
            display_value,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            text,
            (
                rect.x + 10,
                rect.centery - text.get_height() // 2
            )
        )

    # ============================================================
    # DRAW AUTH
    # ============================================================

    def draw_auth(self):

        self.screen.fill((5, 5, 20))

        title_text = (
            "LOGIN"
            if self.auth_mode == "login"
            else
            "REGISTER"
        )

        title = self.big_font.render(
            title_text,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            (
                self.screen_width // 2
                - title.get_width() // 2,
                35
            )
        )

        subtitle = self.small_font.render(
            "SPACE INVADERS",
            True,
            (150, 150, 170)
        )

        self.screen.blit(
            subtitle,
            (
                self.screen_width // 2
                - subtitle.get_width() // 2,
                105
            )
        )

        self.draw_input_box(
            self.auth_username_rect,
            "Username",
            self.auth_username,
            self.auth_active_field == "username"
        )

        if self.auth_mode == "register":

            self.draw_input_box(
                self.auth_email_rect,
                "Email",
                self.auth_email,
                self.auth_active_field == "email"
            )

        self.auth_password_rect = pygame.Rect(
            self.screen_width // 2 - 150,
            310,
            300,
            45
        )

        self.draw_input_box(
            self.auth_password_rect,
            "Password",
            self.auth_password,
            self.auth_active_field == "password",
            password=True
        )

        if self.auth_mode == "register":

            self.auth_confirm_rect = pygame.Rect(
                self.screen_width // 2 - 150,
                375,
                300,
                45
            )

            self.draw_input_box(
                self.auth_confirm_rect,
                "Confirm Password",
                self.auth_confirm_password,
                self.auth_active_field == "confirm",
                password=True
            )

        pygame.draw.rect(
            self.screen,
            (50, 150, 70),
            self.auth_button_rect,
            border_radius=8
        )

        button_text = (
            "LOGIN"
            if self.auth_mode == "login"
            else
            "CREATE ACCOUNT"
        )

        button = self.small_font.render(
            button_text,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            button,
            (
                self.auth_button_rect.centerx
                - button.get_width() // 2,
                self.auth_button_rect.centery
                - button.get_height() // 2
            )
        )

        pygame.draw.rect(
            self.screen,
            (60, 60, 90),
            self.auth_switch_rect,
            border_radius=8
        )

        switch_text = (
            "CREATE NEW ACCOUNT"
            if self.auth_mode == "login"
            else
            "BACK TO LOGIN"
        )

        switch = self.small_font.render(
            switch_text,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            switch,
            (
                self.auth_switch_rect.centerx
                - switch.get_width() // 2,
                self.auth_switch_rect.centery
                - switch.get_height() // 2
            )
        )

        if self.auth_message:

            message_color = (255, 210, 100)

            if "successful" not in self.auth_message.lower():
                message_color = (255, 100, 100)

            message = self.small_font.render(
                self.auth_message,
                True,
                message_color
            )

            self.screen.blit(
                message,
                (
                    self.screen_width // 2
                    - message.get_width() // 2,
                    570
                )
            )

    # ============================================================
    # LOAD SOUNDS
    # ============================================================

    def load_sounds(self):

        try:

            sounds_path = os.path.join(
                "assets",
                "sounds"
            )

            shoot_path = os.path.join(
                sounds_path,
                "shoot.wav"
            )

            explosion_path = os.path.join(
                sounds_path,
                "explosion.wav"
            )

            if os.path.exists(shoot_path):

                self.shoot_sound = pygame.mixer.Sound(
                    shoot_path
                )

                self.shoot_sound.set_volume(
                    self.sound_volume
                )

            else:
                print("Warning: shoot.wav not found.")

            if os.path.exists(explosion_path):

                self.explosion_sound = pygame.mixer.Sound(
                    explosion_path
                )

                self.explosion_sound.set_volume(
                    self.sound_volume
                )

            else:
                print("Warning: explosion.wav not found.")

        except Exception as error:

            print("Sound loading error:", error)

            self.shoot_sound = None
            self.explosion_sound = None

    # ============================================================
    # SOUND VOLUME
    # ============================================================

    def set_sound_volume(self, volume):

        try:

            self.sound_volume = max(
                0.0,
                min(1.0, float(volume))
            )

            if self.shoot_sound:
                self.shoot_sound.set_volume(
                    self.sound_volume
                )

            if self.explosion_sound:
                self.explosion_sound.set_volume(
                    self.sound_volume
                )

            self.settings["audio"]["sound_volume"] = (
                self.sound_volume
            )

            self.settings["sound"]["volume"] = (
                self.sound_volume
            )

            save_settings(self.settings)

            return True

        except Exception as error:

            print(
                "Could not change volume:",
                error
            )

            return False

    # ============================================================
    # MOBILE CONTROLS
    # ============================================================

    def set_mobile_controls(self, enabled):

        self.mobile_controls = bool(enabled)

        self.settings["controls"]["mobile_controls"] = (
            self.mobile_controls
        )

        try:
            save_settings(self.settings)
        except Exception as error:
            print(
                "Could not save mobile setting:",
                error
            )

    # ============================================================
    # RESET GAME
    # ============================================================

    def reset_game(self):

        if self.player_id is None:

            self.game_state = "waiting"

            return

        self.player = Player(
            self.screen_width,
            self.screen_height
        )

        self.apply_selected_ship_to_player()

        self.buttons = MobileButtons(
            self.screen_width,
            self.screen_height
        )

        self.bullets = []
        self.enemies = []

        self.score = 0
        self.stage = 1
        self.spawn_number = 5
        self.weapon_level = 1
        self.fire_cooldown = 0

        self.game_state = "playing"

        self.player_history = []

        self.timer = 0
        self.state_timer = 0

        self.score_saved = False
        self.live_score_id = None

        self.pause_menu_open = False
        self.settings_open = False
        self.leaderboard_open = False

        self.username_input_active = False

        self.start_live_score()
        self.spawn_enemies()

    # ============================================================
    # START LIVE SCORE
    # ============================================================

    def start_live_score(self):

        if self.player_id is None:
            return

        connection = None
        cursor = None

        try:

            connection = self.db.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO scores
                (
                    player_id,
                    score
                )
                VALUES
                (
                    %s,
                    0
                )
                """,
                (self.player_id,)
            )

            connection.commit()

            self.live_score_id = cursor.lastrowid

            print(
                "Live score started:",
                self.live_score_id
            )

        except Exception as error:

            self.db_error = str(error)

            print(
                "Could not start live score:",
                error
            )

        finally:

            if cursor:

                try:
                    cursor.close()
                except Exception:
                    pass

            if connection:

                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # UPDATE LIVE SCORE
    # ============================================================

    def update_live_score(self):

        if self.live_score_id is None:
            return

        connection = None
        cursor = None

        try:

            connection = self.db.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE scores
                SET score = %s
                WHERE id = %s
                AND player_id = %s
                """,
                (
                    int(self.score),
                    self.live_score_id,
                    self.player_id
                )
            )

            connection.commit()

        except Exception as error:

            self.db_error = str(error)

            print(
                "Live score update error:",
                error
            )

        finally:

            if cursor:

                try:
                    cursor.close()
                except Exception:
                    pass

            if connection:

                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # FINISH LIVE SCORE
    # ============================================================

    def finish_live_score(self):

        if self.live_score_id is None:
            return

        connection = None
        cursor = None

        try:

            connection = self.db.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE scores
                SET score = %s
                WHERE id = %s
                AND player_id = %s
                """,
                (
                    int(self.score),
                    self.live_score_id,
                    self.player_id
                )
            )

            connection.commit()

            print(
                "Final score saved:",
                self.score
            )

        except Exception as error:

            self.db_error = str(error)

            print(
                "Could not save final score:",
                error
            )

        finally:

            if cursor:

                try:
                    cursor.close()
                except Exception:
                    pass

            if connection:

                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # SPAWN ENEMIES
    # ============================================================

    def spawn_enemies(self):

        self.enemies = []

        # Gradually increase enemy count, but keep the amount reasonable
        # so mobile/low-end systems remain responsive.
        self.spawn_number = min(5 + (self.stage - 1), 14)

        for i in range(self.spawn_number):
            self.enemies.append(
                Enemy(
                    i,
                    self.spawn_number,
                    self.screen_width
                )
            )

        self.timer = 0

    def load_home_high_score(self):
        self.home_high_score = 0
        try:
            rows = self.get_leaderboard(100)
            for row in rows:
                self.home_high_score = max(
                    self.home_high_score,
                    int(row.get("best_score", 0) or 0)
                )
        except Exception as error:
            print("Could not load high score:", error)

    def get_player_high_score(self):
        if self.player_id is None:
            return 0
        connection = None
        cursor = None
        try:
            connection = self.db.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT COALESCE(MAX(score), 0) AS best_score FROM scores WHERE player_id = %s",
                (self.player_id,)
            )
            row = cursor.fetchone() or {}
            return int(row.get("best_score", 0) or 0)
        except Exception as error:
            print("High score error:", error)
            return 0
        finally:
            try: cursor.close()
            except Exception: pass
            try: connection.close()
            except Exception: pass

    def fire_weapon(self):
        if not self.player or len(self.bullets) >= self.max_bullets:
            return False

        if self.weapon_level <= 1:
            offsets = [0]
        elif self.weapon_level == 2:
            offsets = [-16, 16]
        else:
            offsets = [-24, 0, 24]

        for offset in offsets:
            self.bullets.append(
                Bullet(
                    self.player.x + self.player.width // 2 - 16 + offset,
                    self.player.y
                )
            )

        if self.shoot_sound:
            self.shoot_sound.play()
        return True

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, events):

        # ========================================================
        # AUTH
        # ========================================================

        if self.app_state == "auth":
            self.handle_auth_events(events)
            return

        # ========================================================
        # HOME SCREEN
        # ========================================================

        if self.app_state == "home":
            if self.shop_open:
                if self.shop_message_timer > 0:
                    self.shop_message_timer -= 1
                    if self.shop_message_timer <= 0:
                        self.shop_message = ""

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.shop_open = False
                            return
                        if event.key == pygame.K_LEFT:
                            self.shop_selected_id = 4 if self.shop_selected_id <= 1 else self.shop_selected_id - 1
                        elif event.key == pygame.K_RIGHT:
                            self.shop_selected_id = 1 if self.shop_selected_id >= 4 else self.shop_selected_id + 1
                        elif event.key == pygame.K_RETURN:
                            self.buy_or_select_ship()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.shop_left_button.collidepoint(event.pos):
                            self.shop_selected_id = 4 if self.shop_selected_id <= 1 else self.shop_selected_id - 1
                        elif self.shop_right_button.collidepoint(event.pos):
                            self.shop_selected_id = 1 if self.shop_selected_id >= 4 else self.shop_selected_id + 1
                        elif self.shop_buy_button.collidepoint(event.pos):
                            self.buy_or_select_ship()
                        elif self.shop_back_button.collidepoint(event.pos):
                            self.shop_open = False
                            return
                return

            if self.leaderboard_open:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.leaderboard_back_button.collidepoint(event.pos):
                            self.leaderboard_open = False
                return

            if self.settings_open:
                # Reuse settings input/click handling while returning to home.
                if self.profile_message_timer > 0:
                    self.profile_message_timer -= 1
                    if self.profile_message_timer <= 0:
                        self.profile_message = None
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.volume_minus_button.collidepoint(event.pos):
                            self.set_sound_volume(self.sound_volume - 0.1)
                        elif self.volume_plus_button.collidepoint(event.pos):
                            self.set_sound_volume(self.sound_volume + 0.1)
                        elif self.mobile_toggle_button.collidepoint(event.pos):
                            self.set_mobile_controls(not self.mobile_controls)
                        elif self.username_box_rect.collidepoint(event.pos):
                            self.username_input_active = True
                        elif self.username_save_button.collidepoint(event.pos):
                            self.username_input_active = False
                            self.save_username()
                        elif self.logout_button.collidepoint(event.pos):
                            self.logout()
                            return
                        elif self.settings_back_button.collidepoint(event.pos):
                            self.settings_open = False
                            self.username_input_active = False
                            return
                        else:
                            self.username_input_active = False
                    elif event.type == pygame.KEYDOWN and self.username_input_active:
                        if event.key == pygame.K_RETURN:
                            self.username_input_active = False
                            self.save_username()
                        elif event.key == pygame.K_BACKSPACE:
                            self.username_input = self.username_input[:-1]
                        elif len(self.username_input) < 30 and event.unicode.isprintable():
                            self.username_input += event.unicode
                return

            self.handle_home_events(events)
            return

        # ========================================================
        # ESC
        # ========================================================

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    # Leaderboard -> Game
                    if self.leaderboard_open:

                        self.leaderboard_open = False

                        return

                    # Settings -> Pause Menu
                    if self.settings_open:

                        self.settings_open = False
                        self.pause_menu_open = True
                        self.username_input_active = False

                        return

                    # Pause Menu -> Game
                    if self.pause_menu_open:

                        self.pause_menu_open = False

                        return

                    # Game -> Pause Menu
                    self.pause_menu_open = True
                    self.username_input_active = False

                    return

        # ========================================================
        # LEADERBOARD
        # ========================================================

        if self.leaderboard_open:

            for event in events:

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    if self.leaderboard_back_button.collidepoint(
                        event.pos
                    ):

                        self.leaderboard_open = False

            return

        # ========================================================
        # PAUSE MENU
        # ========================================================

        if self.pause_menu_open:

            for event in events:

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    # CONTINUE
                    if self.pause_continue_button.collidepoint(
                        event.pos
                    ):

                        self.pause_menu_open = False

                        return

                    # SETTINGS
                    elif self.pause_settings_button.collidepoint(
                        event.pos
                    ):

                        self.pause_menu_open = False
                        self.settings_open = True

                        self.username_input_active = False

                        return

                    # RESTART
                    elif self.pause_restart_button.collidepoint(
                        event.pos
                    ):

                        self.finish_live_score()

                        self.reset_game()

                        return

            return

        # ========================================================
        # SETTINGS
        # ========================================================

        if self.settings_open:

            if self.profile_message_timer > 0:

                self.profile_message_timer -= 1

                if self.profile_message_timer <= 0:
                    self.profile_message = None

            for event in events:

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    if self.volume_minus_button.collidepoint(
                        event.pos
                    ):

                        self.set_sound_volume(
                            self.sound_volume - 0.1
                        )

                    elif self.volume_plus_button.collidepoint(
                        event.pos
                    ):

                        self.set_sound_volume(
                            self.sound_volume + 0.1
                        )

                    elif self.mobile_toggle_button.collidepoint(
                        event.pos
                    ):

                        self.set_mobile_controls(
                            not self.mobile_controls
                        )

                    elif self.username_box_rect.collidepoint(
                        event.pos
                    ):

                        self.username_input_active = True

                    elif self.username_save_button.collidepoint(
                        event.pos
                    ):

                        self.username_input_active = False
                        self.save_username()

                    elif self.logout_button.collidepoint(
                        event.pos
                    ):

                        self.logout()

                    elif self.settings_back_button.collidepoint(
                        event.pos
                    ):

                        self.username_input_active = False
                        self.settings_open = False

                        # BACK -> PAUSE MENU
                        self.pause_menu_open = True

                        return

                    else:

                        self.username_input_active = False

                elif (
                    event.type == pygame.KEYDOWN
                    and self.username_input_active
                ):

                    if event.key == pygame.K_RETURN:

                        self.username_input_active = False
                        self.save_username()

                    elif event.key == pygame.K_BACKSPACE:

                        self.username_input = (
                            self.username_input[:-1]
                        )

                    elif (
                        len(self.username_input) < 30
                        and event.unicode.isprintable()
                    ):

                        self.username_input += event.unicode

            return

        # ========================================================
        # MAIN MENU BUTTON
        # ========================================================

        for event in events:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if self.menu_button.collidepoint(
                    event.pos
                ):

                    self.pause_menu_open = True
                    self.username_input_active = False

                    return

        # ========================================================
        # PLAYER HISTORY
        # ========================================================

        if self.game_state in (
            "playing",
            "blinking"
        ):

            self.player_history.append(
                (
                    self.player.x,
                    self.player.y
                )
            )

            if len(self.player_history) > 60:
                self.player_history.pop(0)

        # ========================================================
        # PLAYING
        # ========================================================

        if self.game_state == "playing":

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                self.player.move_left()

            if keys[pygame.K_RIGHT]:
                self.player.move_right()

            screen_button_fired = False
            if self.mobile_controls and self.buttons:
                screen_button_fired = self.buttons.handle_mouse(
                    self.player, events
                )

            # Hold SPACE for continuous firing.
            keyboard_firing = keys[pygame.K_SPACE]
            wants_to_fire = keyboard_firing or screen_button_fired

            if self.fire_cooldown > 0:
                self.fire_cooldown -= 1

            if wants_to_fire and self.fire_cooldown <= 0:
                if self.fire_weapon():
                    self.fire_cooldown = 8

            self.player.keep_inside_screen()

            active_bullets = []
            for bullet in self.bullets:
                bullet.update()
                if bullet.is_active:
                    active_bullets.append(bullet)
            self.bullets = active_bullets

            self.timer += 1

            if self.timer >= max(90, 180 - self.stage * 4):
                waiting_enemies = [
                    enemy for enemy in self.enemies
                    if enemy.state == "waiting"
                ]

                if waiting_enemies and self.player_history:
                    chosen_enemy = random.choice(waiting_enemies)
                    target_x, target_y = self.player_history[0]
                    chosen_enemy.start_drop(target_x, target_y)

                self.timer = 0

            all_despawned = True
            for enemy in self.enemies:
                enemy.update()
                if enemy.state != "offscreen":
                    all_despawned = False

            if all_despawned and self.enemies:
                self.stage += 1
                self.weapon_level = 1 if self.score < 10 else (2 if self.score < 25 else 3)
                self.spawn_enemies()

            self.check_collisions()

        # ========================================================
        # BLINKING
        # ========================================================

        elif self.game_state == "blinking":

            self.player.update_blink()

            self.state_timer += 1

            for enemy in self.enemies:
                enemy.update()

            if self.state_timer >= 180:
                self.finish_game()

        # ========================================================
        # GAME OVER
        # ========================================================

        elif self.game_state == "game_over":

            for event in events:

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    if self.reload_button_rect.collidepoint(
                        event.pos
                    ):

                        self.reset_game()

                    elif self.game_over_home_button.collidepoint(
                        event.pos
                    ):

                        self.return_to_home()

                    elif self.game_over_leaderboard_button.collidepoint(
                        event.pos
                    ):

                        self.leaderboard_data = (
                            self.get_leaderboard(10)
                        )

                        self.leaderboard_open = True

    # ============================================================
    # FINISH GAME
    # ============================================================

    def finish_game(self):

        if self.game_state == "game_over":
            return

        self.game_state = "game_over"

        if not self.score_saved:

            self.finish_live_score()
            self.home_high_score = max(self.home_high_score, self.score)
            self.player_high_score = max(self.player_high_score, self.score)

            self.score_saved = True

    # ============================================================
    # RETURN TO HOME
    # ============================================================

    def return_to_home(self):
        """Return to the home screen without starting a new game."""

        # Make sure the current score has already been finalized.
        if self.game_state != "game_over" and not self.score_saved:
            self.finish_live_score()
            self.score_saved = True

        self.bullets = []
        self.enemies = []
        self.fire_cooldown = 0
        self.pause_menu_open = False
        self.settings_open = False
        self.leaderboard_open = False
        self.shop_open = False
        self.game_state = "waiting"
        self.state_timer = 0
        self.timer = 0

        # Refresh high scores for the home screen.
        self.load_home_high_score()
        self.player_high_score = self.get_player_high_score()

        self.app_state = "home"

    # ============================================================
    # COLLISIONS
    # ============================================================

    def check_collisions(self):

        if not self.player:
            return

        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):
                self.game_state = "blinking"
                self.player.is_blinking = True
                self.state_timer = 0
                return

        # Check every active player bullet.
        remaining_bullets = []
        hit_any = False

        for bullet in self.bullets:
            hit = False
            bullet_rect = bullet.get_rect()

            for enemy in self.enemies:
                if enemy.state == "offscreen":
                    continue

                if bullet_rect.colliderect(enemy.get_rect()):
                    enemy.state = "offscreen"
                    self.score += 1
                    self.add_coins(10)
                    hit = True
                    hit_any = True
                    if self.explosion_sound:
                        self.explosion_sound.play()
                    break

            if not hit:
                remaining_bullets.append(bullet)

        self.bullets = remaining_bullets

        if hit_any:
            # Weapon upgrades are score-based and capped to prevent
            # excessive object creation on slower machines.
            self.weapon_level = 1 if self.score < 10 else (2 if self.score < 25 else 3)
            self.max_bullets = 8 if self.weapon_level == 1 else 10

            # Update MySQL periodically instead of opening a DB connection
            # for every single hit. The final score is always saved.
            if self.score % 5 == 0:
                self.update_live_score()

    # ============================================================
    # LEADERBOARD
    # ============================================================

    def get_leaderboard(self, limit=10):

        self.leaderboard_error = None

        connection = None
        cursor = None

        try:

            connection = self.db.connect()

            cursor = connection.cursor(
                dictionary=True
            )

            limit = max(
                1,
                min(int(limit), 100)
            )

            query = f"""
                SELECT
                    p.id,
                    p.username,
                    MAX(s.score) AS best_score
                FROM players p
                JOIN scores s
                    ON s.player_id = p.id
                GROUP BY
                    p.id,
                    p.username
                ORDER BY
                    best_score DESC,
                    p.username ASC
                LIMIT {limit}
            """

            cursor.execute(query)

            return cursor.fetchall()

        except Exception as error:

            self.db_error = str(error)
            self.leaderboard_error = str(error)

            print(
                "Leaderboard error:",
                error
            )

            return []

        finally:

            if cursor:

                try:
                    cursor.close()
                except Exception:
                    pass

            if connection:

                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # UPDATE PLAYER PROFILE
    # ============================================================

    def update_player_profile(
        self,
        username=None,
        email=None
    ):

        if self.player_id is None:
            return False

        connection = None
        cursor = None

        try:

            connection = self.db.connect()
            cursor = connection.cursor()

            fields = []
            values = []

            if username is not None:

                fields.append(
                    "username = %s"
                )

                values.append(username)

            if email is not None:

                fields.append(
                    "email = %s"
                )

                values.append(email)

            if not fields:
                return False

            values.append(self.player_id)

            query = f"""
                UPDATE players
                SET {', '.join(fields)}
                WHERE id = %s
            """

            cursor.execute(
                query,
                tuple(values)
            )

            connection.commit()

            if cursor.rowcount > 0:

                if username:
                    self.player_name = username

                if email:
                    self.player_email = email

                if self.logged_player:

                    if username:
                        self.logged_player["username"] = username

                    if email:
                        self.logged_player["email"] = email

                return True

            return False

        except Exception as error:

            self.db_error = str(error)

            print(
                "Update profile error:",
                error
            )

            return False

        finally:

            if cursor:

                try:
                    cursor.close()
                except Exception:
                    pass

            if connection:

                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # SAVE USERNAME
    # ============================================================

    def save_username(self):

        new_name = self.username_input.strip()

        if not new_name:

            self.username_input = self.player_name

            self.profile_message = (
                "Username cannot be empty."
            )

            self.profile_message_timer = 150

            return False

        if new_name == self.player_name:

            self.profile_message = (
                "No changes to save."
            )

            self.profile_message_timer = 150

            return False

        updated = self.update_player_profile(
            username=new_name
        )

        if updated:

            self.username_input = self.player_name

            self.settings["player"][
                "default_username"
            ] = self.player_name

            try:
                save_settings(self.settings)
            except Exception as error:
                print(
                    "Could not save username:",
                    error
                )

            self.profile_message = (
                "Profile updated!"
            )

            self.profile_message_timer = 150

        else:

            self.username_input = self.player_name

            self.profile_message = (
                self.db_error
                or
                "Username may already be taken."
            )

            self.profile_message_timer = 180

        return updated

    # ============================================================
    # LOGOUT
    # ============================================================

    def logout(self):

        self.player_id = None
        self.player_name = ""
        self.player_email = ""
        self.player_high_score = 0
        self.coins = 0
        self.selected_ship = 1
        self.owned_ships = {1}
        self.shop_open = False
        self.shop_selected_id = 1

        self.logged_player = None

        self.live_score_id = None
        self.score_saved = False

        self.settings_open = False
        self.pause_menu_open = False
        self.leaderboard_open = False

        self.username_input_active = False

        self.auth_username = ""
        self.auth_email = ""
        self.auth_password = ""
        self.auth_confirm_password = ""

        self.auth_message = ""

        self.auth_mode = "login"
        self.auth_active_field = "username"

        self.game_state = "waiting"
        self.bullets = []

        self.app_state = "auth"

        self.logout_requested = False

        print("Player logged out.")

    # ============================================================
    # BUTTON HELPER
    # ============================================================

    def draw_button(
        self,
        rect,
        text,
        color,
        font=None
    ):

        if font is None:
            font = self.font

        mouse_pos = pygame.mouse.get_pos()

        draw_color = color

        if rect.collidepoint(mouse_pos):

            draw_color = tuple(
                min(255, value + 20)
                for value in color
            )

        pygame.draw.rect(
            self.screen,
            draw_color,
            rect,
            border_radius=10
        )

        label = font.render(
            text,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            label,
            (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2
            )
        )

    # ============================================================
    # DRAW PAUSE MENU
    # ============================================================

    def draw_pause_menu(self):

        # Draw the same background used during gameplay.
        self.background.draw(self.screen)

        if self.player:
            self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        if self.mobile_controls and self.buttons:
            self.buttons.draw(self.screen)

        # Dark overlay
        overlay = pygame.Surface(
            (
                self.screen_width,
                self.screen_height
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 190)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        # Title
        title = self.big_font.render(
            "PAUSED",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            (
                self.screen_width // 2
                - title.get_width() // 2,
                100
            )
        )

        # Player
        player_text = self.small_font.render(
            f"Player: {self.player_name}",
            True,
            (190, 190, 210)
        )

        self.screen.blit(
            player_text,
            (
                self.screen_width // 2
                - player_text.get_width() // 2,
                165
            )
        )

        # Continue
        self.draw_button(
            self.pause_continue_button,
            "CONTINUE",
            (50, 150, 70)
        )

        # Settings
        self.draw_button(
            self.pause_settings_button,
            "SETTINGS",
            (70, 100, 180)
        )

        # Restart
        self.draw_button(
            self.pause_restart_button,
            "RESTART",
            (180, 60, 60)
        )

        esc_text = self.small_font.render(
            "ESC = CONTINUE",
            True,
            (180, 180, 180)
        )

        self.screen.blit(
            esc_text,
            (
                self.screen_width // 2
                - esc_text.get_width() // 2,
                self.screen_height - 50
            )
        )

    # ============================================================
    # DRAW SETTINGS
    # ============================================================

    def draw_settings(self):

        self.screen.fill(
            (10, 10, 25)
        )

        title = self.big_font.render(
            "SETTINGS",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            (
                self.screen_width // 2
                - title.get_width() // 2,
                20
            )
        )

        logged_text = self.small_font.render(
            f"Logged in as: {self.player_name}",
            True,
            (180, 180, 180)
        )

        self.screen.blit(
            logged_text,
            (
                self.screen_width // 2
                - logged_text.get_width() // 2,
                90
            )
        )

        # ========================================================
        # SOUND
        # ========================================================

        volume_title = self.font.render(
            "Sound Volume",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            volume_title,
            (
                self.screen_width // 2
                - volume_title.get_width() // 2,
                130
            )
        )

        volume_percent = int(
            self.sound_volume * 100
        )

        volume_text = self.font.render(
            f"{volume_percent}%",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            volume_text,
            (
                self.screen_width // 2
                - volume_text.get_width() // 2,
                215
            )
        )

        self.draw_button(
            self.volume_minus_button,
            "-",
            (180, 50, 50)
        )

        self.draw_button(
            self.volume_plus_button,
            "+",
            (50, 180, 70)
        )

        # ========================================================
        # MOBILE
        # ========================================================

        mobile_title = self.font.render(
            "Mobile Controls",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            mobile_title,
            (
                self.screen_width // 2
                - mobile_title.get_width() // 2,
                275
            )
        )

        if self.mobile_controls:

            self.draw_button(
                self.mobile_toggle_button,
                "ON",
                (50, 180, 70)
            )

        else:

            self.draw_button(
                self.mobile_toggle_button,
                "OFF",
                (180, 50, 50)
            )

        # ========================================================
        # PROFILE
        # ========================================================

        username_title = self.small_font.render(
            "Update Username",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            username_title,
            (
                self.screen_width // 2
                - username_title.get_width() // 2,
                370
            )
        )

        box_color = (
            (60, 120, 180)
            if self.username_input_active
            else
            (50, 50, 70)
        )

        pygame.draw.rect(
            self.screen,
            box_color,
            self.username_box_rect,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            (150, 150, 170),
            self.username_box_rect,
            width=2,
            border_radius=8
        )

        display_value = self.username_input

        if (
            self.username_input_active
            and
            (pygame.time.get_ticks() // 500) % 2 == 0
        ):
            display_value += "|"

        username_text = self.small_font.render(
            display_value,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            username_text,
            (
                self.username_box_rect.x + 10,
                self.username_box_rect.centery
                - username_text.get_height() // 2
            )
        )

        self.draw_button(
            self.username_save_button,
            "SAVE",
            (50, 150, 50),
            self.small_font
        )

        if self.profile_message:

            message = self.small_font.render(
                self.profile_message,
                True,
                (255, 210, 120)
            )

            self.screen.blit(
                message,
                (
                    self.screen_width // 2
                    - message.get_width() // 2,
                    475
                )
            )

        # ========================================================
        # LOGOUT
        # ========================================================

        self.draw_button(
            self.logout_button,
            "LOGOUT",
            (180, 50, 50),
            self.small_font
        )

        # ========================================================
        # BACK
        # ========================================================

        self.draw_button(
            self.settings_back_button,
            "BACK",
            (70, 70, 100),
            self.small_font
        )

    # ============================================================
    # DRAW LEADERBOARD
    # ============================================================

    def draw_leaderboard(self):

        self.screen.fill(
            (10, 10, 25)
        )

        title = self.big_font.render(
            "LEADERBOARD",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            (
                self.screen_width // 2
                - title.get_width() // 2,
                40
            )
        )

        if self.leaderboard_error:

            error_text = self.small_font.render(
                "Leaderboard unavailable",
                True,
                (255, 100, 100)
            )

            self.screen.blit(
                error_text,
                (
                    self.screen_width // 2
                    - error_text.get_width() // 2,
                    130
                )
            )

        elif not self.leaderboard_data:

            empty_text = self.font.render(
                "No scores yet!",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                empty_text,
                (
                    self.screen_width // 2
                    - empty_text.get_width() // 2,
                    150
                )
            )

        else:

            row_y = 130

            for rank, entry in enumerate(
                self.leaderboard_data,
                start=1
            ):

                is_current_player = (
                    entry.get("id") == self.player_id
                )

                row_color = (
                    (255, 215, 90)
                    if is_current_player
                    else
                    (220, 220, 220)
                )

                username = entry.get(
                    "username",
                    "???"
                )

                best_score = entry.get(
                    "best_score",
                    0
                )

                row_text = self.font.render(
                    f"{rank}. {username} - {best_score}",
                    True,
                    row_color
                )

                self.screen.blit(
                    row_text,
                    (
                        self.screen_width // 2
                        - row_text.get_width() // 2,
                        row_y
                    )
                )

                row_y += 40

        self.draw_button(
            self.leaderboard_back_button,
            "BACK",
            (70, 70, 100)
        )

    # ============================================================
    # HOME SCREEN
    # ============================================================

    def handle_home_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.logout()
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.home_shop_button.collidepoint(event.pos):
                    self.shop_open = True
                    self.shop_selected_id = self.selected_ship
                    self.shop_message = ""
                    self.shop_message_timer = 0
                    return

                if self.home_start_button.collidepoint(event.pos):
                    self.app_state = "game"
                    self.reset_game()
                    return

                if self.home_leaderboard_button.collidepoint(event.pos):
                    self.leaderboard_data = self.get_leaderboard(10)
                    self.leaderboard_open = True
                    return

                if self.home_settings_button.collidepoint(event.pos):
                    self.settings_open = True
                    self.username_input_active = False
                    return

    def draw_home(self):
        self.screen.fill((7, 9, 25))

        # Subtle star field.
        for x, y, size in self.home_star_positions:
            pygame.draw.circle(self.screen, (90, 105, 150), (x, y), size)

        # Decorative panels.
        pygame.draw.circle(
            self.screen, (28, 45, 85),
            (self.screen_width // 2, 245), 145
        )
        pygame.draw.circle(
            self.screen, (13, 17, 42),
            (self.screen_width // 2, 245), 130
        )

        title = self.big_font.render("SPACE INVADERS", True, (245, 248, 255))
        self.screen.blit(
            title,
            (self.screen_width // 2 - title.get_width() // 2, 38)
        )

        welcome = self.small_font.render(
            f"WELCOME, {self.player_name}", True, (145, 210, 255)
        )
        self.screen.blit(
            welcome,
            (self.screen_width // 2 - welcome.get_width() // 2, 112)
        )

        if self.player:
            # Keep the character centered for the simple home-page look.
            old_x, old_y = self.player.x, self.player.y
            self.player.x = self.screen_width // 2 - self.player.width // 2
            self.player.y = 205
            self.player.draw(self.screen)
            self.player.x, self.player.y = old_x, old_y

        high = self.small_font.render(
            f"HIGH SCORE  {self.home_high_score}",
            True, (255, 220, 110)
        )
        self.screen.blit(
            high,
            (self.screen_width // 2 - high.get_width() // 2, 355)
        )

        self.draw_button(self.home_start_button, "START GAME", (45, 145, 95), self.font)
        self.draw_button(self.home_shop_button, "SHOP", (175, 105, 55), self.small_font)
        self.draw_button(self.home_leaderboard_button, "SCORES", (65, 100, 175), self.small_font)
        self.draw_button(self.home_settings_button, "SETTINGS", (120, 75, 165), self.small_font)

        coin_text = self.small_font.render(
            f"COINS: {self.coins}",
            True,
            (255, 220, 100)
        )
        self.screen.blit(
            coin_text,
            (self.screen_width // 2 - coin_text.get_width() // 2, 382)
        )

        hint = self.small_font.render(
            "Hold SPACE to fire  •  Arrow keys to move  •  ESC to logout",
            True, (125, 135, 160)
        )
        self.screen.blit(
            hint,
            (self.screen_width // 2 - hint.get_width() // 2, self.screen_height - 28)
        )

    # ============================================================
    # DRAW GAME
    # ============================================================

    def draw_game(self):

        if self.leaderboard_open:
            self.draw_leaderboard()
            return

        if self.settings_open:
            self.draw_settings()
            return

        if self.pause_menu_open:
            self.draw_pause_menu()
            return

        # Render background.png first so ships, enemies, bullets, and HUD
        # are drawn on top of it.
        self.background.draw(self.screen)

        if self.game_state != "game_over":
            if self.player:
                self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            if self.mobile_controls and self.buttons:
                self.buttons.draw(self.screen)

        # HUD panel.
        pygame.draw.rect(
            self.screen, (12, 16, 35), (12, 12, self.screen_width - 174, 82),
            border_radius=14
        )
        pygame.draw.rect(
            self.screen, (45, 60, 95), (12, 12, self.screen_width - 174, 82),
            width=2, border_radius=14
        )

        score_text = self.font.render(f"{self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (28, 18))
        label = self.small_font.render("SCORE", True, (130, 155, 190))
        self.screen.blit(label, (30, 59))

        stage = self.small_font.render(f"STAGE {self.stage}", True, (115, 220, 255))
        self.screen.blit(stage, (145, 25))

        weapon_name = "SINGLE" if self.weapon_level == 1 else ("TWIN" if self.weapon_level == 2 else "TRIPLE")
        weapon = self.small_font.render(f"WEAPON: {weapon_name}", True, (255, 205, 120))
        self.screen.blit(weapon, (145, 56))

        best = max(self.home_high_score, self.player_high_score) if self.player_id else self.home_high_score
        best_text = self.small_font.render(f"BEST {best}", True, (255, 220, 110))
        self.screen.blit(best_text, (300, 25))

        player_text = self.small_font.render(f"{self.player_name}", True, (175, 185, 205))
        self.screen.blit(player_text, (300, 56))

        self.draw_button(self.menu_button, "MENU", (65, 90, 155), self.small_font)

        if self.game_state == "game_over":
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 10, 185))
            self.screen.blit(overlay, (0, 0))

            go_text = self.big_font.render("GAME OVER", True, (255, 85, 100))
            self.screen.blit(go_text, (self.screen_width // 2 - go_text.get_width() // 2, self.screen_height // 2 - 120))

            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score_text, (self.screen_width // 2 - final_score_text.get_width() // 2, self.screen_height // 2 - 40))

            if self.score >= self.home_high_score and self.score > 0:
                record = self.small_font.render("NEW HIGH SCORE!", True, (255, 220, 100))
                self.screen.blit(record, (self.screen_width // 2 - record.get_width() // 2, self.screen_height // 2 + 5))

            self.draw_button(self.reload_button_rect, "PLAY AGAIN", (45, 145, 95), self.small_font)
            self.draw_button(self.game_over_home_button, "BACK TO HOME", (120, 75, 165), self.small_font)
            self.draw_button(self.game_over_leaderboard_button, "LEADERBOARD", (65, 100, 175), self.small_font)

    # ============================================================
    # DRAW
    # ============================================================

    def draw(self):

        if self.app_state == "auth":
            self.draw_auth()
        elif self.app_state == "home":
            if self.shop_open:
                self.draw_shop()
            elif self.leaderboard_open:
                self.draw_leaderboard()
            elif self.settings_open:
                self.draw_settings()
            else:
                self.draw_home()
        else:
            self.draw_game()