/* Bloxorz TV4 - lop ve 3D (Three.js r158) + hoat anh.
   File nay CHI ve: nhan du lieu man choi / trang thai (JSON tu backend) roi dung hinh.
   Khong co luat choi o day. Toa do: hang r chay theo truc Z, cot c chay theo truc X, mat san o y = 0. */
(() => {
  'use strict';
  const T = THREE;

  const TILE = 0.96;
  const THICK = 0.16;
  const BRIDGE_DOWN = -2.4;               // do cao khi cau dong (tut xuong duoi san)
  const BRIDGE_COLORS = ['#3ec7a5', '#c77dff', '#ffd166', '#5aa9ff'];
  const CUBE_STYLE = [
    { body: '#2f9cff', top: '#85d2ff' },
    { body: '#27c997', top: '#8ff0cd' }
  ];
  const AXIS_X = new T.Vector3(1, 0, 0);
  const AXIS_Z = new T.Vector3(0, 0, 1);

  const easeInOut = (k) => k * k * (3 - 2 * k);
  const easeIn = (k) => k * k;
  const easeOut = (k) => 1 - (1 - k) * (1 - k);
  const key = (r, c) => `${r},${c}`;

  /* ---------- hinh hoc khoi (chi de VE, khong phai luat) ---------- */
  function blockDims(o) {
    return { x: o === 'LYING_H' ? 2 : 1, y: o === 'STANDING' ? 2 : 1, z: o === 'LYING_V' ? 2 : 1 };
  }
  function blockCenter(b) {
    if (b.orientation === 'STANDING') return new T.Vector3(b.c, 1, b.r);
    if (b.orientation === 'LYING_H') return new T.Vector3(b.c + 0.5, 0.5, b.r);
    return new T.Vector3(b.c, 0.5, b.r + 0.5);
  }
  const cubeCenter = (q) => new T.Vector3(q.c, 0.5, q.r);

  /* ---------- texture ve tren mat o (canvas) ---------- */
  function tileTexture(kind, color, maxAniso) {
    const S = 256;
    const cv = document.createElement('canvas');
    cv.width = cv.height = S;
    const g = cv.getContext('2d');
    const base = kind === 'fragile' ? '#d9822b' : (kind === 'goal' ? '#0a0d14' : '#65748b');
    g.fillStyle = base;
    g.fillRect(0, 0, S, S);
    // vien trong de nhin ra tung o
    g.strokeStyle = kind === 'fragile' ? 'rgba(90,40,0,.55)' : 'rgba(255,255,255,.14)';
    g.lineWidth = 6;
    g.strokeRect(10, 10, S - 20, S - 20);

    g.lineCap = 'round';
    g.lineJoin = 'round';
    if (kind === 'fragile') {
      g.strokeStyle = 'rgba(80,35,0,.8)';
      g.lineWidth = 7;
      g.beginPath();
      g.moveTo(40, 60); g.lineTo(110, 105); g.lineTo(95, 150); g.lineTo(170, 190); g.lineTo(200, 230);
      g.moveTo(110, 105); g.lineTo(185, 70); g.lineTo(215, 40);
      g.moveTo(95, 150); g.lineTo(45, 200);
      g.stroke();
    } else if (kind === 'soft') {
      g.strokeStyle = color; g.lineWidth = 20;
      g.beginPath(); g.arc(S / 2, S / 2, 62, 0, Math.PI * 2); g.stroke();
      g.fillStyle = color;
      g.beginPath(); g.arc(S / 2, S / 2, 22, 0, Math.PI * 2); g.fill();
    } else if (kind === 'heavy') {
      g.strokeStyle = color; g.lineWidth = 26;
      g.beginPath();
      g.moveTo(62, 62); g.lineTo(S - 62, S - 62);
      g.moveTo(S - 62, 62); g.lineTo(62, S - 62);
      g.stroke();
    } else if (kind === 'split') {
      g.strokeStyle = '#ffb454'; g.lineWidth = 20;
      g.beginPath();
      g.moveTo(98, 58); g.lineTo(60, 58); g.lineTo(60, S - 58); g.lineTo(98, S - 58);
      g.moveTo(S - 98, 58); g.lineTo(S - 60, 58); g.lineTo(S - 60, S - 58); g.lineTo(S - 98, S - 58);
      g.stroke();
    } else if (kind === 'goal') {
      const grd = g.createRadialGradient(S / 2, S / 2, 20, S / 2, S / 2, S * 0.5);
      grd.addColorStop(0, '#000000'); grd.addColorStop(1, '#0d1118');
      g.fillStyle = grd;
      g.fillRect(0, 0, S, S);
      g.strokeStyle = '#e9bb55'; g.lineWidth = 16;
      g.strokeRect(14, 14, S - 28, S - 28);
    } else if (kind === 'bridge') {
      g.strokeStyle = color; g.lineWidth = 22;
      g.strokeRect(22, 22, S - 44, S - 44);
      g.fillStyle = color;
      g.globalAlpha = 0.25;
      g.fillRect(40, 40, S - 80, S - 80);
      g.globalAlpha = 1;
    }
    const tex = new T.CanvasTexture(cv);
    tex.colorSpace = T.SRGBColorSpace;
    tex.anisotropy = maxAniso;
    return tex;
  }

  /* ---------- tao view ---------- */
  function create(container) {
    const scene = new T.Scene();
    scene.background = new T.Color('#111827');
    scene.fog = new T.Fog('#111827', 26, 70);

    const camera = new T.PerspectiveCamera(32, 1, 0.1, 120);
    const renderer = new T.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = T.PCFSoftShadowMap;
    renderer.outputColorSpace = T.SRGBColorSpace;
    renderer.localClippingEnabled = true;
    container.appendChild(renderer.domElement);
    const maxAniso = Math.min(8, renderer.capabilities.getMaxAnisotropy());

    const controls = new T.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.minDistance = 4;
    controls.maxDistance = 45;

    scene.add(new T.HemisphereLight(0xc9e2ff, 0x273047, 2.0));
    const sun = new T.DirectionalLight(0xffffff, 2.4);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.bias = -0.0005;
    scene.add(sun, sun.target);

    // nen toi phia duoi (vuc tham), nhan bong do
    const ground = new T.Mesh(
      new T.PlaneGeometry(300, 300),
      new T.MeshStandardMaterial({ color: '#0b111b', roughness: 1 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -7;
    scene.add(ground);

    /* ----- vat lieu dung chung ----- */
    const sideMat = new T.MeshStandardMaterial({ color: '#374357', roughness: 0.9 });
    const fragileSide = new T.MeshStandardMaterial({ color: '#8f4f14', roughness: 0.9 });
        const tileGeo = new T.BoxGeometry(TILE, THICK, TILE);
    const tileEdgeGeo = new T.EdgesGeometry(tileGeo);
    const topMats = {}; // cache theo loai+mau

    function topMaterial(kind, color) {
      const k = kind + color;
      if (!topMats[k]) {
        topMats[k] = new T.MeshStandardMaterial({
          map: tileTexture(kind, color, maxAniso), roughness: 0.78, metalness: 0.05
        });
      }
      return topMats[k];
    }

    /* ----- trang thai view ----- */
    const levelGroup = new T.Group();
    scene.add(levelGroup);
    const tiles = new Map();        // "r,c" -> { group, data, kind }
    const bridges = new Map();      // bridgeId -> [{group, y}]
    const bridgeIndex = [];         // thu tu id -> mau
    let level = null;
    const actors = { block: null, cubes: null, active: 0 };
    const view = { speed: 1, scene, camera, renderer, controls };

    const dur = (ms) => ms / view.speed;

    function tween(ms, fn, ease = easeInOut) {
      return new Promise((resolve) => {
        const t0 = performance.now();
        (function frame(now) {
          const k = ms <= 0 ? 1 : Math.min(1, (now - t0) / ms);
          fn(ease(k), k);
          if (k < 1) requestAnimationFrame(frame); else resolve();
        })(t0);
      });
    }

    function disposeObject(o) {
      o.traverse((n) => {
        if (n.geometry && n.userData.ownGeo) n.geometry.dispose();
        if (n.userData.ownMat) {
          (Array.isArray(n.material) ? n.material : [n.material]).forEach((m) => m.dispose());
        }
      });
    }

    /* ----- dung man choi ----- */
    function clearLevel() {
      clearActors();
      for (const child of [...levelGroup.children]) {
        levelGroup.remove(child);
        disposeObject(child);
      }
      tiles.clear();
      bridges.clear();
      bridgeIndex.length = 0;
    }

    function addOutline(x, z, color, y, opacity) {
      const h = 0.5;
      const pts = [
        new T.Vector3(-h, 0, -h), new T.Vector3(h, 0, -h), new T.Vector3(h, 0, h), new T.Vector3(-h, 0, h)
      ];
      const geo = new T.BufferGeometry().setFromPoints(pts);
      const line = new T.LineLoop(geo, new T.LineBasicMaterial({ color, transparent: true, opacity }));
      line.position.set(x, y, z);
      line.userData.ownGeo = true;
      line.userData.ownMat = true;
      levelGroup.add(line);
      return line;
    }

    function makeTile(t) {
      const group = new T.Group();
      group.position.set(t.c, 0, t.r);
      let kind = 'normal';
      let color = '#ffffff';
      switch (t.type) {
        case 'fragile': kind = 'fragile'; break;
        case 'switch_soft': kind = 'soft'; break;
        case 'switch_heavy': kind = 'heavy'; break;
        case 'switch_split': kind = 'split'; break;
        case 'bridge': kind = 'bridge'; break;
        case 'goal': kind = 'goal'; break;
        default: break;
      }
      if (t.type === 'bridge') {
        let i = bridgeIndex.indexOf(t.bridge_id);
        if (i < 0) { bridgeIndex.push(t.bridge_id); i = bridgeIndex.length - 1; }
        color = BRIDGE_COLORS[i % BRIDGE_COLORS.length];
      } else if (t.toggles && t.toggles.length) {
        const i = bridgeIndex.indexOf(t.toggles[0]);
        color = BRIDGE_COLORS[(i < 0 ? 0 : i) % BRIDGE_COLORS.length];
      }
      const side = kind === 'fragile' ? fragileSide : sideMat;
      const mesh = new T.Mesh(tileGeo, [side, side, topMaterial(kind, color), side, side, side]);
      mesh.position.y = -THICK / 2;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      group.add(mesh);
      const edge = new T.LineSegments(
        tileEdgeGeo,
        new T.LineBasicMaterial({ color: kind === 'fragile' ? '#ffb15e' : '#a7b7ce', transparent: true, opacity: 0.3 })
      );
      edge.position.y = -THICK / 2;
      edge.userData.ownMat = true;
      group.add(edge);
      levelGroup.add(group);
      return { group, data: t, kind, color };
    }

    function loadLevel(lv) {
      clearLevel();
      level = lv;
      // gom id cau theo thu tu xuat hien de mau on dinh
      for (const t of lv.tiles) {
        if (t.type === 'bridge' && !bridgeIndex.includes(t.bridge_id)) bridgeIndex.push(t.bridge_id);
      }
      bridgeIndex.sort();
      for (const t of lv.tiles) {
        const obj = makeTile(t);
        tiles.set(key(t.r, t.c), obj);
        if (t.type === 'bridge') {
          if (!bridges.has(t.bridge_id)) bridges.set(t.bridge_id, []);
          bridges.get(t.bridge_id).push(obj);
          // duong vien mo cho biet cau se mo o dau khi dang dong
          obj.ghost = addOutline(t.c, t.r, obj.color, 0.012, 0.55);
        }
        if (t.type === 'switch_split' && t.split_to) {
          t.split_to.forEach(([rr, cc], i) => addOutline(cc, rr, CUBE_STYLE[i].body, 0.02, 0.9));
        }
      }
      frameCamera();
    }

    function frameCamera() {
      // khung hinh theo ranh gioi thuc su cua cac o (khong theo rows/cols)
      let r0 = Infinity, r1 = -Infinity, c0 = Infinity, c1 = -Infinity;
      for (const t of level.tiles) {
        r0 = Math.min(r0, t.r); r1 = Math.max(r1, t.r);
        c0 = Math.min(c0, t.c); c1 = Math.max(c1, t.c);
      }
      const cx = (c0 + c1) / 2, cz = (r0 + r1) / 2;
      const radius = Math.hypot(c1 - c0 + 2, r1 - r0 + 2) / 2;
      controls.target.set(cx, 0, cz);
      const dist = Math.max(10, radius * 2.6 + 3);
      // huong nhin xien 45 do, do cao ~35 do (kieu isometric)
      const dirv = new T.Vector3(1, 1, 1).normalize();
      camera.position.set(cx, 0, cz).addScaledVector(dirv, dist);
      camera.lookAt(controls.target);
      controls.update();
      sun.position.set(cx - 6, 12, cz + 7);
      sun.target.position.set(cx, 0, cz);
      const ext = radius + 3;
      const sc = sun.shadow.camera;
      sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext;
      sc.near = 1; sc.far = 40;
      sc.updateProjectionMatrix();
    }

    /* ----- khoi & cube ----- */
    function clearActors() {
      for (const m of [actors.block, ...(actors.cubes || [])]) {
        if (m) { scene.remove(m); disposeObject(m); }
      }
      actors.block = null;
      actors.cubes = null;
    }

    function makeBlockMesh(b) {
      const d = blockDims(b.orientation);
      const geo = new T.BoxGeometry(d.x, d.y, d.z);
      const body = new T.MeshStandardMaterial({ color: '#2f9cff', roughness: 0.3, metalness: 0.12 });
      const top = new T.MeshStandardMaterial({ color: '#85d2ff', roughness: 0.28, metalness: 0.08 });
      const mesh = new T.Mesh(geo, [body, body, top, body, body, body]);
      mesh.position.copy(blockCenter(b));
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.userData.ownGeo = true;
      mesh.userData.ownMat = true;
      const edges = new T.LineSegments(
        new T.EdgesGeometry(geo),
        new T.LineBasicMaterial({ color: '#d8f2ff', transparent: true, opacity: 0.85 })
      );
      edges.userData.ownGeo = true;
      edges.userData.ownMat = true;
      mesh.add(edges);
      scene.add(mesh);
      return mesh;
    }

    function makeCubeMesh(q, idx) {
      const st = CUBE_STYLE[idx];
      const geo = new T.BoxGeometry(1, 1, 1);
      const body = new T.MeshStandardMaterial({ color: st.body, roughness: 0.3, metalness: 0.12, emissive: st.body, emissiveIntensity: 0 });
      const top = new T.MeshStandardMaterial({ color: st.top, roughness: 0.28, metalness: 0.08, emissive: st.top, emissiveIntensity: 0 });
      const mesh = new T.Mesh(geo, [body, body, top, body, body, body]);
      mesh.position.copy(cubeCenter(q));
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.userData.ownGeo = true;
      mesh.userData.ownMat = true;
      mesh.userData.cubeIndex = idx;
      const edgeMat = new T.LineBasicMaterial({ color: '#d8f2ff', transparent: true, opacity: 0.5 });
      const edges = new T.LineSegments(new T.EdgesGeometry(geo), edgeMat);
      edges.userData.ownGeo = true;
      edges.userData.ownMat = true;
      mesh.userData.edgeMat = edgeMat;
      mesh.add(edges);
      scene.add(mesh);
      return mesh;
    }

    function syncActiveLook() {
      if (!actors.cubes) return;
      actors.cubes.forEach((m, i) => {
        const on = i === actors.active;
        m.userData.edgeMat.color.set(on ? '#fff4b0' : '#9fb4cc');
        m.userData.edgeMat.opacity = on ? 1 : 0.35;
        m.userData.active = on;
        if (!on) m.material.forEach((mt) => { mt.emissiveIntensity = 0; });
      });
    }

    function setActors(state) {
      clearActors();
      if (state.block) {
        actors.block = makeBlockMesh(state.block);
      } else if (state.cubes) {
        actors.cubes = state.cubes.map((q, i) => makeCubeMesh(q, i));
        actors.active = state.active;
        syncActiveLook();
      }
    }

    function applyBridges(map, animate) {
      const jobs = [];
      for (const [id, list] of bridges) {
        const open = !!map[id];
        for (const obj of list) {
          const from = obj.group.position.y;
          const to = open ? 0 : BRIDGE_DOWN;
          if (obj.ghost) obj.ghost.visible = !open;
          if (!animate || from === to) { obj.group.position.y = to; obj.group.visible = open; continue; }
          obj.group.visible = true;
          jobs.push(tween(dur(450), (e) => { obj.group.position.y = from + (to - from) * e; })
            .then(() => { if (!open) obj.group.visible = false; }));
        }
      }
      return Promise.all(jobs);
    }

    function applyBroken(broken) {
      for (const [r, c] of broken || []) {
        const t = tiles.get(key(r, c));
        if (t) t.group.visible = false;
      }
    }

    /* ----- dat trang thai ngay lap tuc (khong hoat anh) ----- */
    function setState(state) {
      for (const t of tiles.values()) {
        if (t.kind === 'fragile') { t.group.visible = true; t.group.position.y = 0; t.group.rotation.set(0, 0, 0); }
      }
      applyBridges(state.bridges, false);
      applyBroken(state.broken);
      setActors(state);
    }

    /* ----- hoat anh ----- */
    function rollMesh(mesh, center, dims, dir, ms) {
      const pivotPos = center.clone();
      pivotPos.y = 0; // truc xoay o canh duoi sat mat san
      let axis, angle;
      if (dir === 'R') { pivotPos.x += dims.x / 2; axis = AXIS_Z; angle = -Math.PI / 2; }
      else if (dir === 'L') { pivotPos.x -= dims.x / 2; axis = AXIS_Z; angle = Math.PI / 2; }
      else if (dir === 'U') { pivotPos.z -= dims.z / 2; axis = AXIS_X; angle = -Math.PI / 2; }
      else { pivotPos.z += dims.z / 2; axis = AXIS_X; angle = Math.PI / 2; }

      const pivot = new T.Group();
      pivot.position.copy(pivotPos);
      scene.add(pivot);
      pivot.attach(mesh);
      return tween(ms, (e) => {
        pivot.quaternion.setFromAxisAngle(axis, angle * e);
      }).then(() => {
        scene.attach(mesh);           // giu nguyen vi tri the gioi sau khi xoay
        scene.remove(pivot);
        return mesh.position.clone();
      });
    }

    function tiltAxis(dir) {
      // truc nghieng khi roi theo huong di
      if (dir === 'R') return [AXIS_Z, -1];
      if (dir === 'L') return [AXIS_Z, 1];
      if (dir === 'U') return [AXIS_X, -1];
      return [AXIS_X, 1];
    }

    function fall(mesh, dir, tile) {
      const y0 = mesh.position.y;
      const [axis, sign] = tiltAxis(dir || 'D');
      const ty0 = tile ? tile.group.position.y : 0;
      return tween(dur(720), (e) => {
        mesh.position.y = y0 - 9 * e;
        mesh.quaternion.setFromAxisAngle(axis, sign * 0.9 * e);
        if (tile) {
          tile.group.position.y = ty0 - 9 * e;
          tile.group.rotation.z = 0.5 * e;
        }
      }, easeIn).then(() => {
        mesh.visible = false;
        if (tile) tile.group.visible = false;
      });
    }

    // cat bo phan nam duoi mat san -> khoi nhu chim vao lo toi
    function clipBelowFloor(mesh) {
      const plane = new T.Plane(new T.Vector3(0, 1, 0), 0);
      mesh.traverse((n) => {
        if (!n.material) return;
        (Array.isArray(n.material) ? n.material : [n.material]).forEach((m) => { m.clippingPlanes = [plane]; });
      });
    }

    function hop(mesh, to, ms) {
      const from = mesh.position.clone();
      return tween(ms, (e) => {
        mesh.position.lerpVectors(from, to, e);
        mesh.position.y = from.y + (to.y - from.y) * e + Math.sin(e * Math.PI) * 1.1;
      });
    }

    function pulse(meshes, ms) {
      return tween(ms, (e, k) => {
        const s = 1 + 0.12 * Math.sin(k * Math.PI);
        meshes.forEach((m) => {
          m.scale.setScalar(s);
          m.material.forEach((mt) => { mt.emissiveIntensity = 0.9 * Math.sin(k * Math.PI); });
        });
      }, (k) => k);
    }

    /* prev, next: trang thai JSON truoc/sau; dir: 'U'|'D'|'L'|'R'. Tra ve Promise khi xong. */
    async function animateMove(prev, dir, next) {
      // 1) lan
      let rolledPos = null;
      if (prev.block && actors.block) {
        rolledPos = await rollMesh(actors.block, blockCenter(prev.block), blockDims(prev.block.orientation), dir, dur(260));
      } else if (prev.cubes && actors.cubes) {
        const m = actors.cubes[prev.active];
        rolledPos = await rollMesh(m, cubeCenter(prev.cubes[prev.active]), { x: 1, y: 1, z: 1 }, dir, dur(220));
      }

      // 2) cau truot song song voi cac hieu ung sau
      const bridgeJob = applyBridges(next.bridges, true);

      const newlyBroken = (next.broken || []).filter(([r, c]) => !(prev.broken || []).some(([a, b]) => a === r && b === c));

      if (prev.block && next.cubes) {
        // cong tac split: khoi tach thanh 2 cube bay ve 2 diem
        const old = actors.block;
        scene.remove(old); disposeObject(old);
        actors.block = null;
        actors.cubes = next.cubes.map((q, i) => {
          const m = makeCubeMesh(q, i);
          m.position.set(rolledPos.x, 0.5, rolledPos.z);
          return m;
        });
        actors.active = next.active;
        await Promise.all(actors.cubes.map((m, i) => hop(m, cubeCenter(next.cubes[i]), dur(520))));
        syncActiveLook();
      } else if (prev.cubes && next.block) {
        // 2 cube ke nhau: ghep lai thanh khoi
        const keep = actors.cubes;
        keep.forEach((m, i) => { m.position.copy(cubeCenter(prev.cubes[i])); });
        const moved = prev.active;
        keep[moved].position.copy(rolledPos ? new T.Vector3(rolledPos.x, 0.5, rolledPos.z) : keep[moved].position);
        keep[moved].quaternion.identity();
        await pulse(keep, dur(260));
        setActors(next);
        const b = actors.block;
        await tween(dur(200), (e, k) => b.scale.setScalar(1 + 0.08 * Math.sin(k * Math.PI)), (k) => k);
        b.scale.setScalar(1);
      } else {
        setActors(next);
      }

      // 3) hau qua
      if (next.status === 'lost') {
        const target = actors.block || actors.cubes[next.active];
        let tile = null;
        if (next.reason === 'fragile' && newlyBroken.length) {
          tile = tiles.get(key(newlyBroken[0][0], newlyBroken[0][1])) || null;
        }
        await Promise.all([fall(target, dir, tile), bridgeJob]);
        return;
      }
      if (next.status === 'won' && actors.block) {
        const b = actors.block;
        const y0 = b.position.y;
        clipBelowFloor(b);
        await tween(dur(650), (e) => { b.position.y = y0 - 2.4 * e; }, easeIn);
        b.visible = false;
      }
      await bridgeJob;
    }

    /* doi cube dang dieu khien: chop sang cube moi */
    async function animateSwitch(next) {
      if (!actors.cubes) return;
      actors.active = next.active;
      syncActiveLook();
      await pulse([actors.cubes[next.active]], dur(220));
    }

    /* ----- vong lap ve ----- */
    function resize() {
      const w = Math.max(1, container.clientWidth);
      const h = Math.max(1, container.clientHeight);
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    new ResizeObserver(resize).observe(container);
    resize();

    renderer.setAnimationLoop((time) => {
      controls.update();
      if (actors.cubes) {
        const k = 0.35 + 0.25 * Math.sin(time / 180);
        const m = actors.cubes[actors.active];
        if (m && m.userData.active && m.visible) m.material.forEach((mt) => { mt.emissiveIntensity = k; });
      }
      renderer.render(scene, camera);
    });

    Object.assign(view, {
      loadLevel, setState, animateMove, animateSwitch,
      resetCamera: () => { if (level) frameCamera(); },
      get hasLevel() { return !!level; }
    });
    return view;
  }

  window.BloxorzScene = { create };
})();
