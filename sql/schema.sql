DROP DATABASE IF EXISTS space_shooter;
CREATE DATABASE space_shooter;

USE space_shooter;

-- Players
CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scores / Leaderboard
CREATE TABLE scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    score INT NOT NULL DEFAULT 0,
    level INT NOT NULL DEFAULT 1,
    enemies_defeated INT NOT NULL DEFAULT 0,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_scores_player
        FOREIGN KEY (player_id)
        REFERENCES players(id)
        ON DELETE CASCADE
);

-- Index for faster leaderboard loading
CREATE INDEX idx_scores_leaderboard
ON scores(score DESC);