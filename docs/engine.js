/**
 * engine.js — client-side port of api_client.py
 * Contains all game simulation logic so the game runs without a backend.
 */

const Settings = {
  WORLD_WIDTH: 800,
  WORLD_HEIGHT: 500,
  STARTING_HEALTH: 3,
  PLAYER_SIZE: 42,
  PLAYER_SPEED: 320,
  SPAWN_INTERVAL: 0.7,
  ASTEROID_MIN_SIZE: 22,
  ASTEROID_MAX_SIZE: 46,
  ASTEROID_MIN_SPEED: 170,
  ASTEROID_MAX_SPEED: 290,
};

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function createPlayer() {
  return {
    type: "player",
    x: Settings.WORLD_WIDTH / 2 - Settings.PLAYER_SIZE / 2,
    y: Settings.WORLD_HEIGHT - Settings.PLAYER_SIZE - 20,
    width: Settings.PLAYER_SIZE,
    height: Settings.PLAYER_SIZE,
    vx: 0,
    vy: 0,
    speed: Settings.PLAYER_SPEED,
  };
}

function createGameState() {
  return {
    status: "menu",
    world: { width: Settings.WORLD_WIDTH, height: Settings.WORLD_HEIGHT },
    player: createPlayer(),
    entities: [],
    score: 0,
    health: Settings.STARTING_HEALTH,
    high_score: 0,
    spawn_cooldown: Settings.SPAWN_INTERVAL,
    next_entity_id: 1,
    events: [],
  };
}

function resetForPlay(state) {
  state.status = "playing";
  state.player = createPlayer();
  state.entities = [];
  state.score = 0;
  state.health = Settings.STARTING_HEALTH;
  state.spawn_cooldown = Settings.SPAWN_INTERVAL;
}

function updatePlayer(player, controls, dt, world) {
  const horizontal = (controls.right ? 1 : 0) - (controls.left ? 1 : 0);
  const vertical = (controls.down ? 1 : 0) - (controls.up ? 1 : 0);

  player.vx = horizontal * player.speed;
  player.vy = vertical * player.speed;

  player.x += player.vx * dt;
  player.y += player.vy * dt;

  player.x = Math.max(0, Math.min(player.x, world.width - player.width));
  player.y = Math.max(0, Math.min(player.y, world.height - player.height));
}

function spawnAsteroid(state) {
  const size = randInt(Settings.ASTEROID_MIN_SIZE, Settings.ASTEROID_MAX_SIZE);
  const speed = randInt(Settings.ASTEROID_MIN_SPEED, Settings.ASTEROID_MAX_SPEED);
  const maxX = state.world.width - size;

  state.entities.push({
    id: state.next_entity_id++,
    type: "asteroid",
    x: randInt(0, Math.max(0, maxX)),
    y: -size,
    width: size,
    height: size,
    vx: 0,
    vy: speed,
  });
}

function isOverlap(a, b) {
  return !(
    a.x + a.width < b.x ||
    a.x > b.x + b.width ||
    a.y + a.height < b.y ||
    a.y > b.y + b.height
  );
}

function updateGameState(state, controls, dt) {
  controls = controls || {};
  dt = Math.max(0, Math.min(dt != null ? dt : 1 / 60, 0.1));

  const events = [];
  state.events = events;

  if (controls.start && (state.status === "menu" || state.status === "game_over")) {
    resetForPlay(state);
    events.push({ type: "game_started" });
  }

  if (state.status !== "playing") return state;

  updatePlayer(state.player, controls, dt, state.world);

  state.spawn_cooldown -= dt;
  if (state.spawn_cooldown <= 0) {
    spawnAsteroid(state);
    state.spawn_cooldown += Settings.SPAWN_INTERVAL;
  }

  const survived = [];
  const player = state.player;

  for (const entity of state.entities) {
    if (isOverlap(player, entity)) {
      state.health -= 1;
      events.push({ type: "player_hit", entity_id: entity.id });
      continue;
    }

    entity.x += entity.vx * dt;
    entity.y += entity.vy * dt;

    if (isOverlap(player, entity)) {
      state.health -= 1;
      events.push({ type: "player_hit", entity_id: entity.id });
      continue;
    }

    if (entity.y > state.world.height) {
      state.score += 1;
      continue;
    }

    survived.push(entity);
  }

  state.entities = survived;

  if (state.health <= 0) {
    state.status = "game_over";
    state.high_score = Math.max(state.high_score, state.score);
    events.push({ type: "game_over", score: state.score });
  }

  return state;
}
