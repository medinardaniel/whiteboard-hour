"""Narration for the Merkle tree walkthrough: writes cues.json and SCRIPT.md here.

Each line: (scene function or "", narration, pause after in ms).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
TITLE = "Repository Merkle tree"
PRONOUNCE = {"io.py": "I O dot pie", "db.py": "D B dot pie", "app.py": "app dot pie", "a.md": "A dot M D", "b.md": "B dot M D", "c.md": "C dot M D",
             "SHA-256": "S H A two fifty six", "scandir": "scan dir", "hexdigest": "hex digest"}
CUES = [
    ("", "Repository Merkle tree. We'll build this from the ground up: what a Merkle tree is, what the problem asks, the idea in pictures, and then every line of code, tied back to its picture.", 1000),
    # what is it
    ("D1", "First, what is a Merkle tree? It's a tree where every node stores a fingerprint of everything below it. It's named after Ralph Merkle, who invented it, and Git uses the same idea to track your code. Let's build one up from nothing, starting with what a fingerprint is.", 1000),
    ("B3", "In code, a fingerprint is called a hash. A hash function takes any content, of any size, and returns a short string. We'll use SHA-256, which is built into Python.", 500),
    ("B4", "It has two properties that matter. The same content gives the same fingerprint, every time, on any machine.", 400),
    ("B5", "And if you change one character, the fingerprint is completely different. So comparing two short fingerprints tells you whether two files match, without comparing the files.", 1000),
    ("D2", "Now let's make a tree out of that. Take one folder, docs, with two files in it. A file's fingerprint is simply the hash of its content.", 500),
    ("D3", "But a folder has no content of its own. So its fingerprint is the hash of what's directly inside it: each child's name, and each child's hash. That single step is the whole idea.", 800),
    ("B6", "Do that at every level, and you have a Merkle tree. Each folder is hashed from its children, level by level, up to the top node, which is called the root. That one root hash depends on every file in the repo.", 500),
    ("B7", "Here's why that's useful. Change one file at the bottom. Its fingerprint changes, which changes its parent's, and so on, all the way up to the root.", 500),
    ("B8", "So here's the key insight. If two folders have the same fingerprint, everything inside them is the same, and you never have to look inside.", 1100),
    # the problem
    ("P1", "Now the problem, the way candidates report it. Build a Merkle tree over a real folder on disk, so that two snapshots of a repo can be compared quickly. You implement three methods, and you write your own tests.", 800),
    ("P2", "Build takes the path of a folder, and returns a tree: your own data structure, in memory.", 500),
    ("P3", "Get hash takes a path inside that tree, like source slash db.py, and returns the hash stored there.", 500),
    ("P4", "And diff takes two trees, and returns a list of what changed. Each item is a file path, plus the word added, removed, or modified.", 1000),
    ("E1", "Let's make that concrete. Here's a folder on Monday, and the same folder on Tuesday.", 500),
    ("E2", "Three things happened. io.py was edited. b.md was deleted. And c.md is new.", 500),
    ("E3", "So diff of Monday and Tuesday must return exactly this list. Everything else, like app.py and the whole lib folder, didn't change, so it doesn't appear. We'll use this example all the way through.", 1200),
    # background
    ("B1", "Why would anyone want this? A code editor keeps an index of your repo on a server, and has to keep it in sync as you work. The obvious way is to compare every file, one by one.", 500),
    ("B2", "On a hundred thousand files, that's a hundred thousand reads, to find one change. So the real constraint is this: find what changed, without reading what didn't. Comparing fingerprints gives us exactly that.", 1000),
    ("C1", "Before coding, ask a few questions, because each answer changes the code. What counts as a change? Content and names, but not timestamps, or two identical folders would look different.", 400),
    ("C2", "Is a rename special? Not at first. It shows up as one removed file, and one added file.", 400),
    ("C3", "Can files be huge? Assume yes, so read them in pieces. And symbolic links? Assume there are none, and say you'd skip them, so a link can't trap you in a loop.", 1100),
    # the plan
    ("L1", "So the plan is two moves. First, going bottom up, compute every hash, and store it on its node.", 400),
    ("L2", "Second, going top down, compare two trees, and only go inside where the hashes differ. The same comparison skips this whole branch, and finds that file.", 1000),
    ("N1", "Now the code, starting with the one data structure we need: a node. On the left is the picture of a node, and on the right is the code for it. Every node has a hash, which is a string.", 500),
    ("N2", "And it has children: a dictionary from a name to another node. A dictionary, because we look children up by name in one step, and a name can't appear twice.", 500),
    ("N3", "For a file, children is None. That's how the code tells a file from a folder.", 1000),
    # build: hash_file
    ("F1", "Next, hashing one file. This line creates a hasher, an object you feed bytes into. We feed it a tag first, the letter F, so a file can never be confused with a folder.", 500),
    ("F2", "This line opens the file. R B means read raw bytes, because a file might not be text. And the with keyword closes it for us when we're done.", 500),
    ("F3", "This loop reads sixty four kilobytes at a time. The walrus operator stores the chunk, and tests it too. At the end of the file the chunk is empty, so the loop stops.", 500),
    ("F4", "Each chunk goes into the hasher. That's the picture: pieces of the file going into the machine, one trip around the loop for each piece. So a huge file never has to fit in memory.", 500),
    ("F5", "When there's nothing left, hexdigest gives us the fingerprint as text.", 1000),
    # build: recursion
    ("G1", "Now build, the heart of it. We'll run it on the util folder, and watch each line against the picture. Is this path a folder? Yes, so we skip the first return.", 500),
    ("G2", "We start an empty dictionary for its children, and loop over what's in the folder. O S dot scandir lists the entries.", 500),
    ("G3", "There's one entry, io.py. And here's the key line: to fill in this child, build calls itself. That's recursion. The util call now waits, and a new call goes on the stack.", 500),
    ("G4", "In the new call, the path is a file. So this branch runs: hash the file, and return a node with no children.", 500),
    ("G5", "That call is done, so it comes off the stack. We're back in the util call, and the node goes into the dictionary, under its name.", 500),
    ("G6", "Now the folder's own hash. A new hasher, tagged D for directory. Then for each child, in sorted order, we feed in its name, a separator, and its hash. Sorted, because scandir can list files in any order, and the same folder must always give the same hash.", 500),
    ("G7", "Finally, we return a node holding the hash and the children. Util now has its fingerprint, in the picture and in the code.", 800),
    ("G8", "Now watch the whole tree, with the call stack growing and shrinking. Each folder call has to wait for its children to return. That's why the hashes appear from the bottom up. We never wrote anything that says bottom up. Recursion gives it to us.", 1200),
    # get_hash
    ("J1", "Get hash is the easy one. First, split the path into its parts: source, util, and io.py.", 400),
    ("J2", "Start at the root. Then for each part, step into that child. Each step is one dictionary lookup in the code, and exactly one arrow in the picture.", 500),
    ("J3", "When we run out of parts, we're standing on the right node, so we return its hash. If a part is missing, we raise a clear error. It costs one step per level, and it never reads a file.", 1100),
    # diff
    ("X1", "Now diff, with Monday on top and Tuesday below. The first line does the most work: compare the two hashes. The roots differ, so something below changed.", 500),
    ("X2", "Both are folders, so we skip those two checks. Then we take the union of both folders' names. The vertical bar means set union, so a name on either side gets visited: docs, lib, and source.", 500),
    ("X3", "Start with docs. It's on both sides, so we call diff on the pair. It's the same function, one level down. Their hashes differ, so we go in.", 500),
    ("X4", "a.md is on both sides, so diff runs again, and the first line fires. Same hash, return nothing.", 400),
    ("X5", "b.md is in the old folder, and not the new one. That's this branch: removed.", 400),
    ("X6", "c.md is in the new folder, and not the old one. That's this branch: added.", 600),
    ("X7", "Next, lib. Same call, and the same first line, but look what it means here. Same hash, return nothing. The whole folder is skipped, and its files are never touched. That one line is the whole point of a Merkle tree.", 800),
    ("X8", "Last, source. The hashes differ, so we go in. app.py and db.py match, and return nothing. Util differs, so we go in.", 400),
    ("X9", "Now we reach io.py. Both sides are files, with different hashes. That's this branch: modified.", 500),
    ("X10", "And there's the list we expected for Monday and Tuesday.", 800),
    ("X11", "One more case. If a path is a file on one side and a folder on the other, this line reports the old as removed, and the new as added. The helper called files walks a whole subtree, and lists every file in it. The same helper handles a brand new folder.", 800),
    ("G9", "What did we gain? With folders five deep and ten entries each, one changed file costs about fifty comparisons, not a hundred thousand. Building reads every file once. After that, diff only walks the branches that changed.", 1100),
    # tests
    ("Q1", "The prompt asks you to write tests. Make a helper that creates a real temporary folder, writes the files, and builds the tree. Python deletes the folder when the with block ends.", 500),
    ("Q2", "Then write one assert per case: identical folders, a nested edit, our Monday to Tuesday example, a rename, and a file that became a folder.", 800),
    ("Q3", "Here's how that fits in the hour, in the order you'd type it. Five minutes to clarify. Then Node and hash file. Then build, get hash, and diff, each with a test before you start the next, so a bug can only be in what you just wrote. That leaves time for edge cases and follow-ups.", 1100),
    # follow-ups
    ("U1", "Expect follow-ups. If one file changes after build, don't rebuild. Rehash that file, then only its parents, up to the root. It's the same folder hashing loop, run once per level.", 500),
    ("U2", "If the trees are on two machines, send the root hash first. If it differs, ask for the children's hashes, and go down only where they differ. It's the same diff, with a network call at each step.", 500),
    ("U3", "And to detect renames, compare the removed and added files. A file's hash comes only from its content, so a matching hash means it moved.", 1000),
    # the full solution
    ("S1", "Here's the full solution, all on one screen. You've now seen every line of it. Pause here if you want to read it through.", 2500),
    ("S2", "At a high level, it has five pieces. Node is the data structure: a hash, and a dictionary of children. Hash file reads a file in chunks, and returns its fingerprint.", 500),
    ("S3", "Build walks the real folder with recursion. A file returns its hash. A folder builds its children first, then hashes their names and hashes, in sorted order.", 500),
    ("S4", "Get hash walks down the stored tree, one dictionary lookup per part of the path.", 500),
    ("S5", "Diff compares two trees from the top. If the hashes match, it stops. If two files differ, that's modified. For two folders, it loops over the union of their names: only in the new one is added, only in the old one is removed, and on both sides it goes deeper.", 500),
    ("S6", "And files is a small helper that lists every file under a node.", 800),
    ("S7", "As for cost: build reads every byte once. Get hash takes one step per level. And diff only walks the branches that changed.", 1000),
    # recap
    ("R1", "Let's tie the pictures to the code. Hashes rising up the tree are build's recursion returning.", 400),
    ("R2", "Skipping a whole folder is one line: if the hashes match, return nothing.", 400),
    ("R3", "And the three results are three branches: only in the new tree is added, only in the old tree is removed, and two different files is modified.", 1000),
    ("Z1", "The one line to remember: hash bottom up, compare top down, and skip every subtree whose hash matches.", 1500),
]

spec = {"target": "index.html", "viewport": [1920, 1080], "voice": "en-US-AndrewMultilingualNeural", "rate": "+4%",
        "pronounce": PRONOUNCE, "load_ms": 1200, "gap_ms": 400, "tail_ms": 1500, "cues": []}
lines = [f"# {TITLE}: walkthrough video", "", "Each numbered line is one step on screen. *(pause)* marks a break of a second or more.", ""]
for i, (fn, say, post) in enumerate(CUES, 1):
    cue = {"say": say, "post_ms": post}
    if fn:
        cue.update({"do": f"js:setTimeout({fn}, 0)", "settle_ms": 350})
    spec["cues"].append(cue)
    lines.append(f"{i}. `{fn or 'title'}` {say}" + (" *(pause)*" if post >= 1000 else ""))
(HERE / "cues.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False), encoding="utf-8")
(HERE / "SCRIPT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(sum(len(c[1].split()) for c in CUES), "words", len(CUES), "cues")
