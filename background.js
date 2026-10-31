(function () {
    "use strict";

    if (typeof THREE === "undefined") {
        console.warn("[background.js] Không tìm thấy Three.js — bỏ qua hiệu ứng nền.");
        return;
    }

    const canvas = document.getElementById("bg-canvas-3d");
    if (!canvas) {
        console.warn("[background.js] Không tìm thấy #bg-canvas-3d — bỏ qua hiệu ứng nền.");
        return;
    }

    const GRID_COLS = 50;
    const GRID_ROWS = 30;
    const GRID_SPACING = 40;
    const WAVE_SPEED = 0.03;

    const COLOR_NORMAL_A = new THREE.Color(0x38bdf8);
    const COLOR_NORMAL_B = new THREE.Color(0x818cf8);
    const COLOR_WARNING_1 = new THREE.Color(0xef4444);
    const COLOR_WARNING_2 = new THREE.Color(0xf97316);
    const COLOR_WARNING_3 = new THREE.Color(0xb91c1c);

    let scene, camera, renderer, particles, grid;
    let waveTime = 0;
    let mouseX = 0, mouseY = 0;
    let isWarning = false;

    function init() {
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x060913, 0.0015);

        camera = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / window.innerHeight,
            1,
            10000
        );
        camera.position.set(0, 300, 500);
        camera.lookAt(0, 0, 0);

        renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        buildParticleField();

        document.addEventListener("mousemove", onMouseMove);
        window.addEventListener("resize", onResize);

        animate();
    }

    function buildParticleField() {
        if (particles) scene.remove(particles);
        if (grid) scene.remove(grid);

        const total = GRID_COLS * GRID_ROWS;
        const positions = new Float32Array(total * 3);
        const colors = new Float32Array(total * 3);

        let i = 0;
        for (let ix = 0; ix < GRID_COLS; ix++) {
            const color = pickColumnColor(ix);
            for (let iy = 0; iy < GRID_ROWS; iy++) {
                positions[i] = ix * GRID_SPACING - 1000;
                positions[i + 1] = 0;
                positions[i + 2] = iy * GRID_SPACING - 600;
                colors[i] = color.r;
                colors[i + 1] = color.g;
                colors[i + 2] = color.b;
                i += 3;
            }
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 5,
            vertexColors: true,
            transparent: true,
            opacity: 0.9,
            blending: THREE.AdditiveBlending
        });

        particles = new THREE.Points(geometry, material);
        scene.add(particles);

        const gridCenterColor = isWarning ? 0xef4444 : 0x818cf8;
        const gridLineColor = isWarning ? 0x7f1d1d : 0x1e293b;
        grid = new THREE.GridHelper(2000, 40, gridCenterColor, gridLineColor);
        grid.position.y = -100;
        scene.add(grid);
    }

    function pickColumnColor(ix) {
        if (!isWarning) {
            return ix % 2 === 0 ? COLOR_NORMAL_A : COLOR_NORMAL_B;
        }
        const m = ix % 3;
        if (m === 0) return COLOR_WARNING_1;
        if (m === 1) return COLOR_WARNING_2;
        return COLOR_WARNING_3;
    }

    function onMouseMove(e) {
        mouseX = (e.clientX - window.innerWidth / 2) * 0.2;
        mouseY = (e.clientY - window.innerHeight / 2) * 0.2;
    }

    function onResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function animate() {
        requestAnimationFrame(animate);
        waveTime += WAVE_SPEED;

        camera.position.x += (mouseX - camera.position.x) * 0.05;
        camera.position.y += (-mouseY + 300 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);

        const positions = particles.geometry.attributes.position.array;
        let i = 0;
        for (let ix = 0; ix < GRID_COLS; ix++) {
            for (let iy = 0; iy < GRID_ROWS; iy++) {
                positions[i + 1] =
                    Math.sin((ix + waveTime) * 0.3) * 30 +
                    Math.sin((iy + waveTime) * 0.5) * 30;
                i += 3;
            }
        }
        particles.geometry.attributes.position.needsUpdate = true;

        renderer.render(scene, camera);
    }

    function setWarning(state) {
        const next = Boolean(state);
        if (next === isWarning) return;
        isWarning = next;
        buildParticleField();
    }

    window.RaiBackground = { setWarning: setWarning };

    init();
})();