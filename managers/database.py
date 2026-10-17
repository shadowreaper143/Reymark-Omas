"""
managers/database.py
MySQL database manager for the Space Invaders / SpaceWar project.

Required package:
    python -m pip install mysql-connector-python

Database:
    game_db

This version supports:
- player registration
- login/profile lookup
- password_hash storage
- scores
- leaderboard
- coins
- selected ship
- purchased ships
"""

import mysql.connector
from mysql.connector import Error


class DatabaseManager:

    def __init__(
        self,
        host="localhost",
        port=3306,
        user="root",
        password="",
        database="game_db"
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    # ============================================================
    # CONNECTION
    # ============================================================

    def connect(self):
        """Create and return a MySQL connection."""
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=False
        )

    def test_connection(self):
        """Return True when MySQL can be reached."""
        connection = None

        try:
            connection = self.connect()
            return connection.is_connected()

        except Error as error:
            print("MySQL connection error:", error)
            return False

        finally:
            if connection:
                try:
                    connection.close()
                except Exception:
                    pass

    # ============================================================
    # DATABASE INITIALIZATION
    # ============================================================

    def initialize_database(self):
        """
        Create the tables required by the game.

        The database itself must already exist, or create_database()
        can be called first.
        """

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            # ----------------------------------------------------
            # PLAYERS
            # ----------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    password_hash VARCHAR(255),
                    coins INT NOT NULL DEFAULT 0,
                    selected_ship INT NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )

            # ----------------------------------------------------
            # SCORES
            # ----------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT NOT NULL,
                    score INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT fk_scores_player
                        FOREIGN KEY (player_id)
                        REFERENCES players(id)
                        ON DELETE CASCADE
                )
                """
            )

            # ----------------------------------------------------
            # PLAYER SHIPS
            # ----------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS player_ships (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT NOT NULL,
                    ship_id INT NOT NULL,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    UNIQUE KEY unique_player_ship
                        (player_id, ship_id),

                    CONSTRAINT fk_player_ships_player
                        FOREIGN KEY (player_id)
                        REFERENCES players(id)
                        ON DELETE CASCADE
                )
                """
            )

            connection.commit()

            print("Database tables initialized successfully.")
            return True

        except Error as error:
            if connection:
                connection.rollback()

            print("Database initialization error:", error)
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
    # REGISTER PLAYER
    # ============================================================

    def register_player(
        self,
        username,
        email=None,
        password_hash=None
    ):
        """
        Register a new player.

        Returns:
            player_id on success
            None on failure
        """

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO players
                (
                    username,
                    email,
                    password_hash,
                    coins,
                    selected_ship
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    0,
                    1
                )
                """,
                (
                    username,
                    email,
                    password_hash
                )
            )

            player_id = cursor.lastrowid

            # Ship 1 is free and automatically owned.
            cursor.execute(
                """
                INSERT IGNORE INTO player_ships
                (
                    player_id,
                    ship_id
                )
                VALUES
                (
                    %s,
                    1
                )
                """,
                (player_id,)
            )

            connection.commit()

            return player_id

        except Error as error:
            if connection:
                connection.rollback()

            print("Register player error:", error)
            return None

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
    # GET PLAYER
    # ============================================================

    def get_player(self, username):
        """Return player information as a dictionary."""

        connection = None
        cursor = None

        try:
            connection = self.connect()

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
                    selected_ship,
                    created_at,
                    updated_at
                FROM players
                WHERE username = %s
                LIMIT 1
                """,
                (username,)
            )

            return cursor.fetchone()

        except Error as error:
            print("Get player error:", error)
            return None

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
    # GET PLAYER BY ID
    # ============================================================

    def get_player_by_id(self, player_id):
        """Return player information by player ID."""

        connection = None
        cursor = None

        try:
            connection = self.connect()

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
                    selected_ship,
                    created_at,
                    updated_at
                FROM players
                WHERE id = %s
                LIMIT 1
                """,
                (player_id,)
            )

            return cursor.fetchone()

        except Error as error:
            print("Get player by ID error:", error)
            return None

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
    # UPDATE PLAYER
    # ============================================================

    def update_player(
        self,
        player_id,
        username=None,
        email=None
    ):
        """Update username and/or email."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            fields = []
            values = []

            if username is not None:
                fields.append("username = %s")
                values.append(username)

            if email is not None:
                fields.append("email = %s")
                values.append(email)

            if not fields:
                return False

            values.append(player_id)

            query = f"""
                UPDATE players
                SET {", ".join(fields)}
                WHERE id = %s
            """

            cursor.execute(query, tuple(values))
            connection.commit()

            return cursor.rowcount > 0

        except Error as error:
            if connection:
                connection.rollback()

            print("Update player error:", error)
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
    # DELETE PLAYER
    # ============================================================

    def delete_player(self, player_id):
        """Delete a player and related scores/ships."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM players
                WHERE id = %s
                """,
                (player_id,)
            )

            connection.commit()

            return cursor.rowcount > 0

        except Error as error:
            if connection:
                connection.rollback()

            print("Delete player error:", error)
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
    # SAVE SCORE
    # ============================================================

    def save_score(self, player_id, score):
        """Save a player's score."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
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
                    %s
                )
                """,
                (
                    player_id,
                    int(score)
                )
            )

            score_id = cursor.lastrowid

            connection.commit()

            return score_id

        except Error as error:
            if connection:
                connection.rollback()

            print("Save score error:", error)
            return None

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
    # LEADERBOARD
    # ============================================================

    def get_leaderboard(self, limit=100):
        """Return highest scores."""

        connection = None
        cursor = None

        try:
            connection = self.connect()

            cursor = connection.cursor(
                dictionary=True
            )

            limit = max(1, min(int(limit), 100))

            query = f"""
                SELECT
                    scores.id,
                    scores.player_id,
                    players.username,
                    scores.score,
                    scores.created_at
                FROM scores
                INNER JOIN players
                    ON players.id = scores.player_id
                ORDER BY scores.score DESC
                LIMIT {limit}
            """

            cursor.execute(query)

            return cursor.fetchall()

        except Error as error:
            print("Leaderboard error:", error)
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
    # PLAYER SCORES
    # ============================================================

    def get_player_scores(self, player_id):
        """Return all scores belonging to one player."""

        connection = None
        cursor = None

        try:
            connection = self.connect()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    id,
                    player_id,
                    score,
                    created_at
                FROM scores
                WHERE player_id = %s
                ORDER BY score DESC
                """,
                (player_id,)
            )

            return cursor.fetchall()

        except Error as error:
            print("Player scores error:", error)
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
    # COINS
    # ============================================================

    def get_coins(self, player_id):
        """Get current coin balance."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT coins
                FROM players
                WHERE id = %s
                """,
                (player_id,)
            )

            row = cursor.fetchone()

            if row:
                return int(row[0] or 0)

            return 0

        except Error as error:
            print("Get coins error:", error)
            return 0

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

    def add_coins(self, player_id, amount):
        """Add coins to a player."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE players
                SET coins = coins + %s
                WHERE id = %s
                """,
                (
                    int(amount),
                    player_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        except Error as error:
            if connection:
                connection.rollback()

            print("Add coins error:", error)
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
    # SET COINS
    # ============================================================

    def set_coins(self, player_id, amount):
        """Set the player's exact coin balance."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE players
                SET coins = %s
                WHERE id = %s
                """,
                (
                    max(0, int(amount)),
                    player_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        except Error as error:
            if connection:
                connection.rollback()

            print("Set coins error:", error)
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
    # SELECTED SHIP
    # ============================================================

    def get_selected_ship(self, player_id):
        """Return selected ship ID."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT selected_ship
                FROM players
                WHERE id = %s
                """,
                (player_id,)
            )

            row = cursor.fetchone()

            if row:
                return int(row[0] or 1)

            return 1

        except Error as error:
            print("Get selected ship error:", error)
            return 1

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

    def set_selected_ship(self, player_id, ship_id):
        """Save the selected ship."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE players
                SET selected_ship = %s
                WHERE id = %s
                """,
                (
                    int(ship_id),
                    player_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        except Error as error:
            if connection:
                connection.rollback()

            print("Set selected ship error:", error)
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
    # PLAYER SHIPS
    # ============================================================

    def owns_ship(self, player_id, ship_id):
        """Check whether a player owns a ship."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id
                FROM player_ships
                WHERE player_id = %s
                  AND ship_id = %s
                LIMIT 1
                """,
                (
                    player_id,
                    ship_id
                )
            )

            return cursor.fetchone() is not None

        except Error as error:
            print("Owns ship error:", error)
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

    def get_owned_ships(self, player_id):
        """Return a set of owned ship IDs."""

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT ship_id
                FROM player_ships
                WHERE player_id = %s
                ORDER BY ship_id
                """,
                (player_id,)
            )

            rows = cursor.fetchall()

            return {
                int(row[0])
                for row in rows
            }

        except Error as error:
            print("Get owned ships error:", error)
            return {1}

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

    def purchase_ship(
        self,
        player_id,
        ship_id,
        price
    ):
        """
        Purchase a ship.

        Returns:
            True  = purchase successful
            False = not enough coins/error/already owned
        """

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            # Lock the player row while purchasing.
            cursor.execute(
                """
                SELECT coins
                FROM players
                WHERE id = %s
                FOR UPDATE
                """,
                (player_id,)
            )

            row = cursor.fetchone()

            if not row:
                connection.rollback()
                return False

            coins = int(row[0] or 0)

            if coins < int(price):
                connection.rollback()
                return False

            cursor.execute(
                """
                SELECT id
                FROM player_ships
                WHERE player_id = %s
                  AND ship_id = %s
                LIMIT 1
                """,
                (
                    player_id,
                    ship_id
                )
            )

            if cursor.fetchone():
                connection.rollback()
                return False

            cursor.execute(
                """
                UPDATE players
                SET coins = coins - %s
                WHERE id = %s
                """,
                (
                    int(price),
                    player_id
                )
            )

            cursor.execute(
                """
                INSERT INTO player_ships
                (
                    player_id,
                    ship_id
                )
                VALUES
                (
                    %s,
                    %s
                )
                """,
                (
                    player_id,
                    ship_id
                )
            )

            connection.commit()

            return True

        except Error as error:
            if connection:
                connection.rollback()

            print("Purchase ship error:", error)
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
    # TEST INSERT
    # ============================================================

    def test_insert(self):
        """
        Basic database test.
        Creates a temporary-style test username only if it
        does not already exist.
        """

        connection = None
        cursor = None

        try:
            connection = self.connect()
            cursor = connection.cursor()

            username = "test_player"

            cursor.execute(
                """
                SELECT id
                FROM players
                WHERE username = %s
                """,
                (username,)
            )

            row = cursor.fetchone()

            if row:
                return row[0]

            cursor.execute(
                """
                INSERT INTO players
                (
                    username,
                    email,
                    password_hash,
                    coins,
                    selected_ship
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    0,
                    1
                )
                """,
                (
                    username,
                    "test@example.com",
                    ""
                )
            )

            player_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT IGNORE INTO player_ships
                (
                    player_id,
                    ship_id
                )
                VALUES
                (
                    %s,
                    1
                )
                """,
                (player_id,)
            )

            connection.commit()

            return player_id

        except Error as error:
            if connection:
                connection.rollback()

            print("Test insert error:", error)
            return None

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


# ================================================================
# SIMPLE TEST
# ================================================================

if __name__ == "__main__":

    print("Testing MySQL Connector...")

    try:
        db = DatabaseManager(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="game_db"
        )

        if db.test_connection():
            print("MySQL connection successful.")

            if db.initialize_database():
                print("Database is ready.")
            else:
                print("Database initialization failed.")

        else:
            print(
                "Could not connect to MySQL."
            )
            print(
                "Make sure MySQL is running in XAMPP."
            )

    except ModuleNotFoundError:
        print()
        print("=" * 60)
        print("MYSQL CONNECTOR IS NOT INSTALLED")
        print("=" * 60)
        print()
        print("Run:")
        print()
        print("python -m pip install mysql-connector-python")
        print()
        print("Then run the game again.")
