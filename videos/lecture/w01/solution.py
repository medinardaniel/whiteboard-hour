"""The code shown in the Merkle tree walkthrough.

    python solution.py            run the tests
    python solution.py --hashes   also write hashes.js: the real hashes the video shows
"""
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Node:
    hash: str
    children: dict = None      # name -> Node. None means a file


def hash_file(path):
    h = hashlib.sha256(b"F\0")
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class MerkleTree:
    def build(self, path):
        if not os.path.isdir(path):
            return Node(hash_file(path))
        children = {}
        for entry in os.scandir(path):
            children[entry.name] = self.build(entry.path)
        h = hashlib.sha256(b"D\0")
        for name in sorted(children):
            h.update(f"{name}\0{children[name].hash}\n".encode())
        return Node(h.hexdigest(), children)

    def get_hash(self, path, tree):
        node = tree
        for part in [p for p in path.split("/") if p]:
            if node.children is None or part not in node.children:
                raise KeyError(path)
            node = node.children[part]
        return node.hash

    def diff(self, a, b, path=""):
        if a.hash == b.hash:
            return []
        if a.children is None and b.children is None:
            return [(path, "MODIFIED")]
        if a.children is None or b.children is None:
            return files(a, path, "REMOVED") + files(b, path, "ADDED")
        old, new = a.children, b.children
        changes = []
        for name in sorted(old.keys() | new.keys()):
            child = f"{path}/{name}" if path else name
            if name not in old:
                changes += files(new[name], child, "ADDED")
            elif name not in new:
                changes += files(old[name], child, "REMOVED")
            else:
                changes += self.diff(old[name], new[name], child)
        return changes


def files(node, path, kind):
    if node.children is None:
        return [(path, kind)]
    found = []
    for name in sorted(node.children):
        found += files(node.children[name], f"{path}/{name}", kind)
    return found


def tree(file_map, dirs=()):
    with tempfile.TemporaryDirectory() as d:
        for rel in dirs:
            Path(d, rel).mkdir(parents=True, exist_ok=True)
        for rel, text in file_map.items():
            p = Path(d, rel)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        return MerkleTree().build(d)


MONDAY = {"src/app.py": "print(1)", "src/db.py": "connect()", "src/util/io.py": "read()",
          "docs/a.md": "# A", "docs/b.md": "# B", "lib/x.py": "x = 1", "lib/y.py": "y = 2"}
TUESDAY = {"src/app.py": "print(1)", "src/db.py": "connect()", "src/util/io.py": "read(path)",
           "docs/a.md": "# A", "docs/c.md": "# C", "lib/x.py": "x = 1", "lib/y.py": "y = 2"}


def short(node):
    return node.hash[:4]


def table(t):
    s, d, l, u = t.children["src"], t.children["docs"], t.children["lib"], t.children["src"].children["util"]
    out = {"root": short(t), "src": short(s), "docs": short(d), "lib": short(l), "util": short(u),
           "app": short(s.children["app.py"]), "db": short(s.children["db.py"]), "io": short(u.children["io.py"]),
           "am": short(d.children["a.md"]), "xx": short(l.children["x.py"]), "yy": short(l.children["y.py"])}
    out["bm"] = short(d.children["b.md"] if "b.md" in d.children else d.children["c.md"])
    return out


if __name__ == "__main__":
    m = MerkleTree()
    a, b = tree(MONDAY), tree(TUESDAY)
    # the worked example in the video
    assert m.diff(a, b) == [("docs/b.md", "REMOVED"), ("docs/c.md", "ADDED"), ("src/util/io.py", "MODIFIED")]
    # identical folders: different temp paths, same hash
    assert m.diff(a, tree(MONDAY)) == [] and a.hash == tree(MONDAY).hash
    # a nested edit
    assert m.diff(a, tree({**MONDAY, "src/util/io.py": "new"})) == [("src/util/io.py", "MODIFIED")]
    # lookup walks down, and a miss is an error
    assert m.get_hash("src/util/io.py", a) == a.children["src"].children["util"].children["io.py"].hash
    assert m.get_hash("", a) == a.hash
    for bad in ("src/nope.py", "src/app.py/x"):
        try:
            m.get_hash(bad, a)
            raise AssertionError(bad)
        except KeyError:
            pass
    # a rename is a removal plus an addition, and its content hash matches
    x, y = tree({"x": "1"}), tree({"y": "1"})
    assert m.diff(x, y) == [("x", "REMOVED"), ("y", "ADDED")]
    assert x.children["x"].hash == y.children["y"].hash
    # a file became a folder, and a whole folder added
    assert m.diff(tree({"p": "1"}), tree({"p/q": "1"})) == [("p", "REMOVED"), ("p/q", "ADDED")]
    assert m.diff(tree({"a": "1"}), tree({"a": "1", "d/e/f": "2"})) == [("d/e/f", "ADDED")]
    # an empty file and an empty folder hash differently
    assert tree({"p": ""}).hash != tree({}, dirs=["p"]).hash
    # the order files are written can't change the hash
    assert tree({"a": "1", "b": "2"}).hash == tree({"b": "2", "a": "1"}).hash
    print("merkle ok")

    if "--hashes" in sys.argv:
        demo = {}
        for key, text in (("demo1", "print(1)"), ("demo2", "print(2)")):
            demo[key] = hashlib.sha256(b"F\0" + text.encode()).hexdigest()[:4]
        data = {"old": table(a), "new": table(b), **demo}
        Path(__file__).with_name("hashes.js").write_text("window.H = " + json.dumps(data) + ";\n", encoding="utf-8")
        print(data)
        # the full solution screen shows this exact source, so it can't drift from the tested code
        src = Path(__file__).read_text(encoding="utf-8").split("\n")
        start, end = src.index("@dataclass"), next(i for i, l in enumerate(src) if l.startswith("def tree("))
        body = src[start:end]
        while not body[-1].strip():
            body.pop()
        cut = body.index("    def get_hash(self, path, tree):")
        left = ["import hashlib", "import os", "from dataclasses import dataclass", "", ""] + body[:cut]
        while not left[-1].strip():
            left.pop()
        full = {"left": left, "right": body[cut:]}
        Path(__file__).with_name("fullcode.js").write_text("window.FULL = " + json.dumps(full) + ";\n", encoding="utf-8")
        print("full solution:", len(left), "+", len(body[cut:]), "lines")
