/* Bloxorz TV4 - Week 1 prototype
   JavaScript chi render giao dien va hoat anh.
   Luat va du lieu hien tai la mau de kiem thu; chua ket noi Python core.
*/
(() => {
  'use strict';

  if (!window.THREE) {
    document.getElementById('status').textContent = 'Lỗi: chưa tải được Three.js';
    throw new Error('Khong tim thay THREE. Kiem tra web/lib/three.min.js');
  }

  const TILE_SIZE = 1;
  const TILE_THICKNESS = 0.16;
  const ROLL_DURATION = 260;

  // Du lieu mau: row tang dan theo truc Z; cot tang dan theo truc X.
  const level = {
    rows: 7,
    cols: 7,
    floor: [
      [1,1],[1,2],[1,3],[1,4],
      [2,1],[2,2],[2,3],[2,4],[2,5],
      [3,1],[3,2],[3,3],[3,4],[3,5],
      [4,2],[4,3],[4,4],[4,5],
      [5,2],[5,3],[5,4],[5,5],
      [6,3],[6,4]
    ],
    start: { r: 2, c: 2, orientation: 'STANDING' },
    goal: { r: 6, c: 3 }
  };

  const floorSet = new Set(level.floor.map(([r,c]) => `${r},${c}`));
  const container = document.getElementById('game-container');
  const statusEl = document.getElementById('status');
  const orientationEl = document.getElementById('orientation');
  const moveCountEl = document.getElementById('moveCount');
  const anchorEl = document.getElementById('anchor');
  const restartBtn = document.getElementById('restartBtn');

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#111827');
  scene.fog = new THREE.Fog('#111827', 12, 28);

  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(7.5, 9, 10);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  let controls = null;
  if (THREE.OrbitControls) {
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(3, 0, 3);
    controls.minDistance = 5;
    controls.maxDistance = 18;
    controls.maxPolarAngle = Math.PI * 0.49;
  }

  scene.add(new THREE.HemisphereLight(0xc9e2ff, 0x273047, 2.0));
  const sun = new THREE.DirectionalLight(0xffffff, 2.4);
  sun.position.set(-5, 10, 7);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -10;
  sun.shadow.camera.right = 10;
  sun.shadow.camera.top = 10;
  sun.shadow.camera.bottom = -10;
  scene.add(sun);

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(200, 200),
    new THREE.MeshStandardMaterial({ color: '#0d1420', roughness: 1 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.14;
  ground.receiveShadow = true;
  scene.add(ground);

  const tileMaterial = new THREE.MeshStandardMaterial({ color: '#65748b', roughness: 0.78, metalness: 0.05 });
  const tileEdgeMaterial = new THREE.MeshStandardMaterial({ color: '#374357', roughness: 0.9 });
  const goalMaterial = new THREE.MeshStandardMaterial({ color: '#151b28', roughness: 0.92, metalness: 0.08 });
  const goalRingMaterial = new THREE.MeshStandardMaterial({ color: '#e9bb55', emissive: '#4b2f09', roughness: 0.45, metalness: 0.25 });
  const blockMaterial = new THREE.MeshStandardMaterial({ color: '#2f9cff', roughness: 0.3, metalness: 0.12 });
  const blockTopMaterial = new THREE.MeshStandardMaterial({ color: '#85d2ff', roughness: 0.28, metalness: 0.08 });

  const tileMeshes = new THREE.Group();
  scene.add(tileMeshes);
  let blockMesh = null;
  let state = copyState(level.start);
  let moveCount = 0;
  let isAnimating = false;
  let gameEnded = false;

  function copyState(s) {
    return { r: s.r, c: s.c, orientation: s.orientation };
  }

  function drawTiles() {
    for (const [r, c] of level.floor) {
      const isGoal = r === level.goal.r && c === level.goal.c;
      const tile = new THREE.Mesh(
        new THREE.BoxGeometry(TILE_SIZE * 0.96, TILE_THICKNESS, TILE_SIZE * 0.96),
        isGoal ? goalMaterial : tileMaterial
      );
      tile.position.set(c, -TILE_THICKNESS / 2, r);
      tile.receiveShadow = true;
      tile.castShadow = true;
      tile.userData.row = r;
      tile.userData.col = c;
      tileMeshes.add(tile);

      const edge = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(TILE_SIZE * 0.96, TILE_THICKNESS, TILE_SIZE * 0.96)),
        new THREE.LineBasicMaterial({ color: isGoal ? '#e9bb55' : '#a7b7ce', transparent: true, opacity: isGoal ? 0.95 : 0.28 })
      );
      edge.position.copy(tile.position);
      tileMeshes.add(edge);

      if (isGoal) {
        const ring = new THREE.Mesh(new THREE.TorusGeometry(0.29, 0.045, 10, 36), goalRingMaterial);
        ring.rotation.x = Math.PI / 2;
        ring.position.set(c, 0.015, r);
        ring.castShadow = true;
        tileMeshes.add(ring);
        const center = new THREE.Mesh(new THREE.CircleGeometry(0.22, 32), goalMaterial);
        center.rotation.x = -Math.PI / 2;
        center.position.set(c, 0.008, r);
        tileMeshes.add(center);
      }
    }
  }

  function occupiedCells(s) {
    if (s.orientation === 'STANDING') return [[s.r, s.c]];
    if (s.orientation === 'LYING_H') return [[s.r, s.c], [s.r, s.c + 1]];
    return [[s.r, s.c], [s.r + 1, s.c]];
  }

  function isValidState(s) {
    return occupiedCells(s).every(([r,c]) => floorSet.has(`${r},${c}`));
  }

  function nextState(s, direction) {
    const n = copyState(s);
    if (s.orientation === 'STANDING') {
      if (direction === 'U') { n.r -= 2; n.orientation = 'LYING_V'; }
      if (direction === 'D') { n.r += 1; n.orientation = 'LYING_V'; }
      if (direction === 'L') { n.c -= 2; n.orientation = 'LYING_H'; }
      if (direction === 'R') { n.c += 1; n.orientation = 'LYING_H'; }
    } else if (s.orientation === 'LYING_H') {
      if (direction === 'U') n.r -= 1;
      if (direction === 'D') n.r += 1;
      if (direction === 'L') { n.c -= 1; n.orientation = 'STANDING'; }
      if (direction === 'R') { n.c += 2; n.orientation = 'STANDING'; }
    } else {
      if (direction === 'U') { n.r -= 1; n.orientation = 'STANDING'; }
      if (direction === 'D') { n.r += 2; n.orientation = 'STANDING'; }
      if (direction === 'L') n.c -= 1;
      if (direction === 'R') n.c += 1;
    }
    return n;
  }

  function stateCenter(s) {
    if (s.orientation === 'STANDING') return new THREE.Vector3(s.c, 1, s.r);
    if (s.orientation === 'LYING_H') return new THREE.Vector3(s.c + 0.5, 0.5, s.r);
    return new THREE.Vector3(s.c, 0.5, s.r + 0.5);
  }

  function blockDimensions(s) {
    return {
      x: s.orientation === 'LYING_H' ? 2 : 1,
      y: s.orientation === 'STANDING' ? 2 : 1,
      z: s.orientation === 'LYING_V' ? 2 : 1
    };
  }

  function createBlock(s) {
    const dims = blockDimensions(s);
    const geometry = new THREE.BoxGeometry(dims.x, dims.y, dims.z);
    const mesh = new THREE.Mesh(geometry, [blockMaterial, blockMaterial, blockTopMaterial, blockMaterial, blockMaterial, blockMaterial]);
    mesh.position.copy(stateCenter(s));
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData.isBlock = true;
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry),
      new THREE.LineBasicMaterial({ color: '#d8f2ff', transparent: true, opacity: 0.85 })
    );
    mesh.add(edges);
    scene.add(mesh);
    return mesh;
  }

  function redrawBlock() {
    if (blockMesh) {
      scene.remove(blockMesh);
      blockMesh.geometry.dispose();
    }
    blockMesh = createBlock(state);
  }

  function updatePanel() {
    const names = { STANDING: 'Đứng', LYING_H: 'Nằm ngang', LYING_V: 'Nằm dọc' };
    orientationEl.textContent = names[state.orientation];
    moveCountEl.textContent = String(moveCount);
    anchorEl.textContent = `(${state.r}, ${state.c})`;
    if (!gameEnded) statusEl.textContent = 'Sẵn sàng';
  }

  function isGoal(s) {
    return s.orientation === 'STANDING' && s.r === level.goal.r && s.c === level.goal.c;
  }

  function roll(direction) {
    if (isAnimating || gameEnded) return;
    const target = nextState(state, direction);
    if (!isValidState(target)) {
      statusEl.textContent = 'Nước đi không hợp lệ';
      return;
    }
    animateRoll(state, target, direction);
  }

  function animateRoll(fromState, toState, direction) {
    if (!blockMesh) return;
    isAnimating = true;
    restartBtn.disabled = true;
    statusEl.textContent = 'Đang lăn…';

    const center = stateCenter(fromState);
    const dims = blockDimensions(fromState);
    const pivotPosition = center.clone();
    let axis;
    let angle;

    if (direction === 'R') {
      pivotPosition.x += dims.x / 2;
      axis = new THREE.Vector3(0, 0, 1);
      angle = -Math.PI / 2;
    } else if (direction === 'L') {
      pivotPosition.x -= dims.x / 2;
      axis = new THREE.Vector3(0, 0, 1);
      angle = Math.PI / 2;
    } else if (direction === 'U') {
      pivotPosition.z -= dims.z / 2;
      axis = new THREE.Vector3(1, 0, 0);
      angle = -Math.PI / 2;
    } else {
      pivotPosition.z += dims.z / 2;
      axis = new THREE.Vector3(1, 0, 0);
      angle = Math.PI / 2;
    }

    const pivot = new THREE.Group();
    pivot.position.copy(pivotPosition);
    scene.add(pivot);
    scene.remove(blockMesh);
    pivot.add(blockMesh);
    blockMesh.position.copy(center).sub(pivotPosition);

    const start = performance.now();
    function tick(now) {
      const raw = Math.min(1, (now - start) / ROLL_DURATION);
      const eased = raw * raw * (3 - 2 * raw);
      pivot.rotation.set(0, 0, 0);
      pivot.rotateOnAxis(axis, angle * eased);
      if (raw < 1) {
        requestAnimationFrame(tick);
      } else {
        scene.remove(pivot);
        state = copyState(toState);
        moveCount += 1;
        blockMesh = createBlock(state);
        isAnimating = false;
        restartBtn.disabled = false;
        if (isGoal(state)) {
          gameEnded = true;
          statusEl.textContent = 'Chiến thắng!';
        } else {
          statusEl.textContent = 'Sẵn sàng';
        }
        updatePanel();
      }
    }
    requestAnimationFrame(tick);
  }

  function restart() {
    if (isAnimating) return;
    state = copyState(level.start);
    moveCount = 0;
    gameEnded = false;
    redrawBlock();
    updatePanel();
  }

  function onKeyDown(event) {
    const key = event.key.toLowerCase();
    const map = { arrowup: 'U', w: 'U', arrowdown: 'D', s: 'D', arrowleft: 'L', a: 'L', arrowright: 'R', d: 'R' };
    const direction = map[key];
    if (!direction) return;
    event.preventDefault();
    roll(direction);
  }

  function resize() {
    const width = Math.max(1, container.clientWidth);
    const height = Math.max(1, container.clientHeight);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function frame() {
    requestAnimationFrame(frame);
    if (controls) controls.update();
    renderer.render(scene, camera);
  }

  drawTiles();
  redrawBlock();
  updatePanel();
  resize();
  window.addEventListener('resize', resize);
  window.addEventListener('keydown', onKeyDown);
  restartBtn.addEventListener('click', restart);
  frame();
})();
