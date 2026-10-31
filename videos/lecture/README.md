# Lecture videos: how to make one

One narrated, animated video per core component (cards.py, 23 of them), 1920x1080, **under 3:00**.
The viewer is an applied scientist preparing for a system design interview: smart, new to the engineering side.
The video should feel like a short lecture from a good teacher, not someone reading bullet points.

References: `c01/` (CDN, hand-built) and `c02/` (load balancer, built with `lib/`). Copy c02's structure.

## Structure (every video, in this order)

1. **Title** (`Title(...)`, visible at load). Narration: "Component N: the X." then a ~0.9 s pause.
2. **Definition first** (`Define(...)`). Say plainly what it IS (what kind of thing: a server, a database feature,
   a pattern, a setting, a practice) and what it does, in one or two sentences. Optionally a second step (`more()`)
   with "you rent it / it's built into X" or a key fact. The right-hand diagram animates the definition.
3. **The problem it solves** (a `Stage`): show what goes wrong without it, with motion (requests piling up, a crash,
   a double charge...).
4. **How it works** (a `Stage`, 2 to 4 steps): the mechanism, animated step by step. Introduce the key terms here.
5. **What you use it for** (`Cards` or `Sort`): 2 to 3 use cases, or what belongs vs doesn't.
6. **A real scenario with numbers** (`Stage`, `Counters` and/or `Bars`): use the card's scenario from `cards.py`
   (same businesses: pizza shop, tire shop, print shop, electronics sale, bike shop...). Show without vs with.
7. **Where it fits** (`System`, highlight the relevant boxes, animate a request with `flow`).
8. **Trade-offs / gotchas** (`Cards`, revealed one per sentence; 2 cards is plenty).
9. **The interview line** (`Say`): the card's `say` line.

## Narration rules

- Lecture voice: explain, connect ideas ("So...", "Here's the catch", "Why does that matter?"). Short sentences.
- **Define before anything else.** Define every term the first time it's used (TTL, idempotent, replica...).
- **Pauses**: every cue has `post_ms`. Use ~700 ms between linked sentences, 1000 to 1300 ms after a key idea or
  before a new scene. Never run three ideas together without a pause.
- One cue = one sentence or two, and **one visual step**: the animation for a sentence starts with that sentence.
  Split long scenes into steps (S3, S3b, S3c) rather than timing animations with long sleeps.
- Numbers on screen and in speech must match. Write numbers for the ear when it helps ("ninety-five percent").
- No em dashes anywhere. No company or employer names other than the vendors already on the cards
  (Stripe, Cloudflare, AWS...). Don't use these scenarios: a bakery on TV, a 2,000-seat ticket drop, a limited
  product preorder, live TV voting, a model launch causing eval jobs.
- Facts must be correct. When unsure, say less.
- **Runtime**: `python videos/lecture/record.py cNN --audio` prints an estimate. It must say OK (<= 178 s).
  Typical budget: ~340 to 380 words and ~18 to 22 s of pauses. Trim words, not pauses.

## cues.json

Copy c02/cues.json's top-level fields (voice, rate +6%, load_ms, gap_ms, tail_ms) and pronounce what's needed
(acronyms as letters: "CDN": "C D N"; "SQL": "sequel"; "Redis": "reddis"; "p95": "p ninety-five"...).
Each cue: `{"say": ..., "post_ms": ..., "do": "js:setTimeout(S3, 0)", "settle_ms": 350}`; the first cue (title) has no `do`.
Always `js:setTimeout(Fn, 0)`, never `js:Fn()` (the recorder would wait for the animation before speaking).
Also write `SCRIPT.md` (numbered lines, `*(pause)*` after cues with post_ms >= 1000).

## Library (lib/lecture.js), all globals

Scenes (each returns an object with `.show()`):
- `Title({num, name, sub, phase, pills})`
- `Define(id, {html, extra: {label, pills}})` -> `{d, more(), show()}`; `d` is a Diagram 960 wide (x 0..960, y 0..1080).
- `Stage(id, {caption: [title, sub], regions})` -> Diagram 1920x1080 with `.cap(title, sub)`.
- `System(id, {highlight: [...keys], caption, only: [...keys], labels: {key: [label, sub]}})` -> Diagram with nodes
  browser dns cdn lb api cache db queue worker pay jobs storage sms, wired up; non-highlighted parts dimmed.
- `Sort(id, {head, left, right, rightBad, items: [[html, 'l'|'r']]})` -> `.left(stepMs)`, `.right(stepMs)`.
- `Counters(id, {head, parts: [{n, fmt, label, cls: 'res'|'good'} | {op: '×'} | {static: '2 MB', label}]})` -> `.run()`, `.note(html)`.
- `Bars(id, {head, max, charts: [{title, bars: [{label, value, text, color, over}], limit: {value, label}}]})` -> `.grow(i)`.
- `Cards(id, {head, cols, items: [{icon, color, title, text}]})` -> `.reveal(i)`.
- `Say(id, text)`.
- `Panel(diagram, {x, y, w, title, items})` -> `.on(i)` lights up list item i.

Diagram methods: `node(key, x, y, icon, label, sub, {tone, w, h, hidden})`, `pop(key)`, `popAll(keys, gapMs)`,
`tone(key, 'good'|'bad'|'warn'|'muted'|'hl'|'')`, `dim(keys)`, `rename(key, label, sub)`, `link(a, b, {dash, curve, tone, id})`,
`linkTone(id, tone)`, `send(a, b, {color, dur, curve, r, label})` (Promise), `flow([keys], opts)`,
`stream(a, b | [b...], {every, color, dur, onSend})` -> stop(), `tag(key, text, color)`, `badge(key, text, color, 'top'|'bottom')`,
`unbadge(key)`, `text(x, y, str, {color, size, anchor, weight})`, `meter(key, 0..1)`, `bump(key, delta)`, `ring(key, ms)`,
`group(keys, title)`, `queue(key, x, y, slots, label)` + `fill(key, n)`. Colors: 'acc', 'good', 'bad', 'warn', 'muted'.
Helpers: `sleep(ms)`, `show(id)`, `icon(name, size, color)`. Icons: see lib/icons.js (server, db, queue, gear, lock, card,
clock, users, globe, split, bolt, bucket, chat, envelope, flag, chart, bell, doc, timer, retry, breaker, shield, gauge,
hourglass, table, key, inbox, sweep, reconcile, scaleup, weight, snow, pipeline, vault, badge, ...).

Layout rules: keep nodes inside 60..1860 x 160..1020 (the caption sits top-left, ~1000x150). Node default 170x124/140.
Text >= 22 px. Leave room for badges above nodes. Stop any `stream`/`setInterval` when the next scene starts.

## Workflow per video

1. Read the component in `cards.py` (and `src/components.md` context). Write `cNN/index.html` (copy c02's head).
2. Preview scenes: `python videos/lecture/preview.py cNN "SD:6000" "S1:3000" ...` -> `cNN/preview/shot_XX.png`.
   Open the shots. Fix overlaps, off-screen nodes, empty-looking scenes. Delete `preview/` when done.
3. Write `cues.json` + `SCRIPT.md`; run `record.py cNN --audio` until it says OK.
4. Record: `python videos/lecture/record.py cNN` (about 3 min, real time). Open `cNN/raw_build/sheet.png`:
   every frame must show what its line says. The clock line must have a close to 1. Fix and re-record if not.
5. Don't touch anything outside `videos/lecture/cNN/`. Don't commit.
