"""Turn src/*.md into the static pages. Run: python build.py

Not needed to host the site: the generated .html files are committed.
Supports a small markdown subset plus three extras:
  ```flow      stacked boxes (one line per row, " | " splits a row)
  ::: answer   a hidden answer revealed by "See answer"
  {#id}        an explicit heading id
Tables become cards, so nothing scrolls sideways on a phone.
"""
import html
import re
from pathlib import Path

import visuals

ROOT = Path(__file__).parent
PAGES = [
    ("framework.md", "index.html", "Framework"),
    ("components.md", "components.html", "Components"),
    ("questions.md", "questions.html", "Questions"),
]
# Built but not in the nav or the PDF.
EXTRA_PAGES = [("reference.md", "reference.html", "All components")]
VISUAL_PAGES = ("components.md", "reference.md")
SITE = "Whiteboard Hour"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def inline(text):
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append("<code>" + html.escape(p[1:-1]) + "</code>")
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
        out.append(p)
    return "".join(out)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def plain_title(cell):
    m = re.search(r"\*\*(.+?)\*\*", cell)
    return (m.group(1) if m else cell).strip()


MISSING = []


def table(lines, with_visuals=False):
    head = cells(lines[0])
    rows = [cells(l) for l in lines[2:]]
    if len(head) == 2:
        items = "".join(
            f'<div class="pair"><div class="k">{inline(r[0])}</div><div class="v">{inline(r[1])}</div></div>'
            for r in rows
        )
        return f'<div class="pairs">{items}</div>'
    numbered = head[0] == "#"
    out = ['<div class="cards">']
    for r in rows:
        if numbered:
            title = f'<span class="num">{inline(r[0])}</span> {inline(r[1])}'
            fields = list(zip(head[2:], r[2:]))
        else:
            title = inline(r[0])
            fields = list(zip(head[1:], r[1:]))
        dl = "".join(
            f"<dt>{inline(h)}</dt><dd>{inline(v)}</dd>" for h, v in fields if v
        )
        vis = ""
        if with_visuals:
            key = plain_title(r[1] if numbered else r[0])
            svg = visuals.visual_for(key)
            if svg is None:
                MISSING.append(key)
            else:
                vis = f'<div class="vis">{svg}</div>'
        out.append(f'<div class="card"><div class="card-title">{title}</div>{vis}<dl>{dl}</dl></div>')
    out.append("</div>")
    return "".join(out)


def flow(lines):
    rows = []
    for line in lines:
        boxes = []
        for b in line.split(" | "):
            name, _, detail = b.partition(": ")
            d = f'<span class="detail">{inline(detail)}</span>' if detail else ""
            ic = visuals.flow_icon(name)
            boxes.append(f'<div class="box">{ic}<strong>{inline(name)}</strong>{d}</div>')
        rows.append(f'<div class="flow-row">{"".join(boxes)}</div>')
    return '<div class="flow">' + '<div class="arrow" aria-hidden="true">&darr;</div>'.join(rows) + "</div>"


def heading(level, text, toc):
    m = re.search(r"\s*\{#([\w-]+)\}\s*$", text)
    if m:
        hid, text = m.group(1), text[: m.start()]
    else:
        hid = slug(text)
    if level == 2:
        toc.append((hid, text))
    return f'<h{level} id="{hid}">{inline(text)}</h{level}>'


def timeline(lines):
    segs = []
    for l in lines:
        num, name, mins = [x.strip() for x in l.split("|")]
        segs.append(f'<div class="seg{" buf" if num == "-" else ""}" style="flex:{int(mins)}">'
                    f'<b>{"" if num == "-" else num}</b><span>{mins}m</span></div>')
    return f'<div class="tl">{"".join(segs)}</div>'


def render(lines, toc, with_visuals=False):
    out, i = [], 0
    para = []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush(); i += 1; continue
        if s.startswith(":::") and s != ":::":
            flush()
            kind, _, args = s[3:].strip().partition(" ")
            depth, j = 1, i + 1
            while j < len(lines):
                t = lines[j].strip()
                if t.startswith(":::") and t != ":::":
                    depth += 1
                elif t == ":::":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = render(lines[i + 1 : j], [], with_visuals)
            if kind == "answer":
                out.append(
                    '<details class="answer"><summary><span class="show">See answer</span>'
                    '<span class="hide">Hide answer</span></summary>'
                    f'<div class="answer-body">{inner}</div></details>'
                )
            elif kind == "phase":
                num, name, mins = [x.strip() for x in args.split("|")]
                out.append(f'<section class="phase" id="phase-{num}"><div class="phase-head"><span class="pn">{num}</span>'
                           f'<span class="pname">{inline(name)}</span><span class="pmin">{inline(mins)}</span></div>{inner}</section>')
            else:
                out.append(f'<div class="{kind}">{inner}</div>')
            i = j + 1; continue
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            j = i + 1
            while not lines[j].strip().startswith("```"):
                j += 1
            body = lines[i + 1 : j]
            if lang == "timeline":
                out.append(timeline([b for b in body if b.strip()]))
            elif lang == "flow":
                out.append(flow([b for b in body if b.strip()]))
            else:
                out.append("<pre><code>" + html.escape("\n".join(body)) + "</code></pre>")
            i = j + 1; continue
        m = re.match(r"(#{1,4}) (.*)", s)
        if m:
            flush()
            out.append(heading(len(m.group(1)), m.group(2), toc))
            i += 1; continue
        if s == "---":
            flush(); out.append("<hr>"); i += 1; continue
        if s.startswith("|"):
            flush()
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            out.append(table(lines[i:j], with_visuals))
            i = j; continue
        if s.startswith("> "):
            flush()
            j = i
            quote = []
            while j < len(lines) and lines[j].strip().startswith(">"):
                quote.append(lines[j].strip()[1:].strip())
                j += 1
            out.append('<blockquote>' + inline(" ".join(quote)) + "</blockquote>")
            i = j; continue
        if re.match(r"([-*]|\d+\.) ", s):
            flush()
            ordered = bool(re.match(r"\d+\. ", s))
            tag = "ol" if ordered else "ul"
            items, j = [], i
            while j < len(lines):
                t = lines[j]
                if re.match(r"\s*([-*]|\d+\.) ", t) and not t.startswith("  "):
                    items.append(re.sub(r"^\s*([-*]|\d+\.) ", "", t).strip())
                elif t.startswith("  ") and t.strip() and items:
                    items[-1] += " " + t.strip()
                else:
                    break
                j += 1
            lis = "".join(f"<li>{inline(x)}</li>" for x in items)
            out.append(f"<{tag}>{lis}</{tag}>")
            i = j; continue
        para.append(s)
        i += 1
    flush()
    return "\n".join(out)


def page(title, current, body, toc):
    nav = "".join(
        f'<a href="{href}"{" aria-current=page" if href == current else ""}>{label}</a>'
        for _, href, label in PAGES
    )
    toc_html = ""
    if toc and current != "questions.html":
        links = "".join(f'<li><a href="#{hid}">{inline(t)}</a></li>' for hid, t in toc)
        toc_html = f'<details class="toc"><summary>On this page</summary><ol>{links}</ol></details>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light dark">
<title>{title} · {SITE}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="top"><a class="brand" href="index.html">{SITE}</a><nav>{nav}</nav></header>
<main>
{toc_html}
{body}
</main>
<footer><a href="#">Back to top</a></footer>
</body>
</html>
"""


PRINT_CSS = """
@page { size: Letter; margin: 0.6in 0.65in; }
:root { --bg:#fff; --fg:#111; --muted:#555; --line:#ccc; --card:#fff; --accent:#1d4aa8; --accent-soft:#eef2fb; --code:#f2f2f2; }
body { font-size: 10pt; line-height: 1.4; }
.card dt { display: inline; font-size: 7.5pt; margin: 0; }
.card dt::after { content: ": "; }
.card dd { display: inline; margin: 0; }
.card dd::after { content: "\\A"; white-space: pre; }
.card-title { margin-bottom: .15rem; }
.flow .box { padding: .25rem .5rem; font-size: 9pt; }
.flow .arrow { line-height: 1.1; }
h2 { margin: 1.4rem 0 .4rem; } h3 { margin: 1rem 0 .3rem; }
li { margin: .15rem 0; }
main { max-width: none; padding: 0; }
.part { break-before: page; }
.part:first-of-type { break-before: auto; }
.part-label { font-size: 9pt; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin: 0; }
h1 { font-size: 18pt; } h2 { font-size: 14pt; break-after: avoid; } h3, h4 { break-after: avoid; }
.q { break-before: page; }
.card, .pair, .box, li, blockquote, pre { break-inside: avoid; }
.cards { grid-template-columns: 1fr 1fr; gap: .45rem; }
.card { padding: .5rem .65rem; }
.card dt { margin-top: .25rem; }
.pair { display: grid; grid-template-columns: 2fr 3fr; gap: 1rem; padding: .35rem .7rem; }
details.answer > summary { display: none; }
.answer-body { border: 0; padding: 0; margin: 0; background: none; }
.answer-label { font-size: 9pt; text-transform: uppercase; letter-spacing: .08em; color: var(--accent); border-top: 1.5px solid var(--accent); padding-top: .3rem; margin-top: 1rem; }
#part-index { columns: 2; column-gap: .25in; font-size: 9pt; }
#part-index h1, #part-index .part-label, #part-index .tl, #part-index h1 + p { column-span: all; }
#part-index .phase, #part-index .cards, #part-index .chips { break-inside: avoid; }
#part-index .phase { padding: .35rem .6rem .15rem; margin: 0 0 .4rem; }
#part-index h2 { font-size: 11pt; margin: .6rem 0 .3rem; }
#part-index .cards { grid-template-columns: 1fr; }
#part-index .flow .box { padding: .1rem .3rem; font-size: 8pt; }
#part-index .flow .fi { width: 14px; height: 14px; }
#part-index .flow .box .detail { display: inline; margin-left: .3rem; }
#part-index .chips li { padding: .1rem .5rem; font-size: 8.5pt; }
.vis { padding: .1rem; margin: .2rem 0 .3rem; }
.vis svg.v { max-height: 1.5in; width: auto; max-width: 100% !important; }
.cover { height: 9in; display: flex; flex-direction: column; justify-content: center; }
.cover h1 { font-size: 30pt; margin: 0 0 .5rem; }
.cover ol { font-size: 12pt; }
"""


def strip_dark(css):
    """Drop every dark-mode block, so print always uses light colors."""
    key = "@media (prefers-color-scheme: dark)"
    while key in css:
        start = css.index(key)
        i, depth = css.index("{", start), 0
        while True:
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
            if depth == 0:
                break
        css = css[:start] + css[i:]
    return css


def build_print():
    """One printable HTML with every answer shown, for print/whiteboard-hour.pdf."""
    parts = []
    for src, _, label in PAGES:
        lines = (ROOT / "src" / src).read_text(encoding="utf-8").splitlines()
        body = render(lines, [], src in VISUAL_PAGES)
        body = body.replace("<details class=\"answer\">", "<details class=\"answer\" open>")
        body = body.replace('<div class="answer-body">', '<div class="answer-body"><p class="answer-label">Answer</p>')
        if src == "questions.md":
            body = re.sub(r'(<hr>\s*)?<h2 id="(q-[\w-]+|drills)"', r'<h2 class="q" id="\2"', body)
        body = re.sub(r'href="(index|components|questions)\.html"', lambda m: f'href="#part-{m.group(1)}"', body)
        dest_key = dict((p[0], p[1]) for p in PAGES)[src].split(".")[0]
        parts.append(f'<section class="part" id="part-{dest_key}"><p class="part-label">{label}</p>{body}</section>')
    cover = (
        f'<section class="cover"><h1>{SITE}</h1><p>System design for a small business with a big traffic spike.</p>'
        '<ol><li><a href="#part-index">Framework</a>: the six phases in 60 minutes</li>'
        '<li><a href="#part-components">Components</a>: the 23 parts you need, drawn</li>'
        '<li><a href="#part-questions">Sample questions</a>: 8 prompts with worked answers, then 20 follow-up drills</li></ol></section>'
    )
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    css = strip_dark(css)
    out = ROOT / "print"
    out.mkdir(exist_ok=True)
    (out / "whiteboard-hour.html").write_text(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{SITE}</title>'
        f"<style>{css}{PRINT_CSS}</style></head><body><main>{cover}{''.join(parts)}</main></body></html>",
        encoding="utf-8",
    )
    print("wrote print/whiteboard-hour.html")


def main():
    for src, dest, label in PAGES + EXTRA_PAGES:
        lines = (ROOT / "src" / src).read_text(encoding="utf-8").splitlines()
        toc = []
        body = render(lines, toc, src in VISUAL_PAGES)
        (ROOT / dest).write_text(page(label, dest, body, toc), encoding="utf-8")
        print("wrote", dest)
    build_print()
    if MISSING:
        print("NO VISUAL:", sorted(set(MISSING)))


if __name__ == "__main__":
    main()
