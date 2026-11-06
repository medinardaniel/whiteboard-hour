"""Screenshot a lecture page at chosen moments, to check animations before recording.

    python videos/lecture/preview.py c01 "S1:2500" "S2:3000" "S3:7500" ...

Each step calls the scene function, waits the given ms, and saves shot_NN.png in videos/lecture/<id>/preview/.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

here = Path(__file__).parent / sys.argv[1]
out = here / "preview"
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto((here / "index.html").resolve().as_uri())
    pg.wait_for_timeout(800)
    for i, step in enumerate(sys.argv[2:]):
        fn, _, ms = step.partition(":")
        if fn != "-":
            pg.evaluate(f"setTimeout(() => window.{fn} && window.{fn}(), 0)")
        pg.wait_for_timeout(int(ms or 1500))
        pg.screenshot(path=str(out / f"shot_{i:02d}.png"))
        print(out / f"shot_{i:02d}.png")
    b.close()
