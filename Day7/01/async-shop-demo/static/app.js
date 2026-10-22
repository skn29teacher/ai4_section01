const MODES = {
  blocking: { label: "블로킹", expected: "약 6초" },
  async: { label: "비동기", expected: "약 2초" },
  threaded: { label: "스레드", expected: "약 2초" },
};

const buttons = [...document.querySelectorAll(".mode-button")];
const compareButton = document.querySelector("#compare-all");
const cards = [...document.querySelectorAll(".product-card")];
const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const totalTime = document.querySelector("#total-time");
const healthTime = document.querySelector("#health-time");
const healthNote = document.querySelector("#health-note");
const eventLog = document.querySelector("#event-log");

let running = false;
let experimentStartedAt = 0;

const secondsSinceStart = () => (performance.now() - experimentStartedAt) / 1000;
const formatSeconds = value => `${value.toFixed(2)}초`;

function addLog(message) {
  const item = document.createElement("li");
  const time = document.createElement("time");
  const text = document.createElement("span");
  time.textContent = `${secondsSinceStart().toFixed(2)}s`;
  text.textContent = message;
  item.append(time, text);
  eventLog.append(item);
  eventLog.scrollTop = eventLog.scrollHeight;
}

function setControlsDisabled(disabled) {
  buttons.forEach(button => { button.disabled = disabled; });
  compareButton.disabled = disabled;
}

function resetCards() {
  cards.forEach(card => {
    card.classList.remove("running", "done");
    card.querySelector(".card-result").textContent = "대기 중";
  });
}

async function checkHealth(mode) {
  await new Promise(resolve => setTimeout(resolve, 250));
  const startedAt = performance.now();
  addLog("상태 확인 요청 시작");
  try {
    const response = await fetch("/api/health", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const elapsed = (performance.now() - startedAt) / 1000;
    healthTime.textContent = formatSeconds(elapsed);
    healthNote.textContent = mode === "blocking" && elapsed > 2
      ? "이벤트 루프가 막혀 상태 확인도 함께 기다렸습니다."
      : "재고 조회를 기다리는 동안에도 바로 응답했습니다.";
    addLog(`상태 확인 완료 (${formatSeconds(elapsed)})`);
  } catch (error) {
    healthTime.textContent = "실패";
    healthNote.textContent = error.message;
    addLog(`상태 확인 실패: ${error.message}`);
  }
}

async function fetchProduct(mode, card) {
  const productId = card.dataset.product;
  const result = card.querySelector(".card-result");
  card.classList.add("running");
  result.textContent = "조회 중…";
  addLog(`상품 ${productId} 요청 시작`);

  const startedAt = performance.now();
  const response = await fetch(`/api/products/${mode}/${productId}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`상품 ${productId}: HTTP ${response.status}`);
  const data = await response.json();
  const elapsed = (performance.now() - startedAt) / 1000;

  card.classList.remove("running");
  card.classList.add("done");
  result.textContent = `${elapsed.toFixed(2)}초 · 재고 ${data.stock}개`;
  addLog(`상품 ${productId} 완료 (${formatSeconds(elapsed)})`);
  return elapsed;
}

function updateChart(mode, elapsed) {
  const row = document.querySelector(`[data-chart="${mode}"]`);
  const width = Math.min(100, (elapsed / 6.5) * 100);
  row.querySelector("i").style.width = `${width}%`;
  row.querySelector("strong").textContent = formatSeconds(elapsed);
}

async function runExperiment(mode, keepControlsLocked = false) {
  if (running && !keepControlsLocked) return;
  running = true;
  setControlsDisabled(true);
  resetCards();
  eventLog.replaceChildren();
  healthTime.textContent = "측정 중…";
  healthNote.textContent = "실험 시작 0.25초 뒤 상태 확인을 요청합니다.";
  buttons.forEach(button => button.classList.toggle("active", button.dataset.mode === mode));

  experimentStartedAt = performance.now();
  statusDot.className = "status-dot running";
  statusText.textContent = `${MODES[mode].label} 방식 실행 중 · 예상 ${MODES[mode].expected}`;
  totalTime.textContent = "측정 중";
  addLog(`${MODES[mode].label} 실험 시작`);

  const healthPromise = checkHealth(mode);
  try {
    await Promise.all(cards.map(card => fetchProduct(mode, card)));
    const elapsed = secondsSinceStart();
    await healthPromise;
    totalTime.textContent = formatSeconds(elapsed);
    statusDot.className = "status-dot done";
    statusText.textContent = `${MODES[mode].label} 실험 완료`;
    updateChart(mode, elapsed);
    addLog(`전체 완료 (${formatSeconds(elapsed)})`);
    return elapsed;
  } catch (error) {
    statusDot.className = "status-dot";
    statusText.textContent = `오류: ${error.message}`;
    totalTime.textContent = "실패";
    addLog(error.message);
    return null;
  } finally {
    running = false;
    if (!keepControlsLocked) setControlsDisabled(false);
  }
}

buttons.forEach(button => {
  button.addEventListener("click", () => runExperiment(button.dataset.mode));
});

compareButton.addEventListener("click", async () => {
  if (running) return;
  setControlsDisabled(true);
  for (const mode of ["blocking", "async", "threaded"]) {
    await runExperiment(mode, true);
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  setControlsDisabled(false);
  statusText.textContent = "전체 비교 완료 · 아래 결과 막대를 확인하세요.";
});

document.querySelector("#clear-log").addEventListener("click", () => {
  eventLog.replaceChildren();
});

