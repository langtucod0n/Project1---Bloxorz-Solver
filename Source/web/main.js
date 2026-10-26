/* Bloxorz TV4 - dieu khien giao dien (tuan 2).
   Luong du lieu:  phim / nut bam  ->  BloxorzApi (fetch)  ->  backend Python  ->  trang thai JSON
                   ->  BloxorzScene (ve + hoat anh).   JS khong tu tinh luat choi.               */
(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const el = {
    status: $('status'), container: $('game-container'), banner: $('banner'),
    toast: $('toast'), toastText: $('toastText'), toastClose: $('toastClose'),
    level: $('levelSelect'), prevBtn: $('prevLevel'), nextBtn: $('nextLevel'), newBtn: $('newBtn'), restartBtn: $('restartBtn'),
    replayBtn: $('replayBtn'), stopBtn: $('stopBtn'),
    relative: $('relativeKeys'), speed: $('speed'), speedLabel: $('speedLabel'), solution: $('solutionBox'),
    gameStatus: $('gameStatus'), orientation: $('orientation'), moveCount: $('moveCount'), anchor: $('anchor'),
    statsBody: document.querySelector('#statsTable tbody')
  };
  const solveBtns = [...document.querySelectorAll('button.solve')];
  const allButtons = [...document.querySelectorAll('button')].filter((b) => b !== el.toastClose && b !== el.stopBtn);

  if (!window.THREE || !THREE.OrbitControls) {
    el.status.textContent = 'Lỗi: chưa tải được Three.js / OrbitControls';
    throw new Error('Thieu THREE hoac THREE.OrbitControls - kiem tra web/lib/');
  }

  const api = window.BloxorzApi;
  const view = window.BloxorzScene.create(el.container);

  const ALGO_LABEL = { bfs: 'BFS', ids: 'IDS', dfs: 'DFS', ucs: 'UCS', astar: 'A*' };
  const ORIENT = { STANDING: 'Đứng', LYING_H: 'Nằm ngang', LYING_V: 'Nằm dọc' };
  const STATUS = { playing: 'Đang chơi', won: 'Thắng', lost: 'Thua' };

  let level = null;
  let levelId = null;
  let state = null;
  let busy = false;          // dang co hoat anh / dang goi API
  let autoplay = false;      // dang tu chay loi giai
  let stopRequested = false;
  let lastSolution = null;   // { algo, moves }
  let stats = {};            // algo -> stats cua lan giai gan nhat tren man hien tai
  let latestAlgo = null;
  let toastTimer = null;
  let pendingDir = null;     // phim bam khi dang co hoat anh: nho 1 nuoc de chay ngay sau do

  /* ---------------- giao dien phu ---------------- */
  function setStatus(text) { el.status.textContent = text; }

  function showError(err) {
    el.toastText.textContent = err && err.message ? err.message : String(err);
    el.toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.toast.hidden = true; }, 12000);
    setStatus('Lỗi');
  }

  function setBusy(v) {
    busy = v;
    syncButtons();
  }

  function syncButtons() {
    const lock = busy || autoplay;
    allButtons.forEach((b) => { b.disabled = lock; });
    el.stopBtn.disabled = !autoplay;
    el.level.disabled = lock;
    if (!lock) el.replayBtn.disabled = !lastSolution;
    // nút < > : khóa ở màn đầu / màn cuối
    el.prevBtn.disabled = lock || el.level.selectedIndex <= 0;
    el.nextBtn.disabled = lock || el.level.selectedIndex >= el.level.options.length - 1;
  }

  function stepLevel(delta) {
    const i = el.level.selectedIndex + delta;
    if (i < 0 || i >= el.level.options.length) return;
    el.level.selectedIndex = i;
    guarded(() => loadLevel(el.level.value));
  }

  function updatePanel() {
    if (!state) return;
    el.gameStatus.textContent = STATUS[state.status] || state.status;
    if (state.block) {
      el.orientation.textContent = ORIENT[state.block.orientation] || state.block.orientation;
      el.anchor.textContent = `(${state.block.r}, ${state.block.c})`;
    } else if (state.cubes) {
      const [a, b] = state.cubes;
      el.orientation.textContent = `Tách đôi · đang điều khiển cube ${state.active === 0 ? 'A (xanh dương)' : 'B (xanh lục)'}`;
      el.anchor.textContent = `A(${a.r}, ${a.c}) · B(${b.r}, ${b.c})`;
    }
    el.moveCount.textContent = String(state.moves);

    if (state.status === 'won') {
      el.banner.className = 'banner won';
      el.banner.textContent = `Chiến thắng! ${state.moves} nước đi`;
      el.banner.hidden = false;
      setStatus('Chiến thắng!');
    } else if (state.status === 'lost') {
      el.banner.className = 'banner lost';
      el.banner.textContent = state.reason === 'fragile' ? 'Thua: ô dễ vỡ bị gãy' : 'Thua: rơi khỏi sàn';
      el.banner.hidden = false;
      setStatus('Thua');
    } else {
      el.banner.hidden = true;
      if (!autoplay) setStatus('Sẵn sàng');
    }
  }

  function renderStats() {
    const rows = Object.keys(ALGO_LABEL).filter((a) => stats[a]);
    if (!rows.length) {
      el.statsBody.innerHTML = '<tr class="empty"><td colspan="5">Chưa giải lần nào</td></tr>';
      return;
    }
    el.statsBody.innerHTML = rows.map((a) => {
      const s = stats[a];
      const len = s.length === null || s.length === undefined ? 'không có' : s.length;
      return `<tr class="${a === latestAlgo ? 'latest' : ''}"><td>${ALGO_LABEL[a]}</td><td>${s.time_ms}</td><td>${s.memory_kb}</td><td>${s.expanded}</td><td>${len}</td></tr>`;
    }).join('');
  }

  function renderSolution(moves, current) {
    if (!moves) { el.solution.hidden = true; return; }
    el.solution.hidden = false;
    el.solution.innerHTML = moves.map((m, i) => {
      const cls = i < current ? 'done' : (i === current ? 'cur' : '');
      return `<span class="${cls}">${m}</span>`;
    }).join(' ');
  }

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  /* ---------------- goi API + ve ---------------- */
  async function loadLevel(id) {
    const res = await api.load(id);
    levelId = id;
    level = res.level;
    state = res.state;
    view.loadLevel(level);
    view.setState(state);
    lastSolution = null;
    stats = {};
    latestAlgo = null;
    renderStats();
    renderSolution(null);
    updatePanel();
  }

  async function restart() {
    const res = await api.load(levelId);       // backend khong co /restart: nap lai man
    state = res.state;
    view.setState(state);
    updatePanel();
  }

  // Gui 1 nuoc di len backend, roi ve hoat anh theo trang thai backend tra ve.
  // Tra ve false neu backend tu choi nuoc di.
  async function applyMove(dir) {
    const prev = state;
    if (dir === 'S') {
      const res = await api.switchCube();
      if (res.result !== 'moved') return false;
      state = res.state;
      await view.animateSwitch(state);
      updatePanel();
      return true;
    }
    const res = await api.move(dir);
    if (res.result !== 'moved') return false;
    state = res.state;
    el.moveCount.textContent = String(state.moves);
    setStatus('Đang lăn…');
    await view.animateMove(prev, dir, state);
    updatePanel();
    return true;
  }

  async function guarded(fn) {
    setBusy(true);
    try {
      return await fn();
    } catch (err) {
      showError(err);
      autoplay = false;
      return undefined;
    } finally {
      setBusy(false);
      runPending();
    }
  }

  function runPending() {
    const d = pendingDir;
    pendingDir = null;
    if (!d || busy || autoplay || !state || state.status !== 'playing') return;
    if (d === 'S' && !state.cubes) return;
    guarded(() => applyMove(d));
  }

  /* ---------------- phat loi giai ---------------- */
  async function play(moves) {
    autoplay = true;
    stopRequested = false;
    syncButtons();
    let i = 0;
    try {
      for (; i < moves.length; i++) {
        if (stopRequested) break;
        renderSolution(moves, i);
        setStatus(`Đang chạy lời giải: bước ${i + 1}/${moves.length}`);
        const ok = await applyMove(moves[i]);
        if (!ok) throw new Error(`Backend từ chối nước đi thứ ${i + 1} (${moves[i]}).`);
        await sleep(160 / view.speed);
      }
      renderSolution(moves, stopRequested ? i : moves.length);
      if (stopRequested) setStatus('Đã dừng');
    } finally {
      autoplay = false;
      syncButtons();
    }
  }

  async function solve(algo) {
    setStatus(`Đang giải bằng ${ALGO_LABEL[algo]}…`);
    await restart();                       // loi giai tinh tu dau man
    const res = await api.solve(algo, levelId);
    stats[algo] = res.stats;
    latestAlgo = algo;
    renderStats();
    if (!res.solution) {
      lastSolution = null;
      renderSolution(null);
      setStatus(`${ALGO_LABEL[algo]}: không tìm thấy lời giải`);
      return;
    }
    lastSolution = { algo, moves: res.solution };
    await play(res.solution);
  }

  /* ---------------- su kien ---------------- */
  // Phím -> vị trí trên màn hình (0 lên, 1 phải, 2 xuống, 3 trái), rồi xoay theo góc nhìn camera.
  const FWD = ['U', 'R', 'D', 'L'];     // hướng lưới theo chiều kim đồng hồ, bắt đầu từ "lên"
  const KEY_SLOT = {
    arrowup: 0, w: 0, arrowright: 1, d: 1, arrowdown: 2, s: 2, arrowleft: 3, a: 3
  };
  function keyToDir(key) {
    if (key === ' ') return 'S';
    const slot = KEY_SLOT[key];
    if (slot === undefined) return null;
    const k = el.relative.checked ? view.viewQuarter() : 0;
    return FWD[(k + slot) % 4];
  }

  window.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target && e.target.tagName === 'SELECT') return;
    const dir = keyToDir(e.key.toLowerCase());
    if (!dir) return;
    e.preventDefault();
    if (autoplay || !state || state.status !== 'playing') return;
    if (busy) { pendingDir = dir; return; }         // dang lan: xep hang 1 nuoc cho muot
    if (dir === 'S' && !state.cubes) return;      // chi co y nghia khi da tach 2 cube (backend cung se tu choi)
    guarded(() => applyMove(dir));
  });

  document.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (b) b.blur();                               // tranh phim Space "bam lai" nut dang focus
  });

  el.level.addEventListener('change', () => { el.level.blur(); guarded(() => loadLevel(el.level.value)); });
  el.prevBtn.addEventListener('click', () => stepLevel(-1));
  el.nextBtn.addEventListener('click', () => stepLevel(1));
  el.newBtn.addEventListener('click', () => guarded(() => loadLevel(el.level.value)));
  el.restartBtn.addEventListener('click', () => guarded(async () => { await restart(); renderSolution(null); }));
  solveBtns.forEach((b) => b.addEventListener('click', () => guarded(() => solve(b.dataset.algo))));
  el.replayBtn.addEventListener('click', () => guarded(async () => {
    if (!lastSolution) return;
    await restart();
    await play(lastSolution.moves);
  }));
  el.relative.addEventListener('change', () => el.relative.blur());
  el.stopBtn.addEventListener('click', () => { stopRequested = true; });
  el.speed.addEventListener('input', () => {
    view.speed = parseFloat(el.speed.value);
    el.speedLabel.textContent = `${view.speed.toFixed(2).replace(/0$/, '')}×`;
  });
  el.toastClose.addEventListener('click', () => { el.toast.hidden = true; });

  /* ---------------- khoi dong ---------------- */
  guarded(async () => {
    const levels = await api.levels();
    el.level.innerHTML = levels.map((l) => `<option value="${l.id}">${l.name}</option>`).join('');
    await loadLevel(levels[0].id);
  });
})();
