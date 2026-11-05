// The little animated week on the home page: classes drop into a grid, two of
// them overlap and turn red, one moves to a free time, and it ends on
// "No overlaps". Plays once when it scrolls into view; Replay runs it again.
// With reduced motion on, the finished week shows right away.

const NS = "http://www.w3.org/2000/svg";
const W = 520, H = 330;
const GX = 44, GY = 34, COL = 92, ROW = 27, START = 8, HOURS = 10;
const colX = (d) => GX + d * COL;
const timeY = (h) => GY + (h - START) * ROW;

// day 0 = Monday. Entries with the same key belong to one class.
const BLOCKS = [
  { key: "a", day: 0, s: 9, e: 10.25, label: "CS 150", c: 0 },
  { key: "a", day: 2, s: 9, e: 10.25, label: "CS 150", c: 0 },
  { key: "b", day: 1, s: 11, e: 12.25, label: "MATH 150", c: 1 },
  { key: "b", day: 3, s: 11, e: 12.25, label: "MATH 150", c: 1 },
  { key: "c", day: 4, s: 13, e: 15.5, label: "BIOL 100L", c: 2 },
  { key: "d", day: 0, s: 9.5, e: 10.75, label: "PSY 101", c: 3, moveTo: { day: 1, s: 14 } },
  { key: "d", day: 2, s: 9.5, e: 10.75, label: "PSY 101", c: 3, moveTo: { day: 3, s: 14 } },
];
const ORDER = ["a", "b", "c", "d"];
const DURATION = 5000;

const clamp = (v) => Math.max(0, Math.min(1, v));
const seg = (p, a, b) => clamp((p - a) / (b - a));
const ease = (t) => 1 - Math.pow(1 - t, 3);

function svg(tag, attrs = {}, text) {
  const node = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, String(v));
  if (text) node.textContent = text;
  return node;
}

function build() {
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-labelledby": "hero-svg-title" });
  root.append(svg("title", { id: "hero-svg-title" },
    "A week of classes fills in. PSY 101 overlaps CS 150, moves to a free time, and the week ends with no overlaps."));
  const grid = svg("g", { class: "h-grid" });
  for (let d = 0; d <= 5; d++) grid.append(svg("line", { class: "h-line", x1: colX(d), y1: GY, x2: colX(d), y2: GY + ROW * HOURS }));
  for (let h = 0; h <= HOURS; h++) grid.append(svg("line", { class: "h-line", x1: GX, y1: GY + h * ROW, x2: GX + COL * 5, y2: GY + h * ROW }));
  ["Mon", "Tue", "Wed", "Thu", "Fri"].forEach((d, i) => grid.append(svg("text", { class: "h-label", x: colX(i) + COL / 2, y: GY - 12, "text-anchor": "middle" }, d)));
  for (let h = 1; h < HOURS; h += 2) {
    const hr = START + h;
    grid.append(svg("text", { class: "h-label", x: GX - 8, y: timeY(hr) + 4, "text-anchor": "end" }, `${((hr + 11) % 12) + 1}${hr < 12 ? "a" : "p"}`));
  }
  const blocks = BLOCKS.map((b) => {
    const g = svg("g", { class: `h-blk sub-${b.c}` });
    g.append(svg("rect", { x: colX(b.day) + 4, y: timeY(b.s) + 2, width: COL - 8, height: (b.e - b.s) * ROW - 4, rx: 7 }));
    g.append(svg("text", { x: colX(b.day) + 11, y: timeY(b.s) + 18 }, b.label));
    return g;
  });
  const cx = GX + COL * 5 - 26, cy = GY + ROW * HOURS - 24;
  const done = svg("g", { class: "h-done" });
  done.append(svg("circle", { cx, cy, r: 17 }), svg("path", { d: `M ${cx - 7} ${cy + 1} l 5 5 l 10 -11` }),
    svg("text", { x: cx - 26, y: cy + 5, "text-anchor": "end" }, "No overlaps"));
  root.append(grid, ...blocks, done);
  return { root, grid, blocks, done };
}

export function initHero(stage, caption, replay) {
  if (!stage) return;
  const { root, grid, blocks, done } = build();
  stage.append(root);

  function paint(p) {
    grid.style.opacity = String(seg(p, 0, 0.12));
    const clash = p >= 0.48 && p < 0.7;
    blocks.forEach((g, i) => {
      const b = BLOCKS[i];
      const k = ORDER.indexOf(b.key);
      const t = ease(seg(p, 0.12 + k * 0.08, 0.24 + k * 0.08));
      let dx = 0, dy = -18 * (1 - t);
      if (b.moveTo) {
        const m = ease(seg(p, 0.7, 0.84));
        dx += (colX(b.moveTo.day) - colX(b.day)) * m;
        dy += (timeY(b.moveTo.s) - timeY(b.s)) * m;
      }
      g.setAttribute("transform", `translate(${dx} ${dy})`);
      g.style.opacity = String(t);
      g.classList.toggle("clash", clash && (b.key === "a" || b.key === "d"));
    });
    done.style.opacity = String(seg(p, 0.86, 0.96));
    if (caption) {
      const [text, state] = p < 0.45 ? ["Adding classes…", ""] : p < 0.7 ? ["PSY 101 overlaps CS 150", "bad"]
        : p < 0.86 ? ["Moving PSY 101 to a free time…", ""] : ["All 4 classes fit", "good"];
      if (caption.textContent !== text) caption.textContent = text;
      caption.dataset.state = state;
    }
  }

  let frame = 0;
  function play() {
    cancelAnimationFrame(frame);
    const t0 = performance.now();
    const step = (now) => {
      const p = clamp((now - t0) / DURATION);
      paint(p);
      if (p < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
  }

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !("IntersectionObserver" in window)) {
    paint(1);
  } else {
    paint(0);
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { io.disconnect(); play(); }
    }, { threshold: 0.4 });
    io.observe(stage);
  }
  replay?.addEventListener("click", () => (reduce ? paint(1) : play()));
}
