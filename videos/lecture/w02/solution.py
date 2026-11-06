"""The code shown in the streaming parser walkthrough. The interface is one clean option: reports differ.

    python solution.py          run the tests
    python solution.py --data   also write data.js: the real trace and source the video shows
"""
import json
import random
import sys
from pathlib import Path

TEXT, INLINE, FENCE = "text", "inline", "fence"
TICK = "`"


class StreamParser:
    def __init__(self):
        self.state = TEXT
        self.ticks = 0    # backticks held, not yet decided
        self.buf = []     # characters waiting to go out

    def feed(self, chunk):
        out = []
        for ch in chunk:
            if ch == TICK:
                self._tick(out)
            else:
                self._settle(out)
                self.buf.append(ch)
        self._flush(out)
        return out

    def finish(self):
        out = []
        if self.ticks:
            out.append((self.state, TICK * self.ticks))
            self.ticks = 0
        return out

    def _tick(self, out):
        if self.state == INLINE:
            self._switch(TEXT, out)
            return
        self.ticks += 1
        if self.ticks == 3:
            self.ticks = 0
            target = TEXT if self.state == FENCE else FENCE
            self._switch(target, out)

    def _settle(self, out):
        if self.ticks == 1 and self.state == TEXT:
            self.ticks = 0
            self._switch(INLINE, out)
        elif self.ticks:
            self.buf.append(TICK * self.ticks)
            self.ticks = 0

    def _switch(self, state, out):
        self._flush(out)
        self.state = state

    def _flush(self, out):
        if self.buf:
            out.append((self.state, "".join(self.buf)))
            self.buf = []


def merged(events):
    res = []
    for kind, text in events:
        if res and res[-1][0] == kind:
            res[-1] = (kind, res[-1][1] + text)
        else:
            res.append((kind, text))
    return res


def run(chunks):
    p = StreamParser()
    events = []
    for c in chunks:
        events += p.feed(c)
    return merged(events + p.finish())


def random_cuts(s):
    cuts = sorted(random.sample(range(len(s) + 1), random.randint(0, min(len(s), 5))))
    return [s[i:j] for i, j in zip([0] + cuts, cuts + [len(s)])]


SAMPLE = "Use `x` then ```py\nprint(1)\n``` done"
CHUNKS = ["Use `x` th", "en `", "``py\npr", "int(1)\n`", "``", " done"]
NASTY = [SAMPLE, "a``b", "`a", "```a", "a`", "a``", "```a``b```c", "````", "`a``b`", "```a`b```", "", "``````", "x```"]


def trace(chunks):
    """One snapshot after every character, taken from the real parser."""
    p = StreamParser()
    steps, done = [], []

    def snap(n, i, out):
        steps.append({"chunk": chunks[n], "n": n, "total": len(chunks), "i": i, "state": p.state, "ticks": p.ticks,
                      "buf": "".join(p.buf), "out": list(out), "shown": merged(done + out)})

    for n, chunk in enumerate(chunks):
        out = []
        for i, ch in enumerate(chunk):
            if ch == TICK:
                p._tick(out)
            else:
                p._settle(out)
                p.buf.append(ch)
            snap(n, i, out)
        p._flush(out)
        snap(n, -1, out)
        done += out
    return steps


if __name__ == "__main__":
    want = [("text", "Use "), ("inline", "x"), ("text", " then "), ("fence", "py\nprint(1)\n"), ("text", " done")]
    # the worked example in the video, however it's cut
    assert run([SAMPLE]) == want
    assert run(list(SAMPLE)) == want
    assert run(CHUNKS) == want
    # any random cut gives the same answer as no cuts at all
    random.seed(1)
    for s in NASTY:
        for _ in range(300):
            assert run(random_cuts(s)) == run([s]), s
    # one chunk can hold several changes of state
    assert StreamParser().feed("Use `x` th") == [("text", "Use "), ("inline", "x"), ("text", " th")]
    # two backticks mean nothing, and a lone backtick inside a fence is just code
    assert run(["a``b"]) == [("text", "a``b")]
    assert run(["```a`b```c"]) == [("fence", "a`b"), ("text", "c")]
    # the end of the stream settles what's held, and an unclosed span stays styled
    assert run(["a``"]) == [("text", "a``")]
    assert run(["`a"]) == [("inline", "a")]
    assert run(["```py\npr"]) == [("fence", "py\npr")]
    # optimistic styling: code is styled before the closing backtick arrives
    assert StreamParser().feed('`print("hello wor') == [("inline", 'print("hello wor')]
    # at most two backticks are ever held between chunks
    for s in NASTY:
        p = StreamParser()
        for ch in s:
            p.feed(ch)
            assert p.ticks <= 2 and p.buf == []
    print("parser ok")

    if "--data" in sys.argv:
        src = Path(__file__).read_text(encoding="utf-8").split("\n")
        start, end = src.index('TEXT, INLINE, FENCE = "text", "inline", "fence"'), src.index("def merged(events):")
        body = src[start:end]
        while not body[-1].strip():
            body.pop()
        cut = body.index("    def _tick(self, out):")
        left = body[:cut]
        while not left[-1].strip():
            left.pop()
        events = []
        p = StreamParser()
        for c in CHUNKS:
            events.append(p.feed(c))
        data = {"SAMPLE": SAMPLE, "CHUNKS": CHUNKS, "EVENTS": events, "FINAL": want, "TR": trace(CHUNKS), "TR2": trace(["a``b"]), "TR3": trace(["a``"]),
                "TR4": trace(["```py\npr"]), "FULL": {"left": left, "right": body[cut:]}}
        js = "".join(f"window.{k} = {json.dumps(v)};\n" for k, v in data.items())
        Path(__file__).with_name("data.js").write_text(js, encoding="utf-8")
        print("data.js:", len(data["TR"]), "steps; full solution", len(left), "+", len(body[cut:]), "lines")
