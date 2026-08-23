"""Configuration values for the browser game."""

import os

WORLD_WIDTH = int(os.getenv("WORLD_WIDTH", "800"))
WORLD_HEIGHT = int(os.getenv("WORLD_HEIGHT", "500"))

STARTING_HEALTH = int(os.getenv("STARTING_HEALTH", "3"))
PLAYER_SIZE = int(os.getenv("PLAYER_SIZE", "42"))
PLAYER_SPEED = int(os.getenv("PLAYER_SPEED", "320"))

SPAWN_INTERVAL = float(os.getenv("SPAWN_INTERVAL", "0.7"))
ASTEROID_MIN_SIZE = int(os.getenv("ASTEROID_MIN_SIZE", "22"))
ASTEROID_MAX_SIZE = int(os.getenv("ASTEROID_MAX_SIZE", "46"))
ASTEROID_MIN_SPEED = int(os.getenv("ASTEROID_MIN_SPEED", "170"))
ASTEROID_MAX_SPEED = int(os.getenv("ASTEROID_MAX_SPEED", "290"))
