// Shared building blocks for the 1920x1080 lecture videos. Read README.md first.
// Every animation is timed with performance.now() (requestAnimationFrame timestamps lag in headless recording).
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const COLORS = { acc: '#2456c7', good: '#1a7f37', bad: '#cf222e', warn: '#bf8700', muted: '#5f6368' };
  const col = c => COLORS[c] || c || COLORS.acc;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const el = (tag, attrs, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.append(e);
    return e;
  };
  const div = (cls, parent, html) => {
    const d = document.createElement('div');
    if (cls) d.className = cls;
    if (html != null) d.innerHTML = html;
    if (parent) parent.append(d);
    return d;
  };
  const icon = (name, size, color) =>
    `<svg viewBox="0 0 24 24" class="ico" style="width:${size}px;height:${size}px;${color ? 'stroke:' + col(color) : ''}">${ICON[name] || ''}</svg>`;

  function section(id, cls) {
    let s = document.getElementById(id);
    if (!s) { s = document.createElement('section'); s.id = id; s.className = 'scene ' + (cls || ''); document.body.append(s); }
    return s;
  }
  function show(id) { document.querySelectorAll('.scene').forEach(s => s.classList.toggle('on', s.id === id)); }

  // ---------------------------------------------------------------- diagram
  class Diagram {
    constructor(parent, w, h, x0 = 0) {
      this.svg = el('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, class: 'dia' }, parent);
      if (x0) this.svg.style.cssText = `position:absolute;left:${x0}px;top:0`;
      this.bg = el('g', {}, this.svg); this.links = el('g', {}, this.svg);
      this.nodes = el('g', {}, this.svg); this.fx = el('g', {}, this.svg);
      this.N = {}; this.L = {};
    }
    // a node: key, center x/y, icon name, label, small label. opts: {tone, w, h, hidden}
    node(key, x, y, ic, label, sub = '', opts = {}) {
      const w = opts.w || 170, h = opts.h || (sub ? 140 : 124);
      const outer = el('g', { transform: `translate(${x - w / 2},${y - h / 2})` }, this.nodes);
      const g = el('g', { class: `node ${opts.tone || ''} ${opts.hidden ? 'pop' : ''}` }, outer);
      el('rect', { class: 'box', width: w, height: h, rx: 18 }, g);
      if (ic) { const i = el('g', { class: 'ico', transform: `translate(${w / 2 - 24},14) scale(2)` }, g); i.innerHTML = ICON[ic] || ''; }
      const t = el('text', { x: w / 2, y: ic ? 88 : h / 2 + 9 }, g); t.textContent = label;
      if (!ic) t.setAttribute('style', 'font-size:30px');
      let s = null;
      if (sub) { s = el('text', { x: w / 2, y: ic ? 116 : h / 2 + 40, class: 'sm' }, g); s.textContent = sub; }
      this.N[key] = { x, y, w, h, g, outer, label: t, sub: s };
      return this.N[key];
    }
    pop(key) { const n = this.N[key]; requestAnimationFrame(() => requestAnimationFrame(() => n.g.classList.add('in'))); }
    popAll(keys, gap = 300) { keys.forEach((k, i) => setTimeout(() => this.pop(k), i * gap)); }
    hide(key) { this.N[key].g.style.opacity = 0; }
    unhide(key) { this.N[key].g.style.opacity = 1; }
    tone(key, t) { const g = this.N[key].g; ['good', 'bad', 'warn', 'muted', 'hl'].forEach(c => g.classList.remove(c)); if (t) t.split(' ').forEach(c => g.classList.add(c)); }
    dim(keys, on = true) { keys.forEach(k => this.N[k] && this.N[k].g.classList.toggle('dim', on)); }
    rename(key, label, sub) { const n = this.N[key]; if (label != null) n.label.textContent = label; if (sub != null && n.sub) n.sub.textContent = sub; }
    // straight or curved connector between two nodes. opts: {dash, curve, tone, id}
    link(a, b, opts = {}) {
      const p = this.N[a], q = this.N[b];
      const mx = (p.x + q.x) / 2, my = (p.y + q.y) / 2 - (opts.curve || 0);
      const path = el('path', { d: `M${p.x},${p.y} Q${mx},${my} ${q.x},${q.y}`, class: `link ${opts.dash ? 'dash' : ''} ${opts.tone || ''}` }, this.links);
      this.L[opts.id || `${a}-${b}`] = path;
      return path;
    }
    linkTone(id, tone) { const l = this.L[id]; l.classList.remove('good', 'bad', 'acc', 'dim'); if (tone) l.classList.add(tone); }
    // move a dot from node a to node b. opts: {color, dur, curve, r, label}
    send(a, b, opts = {}) {
      const p = this.N[a] || a, q = this.N[b] || b;
      const dur = opts.dur || 900, r = opts.r || 11;
      return new Promise(res => {
        const g = el('g', {}, this.fx);
        el('circle', { r, fill: col(opts.color) }, g);
        if (opts.label) { const t = el('text', { y: -r - 8, class: 'tag', fill: col(opts.color), style: 'font-size:22px' }, g); t.textContent = opts.label; }
        const mx = (p.x + q.x) / 2, my = (p.y + q.y) / 2 - (opts.curve || 0), t0 = performance.now();
        const step = () => {
          const k = Math.min(1, (performance.now() - t0) / dur), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
          const x = (1 - e) ** 2 * p.x + 2 * (1 - e) * e * mx + e * e * q.x, y = (1 - e) ** 2 * p.y + 2 * (1 - e) * e * my + e * e * q.y;
          g.setAttribute('transform', `translate(${x},${y})`);
          if (k < 1) requestAnimationFrame(step); else { g.remove(); res(); }
        };
        step();
      });
    }
    // send along a path of node keys, one hop after another
    async flow(keys, opts = {}) { for (let i = 0; i < keys.length - 1; i++) await this.send(keys[i], keys[i + 1], opts); }
    // keep sending dots from a to b every `every` ms until the returned stop() is called
    stream(a, b, opts = {}) {
      const every = opts.every || 300;
      const id = setInterval(() => { const bb = Array.isArray(b) ? b[Math.floor(Math.random() * b.length)] : b; this.send(a, bb, opts); if (opts.onSend) opts.onSend(); }, every);
      return () => clearInterval(id);
    }
    // a word that floats up from a node and fades
    tag(key, text, color = 'bad', dy = -90) {
      const n = this.N[key];
      const t = el('text', { x: n.x, y: n.y + dy, class: 'tag', fill: col(color), style: 'font-size:32px' }, this.fx);
      t.textContent = text;
      t.animate([{ transform: 'translateY(0)', opacity: 1 }, { transform: 'translateY(-50px)', opacity: 0 }], { duration: 1600, easing: 'ease-out', fill: 'forwards' });
      setTimeout(() => t.remove(), 1700);
    }
    // a pill that stays above (or below) a node until unbadge()
    badge(key, text, color = 'good', where = 'top') {
      this.unbadge(key);
      const n = this.N[key], w = Math.max(110, text.length * 14 + 30);
      const y = where === 'top' ? n.y - n.h / 2 - 30 : n.y + n.h / 2 + 30;
      const g = el('g', { transform: `translate(${n.x - w / 2},${y - 22})` }, this.fx);
      el('rect', { width: w, height: 44, rx: 22, fill: col(color) }, g);
      const t = el('text', { x: w / 2, y: 31, class: 'tag', fill: '#fff', style: 'font-size:24px' }, g); t.textContent = text;
      n.badge = g;
    }
    unbadge(key) { const n = this.N[key]; if (n.badge) { n.badge.remove(); n.badge = null; } }
    // free text anywhere. opts: {color, size, anchor, weight}
    text(x, y, str, opts = {}) {
      const t = el('text', { x, y, class: 'lbl', fill: col(opts.color || 'fg'), style: `font-size:${opts.size || 30}px;text-anchor:${opts.anchor || 'middle'};font-weight:${opts.weight || 700}` }, this.fx);
      if (!opts.color) t.setAttribute('fill', '#1d1d1f');
      t.textContent = str; return t;
    }
    // a load bar under a node: value 0..1, colored by level, with a word
    meter(key, value) {
      const n = this.N[key];
      if (!n.meter) {
        const g = el('g', { transform: `translate(${n.x - 120},${n.y + n.h / 2 + 18})` }, this.fx);
        el('rect', { width: 240, height: 20, rx: 10, fill: '#e3e0d8' }, g);
        const bar = el('rect', { width: 0, height: 20, rx: 10, fill: COLORS.good, style: 'transition: width .4s, fill .4s' }, g);
        const t = el('text', { x: 120, y: 52, class: 'tag', fill: COLORS.muted, style: 'font-size:22px' }, g);
        n.meter = { bar, t, v: 0 };
      }
      const v = Math.max(0, Math.min(1, value)); n.meter.v = v;
      n.meter.bar.setAttribute('width', 240 * v);
      n.meter.bar.setAttribute('fill', v > .75 ? COLORS.bad : v > .4 ? COLORS.warn : COLORS.good);
      n.meter.t.textContent = v > .75 ? 'overloaded' : v > .4 ? 'busy' : 'calm';
    }
    bump(key, d) { const n = this.N[key]; this.meter(key, (n.meter ? n.meter.v : 0) + d); }
    // a countdown ring around a node; resolves when it runs out
    ring(key, ms, color = 'warn') {
      const n = this.N[key], R = Math.max(n.w, n.h) / 2 + 22, C = 2 * Math.PI * R;
      const c = el('circle', { cx: n.x, cy: n.y, r: R, fill: 'none', stroke: col(color), 'stroke-width': 10, 'stroke-dasharray': C, 'stroke-dashoffset': 0, transform: `rotate(-90 ${n.x} ${n.y})` }, this.fx);
      c.animate([{ strokeDashoffset: 0 }, { strokeDashoffset: C }], { duration: ms, fill: 'forwards', easing: 'linear' });
      return sleep(ms).then(() => c);
    }
    // a dashed box around a set of nodes, with a title
    group(keys, title, pad = 30) {
      const ns = keys.map(k => this.N[k]);
      const x1 = Math.min(...ns.map(n => n.x - n.w / 2)) - pad, x2 = Math.max(...ns.map(n => n.x + n.w / 2)) + pad;
      const y1 = Math.min(...ns.map(n => n.y - n.h / 2)) - pad - 34, y2 = Math.max(...ns.map(n => n.y + n.h / 2)) + pad;
      const g = el('g', { class: 'group' }, this.bg);
      el('rect', { x: x1, y: y1, width: x2 - x1, height: y2 - y1, rx: 24 }, g);
      el('text', { x: (x1 + x2) / 2, y: y1 + 30 }, g).textContent = title;
      return g;
    }
    // a queue drawn as slots that fill up: queue(key, x, y, slots), then fill(key, n)
    queue(key, x, y, slots = 8, label = 'Queue') {
      const w = slots * 46 + 20, h = 90;
      const outer = el('g', { transform: `translate(${x - w / 2},${y - h / 2})` }, this.nodes);
      const g = el('g', { class: 'node' }, outer);
      el('rect', { class: 'box', width: w, height: h, rx: 16 }, g);
      const cells = [];
      for (let i = 0; i < slots; i++) cells.push(el('rect', { x: 14 + i * 46, y: 16, width: 38, height: 58, rx: 8, fill: '#e3e0d8', style: 'transition: fill .3s' }, g));
      const t = el('text', { x: w / 2, y: h + 34 }, g); t.textContent = label;
      this.N[key] = { x, y, w, h, g, outer, label: t, cells, n: 0 };
      return this.N[key];
    }
    fill(key, n, color = 'acc') {
      const q = this.N[key]; q.n = Math.max(0, Math.min(q.cells.length, n));
      q.cells.forEach((c, i) => c.setAttribute('fill', i < q.n ? col(q.n === q.cells.length ? 'bad' : color) : '#e3e0d8'));
    }
  }

  function makeStage(id, opts = {}) {
    const s = section(id, 'stage');
    if (opts.head) div('', s).outerHTML = `<h2 class="head">${opts.head}</h2>`;
    const d = new Diagram(s, 1920, 1080);
    const cap = div('caption', s);
    d.cap = (title, sub) => { cap.innerHTML = title ? `${title}${sub ? `<small>${sub}</small>` : ''}` : ''; };
    if (opts.caption) d.cap(...opts.caption);
    if (opts.regions) opts.regions.forEach(([x, y, rx, ry, name, lx, ly]) => {
      el('ellipse', { class: 'region', cx: x, cy: y, rx, ry }, d.bg);
      if (name) { const t = el('text', { x: lx || x, y: ly || y - ry + 40, class: 'lbl', fill: '#9aa0a6', style: 'font-size:26px;letter-spacing:.08em' }, d.bg); t.textContent = name; }
    });
    d.show = () => show(id);
    return d;
  }

  // ---------------------------------------------------------------- scenes
  const API = {
    sleep, show, icon, Diagram,

    // title card: {num, name, sub, pills}. Visible at load.
    Title({ num, name, sub, phase, pills = [] }) {
      const s = section('title', 's-title on');
      s.innerHTML = `<div class="kicker">Component ${num} of 23 · ${phase}</div><h1>${name}</h1><div class="sub">${sub}</div>
        <div class="row">${pills.map(p => `<span class="pill">${p}</span>`).join('')}</div>`;
    },

    // definition: left text (html with <b>), optional extra pill row, right-hand Diagram (960 wide, coordinates 0..960).
    // Returns {d, more()} where more() reveals the extra row. Call d.show() or show('def') first.
    Define(id, { html, extra }) {
      const s = section(id, 's-def');
      const t = div('def-text', s, `<div class="kicker">What it is</div><p>${html}</p>`);
      let ex = null;
      if (extra) ex = div('extra', t, `<span>${extra.label}</span>${(extra.pills || []).map(p => `<em>${p}</em>`).join('')}`);
      const d = new Diagram(s, 960, 1080, 960);
      d.show = () => show(id);
      return { d, more: () => ex && ex.classList.add('on'), show: () => show(id) };
    },

    // a full-screen diagram scene with an optional caption box and region blobs.
    Stage: makeStage,

    // the standard small-business system, with some parts highlighted and the rest dimmed.
    // keys: browser dns cdn lb api cache db queue worker pay jobs storage sms
    System(id, { highlight = [], caption, only, labels = {} } = {}) {
      const d = makeStage(id, { caption: caption || ['Where it fits', 'The whole system, and where this part sits'] });
      const P = {
        browser: [150, 560, 'browser', 'Browser', ''], dns: [420, 290, 'signpost', 'DNS', ''], cdn: [420, 560, 'globe', 'CDN', ''],
        lb: [700, 560, 'split', 'Load balancer', ''], api: [980, 560, 'server', 'API', '2+ copies'],
        cache: [1270, 330, 'bolt', 'Cache', 'Redis'], db: [1270, 560, 'db', 'Postgres', ''], queue: [1270, 800, 'queue', 'Queue', ''],
        worker: [1560, 800, 'gear', 'Workers', ''], pay: [1560, 330, 'card', 'Stripe', 'payments'], jobs: [1560, 560, 'clock', 'Jobs', 'sweeper'],
        storage: [700, 860, 'bucket', 'Object storage', ''], sms: [1810, 800, 'chat', 'SMS, email', ''],
      };
      const keys = only || Object.keys(P);
      keys.forEach(k => { const [x, y, ic, l, s] = P[k]; const [L2, S2] = labels[k] || [l, s]; d.node(k, x, y, ic, L2, S2, { w: 180 }); });
      const E = [['browser', 'dns', 1], ['browser', 'cdn'], ['cdn', 'lb'], ['lb', 'api'], ['api', 'cache'], ['api', 'db'], ['api', 'queue'],
        ['queue', 'worker'], ['api', 'pay'], ['jobs', 'db'], ['worker', 'sms'], ['browser', 'storage', 1], ['storage', 'cdn', 1]];
      E.forEach(([a, b, dash]) => { if (d.N[a] && d.N[b]) d.link(a, b, { dash }); });
      if (highlight.length) {
        keys.forEach(k => { if (!highlight.includes(k)) d.dim([k]); else d.tone(k, 'hl'); });
        Object.entries(d.L).forEach(([id, l]) => { const [a, b] = id.split('-'); if (!(highlight.includes(a) || highlight.includes(b))) l.classList.add('dim'); });
      }
      return d;
    },

    // sort chips into two bins. items: [[html, 'l' | 'r'], ...]. Returns {left(step), right(step)}.
    Sort(id, { head, left, right, rightBad = false, items }) {
      const s = section(id, 's-sort');
      s.innerHTML = `<h2 class="head">${head}</h2><div class="bin l"><h3>${left}</h3></div><div class="bin r ${rightBad ? 'bad' : ''}"><h3>${right}</h3></div><div class="chips"></div>`;
      const box = s.querySelector('.chips');
      const chips = items.map(([t]) => { const c = div('chip', box, t); c.style.left = '880px'; c.style.top = '1120px'; return c; });
      const go = (side, step = 650) => {
        let j = 0;
        items.forEach(([, k], i) => {
          if (k !== side) return;
          const n = j++;
          setTimeout(() => {
            const c = chips[i]; c.classList.add(k);
            c.style.left = (k === 'l' ? 150 : 1170) + (n % 2) * 350 + 'px';
            c.style.top = 320 + Math.floor(n / 2) * 105 + 'px';
          }, 300 + n * step);
        });
      };
      return { show: () => show(id), left: s2 => go('l', s2), right: s2 => go('r', s2) };
    },

    // a big equation: parts like {n: 50000, fmt: v => v.toLocaleString(), label: 'visitors'} or {op: '×'}.
    // run() counts each number up in turn; note(text) shows a line under it.
    Counters(id, { head, parts }) {
      const s = section(id, 's-count');
      s.innerHTML = `<h2 class="head">${head}</h2><div class="eq"></div><div class="eq-note"></div>`;
      const eq = s.querySelector('.eq');
      const nums = [];
      parts.forEach(p => {
        if (p.op) { div('op', eq, p.op); return; }
        const b = div('big ' + (p.cls || ''), eq, `<b>${p.static || 0}</b><span>${p.label || ''}</span>`);
        if (!p.static) nums.push({ p, b: b.querySelector('b') });
      });
      const fmt = p => p.fmt || (v => v.toLocaleString());
      const count = (b, p, ms) => new Promise(res => {
        const t0 = performance.now();
        const step = () => { const k = Math.min(1, (performance.now() - t0) / ms); b.textContent = fmt(p)(Math.round(p.n * k)); if (k < 1) requestAnimationFrame(step); else res(); };
        step();
        setTimeout(() => { b.textContent = fmt(p)(p.n); res(); }, ms + 60);
      });
      return {
        show: () => show(id),
        async run(ms = 1600, gap = 900) { for (const { p, b } of nums) { await count(b, p, ms); await sleep(gap); } },
        note(t) { const n = s.querySelector('.eq-note'); n.innerHTML = t; n.classList.add('on'); },
      };
    },

    // bar charts. charts: [{title, bars: [{label, value, color}], limit: {value, label}}], max = value of full height.
    // grow(i) animates chart i. Values are in the same unit as max.
    Bars(id, { head, charts, max }) {
      const s = section(id, 's-bars');
      s.innerHTML = `<h2 class="head">${head}</h2>`;
      const H = 560, refs = [];
      charts.forEach((c, ci) => {
        const ch = div('chart', s, `<h3>${c.title}</h3>`);
        ch.style.left = (charts.length === 1 ? 580 : 110 + ci * 940) + 'px';
        const n = c.bars.length, bw = 220, gap = 60, start = (760 - (n * bw + (n - 1) * gap)) / 2;
        const bars = c.bars.map((b, i) => {
          const x = start + i * (bw + gap);
          const bar = div('bar', ch, `<div class="v">${b.text || b.value}</div>`);
          bar.style.left = x + 'px'; bar.style.background = col(b.color || 'acc');
          const l = div('bar-l', ch, b.label); l.style.left = (x - 20) + 'px';
          return { bar, h: Math.max(6, H * b.value / max), over: b.over };
        });
        div('axis', ch);
        if (c.limit) { const lim = div('limit', ch, `<span>${c.limit.label}</span>`); lim.style.bottom = (124 + H * c.limit.value / max) + 'px'; }
        refs.push(bars);
      });
      return {
        show: () => show(id),
        async grow(i, stagger = 700) { for (const b of refs[i]) { b.bar.style.height = b.h + 'px'; if (b.over) setTimeout(() => b.bar.classList.add('over'), 1600); await sleep(stagger); } },
      };
    },

    // cards revealed one at a time. items: [{icon, color, title, text}]. reveal(i).
    Cards(id, { head, items, cols }) {
      const s = section(id, 's-cards');
      s.innerHTML = `<h2 class="head">${head}</h2><div class="cards" style="grid-template-columns:repeat(${cols || items.length},1fr)"></div>`;
      const box = s.querySelector('.cards');
      const cs = items.map(it => div('card', box, `${icon(it.icon || 'check', 90, it.color)}<b>${it.title}</b>${it.text || ''}`));
      return { show: () => show(id), reveal: i => cs[i].classList.add('in') };
    },

    // a numbered list panel whose items light up one by one: panel.on(i)
    Panel(parent, { x, y, w, title, items }) {
      const p = div('panel', parent.svg ? parent.svg.parentNode : parent, `${title ? `<h3>${title}</h3>` : ''}<ol>${items.map(i => `<li>${i}</li>`).join('')}</ol>`);
      p.style.left = x + 'px'; p.style.top = y + 'px'; p.style.width = w + 'px';
      const lis = p.querySelectorAll('li');
      return { on: i => lis[i].classList.add('on'), el: p };
    },

    // the closing interview line
    Say(id, text) {
      const s = section(id, 's-say');
      s.innerHTML = `<div class="kicker">In the interview, say</div><div class="bubble">"${text}"</div>`;
      return { show: () => show(id) };
    },
  };
  Object.assign(window, API);
})();
