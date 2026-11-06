// Extras for the coding walkthrough videos (w01, w02, w03), on top of lecture.js. Load after it.
(() => {
  const SVG = 'http://www.w3.org/2000/svg';
  const PY = /(#.*$)|("[^"]*"|f"[^"]*"|b"[^"]*")|\b(class|def|if|elif|else|raise|return|in|not|and|or|None|assert|from|import|pass|for|while|with|as|self|True|False)\b/g;
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const py = s => esc(s).replace(PY, (m, c, st, k) => c ? `<span class="cm">${c}</span>` : st ? `<span class="st">${st}</span>` : `<span class="kw">${k}</span>`);

  // a code scene: lines appear with on(a, b); hl([i...], 'hl' | 'new') highlights lines
  function Code(id, { caption, lines, size = 30, top = 230, width = 1780 }) {
    const s = document.createElement('section'); s.id = id; s.className = 'scene s-code'; document.body.append(s);
    const cap = document.createElement('div'); cap.className = 'caption'; s.append(cap);
    const box = document.createElement('div'); box.className = 'code'; s.append(box);
    box.style.cssText = `top:${top}px;width:${width}px;font-size:${size}px`;
    const L = lines.map(t => { const d = document.createElement('div'); d.className = 'ln'; d.innerHTML = py(t) || ' '; box.append(d); return d; });
    const api = {
      show: () => show(id),
      cap: (t, sub) => { cap.innerHTML = `${t}${sub ? `<small>${sub}</small>` : ''}`; },
      on: (a = 0, b = lines.length - 1) => { for (let i = a; i <= b; i++) L[i].classList.add('on'); },
      hl: (idx, cls = 'hl') => { L.forEach(l => l.classList.remove('hl', 'new')); idx.forEach(i => L[i].classList.add(cls)); },
      mark: (i, cls = 'new') => L[i].classList.add(cls),
    };
    if (caption) api.cap(...caption);
    return api;
  }

  // ---------------------------------------------------------------- picture on the left, code on the right
  // Split(id, {lines, size}) -> {d: Diagram 960 wide, step(lines, {from, note}), note(html), show()}
  // step() highlights code lines and draws a connector from a picture element to the first of them.
  function Split(id, { lines, size = 25, top = 62, left = 975, width = 925 }) {
    const s = document.createElement('section'); s.id = id; s.className = 'scene s-code s-split'; document.body.append(s);
    const d = new Diagram(s, 960, 1080);
    d.show = () => show(id);
    const box = document.createElement('div'); box.className = 'code on-all'; s.append(box);
    box.style.cssText = `top:${top}px;left:${left}px;width:${width}px;font-size:${size}px`;
    const L = lines.map(t => { const e = document.createElement('div'); e.className = 'ln on'; e.innerHTML = py(t) || ' '; box.append(e); return e; });
    const noteEl = document.createElement('div'); noteEl.className = 'sp-note';
    noteEl.style.cssText = `top:${top + lines.length * size * 1.42 + 52 + 22}px;left:${left}px;width:${width}px`;
    s.append(noteEl);
    const api = {
      d, L,
      show: () => show(id),
      note: html => { noteEl.innerHTML = html; },
      hl: idx => { L.forEach(l => l.classList.remove('hl', 'new', 'bad')); [].concat(idx).forEach(i => L[i].classList.add('hl')); },
      step(idx, { from, note, keep } = {}) {
        api.hl(idx);
        if (note != null) api.note(note);
        if (!keep) clearLinks();
        if (from != null) {
          const first = [].concat(idx)[0];
          connect(typeof from === 'string' ? d.N[from].g : from, L[first]);
        }
      },
    };
    return api;
  }

  // ---------------------------------------------------------------- connectors from a picture to a line of code
  let overlay = null;
  function layer() {
    if (!overlay) {
      overlay = document.createElementNS(SVG, 'svg');
      overlay.setAttribute('width', 1920); overlay.setAttribute('height', 1080);
      overlay.style.cssText = 'position:absolute;left:0;top:0;z-index:50;pointer-events:none';
      document.body.append(overlay);
    }
    return overlay;
  }
  function clearLinks() { if (overlay) overlay.innerHTML = ''; }
  function connect(a, b, color = '#d97706') {
    const g = layer();
    const r1 = a.getBoundingClientRect(), r2 = b.getBoundingClientRect();
    const x1 = r1.right, y1 = r1.top + r1.height / 2, x2 = r2.left, y2 = r2.top + r2.height / 2;
    const dx = Math.max(60, (x2 - x1) * .45);
    const p = document.createElementNS(SVG, 'path');
    p.setAttribute('d', `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`);
    p.setAttribute('fill', 'none'); p.setAttribute('stroke', color); p.setAttribute('stroke-width', 5);
    g.append(p);
    const len = p.getTotalLength();
    p.style.strokeDasharray = len; p.style.strokeDashoffset = len; p.style.transition = 'stroke-dashoffset .55s ease-out';
    setTimeout(() => { p.style.strokeDashoffset = 0; }, 30);
    [[x1, y1], [x2, y2]].forEach(([cx, cy]) => { const c = document.createElementNS(SVG, 'circle'); c.setAttribute('cx', cx); c.setAttribute('cy', cy); c.setAttribute('r', 9); c.setAttribute('fill', color); g.append(c); });
  }

  // ---------------------------------------------------------------- chapter bar along the top
  function Chapters(names) {
    const bar = document.createElement('div'); bar.className = 'chapbar';
    bar.innerHTML = names.map(n => `<span>${n}</span>`).join('');
    document.body.append(bar);
    const spans = [...bar.children];
    return { set(i) { bar.classList.add('on'); spans.forEach((s, j) => { s.classList.toggle('now', j === i); s.classList.toggle('past', j < i); }); } };
  }

  // a small figure on the title card, to the right of the words
  function titleFigure(kicker, h1Width = 1000) {
    const s = document.getElementById('title');
    s.querySelector('.kicker').textContent = kicker;
    s.querySelector('h1').style.cssText = `max-width:${h1Width}px;font-size:130px`;
    s.querySelector('.sub').style.cssText = `max-width:${h1Width}px;font-size:48px;margin-top:20px`;
    return new Diagram(s, 760, 1080, 1140);
  }

  // an svg element in any group of a Diagram
  function shape(parent, tag, attrs, text) {
    const e = document.createElementNS(SVG, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    parent.append(e);
    return e;
  }

  // a scene-owned block of html at absolute coordinates
  function block(parent, cls, x, y, html, w) {
    const d = document.createElement('div');
    d.className = cls; d.style.position = 'absolute'; d.style.left = x + 'px'; d.style.top = y + 'px';
    if (w) d.style.width = w + 'px';
    d.innerHTML = html;
    (parent.svg ? parent.svg.parentNode : parent).append(d);
    return d;
  }

  Object.assign(window, { Code, Split, Chapters, connect, clearLinks, py, esc, titleFigure, shape, block });
})();
