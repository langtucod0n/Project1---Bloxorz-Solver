/* Lop goi API cua TV5 (FastAPI, server/app.py). JavaScript KHONG chua luat choi:
   moi nuoc di deu gui len backend roi ve lai trang thai nhan duoc.

   File nay dich JSON that cua backend sang "mo hinh ve" ma scene.js hieu (xem normLevel / normState).
   Khi TV2/TV3 chot dinh dang cau, cong tac, tach khoi thi chi sua o day.

   Dia chi backend:
   - Mo qua http://127.0.0.1:8000 (python main.py): dung cung origin, khong can cau hinh.
   - Mo tu noi khac (vd. Live Server cong 5500): goi http://127.0.0.1:8000 (server can bat CORS).
   - Muon doi: them ?api=http://host:port vao URL.                                              */
(() => {
  'use strict';

  const params = new URLSearchParams(location.search);
  const defaultBase = location.port === '8000' ? '' : 'http://127.0.0.1:8000';
  const BASE = (params.get('api') ?? defaultBase).replace(/\/$/, '');

  class ApiError extends Error {
    constructor(message, kind, status) {
      super(message);
      this.kind = kind;     // 'network' | 'http'
      this.status = status; // ma HTTP neu co
    }
  }

  async function request(method, path, body) {
    let res;
    try {
      res = await fetch(BASE + path, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body)
      });
    } catch (err) {
      throw new ApiError(
        `Không kết nối được máy chủ (${BASE || location.origin}). Hãy chạy "python main.py" trong thư mục Source rồi tải lại trang.`,
        'network'
      );
    }
    let data = null;
    try { data = await res.json(); } catch (_) { /* body rong / khong phai JSON */ }
    if (!res.ok) {
      // FastAPI: {"detail": "thong bao"}; loi 422 thi detail la danh sach
      let msg = data && data.detail;
      if (Array.isArray(msg)) msg = 'Dữ liệu gửi lên sai dạng (422).';
      throw new ApiError(msg || `Máy chủ trả lỗi ${res.status}`, 'http', res.status);
    }
    return data;
  }

  /* ---------- dich JSON backend -> mo hinh ve ---------- */
  const ORIENT = ['STANDING', 'LYING_H', 'LYING_V'];          // state.orient: 0 / 1 / 2
  const TILE_TYPE = { floor: 'normal', fragile: 'fragile', goal: 'goal' };
  let level = null;       // man dang choi (da chuan hoa)
  let moves = 0;          // dem nuoc di (backend khong dem)

  function normLevel(id, raw) {
    const tiles = [];
    let goal = null;
    raw.grid.forEach((row, r) => {
      [...row].forEach((ch, c) => {
        const kind = raw.legend[ch];
        if (kind === 'void') return;                  // o hong: khong ve
        if (!(kind in TILE_TYPE)) console.warn(`Loai o chua ho tro: ${kind}; ve nhu o thuong`);
        const type = TILE_TYPE[kind] || 'normal';
        if (type === 'goal') goal = { r, c };
        tiles.push({ r, c, type });
      });
    });
    // Cau: o cau do bridges[].cells quyet dinh (ky tu tren grid bo qua)
    const bridgeIds = [];
    for (const b of raw.bridges || []) {
      const bid = `B${b.id}`;
      bridgeIds.push(bid);
      for (const [r, c] of b.cells) {
        const i = tiles.findIndex((t) => t.r === r && t.c === c);
        const t = { r, c, type: 'bridge', bridge_id: bid };
        if (i >= 0) tiles[i] = t; else tiles.push(t);
      }
    }
    // Cong tac: ve len o floor tuong ung
    for (const sw of raw.switches || []) {
      const [r, c] = sw.cell;
      const t = tiles.find((x) => x.r === r && x.c === c);
      if (!t) continue;
      t.type = `switch_${sw.type}`;                       // switch_soft | switch_heavy | switch_split
      if (sw.targets) t.toggles = sw.targets.map((id) => `B${id}`);
      if (sw.split_to) t.split_to = sw.split_to;
    }
    return { id, name: id, rows: raw.grid.length, cols: raw.grid[0].length, goal, tiles, bridgeIds };
  }

  function normState(raw) {
    const status = String(raw.status).toLowerCase();       // playing | won | lost
    // bridges: bitmask, bit i = 1 <=> cau id=i dang mo
    const bridges = {};
    for (const bid of (level && level.bridgeIds) || []) bridges[bid] = ((raw.bridges >> Number(bid.slice(1))) & 1) === 1;
    const st = { status, reason: null, moves, block: null, cubes: null, active: 0, bridges, broken: [] };

    let cell;                                               // o cua khoi / cube dang dieu khien
    if (raw.split) {                                        // [[r0,c0],[r1,c1],active]
      st.cubes = [{ r: raw.split[0][0], c: raw.split[0][1] }, { r: raw.split[1][0], c: raw.split[1][1] }];
      st.active = raw.split[2];
      cell = st.cubes[st.active];
    } else {
      st.block = { r: raw.r, c: raw.c, orientation: ORIENT[raw.orient] };
      cell = st.block.orientation === 'STANDING' ? st.block : null;
    }
    if (status === 'lost') {
      // Backend chi bao LOST. De chon hoat anh: dung tren o fragile -> vo, nguoc lai -> roi.
      const t = cell && level ? level.tiles.find((x) => x.r === cell.r && x.c === cell.c) : null;
      if (t && t.type === 'fragile') { st.reason = 'fragile'; st.broken = [[cell.r, cell.c]]; }
      else st.reason = 'fell';
    }
    return st;
  }

  window.BloxorzApi = {
    base: BASE,
    ApiError,

    async levels() {
      const res = await request('GET', '/api/levels');
      return res.levels.map((id) => ({ id, name: id }));
    },

    // Nap man (cung dung de Restart vi backend khong co endpoint restart)
    async load(levelId) {
      const res = await request('POST', '/api/load', { level_id: levelId });
      level = normLevel(res.level_id || levelId, res.level);
      moves = 0;
      return { level, state: normState(res.state) };
    },

    async move(direction) {
      const res = await request('POST', '/api/move', { direction });
      moves += 1;
      return { result: 'moved', state: normState(res.state) };
    },

    // Doi cube dang dieu khien (hanh dong 'S'). Backend tra {state, status} nhu /api/move.
    async switchCube() {
      const res = await request('POST', '/api/switch_control', {});
      moves += 1;
      return { result: 'moved', state: normState(res.state) };
    },

    // algorithm: bfs | ids | dfs | ucs | astar. Tra ve loi giai tu DAU man.
    async solve(algorithm, levelId) {
      const res = await request('POST', '/api/solve', { algorithm, level_id: levelId });
      const m = res.metrics || {};
      return {
        algorithm: res.algorithm,
        solution: res.solved ? res.moves : null,
        stats: {
          time_ms: Math.round(m.time * 1e6) / 1e3,            // giay -> ms
          memory_kb: Math.round(m.peak_memory / 102.4) / 10,  // byte -> KB
          expanded: m.expanded,
          length: m.length
        }
      };
    }
  };
})();
