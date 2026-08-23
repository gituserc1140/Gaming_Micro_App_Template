"""Flask entrypoint for the browser-based game."""

from __future__ import annotations

import os
import time
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_from_directory

from api_client import create_game_state, update_game_state


app = Flask(__name__, template_folder="ui", static_folder="static")
GAME_STATES = {}
STATE_TTL_SECONDS = int(os.getenv("GAME_STATE_TTL_SECONDS", "600"))
MAX_ACTIVE_GAMES = int(os.getenv("MAX_ACTIVE_GAMES", "200"))


def _cleanup_states() -> None:
    now = time.time()
    expired_ids = [
        game_id
        for game_id, entry in GAME_STATES.items()
        if now - entry["updated_at"] > STATE_TTL_SECONDS
    ]
    for game_id in expired_ids:
        GAME_STATES.pop(game_id, None)

    while len(GAME_STATES) > MAX_ACTIVE_GAMES:
        oldest_game_id = min(
            GAME_STATES, key=lambda game_id: GAME_STATES[game_id]["updated_at"]
        )
        GAME_STATES.pop(oldest_game_id, None)


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/ui/<path:filename>")
def ui_assets(filename: str):
    return send_from_directory(app.template_folder, filename)


@app.post("/api/start")
def start_game():
    _cleanup_states()
    game_id = str(uuid4())
    state = create_game_state()
    update_game_state(state, {"start": True}, 0)
    GAME_STATES[game_id] = {"state": state, "updated_at": time.time()}
    return jsonify({"game_id": game_id, "state": state})


@app.get("/api/state/<game_id>")
def get_state(game_id: str):
    _cleanup_states()
    entry = GAME_STATES.get(game_id)
    if not entry:
        return jsonify({"error": "Game not found"}), 404
    entry["updated_at"] = time.time()
    state = entry["state"]
    return jsonify({"game_id": game_id, "state": state})


@app.post("/api/update")
def update_state():
    _cleanup_states()
    payload = request.get_json(silent=True) or {}
    game_id = payload.get("game_id")

    if not game_id:
        return jsonify({"error": "Missing game_id"}), 400
    if game_id not in GAME_STATES:
        return jsonify({"error": "Invalid or missing game_id"}), 404

    controls = payload.get("input") or {}
    dt = payload.get("dt", 1 / 60)

    entry = GAME_STATES[game_id]
    entry["state"] = update_game_state(entry["state"], controls=controls, dt=dt)
    state = entry["state"]
    entry["updated_at"] = time.time()
    return jsonify({"game_id": game_id, "state": state})


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(
        host=host,
        port=port,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
