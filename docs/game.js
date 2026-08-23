const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById("score");
const healthEl = document.getElementById("health");
const finalScoreEl = document.getElementById("finalScore");

const menuScreen = document.getElementById("menuScreen");
const gameOverScreen = document.getElementById("gameOverScreen");
const startButton = document.getElementById("startButton");
const restartButton = document.getElementById("restartButton");

const assets = {
  background: new Image(),
  player: new Image(),
  asteroid: new Image(),
};
assets.background.src = "./static/images/background.svg";
assets.player.src = "./static/sprites/player.svg";
assets.asteroid.src = "./static/sprites/asteroid.svg";

let gameState = null;
let lastFrame = performance.now();
let accumulator = 0;

const controls = {
  left: false,
  right: false,
  up: false,
  down: false,
};

const STEP_SECONDS = 1 / 30;
const MAX_QUEUED_STEPS = 5;

function startGame() {
  const prevHighScore = gameState ? gameState.high_score : 0;
  gameState = createGameState();
  gameState.high_score = prevHighScore;
  updateGameState(gameState, { start: true }, 0);
  menuScreen.classList.add("hidden");
  menuScreen.classList.remove("visible");
  gameOverScreen.classList.add("hidden");
  gameOverScreen.classList.remove("visible");
}

function syncUiState() {
  if (!gameState) return;

  scoreEl.textContent = gameState.score;
  healthEl.textContent = gameState.health;

  if (gameState.status === "menu") {
    menuScreen.classList.remove("hidden");
    menuScreen.classList.add("visible");
  }

  if (gameState.status === "game_over") {
    finalScoreEl.textContent = gameState.score;
    gameOverScreen.classList.remove("hidden");
    gameOverScreen.classList.add("visible");
  }
}

function drawEntity(entity, image) {
  if (image.complete && image.naturalWidth > 0) {
    ctx.drawImage(image, entity.x, entity.y, entity.width, entity.height);
    return;
  }

  ctx.fillStyle = "#f7b267";
  ctx.fillRect(entity.x, entity.y, entity.width, entity.height);
}

function render() {
  if (assets.background.complete && assets.background.naturalWidth > 0) {
    ctx.drawImage(assets.background, 0, 0, canvas.width, canvas.height);
  } else {
    ctx.fillStyle = "#050914";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  if (!gameState) return;

  drawEntity(gameState.player, assets.player);
  for (const entity of gameState.entities) {
    drawEntity(entity, assets.asteroid);
  }
}

function frame(timestamp) {
  const dt = Math.min(0.1, (timestamp - lastFrame) / 1000);
  lastFrame = timestamp;
  accumulator += dt;
  accumulator = Math.min(accumulator, STEP_SECONDS * MAX_QUEUED_STEPS);

  if (gameState && gameState.status === "playing") {
    while (accumulator >= STEP_SECONDS) {
      updateGameState(gameState, controls, STEP_SECONDS);
      accumulator -= STEP_SECONDS;
    }
  }

  if (gameState) {
    syncUiState();
  }

  render();
  requestAnimationFrame(frame);
}

function setControl(key, isDown) {
  if (key === "ArrowLeft" || key === "a" || key === "A") controls.left = isDown;
  if (key === "ArrowRight" || key === "d" || key === "D") controls.right = isDown;
  if (key === "ArrowUp" || key === "w" || key === "W") controls.up = isDown;
  if (key === "ArrowDown" || key === "s" || key === "S") controls.down = isDown;
}

window.addEventListener("keydown", (event) => setControl(event.key, true));
window.addEventListener("keyup", (event) => setControl(event.key, false));

startButton.addEventListener("click", startGame);
restartButton.addEventListener("click", startGame);

// ── On-screen D-pad touch/click controls ──────────────────────────────────────
const dpadMap = {
  dpadUp:    "up",
  dpadDown:  "down",
  dpadLeft:  "left",
  dpadRight: "right",
};

for (const [id, dir] of Object.entries(dpadMap)) {
  const btn = document.getElementById(id);
  if (!btn) continue;

  const press   = (e) => { e.preventDefault(); controls[dir] = true; };
  const release = (e) => { e.preventDefault(); controls[dir] = false; };

  btn.addEventListener("touchstart",  press,   { passive: false });
  btn.addEventListener("touchend",    release, { passive: false });
  btn.addEventListener("touchcancel", release, { passive: false });
  btn.addEventListener("mousedown",   press);
  btn.addEventListener("mouseup",     release);
  btn.addEventListener("mouseleave",  release);
}

// Prevent the page from scrolling while the player is using the D-pad
document.getElementById("dpad")?.addEventListener("touchmove", (e) => {
  e.preventDefault();
}, { passive: false });

requestAnimationFrame(frame);
