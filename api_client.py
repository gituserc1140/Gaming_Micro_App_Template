"""Core game logic for the browser game backend."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from config import settings


GameState = Dict[str, Any]


def create_game_state() -> GameState:
    """Create a new game state in menu mode."""
    return {
        "status": "menu",
        "world": {"width": settings.WORLD_WIDTH, "height": settings.WORLD_HEIGHT},
        "player": _create_player(),
        "entities": [],
        "score": 0,
        "health": settings.STARTING_HEALTH,
        "high_score": 0,
        "spawn_cooldown": settings.SPAWN_INTERVAL,
        "next_entity_id": 1,
        "events": [],
    }


def update_game_state(game_state: GameState, controls: Optional[Dict[str, Any]] = None, dt: float = 1 / 60) -> GameState:
    """Update the game state for one simulation step."""
    controls = controls or {}
    dt = max(0.0, min(float(dt), 0.1))

    events: List[Dict[str, Any]] = []
    game_state["events"] = events

    if controls.get("start") and game_state["status"] in {"menu", "game_over"}:
        _reset_for_play(game_state)
        events.append({"type": "game_started"})

    if game_state["status"] != "playing":
        return game_state

    _update_player(game_state["player"], controls, dt, game_state["world"])

    game_state["spawn_cooldown"] -= dt
    if game_state["spawn_cooldown"] <= 0:
        _spawn_asteroid(game_state)
        game_state["spawn_cooldown"] += settings.SPAWN_INTERVAL

    survived_entities: List[Dict[str, Any]] = []
    player = game_state["player"]
    for entity in game_state["entities"]:
        if _is_overlap(player, entity):
            game_state["health"] -= 1
            game_state["events"].append({"type": "player_hit", "entity_id": entity.get("id")})
            continue

        entity["x"] += entity["vx"] * dt
        entity["y"] += entity["vy"] * dt

        if _is_overlap(player, entity):
            game_state["health"] -= 1
            game_state["events"].append({"type": "player_hit", "entity_id": entity.get("id")})
            continue

        if entity["y"] > game_state["world"]["height"]:
            game_state["score"] += 1
            continue
        survived_entities.append(entity)

    game_state["entities"] = survived_entities

    if game_state["health"] <= 0:
        game_state["status"] = "game_over"
        game_state["high_score"] = max(game_state["high_score"], game_state["score"])
        events.append({"type": "game_over", "score": game_state["score"]})

    return game_state


def _create_player() -> Dict[str, Any]:
    return {
        "type": "player",
        "x": settings.WORLD_WIDTH / 2 - settings.PLAYER_SIZE / 2,
        "y": settings.WORLD_HEIGHT - settings.PLAYER_SIZE - 20,
        "width": settings.PLAYER_SIZE,
        "height": settings.PLAYER_SIZE,
        "vx": 0.0,
        "vy": 0.0,
        "speed": settings.PLAYER_SPEED,
    }


def _reset_for_play(game_state: GameState) -> None:
    game_state["status"] = "playing"
    game_state["player"] = _create_player()
    game_state["entities"] = []
    game_state["score"] = 0
    game_state["health"] = settings.STARTING_HEALTH
    game_state["spawn_cooldown"] = settings.SPAWN_INTERVAL


def _update_player(player: Dict[str, Any], controls: Dict[str, Any], dt: float, world: Dict[str, int]) -> None:
    horizontal = float(bool(controls.get("right"))) - float(bool(controls.get("left")))
    vertical = float(bool(controls.get("down"))) - float(bool(controls.get("up")))

    player["vx"] = horizontal * player["speed"]
    player["vy"] = vertical * player["speed"]

    player["x"] += player["vx"] * dt
    player["y"] += player["vy"] * dt

    player["x"] = max(0, min(player["x"], world["width"] - player["width"]))
    player["y"] = max(0, min(player["y"], world["height"] - player["height"]))


def _spawn_asteroid(game_state: GameState) -> None:
    size = random.randint(settings.ASTEROID_MIN_SIZE, settings.ASTEROID_MAX_SIZE)
    speed = random.randint(settings.ASTEROID_MIN_SPEED, settings.ASTEROID_MAX_SPEED)
    max_x = game_state["world"]["width"] - size

    game_state["entities"].append(
        {
            "id": game_state["next_entity_id"],
            "type": "asteroid",
            "x": random.randint(0, max(0, max_x)),
            "y": -size,
            "width": size,
            "height": size,
            "vx": 0.0,
            "vy": float(speed),
        }
    )
    game_state["next_entity_id"] += 1


def _is_overlap(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return not (
        a["x"] + a["width"] < b["x"]
        or a["x"] > b["x"] + b["width"]
        or a["y"] + a["height"] < b["y"]
        or a["y"] > b["y"] + b["height"]
    )
