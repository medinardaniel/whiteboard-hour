"""Small SVG diagrams, drawn from one-line specs.

Spec language (one diagram = one string):
  icon:Label            a node with an icon; "~" breaks the label into lines
  :Label                a label-only node (states, steps)
  #12:Label             a node whose "icon" is the text 12
  !good !bad !muted     tone suffix on a node; an arrow INTO a bad node is drawn blocked
  [a, b, c]             a vertical stack of nodes (arrows fan in or out, or pair up)
  {Title| a, b}         a stack inside a dashed box with a title
  ->  -->  -x>  <-  <->  --  ..     arrow, dashed arrow, blocked, back, both, line, nothing
  ->"label"             a label above the arrow
  a ;; b                draw a second row under the first
  Title:: a -> b        a row with a small title
Colors come from CSS variables, so diagrams follow light and dark mode.
"""
import html
import itertools
import re

_P = {
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    "users": '<circle cx="9" cy="8" r="3.3"/><path d="M2.5 20c0-3.5 3-5.3 6.5-5.3s6.5 1.8 6.5 5.3"/><path d="M15.5 4.9a3.3 3.3 0 0 1 0 6.3M17.5 14.9c2.3.6 4 2.3 4 5.1"/>',
    "browser": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/><path d="M6 6.5h.01M8.5 6.5h.01"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18h2"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3.2 3 3.2 15 0 18M12 3c-3.2 3-3.2 15 0 18"/>',
    "signpost": '<path d="M12 3v18M5 5h11l3 2.5-3 2.5H5zM19 12H8l-3 2.5 3 2.5h11z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
    "gauge": '<path d="M3.5 17a8.5 8.5 0 1 1 17 0"/><path d="M12 17l4.5-5.5"/><circle cx="12" cy="17" r="1.2"/>',
    "hourglass": '<path d="M6 3h12M6 21h12M7 3h10l-5 9 5 9H7l5-9z"/>',
    "gate": '<path d="M4 21V8l8-5 8 5v13"/><path d="M9 21v-7h6v7"/>',
    "split": '<circle cx="5" cy="12" r="2.2"/><path d="M7.2 12H11M11 12l8-6.5M11 12h8M11 12l8 6.5"/>',
    "proxy": '<rect x="8" y="5" width="8" height="14" rx="2"/><path d="M2 12h6M16 12h6"/>',
    "server": '<rect x="4" y="3.5" width="16" height="7.5" rx="1.5"/><rect x="4" y="13" width="16" height="7.5" rx="1.5"/><path d="M8 7.25h.01M8 16.75h.01"/>',
    "box": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
    "k8s": '<path d="M12 2.5l8.3 4.8v9.4L12 21.5l-8.3-4.8V7.3z"/><circle cx="12" cy="12" r="3"/><path d="M12 5v4M12 15v4M6 8.5l3.4 2M14.6 13.5L18 15.5M6 15.5l3.4-2M14.6 10.5L18 8.5"/>',
    "lambda": '<path d="M6 20l6-10M8 4h3l7 16"/>',
    "gear": '<circle cx="12" cy="12" r="3.5"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "sweep": '<path d="M15 3l-4 9"/><path d="M6.5 12h9l1.8 9H4.7z"/><path d="M9 16v5M13 16v5"/>',
    "reconcile": '<path d="M4 8h15l-3.5-3.5M20 16H5l3.5 3.5"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.6"/><path d="M4.5 5.5v13c0 1.4 3.4 2.6 7.5 2.6s7.5-1.2 7.5-2.6v-13"/><path d="M4.5 12c0 1.4 3.4 2.6 7.5 2.6s7.5-1.2 7.5-2.6"/>',
    "key": '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2.5"/>',
    "doc": '<path d="M6 2.5h8l4 4v15H6z"/><path d="M14 2.5v4h4M9 12h6M9 16h6"/>',
    "table": '<rect x="3" y="4" width="18" height="16" rx="1.5"/><path d="M3 9h18M3 14.5h18M9.5 4v16"/>',
    "search": '<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L21 21"/>',
    "chart": '<path d="M3 20.5h18"/><path d="M4 16l5-5 4 3 7-8"/>',
    "graph": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="8" r="2.5"/><circle cx="10" cy="18" r="2.5"/><path d="M8.4 6.4l7.2 1.3M7 8.3l2.2 7.4M16.6 10.1l-4.9 6"/>',
    "bucket": '<path d="M4 6l2 15h12l2-15"/><ellipse cx="12" cy="6" rx="8" ry="2.4"/>',
    "warehouse": '<path d="M5 20V11M10 20V5M15 20v-7M20 20V8M3 20.5h19"/>',
    "bolt": '<path d="M13 2L5 14h6l-1 8 8-12h-6z"/>',
    "queue": '<rect x="2" y="7.5" width="20" height="9" rx="1.5"/><path d="M7 7.5v9M12 7.5v9M17 7.5v9"/>',
    "log": '<path d="M3 5.5h18M3 10h18M3 14.5h18M3 19h11"/>',
    "broadcast": '<circle cx="12" cy="12" r="2"/><path d="M7.8 7.8a6 6 0 0 0 0 8.4M16.2 7.8a6 6 0 0 1 0 8.4M4.9 4.9a10 10 0 0 0 0 14.2M19.1 4.9a10 10 0 0 1 0 14.2"/>',
    "inbox": '<path d="M3 13l3-8h12l3 8v6H3z"/><path d="M3 13h5l1.2 2.2h5.6L16 13h5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7.5a4 4 0 0 1 8 0V11"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
    "callback": '<path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 3.5v4.5h-4.5"/>',
    "envelope": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6.5L21 7"/>',
    "chat": '<path d="M4 4.5h16v11H9.5L4 20z"/>',
    "badge": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M5.5 16.5c.8-1.7 2-2.6 3.5-2.6s2.7.9 3.5 2.6M14.5 10h4M14.5 13.5h4"/>',
    "flag": '<path d="M5 21V3.5"/><path d="M5 4h12l-2.5 4L17 12H5"/>',
    "pin": '<path d="M12 21.5s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "timer": '<circle cx="12" cy="13.5" r="7.5"/><path d="M12 13.5V9.5M10 2.5h4M12 2.5v3.5"/>',
    "retry": '<path d="M4 12a8 8 0 1 0 2.4-5.7"/><path d="M4 3.5V8h4.5"/>',
    "breaker": '<path d="M2 15h4.5M17.5 15H22M7.5 14.3L16 8"/><circle cx="7" cy="15" r="1.6"/><circle cx="17" cy="15" r="1.6"/>',
    "compart": '<rect x="3" y="4.5" width="18" height="15" rx="1.5"/><path d="M9 4.5v15M15 4.5v15"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/>',
    "stop": '<path d="M8 2.5h8l5.5 5.5v8L16 21.5H8L2.5 16V8z"/><path d="M8 12h8"/>',
    "power": '<path d="M12 3v8.5"/><path d="M6.3 6.5a8 8 0 1 0 11.4 0"/>',
    "pulse": '<path d="M2.5 12h4.5l2.2-6 4.6 12 2.2-6h5.5"/>',
    "building": '<path d="M4 21V5.5l8-2.5v18M12 9l8 2.2V21M2.5 21h19"/><path d="M7 8h2M7 12h2M7 16h2M15 14h2M15 17.5h2"/>',
    "cloud": '<path d="M7 18.5h10.5a4 4 0 0 0 .4-8 6 6 0 0 0-11.6 1.4A3.4 3.4 0 0 0 7 18.5z"/>',
    "scaleup": '<path d="M4 20.5h4v-5H4zM10 20.5h4v-10h-4zM16 20.5h4V4h-4z"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3.5 6h.01M3.5 12h.01M3.5 18h.01"/>',
    "dashboard": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 10h18M10 10v11"/><path d="M5.5 6.5h5"/>',
    "bell": '<path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l2 2H4z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
    "pipeline": '<circle cx="4.5" cy="12" r="2.5"/><circle cx="12" cy="12" r="2.5"/><circle cx="19.5" cy="12" r="2.5"/><path d="M7 12h2.5M14.5 12H17"/>',
    "snow": '<path d="M12 2.5v19M3.8 7.2l16.4 9.6M3.8 16.8l16.4-9.6"/><path d="M9.5 4.5L12 7l2.5-2.5M9.5 19.5L12 17l2.5 2.5"/>',
    "weight": '<path d="M5.5 9h13l2.5 11.5H3z"/><path d="M9.5 9a2.5 2.5 0 1 1 5 0"/>',
    "dice": '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8.5 8.5h.01M15.5 15.5h.01M15.5 8.5h.01M8.5 15.5h.01M12 12h.01"/>',
    "calc": '<rect x="5" y="2.5" width="14" height="19" rx="2"/><path d="M8 6.5h8M8 11.5h.01M12 11.5h.01M16 11.5h.01M8 15.5h.01M12 15.5h.01M16 15.5h.01"/>',
    "check": '<path d="M4.5 12.5l5 5 10-11"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "vault": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="12" cy="12" r="4"/><path d="M12 8v1.5M12 14.5V16M8 12h1.5M14.5 12H16"/>',
    "money": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.8"/>',
    "trace": '<path d="M3 5h12M6 10h9M9 15h10M3 20h18"/>',
    "bulb": '<path d="M9.5 18h5M10.5 21h3"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.1v.1h5v-.1c0-.8.4-1.5 1.1-2.1A6 6 0 0 0 12 3z"/>',
    "branch": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 7v10M18 10c0 4-6 3-11 7"/>',
}

CH = 5.7       # average character width at 10px
LCH = 5.0      # at 9px (arrow labels)
_count = itertools.count()


def esc(s):
    return html.escape(s, quote=True)


def icon_svg(name, size=22, cls="fi"):
    """A standalone inline icon, used by the HTML flow boxes."""
    if name not in _P:
        return ""
    return f'<svg class="{cls}" viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true">{_P[name]}</svg>'


# ---------------------------------------------------------------- spec diagrams

def _node(tok):
    tok = tok.strip()
    tone = ""
    m = re.search(r"!(good|bad|muted)$", tok)
    if m:
        tone, tok = m.group(1), tok[: m.start()].strip()
    icon, sep, label = tok.partition(":")
    if not sep:
        icon, label = "", tok
    lines = [l.strip() for l in label.split("~")]
    icon = icon.strip()
    n = {"icon": icon, "lines": lines, "tone": tone}
    width = max(len(l) for l in lines) * CH + 14
    if icon.startswith("#"):
        width = max(width, len(icon) * 8 + 14)
    n["w"] = max(60, width)
    n["h"] = (34 + 12 * len(lines)) if icon else (14 + 13 * len(lines))
    return n


def _item(tok):
    tok = tok.strip()
    if tok.startswith("{") and tok.endswith("}"):
        title, _, inner = tok[1:-1].partition("|")
        nodes = [_node(t) for t in inner.split(",")]
        return {"title": title.strip(), "nodes": nodes}
    if tok.startswith("[") and tok.endswith("]"):
        return {"title": None, "nodes": [_node(t) for t in tok[1:-1].split(",")]}
    return {"title": None, "nodes": [_node(tok)]}


ARROW = r"\s+(<->|-x>|-->|->|<-|--|\.\.)(\"[^\"]*\")?\s+"


def _row(spec):
    title = None
    if "::" in spec:
        title, spec = spec.split("::", 1)
        title = title.strip()
    parts = re.split(ARROW, spec.strip())
    items = [_item(p) for p in parts[0::3]]
    arrows = parts[1::3]
    labels = [(l or "").strip('"') for l in parts[2::3]]
    for it in items:
        it["w"] = max(n["w"] for n in it["nodes"]) + (14 if it["title"] else 0)
        inner = sum(n["h"] for n in it["nodes"]) + 8 * (len(it["nodes"]) - 1)
        it["h"] = inner + (26 if it["title"] else 0)
    gaps = []
    for a, l in zip(arrows, labels):
        g = 12 if a == ".." else 30
        if l:
            g = max(g, len(l) * LCH + 14)
        gaps.append(g)
    width = sum(it["w"] for it in items) + sum(gaps)
    has_label = any(labels)
    body_h = max(it["h"] for it in items)
    top = (14 if title else 0) + (14 if has_label else 2)
    return {"title": title, "items": items, "arrows": arrows, "labels": labels,
            "gaps": gaps, "w": width, "h": top + body_h + 2, "top": top, "body_h": body_h}


def _draw_node(n, x, y):
    cls = "n" + (" " + n["tone"] if n["tone"] else "")
    out = [f'<g class="{cls}"><rect x="{x:.1f}" y="{y:.1f}" width="{n["w"]:.1f}" height="{n["h"]}" rx="7"/>']
    cx = x + n["w"] / 2
    if n["icon"].startswith("#"):
        out.append(f'<text class="gl" x="{cx:.1f}" y="{y + 22:.1f}">{esc(n["icon"][1:])}</text>')
        ty = y + 40
    elif n["icon"]:
        p = _P.get(n["icon"])
        if p is None:
            raise KeyError(f"unknown icon {n['icon']!r}")
        out.append(f'<g class="ic" transform="translate({cx - 11:.1f},{y + 6:.1f}) scale(.9167)">{p}</g>')
        ty = y + 40
    else:
        ty = y + 18
    for i, line in enumerate(n["lines"]):
        cls_t = "t" if n["icon"] else "t big"
        out.append(f'<text class="{cls_t}" x="{cx:.1f}" y="{ty + i * (12 if n["icon"] else 13):.1f}">{esc(line)}</text>')
    out.append("</g>")
    return "".join(out)


def _arrow(x1, y1, x2, y2, style, bad):
    cls = "a"
    if style == "-->":
        cls += " dash"
    if style == "-x>" or bad:
        cls += " bad"
    out = [f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>']

    def head(tx, ty, fx, fy):
        dx, dy = tx - fx, ty - fy
        d = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / d, dy / d
        bx, by = tx - ux * 7, ty - uy * 7
        px, py = -uy * 3.6, ux * 3.6
        return (f'<path class="ah{" bad" if "bad" in cls else ""}" d="M{tx:.1f},{ty:.1f} '
                f'L{bx + px:.1f},{by + py:.1f} L{bx - px:.1f},{by - py:.1f}z"/>')

    if style in ("->", "-->", "-x>", "<->"):
        out.append(head(x2, y2, x1, y1))
    if style in ("<-", "<->"):
        out.append(head(x1, y1, x2, y2))
    if style == "-x>" or bad:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        out.append(f'<path class="a bad xm" d="M{mx - 4:.1f},{my - 4:.1f}l8,8M{mx + 4:.1f},{my - 4:.1f}l-8,8"/>')
    return "".join(out)


def _draw_row(r, ox, oy):
    out = []
    if r["title"]:
        out.append(f'<text class="rt" x="{ox:.1f}" y="{oy + 10:.1f}">{esc(r["title"].upper())}</text>')
    mid = oy + r["top"] + r["body_h"] / 2
    x = ox
    ends = []  # per item: list of (left_x, right_x, cy, node)
    for k, it in enumerate(r["items"]):
        y = mid - it["h"] / 2
        pts = []
        if it["title"]:
            out.append(f'<g class="g"><rect x="{x:.1f}" y="{y:.1f}" width="{it["w"]:.1f}" height="{it["h"]:.1f}" rx="9"/>'
                       f'<text class="gt" x="{x + it["w"] / 2:.1f}" y="{y + 13:.1f}">{esc(it["title"])}</text></g>')
            ny = y + 20
            for n in it["nodes"]:
                nx = x + (it["w"] - n["w"]) / 2
                out.append(_draw_node(n, nx, ny))
                ny += n["h"] + 8
            pts = [(x, x + it["w"], mid, {"tone": ""})]
        else:
            ny = y
            for n in it["nodes"]:
                nx = x + (it["w"] - n["w"]) / 2
                out.append(_draw_node(n, nx, ny))
                pts.append((nx, nx + n["w"], ny + n["h"] / 2, n))
                ny += n["h"] + 8
        ends.append(pts)
        x += it["w"]
        if k < len(r["gaps"]):
            x += r["gaps"][k]
    x = ox
    for k, style in enumerate(r["arrows"]):
        x += r["items"][k]["w"]
        src, dst = ends[k], ends[k + 1]
        if style != "..":
            pairs = list(zip(src, dst)) if len(src) == len(dst) and len(src) > 1 else [(s, d) for s in src for d in dst]
            for s, d in pairs:
                bad = d[3].get("tone") == "bad" and style in ("->", "-->")
                out.append(_arrow(s[1] + 2, s[2], d[0] - 2, d[2], style, bad))
            if r["labels"][k]:
                ys = [min(s[2], d[2]) for s, d in pairs]
                ly = min(ys) - 5
                out.append(f'<text class="lbl" x="{x + r["gaps"][k] / 2:.1f}" y="{ly:.1f}">{esc(r["labels"][k])}</text>')
        x += r["gaps"][k]
    return "".join(out)


def _wrap(w, h, body, label):
    uid = next(_count)
    return (f'<svg class="v" viewBox="0 0 {w:.0f} {h:.0f}" style="max-width:{w * 1.3:.0f}px" '
            f'role="img" aria-label="{esc(label)}" data-v="{uid}">{body}</svg>')


def spec_svg(spec, label=""):
    rows = [_row(s) for s in spec.split(";;")]
    W = max(r["w"] for r in rows) + 8
    H = sum(r["h"] for r in rows) + 12 * (len(rows) - 1) + 6
    out, y = [], 3
    for r in rows:
        out.append(_draw_row(r, (W - r["w"]) / 2, y))
        y += r["h"] + 12
    return _wrap(W, H, "".join(out), label)


# ---------------------------------------------------------------- custom diagrams

def _axis(x1, x2, y, ticks):
    out = [f'<line class="ax" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/>',
           f'<path class="ahm" d="M{x2},{y} l-6,-3.5 v7z"/>']
    for tx, t in ticks:
        out.append(f'<line class="ax" x1="{tx}" y1="{y - 3}" x2="{tx}" y2="{y + 3}"/>'
                   f'<text class="lbl" x="{tx}" y="{y + 14}">{esc(t)}</text>')
    return "".join(out)


def ttl():
    b = [_axis(10, 330, 64, [(14, "0 s"), (164, "5 s"), (314, "10 s")])]
    b.append('<rect class="fill-good" x="14" y="30" width="150" height="24" rx="5"/>'
             '<text class="t" x="89" y="46">served from cache</text>')
    b.append('<line class="a bad" x1="164" y1="18" x2="164" y2="62"/><text class="lbl bad-t" x="164" y="13">TTL ends</text>')
    b.append('<rect class="fill-warn" x="166" y="30" width="22" height="24" rx="5"/><text class="t" x="177" y="46">DB</text>')
    b.append('<rect class="fill-good" x="190" y="30" width="124" height="24" rx="5"/>'
             '<text class="t" x="252" y="46">cached again</text>')
    return _wrap(340, 84, "".join(b), "TTL timeline")


def backoff():
    b = [_axis(10, 335, 62, [(20, "0"), (60, "100 ms"), (120, "300"), (200, "700"), (300, "1.5 s")])]
    for x, ok in ((20, False), (60, False), (120, False), (200, False), (300, True)):
        cls = "fill-good" if ok else "fill-bad"
        b.append(f'<circle class="{cls}" cx="{x}" cy="46" r="8"/>')
        mark = "M-3.5,0.5 l2.5,2.5 l5,-5.5" if ok else "M-3,-3 l6,6 M3,-3 l-6,6"
        b.append(f'<path class="mk" transform="translate({x},46)" d="{mark}"/>')
    for x1, x2, t in ((20, 60, "wait 100"), (60, 120, "200"), (120, 200, "400"), (200, 300, "800 + jitter")):
        b.append(f'<path class="a dash" d="M{x1 + 8},38 Q{(x1 + x2) / 2},18 {x2 - 8},38"/>'
                 f'<text class="lbl" x="{(x1 + x2) / 2}" y="20">{t}</text>')
    b.append('<text class="lbl" x="20" y="8" style="text-anchor:start">x = failed call, wait doubles each time</text>')
    return _wrap(345, 84, "".join(b), "Retry with backoff timeline")


def percentiles():
    heights = [10, 34, 52, 46, 32, 22, 15, 10, 7, 5, 4, 3, 2, 2, 1]
    b = [_axis(10, 335, 80, [(14, "fast"), (300, "slow")])]
    for i, h in enumerate(heights):
        b.append(f'<rect class="fill-acc" x="{16 + i * 20}" y="{78 - h}" width="15" height="{h}" rx="2"/>')
    for x, t in ((70, "p50"), (190, "p95"), (250, "p99")):
        b.append(f'<line class="a bad" x1="{x}" y1="10" x2="{x}" y2="78"/><text class="lbl bad-t" x="{x}" y="8">{t}</text>')
    return _wrap(345, 98, "".join(b), "Latency histogram with percentiles")


def waterfall():
    rows = [("POST /orders", 0, 300, "300 ms"), ("DB: reserve", 10, 40, "30"), ("Stripe session", 50, 270, "220"),
            ("DB: save id", 275, 295, "20")]
    b = []
    for i, (name, s, e, t) in enumerate(rows):
        y = 8 + i * 22
        cls = "fill-acc" if i == 0 else ("fill-bad" if e - s > 150 else "fill-good")
        b.append(f'<text class="lbl" x="4" y="{y + 12}" style="text-anchor:start">{esc(name)}</text>'
                 f'<rect class="{cls}" x="{100 + s * .75:.1f}" y="{y}" width="{(e - s) * .75:.1f}" height="15" rx="3"/>'
                 f'<text class="lbl" x="{100 + e * .75 + 14:.1f}" y="{y + 12}">{t}</text>')
    return _wrap(345, 96, "".join(b), "Trace waterfall")


def rolling():
    b = []
    for r in range(3):
        y = 6 + r * 26
        b.append(f'<text class="lbl" x="4" y="{y + 14}" style="text-anchor:start">step {r + 1}</text>')
        for c in range(4):
            new = c <= r
            x = 60 + c * 64
            b.append(f'<rect class="{"fill-acc" if new else "fill-mute"}" x="{x}" y="{y}" width="56" height="20" rx="4"/>'
                     f'<text class="t{" on" if new else ""}" x="{x + 28}" y="{y + 14}">{"v2" if new else "v1"}</text>')
    return _wrap(320, 86, "".join(b), "Rolling deploy steps")


def pitr():
    b = [_axis(10, 335, 56, [(20, "Mon"), (100, "Tue"), (180, "Wed"), (260, "Thu")])]
    b.append('<line class="a" x1="20" y1="40" x2="290" y2="40"/><text class="lbl" x="150" y="34">change log, every write</text>')
    for x in (20, 100, 180, 260):
        b.append(f'<rect class="fill-acc" x="{x - 5}" y="44" width="10" height="10" transform="rotate(45 {x} 49)"/>')
    b.append('<line class="a bad" x1="300" y1="14" x2="300" y2="56"/><text class="lbl bad-t" x="300" y="10">bad delete</text>')
    b.append('<path class="a dash" d="M298,22 Q280,18 286,36"/><text class="lbl" x="240" y="20">restore to 1 min before</text>')
    return _wrap(345, 76, "".join(b), "Point-in-time restore timeline")


def rpo_rto():
    b = [_axis(10, 335, 60, [(60, "last save"), (170, "failure"), (300, "back up")])]
    b.append('<rect class="fill-bad" x="60" y="30" width="110" height="18" rx="4"/><text class="t on" x="115" y="43">RPO: data lost</text>')
    b.append('<rect class="fill-warn" x="170" y="30" width="130" height="18" rx="4"/><text class="t" x="235" y="43">RTO: downtime</text>')
    return _wrap(345, 80, "".join(b), "RPO and RTO timeline")


CUSTOM = {
    "TTL": ttl, "Retry with exponential backoff and jitter": backoff, "Percentiles": percentiles,
    "Traces": waterfall, "Rolling deploy": rolling, "Backups / point-in-time restore": pitr, "RPO / RTO": rpo_rto,
}

# One diagram per component card, keyed by the card's bold title.
SPECS = {
    # Edge
    "DNS": 'user:Browser ->"pizza.com?" signpost:DNS ;; user:Browser ->"203.0.113.7" server:Your site',
    "CDN": 'user:User ->"near, fast" globe:CDN edge -->"miss only" server:Origin',
    "WAF": 'user:User -> shield:WAF -> server:API ;; user:Bot!bad -x>"blocked" shield:WAF',
    "DDoS protection": '[user:Junk!bad, user:Junk!bad, user:Junk!bad] -x> shield:Shield ;; user:Real user -> shield:Shield -> server:API',
    "Rate limiter": 'user:One IP ->"100/s" gauge:Limit~10/s ->"10/s" server:API ;; user:The other 90!bad -x> #429:Too many',
    "Waiting room / virtual queue": 'users:10,000~at once -> hourglass:Waiting~room ->"200/s" server:Checkout',
    "API gateway": '[phone:App, user:Partner] ->"auth, limits" gate:Gateway -> [server:Orders, server:Users]',
    "Load balancer": 'users:Users -> split:LB -> [server:API 1, server:API 2, server:Unhealthy!bad]',
    "Reverse proxy": 'user:Browser ->"HTTPS" proxy:Proxy ->"HTTP" server:App',
    # Compute
    "API service (stateless)": 'split:LB -> [server:API, server:API, server:API] -> db:State lives~in the DB',
    "Monolith (modular)": 'user:Request -> {one deploy| box:Orders, box:Payments, box:Menu} -> db:One DB',
    "Microservices": 'gate:Gateway -> [box:Orders, box:Payments, box:Menu] -> [db:DB, db:DB, db:DB]',
    "Managed containers": 'box:Your image -> cloud:Platform~runs it -> [box:Copy, box:Copy]',
    "Kubernetes": 'box:Images -> {you run this| k8s:Control plane, server:Node, server:Node}',
    "Serverless functions": 'callback:Event -> lambda:Function ->"per run" money:Pay per run',
    "Autoscaling": 'chart:CPU 80% ->"1 to 5 min" [server:API, server:API, server:New!good]',
    "Background worker": 'server:API ->"enqueue" queue:Queue -> gear:Worker -> envelope:Email',
    "Scheduled job (cron)": 'clock:Every night -> gear:Job -> db:DB',
    "Sweeper job": 'clock:Every minute -> sweep:Sweeper ->"expired?" db:Holds ;; sweep:Sweeper ->"paid?" card:Stripe',
    "Reconciliation job": 'db:Our records -> reconcile:Compare~and fix <- card:Stripe',
    # Database kinds
    "Relational (SQL)": 'server:API -> {one transaction| table:orders, table:stock}',
    "Key-value": 'server:API ->"get cart:42" key:KV store ->"1 ms" doc:Value',
    "Document": '[doc:Pizza~has toppings, doc:Drink~has size] -> db:Doc store',
    "Wide-column": 'pulse:Sensors ->"huge writes" {split by key| table:Part A, table:Part B, table:Part C}',
    "Search engine": 'user:"red shoes" -> search:Index -> list:Ranked ;; db:Postgres -->"copy, lags" search:Index',
    "Time-series": 'server:Hosts ->"every 10 s" chart:TSDB -> dashboard:Graphs',
    "Graph": 'user:You -- graph:Graph DB ->"friends of~friends" users:Suggestions',
    "Object storage": 'user:Upload ->"photo.jpg" bucket:Bucket -> globe:CDN',
    "Data warehouse": 'db:App DB -->"nightly copy" warehouse:Warehouse -> dashboard:Reports',
    # Database concepts
    "ACID transaction": '{all or nothing| table:Reserve seat, table:Create order} -> check:Both,~or neither',
    "Isolation levels": 'user:Txn A ->"writing" table:Row ;; user:Txn B ->"sees old value" table:Row',
    "Index": 'search:phone = ? ->"jump" table:1 row ;; search:No index!muted ->"scan" table:1M rows!bad',
    "Unique constraint": '[user:Insert key A, user:Insert key A!bad] -> lock:UNIQUE(key)',
    "Primary / replica": 'server:Writes -> db:Primary -->"copies" [db:Replica, db:Replica] <- server:Reads',
    "Failover": 'db:Primary!bad -->"30 to 60 s" db:Standby~promoted!good <- server:API~retries',
    "Sharding / partitioning": 'server:API ->"A to M" db:Shard 1 ;; server:API ->"N to Z" db:Shard 2',
    "Connection pooling": '[server:API, server:API, server:API] ->"300 conns" proxy:Pooler ->"20 conns" db:Postgres',
    "CAP / consistency": 'db:Node A -x>"network split" db:Node B ;; Pick one:: :C~refuse writes .. :A~accept, fix later',
    "Eventual consistency": 'user:Write -> db:Primary -->"100 ms later" db:Replica -> user:Reader~sees old',
    # Caching
    "Cache": 'server:API ->"hit, 1 ms" bolt:Cache ;; server:API -->"miss, 10 ms" db:DB',
    "In-memory store": '[server:API, server:API] ->"100k ops/s" bolt:Redis',
    "Cache-aside": 'server:API ->"1 check" bolt:Cache ;; server:API ->"2 miss: read" db:DB ;; server:API ->"3 fill" bolt:Cache',
    "Write-through": 'server:API ->"write" bolt:Cache ->"same time" db:DB',
    "Invalidation": 'user:Edit price -> db:DB -->"delete key" bolt:Cache',
    "Cache stampede": 'Problem:: users:1,000 at once ->"key expired" db:DB!bad ;; Fix:: users:1,000 at once -> bolt:Cache ->"1 refresh" db:DB',
    "Hot key": 'Problem:: users:Everyone ->"deal_7" bolt:One shard!bad ;; Fix:: users:Everyone -> [bolt:Local copy, bolt:Local copy]',
    "Local (in-process) cache": 'split:LB -> [bolt:API + memory, bolt:API + memory] -->"rarely" db:DB',
    # Async
    "Message queue": 'server:API -> queue:Queue ->"each job once" [gear:Worker, gear:Worker]',
    "Log / stream": 'server:Producers -> log:Log ->"all read, replay" [gear:Analytics, gear:Billing, gear:Search]',
    "Pub/sub": 'card:Order paid -> broadcast:Topic -> [server:Kitchen, envelope:Email, chart:Analytics]',
    "Dead-letter queue (DLQ)": 'queue:Queue -> gear:Worker ->"5th failure" inbox:Dead~letters -> bell:Alert',
    "At-least-once delivery": 'queue:Queue ->"msg 7" gear:Worker ;; queue:Queue ->"msg 7 again" gear:Worker ;; Fix:: gear:Worker ->"seen 7? skip" table:Done ids',
    "Exactly-once": 'queue:At least~once -> check:Idempotent~consumer -> #1x:Effect once',
    "Backpressure": 'server:Producer ->"1,000/s" queue:Queue~grows ->"200/s" gear:Workers ;; server:Producer <-"slow down" queue:Depth high',
    "Outbox pattern": 'server:API -> {one transaction| table:orders, table:outbox} -> gear:Relay -> queue:Queue',
    # Correctness
    "Atomic conditional update": '[user:Buyer A, user:Buyer B] -> table:1 left -> [check:A: 1 row!good, x:B: 0 rows!bad]',
    "Pessimistic lock": 'user:Txn A ->"FOR UPDATE" lock:Row~locked ;; user:Txn B -x>"waits" lock:Row~locked',
    "Optimistic lock": 'user:Read v3 ->"write if v3" table:Row -> check:Now v4 ;; user:Late writer ->"write if v3" table:Row is v4!bad',
    "Holds / reservations with expiry": 'user:Checkout -> clock:Hold~10 min -> [card:Paid!good, retry:Expired:~released]',
    "Idempotency key": '[user:Tap~key abc, user:Tap again~key abc] -> lock:UNIQUE key -> #1:One order',
    "Webhook dedupe": '[callback:evt_9, callback:evt_9 again!bad] -> table:Seen events -> check:Handled once',
    "State machine": ':Held -> :Paid ;; :Held -> :Expired ;; :Paid -x>"never back" :Held',
    "Saga": 'check:Book flight!good -> x:Book hotel~fails!bad ;; Undo:: retry:Cancel flight -> check:Clean state',
    "Distributed lock": 'Avoid:: [server:API, server:API] -> lock:Redis lock!muted ;; Prefer:: [server:API, server:API] -> db:DB constraint!good',
    "Reconciliation": 'db:Our orders -> reconcile:Compare~every 5 min <- card:Provider',
    # Third parties
    "Payment provider": 'user:Customer -> server:Your API ->"session" card:Stripe page ;; card:Stripe -->"webhook: paid" server:Your API',
    "Webhook": 'card:Provider ->"POST /webhooks" server:Your API ->"200 fast" queue:Work later',
    "SMS / voice": 'queue:Queue -> gear:Worker ->"rate limited" chat:SMS~provider -> phone:Phone',
    "Email": 'queue:Queue -> gear:Worker -> envelope:Email~provider -> user:Inbox',
    "Auth / identity": 'user:User ->"login" badge:Auth~provider ->"token" server:Your API',
    "Feature flags": 'flag:Waiting room~ON -->"no deploy" [server:API, server:API]',
    "Maps / geo": 'server:API ->"address" pin:Maps API ;; server:API ->"save result" bolt:Cache',
    # Reliability
    "Timeout": 'server:API ->"wait max 2 s" timer:Slow~provider -> x:Stop,~return error',
    "Circuit breaker": ':Closed ->"5 failures" :Open ->"after 30 s" :Half-open ;; :Half-open ->"call works" :Closed',
    "Bulkhead": 'server:API -> [compart:Checkout~pool, compart:Stripe~pool] -> [check:Still fast!good, timer:Slow but~contained]',
    "Graceful degradation": 'chart:High load -> [check:Checkout on!good, sun:Photos off!muted, sun:Recs off!muted]',
    "Load shedding": 'users:Too many -> server:API ->"90%" check:Fast ;; server:API ->"10%" #503:Try later',
    "Kill switch": 'flag:Pause orders~ON -> server:API -> :Back soon page',
    "Health checks": 'split:LB ->"GET /health" [server:200 OK!good, server:Timeout!bad]',
    "Multi-AZ": 'split:LB -> {one region| building:AZ 1, building:AZ 2, building:AZ 3}',
    "Multi-region": 'signpost:DNS -> [cloud:Region A!good, cloud:Region B!muted]',
    "Pre-scaling / pre-warming": 'clock:T minus 1 h -> scaleup:Scale to 10 -> users:Spike hits~warm servers',
    # Observability
    "Metrics": '[server:API, db:DB, queue:Queue] -> chart:Metrics',
    "Logs": 'server:API ->"JSON lines" list:Log store -> search:Search',
    "Dashboards": 'chart:Metrics -> dashboard:Dashboard -> user:You, launch day',
    "Alerts": 'chart:Errors > 2% -> bell:Alert -> phone:On-call',
    "Golden signals": 'timer:Latency .. users:Traffic .. x:Errors .. gauge:Saturation',
    "Business metrics": 'card:Orders/min .. reconcile:Held vs~paid .. table:Stock left',
    "SLI / SLO / error budget": 'pulse:SLI~measured -> target:SLO~99.9% -> #0.1%:Error budget',
    "Runbook": 'bell:Alert fires -> doc:Runbook:~if X do Y -> flag:Flip switch',
    # Release
    "CI/CD": 'branch:Merge -> pipeline:Build + test -> cloud:Deploy',
    "Blue-green": 'split:LB ->"100% now" server:Blue v1 ;; split:LB -->"switch" server:Green v2',
    "Canary": 'split:LB ->"95%" server:v1 ;; split:LB ->"5%" server:v2 canary',
    "Rollback": 'server:v2 broken!bad ->"one command" server:v1~back!good',
    "Code freeze": 'snow:Freeze Fri -> users:Event Sun -> pipeline:Deploys~Mon',
    "Load test": 'weight:k6 at~3x peak -> server:Staging -> check:Pass bar~met!good',
    "Game day": 'weight:Load test -> flag:Flip~switches -> x:Fake~outage -> doc:Fix~runbook',
    "Chaos testing": 'dice:Kill a~node -> [server:API!bad, server:API, server:API]',
    "Capacity planning": 'users:20k~visitors -> calc:500 req/s -> server:4 instances',
    # Security
    "TLS": 'user:Browser ->"HTTPS" lock:LB / CDN ->"private" server:API',
    "Authn vs authz": 'user:User -> badge:Authn:~who? -> lock:Authz:~allowed? -> server:Action',
    "Secrets": 'vault:Secrets~manager ->"at start" server:API ;; doc:Key in code!muted -x> server:API',
    "PCI": 'user:Card number -> card:Stripe page ;; card:Stripe page ->"token only" server:Your API',
    "PII": 'user:Name, phone ->"store less" lock:Encrypted -> db:DB',
    "Least privilege": 'gear:Worker ->"read only" queue:Queue ;; gear:Worker -x>"no admin" db:DB',
}


# The 23 core cards. Reuse a reference drawing where it already fits.
CORE = {
    "Stateless API, one service": 'split:LB -> [server:API, server:API, server:API] -> db:State lives~in the DB',
    "Postgres (managed)": 'server:API -> {one transaction| table:orders, table:stock} ;; Not yet:: key:DynamoDB!muted .. :only past one~primary at scale',
    "Object storage": 'user:Browser ->"signed URL" bucket:Bucket -> globe:CDN ;; user:Browser -x>"not through" server:API',
    "Queue + workers": 'server:API -> queue:Queue -> [gear:Worker, gear:Worker] ;; gear:Worker ->"5th failure" inbox:Dead~letters -> bell:Alert',
    "Sweeper and reconciliation jobs": 'clock:Every minute -> sweep:Sweeper ->"expired?" db:Holds ;; db:Our orders <->"compare, fix gaps" card:Stripe',
    "Conditional update": SPECS["Atomic conditional update"],
    "Holds that expire": 'user:Checkout -> clock:Hold~10 min -> [card:Paid!good, retry:Expired:~released] ;; :Paid -x>"never back" :Held',
    "Cache with a short TTL": 'server:API ->"hit, 1 ms" bolt:Redis ;; server:API -->"miss: read, then fill" db:DB',
    "Rate limits": SPECS["Rate limiter"],
    "Waiting room": SPECS["Waiting room / virtual queue"],
    "Replicas and failover": 'server:Writes -> db:Primary -->"copies" [db:Replica, db:Replica] <- server:Reads ;; db:Primary!bad -->"30 to 60 s" db:Standby~promoted!good',
    "Connection pooler": SPECS["Connection pooling"],
    "Pre-scaling": 'clock:T minus 1 h -> scaleup:Scale to 10 -> users:Spike hits~warm servers ;; chart:Autoscaling!muted ->"1 to 5 min" :Too late for~a fast spike',
    "Hosted checkout + webhooks": SPECS["Payment provider"],
    "Timeouts, retries, circuit breaker": 'server:API ->"2 s timeout, same key" card:Stripe ;; :Closed ->"5 fails" :Open ->"30 s" :Half-open',
    "Flags and kill switches": 'flag:Pause orders~ON -->"no deploy" [server:API, server:API] -> :Back soon page',
    "Load test and game day": 'weight:Load test~3x peak -> server:Staging -> check:Pass bar!good ;; flag:Flip~switches -> x:Fake~outage -> doc:Fix~runbook',
    "Safe deploys": 'split:LB ->"95%" server:v1 ;; split:LB ->"5%" server:v2 canary ;; snow:Freeze -> users:Event -> pipeline:Deploys~resume',
    "Dashboards and alerts": 'chart:Errors > 2% -> bell:Alert -> doc:Runbook -> flag:Flip switch',
    "Security basics": 'user:Browser ->"HTTPS" lock:LB ->"private" server:API <- vault:Secrets',
}
SPECS.update(CORE)


def visual_for(title):
    if title in CUSTOM:
        return CUSTOM[title]()
    if title in SPECS:
        return spec_svg(SPECS[title], title)
    return None


# Icons for the HTML flow boxes, matched on the box name (first match wins).
FLOW_ICONS = [
    ("third part", "card"), ("waf", "shield"), ("object storage", "bucket"), ("load balancer", "split"),
    ("worker", "gear"), ("redis", "bolt"), ("cache", "bolt"), ("queue", "queue"), ("outbox", "inbox"),
    ("sweeper", "sweep"), ("job", "clock"), ("builder", "clock"), ("stripe", "card"), ("checkout", "card"),
    ("postgres", "db"), ("mysql", "db"), ("database", "db"), ("cdn", "globe"), ("edge", "globe"),
    ("phone", "phone"), ("browser", "browser"), ("admin", "user"), ("users", "users"), ("timing", "pulse"),
    ("print-shop", "dashboard"), ("vm", "server"), ("api", "server"), ("compute", "server"), ("sms", "chat"),
    ("push", "phone"), ("email", "envelope"),
]


def flow_icon(name):
    low = name.lower()
    for key, ic in FLOW_ICONS:
        if key in low:
            return icon_svg(ic)
    return ""
