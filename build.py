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

ROOT = Path(__file__).parent
PAGES = [
    ("framework.md", "index.html", "Framework"),
    ("components.md", "components.html", "Components"),
    ("questions.md", "questions.html", "Questions"),
]
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


def table(lines):
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
        out.append(f'<div class="card"><div class="card-title">{title}</div><dl>{dl}</dl></div>')
    out.append("</div>")
    return "".join(out)


def flow(lines):
    rows = []
    for line in lines:
        boxes = []
        for b in line.split(" | "):
            name, _, detail = b.partition(": ")
            d = f'<span class="detail">{inline(detail)}</span>' if detail else ""
            boxes.append(f'<div class="box"><strong>{inline(name)}</strong>{d}</div>')
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


def render(lines, toc):
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
        if s.startswith("::: answer"):
            flush()
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
            inner = render(lines[i + 1 : j], [])
            out.append(
                '<details class="answer"><summary><span class="show">See answer</span>'
                '<span class="hide">Hide answer</span></summary>'
                f'<div class="answer-body">{inner}</div></details>'
            )
            i = j + 1; continue
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            j = i + 1
            while not lines[j].strip().startswith("```"):
                j += 1
            body = lines[i + 1 : j]
            if lang == "flow":
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
            out.append(table(lines[i:j]))
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


def main():
    for src, dest, label in PAGES:
        lines = (ROOT / "src" / src).read_text(encoding="utf-8").splitlines()
        toc = []
        body = render(lines, toc)
        (ROOT / dest).write_text(page(label, dest, body, toc), encoding="utf-8")
        print("wrote", dest)


if __name__ == "__main__":
    main()
