"""Build one narrated-video deck + cue file per core component, from cards.py.

    python videos/make_videos.py            # writes videos/deck/cNN.html, videos/cues/cNN.json, videos/SCRIPT.md

Each deck is a 1920x1080 slideshow (ArrowRight advances or reveals the next step). The cue files are recorded
with the demo skill's make_demo.py, which narrates each cue while the deck is on screen.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import cards  # noqa: E402
import visuals  # noqa: E402

PHASE = {
    "v1": ("Version 1", "version one, when you draw the basic design"),
    "invariants": ("Protect the invariants", "version one and the spike, to protect what must never break"),
    "spike": ("Survive the spike", "the spike defenses"),
    "third": ("Third parties", "version one, wherever you call an outside service"),
    "golive": ("Go-live", "go-live prep"),
}

PRONOUNCE = {
    "CDN": "C D N", "DNS": "D N S", "API": "A P I", "APIs": "A P Is", "SQL": "sequel", "HTTPS": "H T T P S",
    "WAF": "waff", "DDoS": "D dos", "PCI": "P C I", "RPO": "R P O", "RTO": "R T O", "SLO": "S L O",
    "TTL": "T T L", "k6": "K six", "PgBouncer": "P G bouncer", "Redis": "reddis", "ECS": "E C S",
    "Multi-AZ": "multi A Z", "ACID": "acid", "429": "four twenty-nine", "SMS": "S M S", "a7f3": "A 7 F 3",
    "Pub/sub": "pub sub", "OK": "okay", "TVs": "T Vs", "TV": "T V", "IP": "I P", "IPs": "I Ps", "CPU": "C P U",
    "PDFs": "P D Fs", "URL": "U R L", "AM": "A M", "PM": "P M", "SELECT": "select", "UPDATE": "update",
    "FOR": "for", "id": "I D", "ids": "I Ds", "DynamoDB": "Dynamo D B",
    "Kubernetes": "kubernetes", "Cloud Run": "Cloud Run", "Locust": "locust", "Queue-it": "queue it",
}


def speak(t):
    """Rewrite card text for the ear."""
    t = re.sub(r"(?<!\w)'|'(?!\w)", "", t).replace('"', "")
    t = re.sub(r"\bp95\b", "p ninety-five", t)
    t = re.sub(r"(\d)\s?x\b", r"\1 times", t)
    t = re.sub(r"(\d[\d,]*)\s?/s\b", r"\1 a second", t)
    t = t.replace("requests/s", "requests a second").replace("writes/s", "writes a second")
    t = re.sub(r"\b1 s\b", "1 second", t)
    t = re.sub(r"(\d) s\b", r"\1 seconds", t)
    t = re.sub(r"(\d) ?ms\b", r"\1 milliseconds", t)
    t = re.sub(r"(\d) min\b", r"\1 minutes", t)
    t = re.sub(r"(\d) MB\b", r"\1 megabytes", t)
    t = t.replace("~", "about ").replace(" = ", " equals ").replace(" vs ", " versus ")
    t = t.replace("2+", "two or more").replace("(ACID)", "").replace("DB", "database")
    t = t.replace(" < ", " under ").replace(" > ", " over ").replace("$24", "24 dollars")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def sentence(t):
    t = t.strip()
    return t if t.endswith((".", "?", "!", ":")) else t + "."


def join_list(xs):
    xs = [x[0].lower() + x[1:] if not x[:2].isupper() else x for x in xs]
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + ", and " + xs[-1]


def build(c, phase_key, total):
    n = c["num"]
    label, phrase = PHASE[phase_key]
    svg = visuals.visual_for(c["title"])
    ic = visuals.icon_svg
    code = f'<pre class="code">{html.escape(c["code"])}</pre>' if c["code"] else ""
    li = lambda xs, cls, extra="": "".join(
        f'<li class="step {cls}">{html.escape(x)}{extra if k == 0 else ""}</li>' for k, x in enumerate(xs))
    tags = "".join(f'<span class="tag">{html.escape(u)}</span>' for u in c["use"])
    terms = "".join(f'<div class="term step"><b>{html.escape(t)}</b><span>{html.escape(d)}</span></div>' for t, d in c["also"])
    bad, good = c["labels"]
    slides = [
        f'''<section class="slide s-title"><div class="kicker">{label} · Component {n} of {total}</div>
<h1><span class="num">{n}</span>{html.escape(c["title"])}</h1><div class="dia">{svg}</div>
<p class="plain">{html.escape(c["plain"])}</p></section>''',
        f'''<section class="slide s-analogy"><h2>Think of it as</h2>
<div class="analogy">{ic("bulb", 64)}<span>{html.escape(c["analogy"])}</span></div>
<h2>Use it for</h2><div class="tags">{tags}</div></section>''',
        f'''<section class="slide s-scene"><div class="scene">{ic("doc", 52)}<span><b>Scenario.</b> {html.escape(c["setup"])}</span></div>
<div class="vs"><div class="side bad"><div class="side-h">{ic("x", 34)}{bad}</div><ol>{li(c["without"], "w")}</ol></div>
<div class="side good"><div class="side-h">{ic("check", 34)}{good}</div><ol>{li(c["with_"], "g", code)}</ol></div></div></section>''',
        f'''<section class="slide s-why"><div class="why"><b>Why it works</b><span>{html.escape(c["why"])}</span></div>
<div class="say step">{ic("chat", 56)}<span>"{html.escape(c["say"])}"</span></div></section>''',
        f'''<section class="slide s-terms"><h2>Related terms</h2><div class="terms">{terms}</div></section>''',
    ]
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="color-scheme" content="light">
<title>{n}. {html.escape(c["title"])}</title><link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="deck.css"></head>
<body class="deck">{"".join(slides)}<script src="deck.js"></script></body></html>'''

    cues = [{"say": speak(f"Component {n}: {c['title']}. {sentence(c['plain'])} You'll bring this up during {phrase}.")}]
    cues.append({"do": "press:ArrowRight", "say": speak(f"Think of it as: {sentence(c['analogy'])} Use it for {join_list(c['use'])}.")})
    cues.append({"do": "press:ArrowRight", "say": speak(f"Here's a real scenario. {sentence(c['setup'])}")})
    for i, s in enumerate(c["without"]):
        pre = f"{bad}: " if i == 0 else ""
        cues.append({"do": "press:ArrowRight", "settle_ms": 450, "say": speak(pre + sentence(s))})
    for i, s in enumerate(c["with_"]):
        pre = f"{good}: " if i == 0 else ""
        line = speak(pre + sentence(s))
        if i == 0 and c["code"]:
            line = "With it: both run this one statement. It subtracts one only where at least one is left."
        cues.append({"do": "press:ArrowRight", "settle_ms": 450, "say": line})
    cues.append({"do": "press:ArrowRight", "say": speak(f"Why it works: {sentence(c['why'])}")})
    cues.append({"do": "press:ArrowRight", "settle_ms": 450, "say": speak(f"In the interview, say: {sentence(c['say'])}")})
    cues.append({"do": "press:ArrowRight", "say": "A few related terms you may hear."})
    for t, d in c["also"]:
        cues.append({"do": "press:ArrowRight", "settle_ms": 400, "say": speak(f"{t}: {sentence(d)}")})
    cues[-1]["post_ms"] = 900
    spec = {
        "target": f"deck/c{n:02d}.html",
        "viewport": [1920, 1080], "voice": "en-US-AndrewMultilingualNeural", "rate": "+2%",
        "pronounce": PRONOUNCE, "load_ms": 1800, "gap_ms": 450, "tail_ms": 1500, "cues": cues,
    }
    return page, spec


def main():
    (HERE / "deck").mkdir(exist_ok=True)
    (HERE / "cues").mkdir(exist_ok=True)
    order = [(k, c) for k, cs in cards.SECTIONS.items() for c in cs]
    script = ["# Component videos: narration script", "",
              "One video per component. Each cue is one visual step; the voice reads the line while it is on screen.", ""]
    for k, c in order:
        page, spec = build(c, k, len(order))
        (HERE / "deck" / f"c{c['num']:02d}.html").write_text(page, encoding="utf-8")
        (HERE / "cues" / f"c{c['num']:02d}.json").write_text(json.dumps(spec, indent=1), encoding="utf-8")
        words = sum(len(q["say"].split()) for q in spec["cues"])
        script.append(f"## {c['num']} · {c['title']}  (~{words} words, {len(spec['cues'])} steps)")
        script.append("")
        script += [f"{i + 1}. {q['say']}" for i, q in enumerate(spec["cues"])]
        script.append("")
    script += ["## Pronunciation", "", "| On screen | Spoken |", "|---|---|"]
    script += [f"| {k} | {v} |" for k, v in PRONOUNCE.items()]
    (HERE / "SCRIPT.md").write_text("\n".join(script) + "\n", encoding="utf-8")
    print("built", len(order), "decks")


if __name__ == "__main__":
    main()
