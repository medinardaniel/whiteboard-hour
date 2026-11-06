"""Run every answer key in src/coding.md: each question's python blocks, in order, after the shared helper.

    python check_coding.py
"""
import re
import sys
from pathlib import Path

text = (Path(__file__).parent / "src" / "coding.md").read_text(encoding="utf-8")
blocks = lambda s: re.findall(r"^```python\n(.*?)^```", s, re.S | re.M)
head, *sections = re.split(r"\n## ", text)
prelude = "\n".join(blocks(head))
failed = 0
for sec in sections:
    title = sec.splitlines()[0]
    try:
        exec(prelude + "\n" + "\n".join(blocks(sec)), {"__name__": "check"})
        print("PASS", title)
    except Exception as e:
        failed += 1
        print("FAIL", title, type(e).__name__, e)
sys.exit(1 if failed else 0)
