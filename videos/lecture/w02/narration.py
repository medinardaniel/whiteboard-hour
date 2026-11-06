"""Narration for the streaming parser walkthrough: writes cues.json and SCRIPT.md here.

Each line: (scene function or "", narration, pause after in ms).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
TITLE = "Streaming text parser"
PRONOUNCE = {}
CUES = [
    ("", "Streaming text parser. We'll build it from the ground up: what the words mean, what the problem asks, the idea in pictures, and then every line of code, tied back to its picture.", 1000),
    # the words
    ("D1", "First, the words. Markdown is a way to style plain text using small marks. On the left is the raw text a language model actually sends. On the right is what the reader should see.", 600),
    ("D2", "The mark we care about is this character, the backtick. Put one backtick on each side of a few characters, and that's inline code: a bit of code inside a sentence.", 500),
    ("D3", "Three backticks in a row open a code block, which is also called a code fence. Everything after that is code, until three more backticks close it. The letters right after the opening, here P Y, name the language.", 800),
    ("D4", "A parser is code that reads raw text, and works out what each part means. Here that means labeling every part as plain text, inline code, or fence.", 800),
    ("D5", "Now, streaming. A language model doesn't send its reply all at once. It sends small pieces as it writes them. Each piece is called a chunk.", 500),
    ("D6", "And the cuts land anywhere. Look at these two chunks: the cut goes right through the middle of three backticks. You don't choose where the cuts land.", 500),
    ("D7", "So a streaming parser handles each chunk as it arrives, instead of waiting for the whole reply. The reader sees the styled text grow, piece by piece.", 1000),
    # the problem
    ("P1", "Now the problem, the way candidates report it. Text from a model arrives in chunks. As each chunk arrives, work out what can be shown, and how it's styled. Reports differ on the exact interface, so here's a clean one you can propose.", 500),
    ("P2", "Feed takes one chunk, and returns a list of events. An event is just a pair: a kind, and some text.", 400),
    ("P3", "Finish is called once, when the stream ends. It returns anything that's still waiting.", 900),
    ("E1", "Let's make that concrete. Here's our text, cut into six chunks. We'll use this example all the way through.", 400),
    ("E2", "Feed gets called six times, and these are the events that come back. Notice the fifth chunk returns nothing at all, and that's fine.", 1000),
    ("E3", "Put them together, and this is what's on screen.", 1000),
    ("P4", "There are three rules. First: the result can't depend on where the cuts landed. Here's the same text, cut three different ways, and the same styled text every time.", 700),
    ("P5", "Second: style it as soon as you can. Once you know you're in code, show it as code, even before the closing backtick arrives. This is called optimistic styling.", 500),
    ("P6", "Third: never take back what's on screen. Events only add to the end. So a reader can select some text, while the reply is still arriving, and the selection stays put.", 1000),
    # why it's hard
    ("B1", "Why is this hard? The obvious way to avoid the cuts is to wait for the whole reply, then parse it. But then the reader stares at a blank screen until the very end.", 400),
    ("B2", "Next idea: on every chunk, parse everything so far, and redraw it all. It gives the right answer, but the screen is replaced over and over, the reader's selection is lost, and the work grows with every chunk.", 600),
    ("B3", "So parse each chunk on its own? That breaks too. This chunk ends in one backtick, so it looks like inline code. The next one starts with two, which looks like nothing.", 400),
    ("B4", "The real answer is three, a code fence, and neither chunk can see that. So the real constraint is this: one pass, one character at a time, remembering just enough between chunks to pick up where you left off.", 1000),
    ("C1", "Before coding, ask a few questions, because each answer changes the code. What if the stream ends inside code? Then it stays code. It's already on screen.", 400),
    ("C2", "What about two backticks on their own? Treat them as ordinary characters.", 400),
    ("C3", "A single backtick inside a fence? That's ordinary code. Only three in a row close a fence.", 400),
    ("C4", "And the language name, or a fence in the middle of a line? Keep it simple first, and handle those as follow-ups.", 1000),
    # the plan
    ("L1", "Now the plan. The tool is called a state machine. It's a thing that's in exactly one state at a time, and each input may move it to another state. A traffic light is one. It's always exactly one color, and a timer moves it on.", 600),
    ("L2", "Ours has three states: text, inline, and fence. One backtick moves between text and inline. Three move between text and fence. And every character we read belongs to whichever state we're in.", 800),
    ("L3", "Here's the catch. You read one backtick. What does it mean? If a letter comes next, it opened inline code. If two more come, it's a fence. If one more comes and then a letter, it was just two ordinary characters.", 500),
    ("L4", "You can't know yet, so don't decide. Hold it, and keep a count. When a character that isn't a backtick arrives, or the count hits three, you can finally decide.", 500),
    ("L5", "That's the whole design. Between chunks, the parser only has to remember two things: the state it's in, and how many backticks it's holding.", 1100),
    # state
    ("N1", "Now the code, starting with what the parser remembers. On the left is the picture, and on the right is the code for it. State is which of these three boxes is lit. It starts as text.", 500),
    ("N2", "Ticks is the count of held backticks: how many of these slots are full.", 500),
    ("N3", "And buff, short for buffer, is a list of characters waiting to go out. A buffer is just a temporary holding area. It's a list, because adding to a list is cheap, and joining it at the end is the usual way to build a string in Python.", 1000),
    # feed
    ("F1", "Now feed, with the first chunk. Out is the list of events this call will return. It's a local variable, so it disappears when the call ends. That will matter soon.", 500),
    ("F2", "The loop looks at one character at a time. The first is U. It isn't a backtick, so we take the else branch. Settle deals with any held backticks. There are none, so it does nothing. Then the letter goes into the buffer.", 400),
    ("F3", "The same for S, E, and the space. That's the plain path: one trip around the loop, one tile in the buffer.", 800),
    # the backticks
    ("K1", "Now a backtick, so we call tick. The state isn't inline, so we skip that branch. The count goes up to one. It isn't three, so we're done. Notice that nothing was decided. The backtick went into a slot, not the buffer.", 600),
    ("K2", "Next, X. It isn't a backtick, so settle runs first, and this is where the decision happens. One held, and we're in text. So that backtick opened inline code. Reset the count, and switch.", 500),
    ("K3", "Switch does two things, in this order. First it flushes, because the characters in the buffer belong to the old state. Flush joins them into one string, adds an event with the current state, and empties the buffer. Only then does the state change.", 700),
    ("K4", "Back in feed, X goes into the buffer, now in the inline state. The next character is a backtick. In inline, one backtick always closes it. So we switch back to text, and that flushes X as inline code.", 600),
    ("K5", "The space, T, and H go into the buffer, and the chunk runs out. This last line flushes what's left, so the reader sees it now, not later. One chunk gave us three events, and two changes of state. A chunk can hold any number of them.", 900),
    ("K6", "The second chunk is the tricky one. E, N, and a space. Then a backtick: the count goes to one, and the chunk ends. Feed flushes the text, and returns, so out is gone. But ticks lives on self, on the object, so it survives until the next call. That's how we remember across a cut.", 800),
    ("K7", "Third chunk. Two more backticks. One makes two. The next makes three, so this branch fires. Reset the count, and pick the new state. This is Python's one-line if: if we're in a fence, go to text, otherwise go to fence. So the same line opens and closes.", 600),
    ("K8", "Now we're in the fence. P Y, a newline, P R. They all go through the buffer, and come out labeled fence. The next chunk does the same, and it ends with one backtick held, again.", 500),
    ("K9", "The fifth chunk is only two backticks. That makes three, so the fence closes. The buffer is empty, so flush adds nothing, and feed returns an empty list. The last chunk is plain text. And there's our result, exactly what we wanted.", 1000),
    ("K10", "One branch left. Take A, two backticks, then B. When B arrives, settle sees two held. Two means nothing, so this branch puts them back as ordinary characters, ahead of B. The same branch handles a lone backtick inside a fence.", 800),
    ("K11", "Last method. What if the stream ends with backticks still held? Nothing will ever come along to settle them. So finish sends them out as ordinary characters, in the current state.", 400),
    ("K12", "And a fence that never closed needs nothing at all. Its code is already on screen, already styled.", 1000),
    # tests
    ("Q1", "Now tests. The one that catches almost everything is this: cut the same text at random, run it, and compare the result with no cuts at all. Cuts change the sizes of the pieces, so merged glues neighbors of the same kind together before comparing.", 500),
    ("Q2", "Run that on a list of nasty strings: a backtick at the very end, two backticks, a fence that never closes, four backticks in a row, and a fence with a backtick inside.", 800),
    ("Q3", "Here's how that fits in the hour, in the order you'd type it. Five minutes to clarify. Then the state and feed for plain text. Then tick and settle, testing inline code first and fences second. Then finish, then the random cut test, which leaves time for follow-ups.", 1100),
    # follow-ups
    ("U1", "Expect follow-ups. To pull out the language name, add a fourth state after the opening fence, which collects characters up to the newline.", 400),
    ("U2", "To open a fence only at the start of a line, remember whether the last character was a newline. Anywhere else, three backticks are ordinary characters.", 400),
    ("U3", "For other marks, like bold, it's the same trick. A star might be the first of two stars, so hold it until you can tell.", 400),
    ("U4", "And on the screen: each event adds to the last block, or opens a new one. Old text is never touched, which is what keeps a selection working.", 1000),
    # the full solution
    ("S1", "Here's the full solution, all on one screen. You've now seen every line of it. Pause here if you want to read it through.", 2500),
    ("S2", "At a high level, it has six pieces. Init holds what survives between chunks: the state, the held count, and the buffer.", 500),
    ("S3", "Feed loops over the characters. A backtick goes to tick. Anything else settles what's held, then goes in the buffer. At the end of the chunk, it flushes.", 500),
    ("S4", "Tick: in inline, one backtick closes it. Otherwise count it, and at three, open or close the fence.", 500),
    ("S5", "Settle runs when a normal character arrives. One held in text opens inline code. Anything else held was just ordinary characters.", 500),
    ("S6", "Switch flushes, then changes the state. And flush turns the buffer into one event.", 500),
    ("S7", "Finally, finish sends out whatever is still held when the stream ends.", 800),
    ("S8", "As for cost: it's one step per character. And between chunks, we hold at most two backticks, however long the reply gets.", 1000),
    # recap
    ("R1", "Let's tie the pictures to the code. The lit box is self dot state. The filled slots are self dot ticks.", 400),
    ("R2", "The tiles waiting to go out are self dot buff. And the tiles leaving together as one piece are flush.", 400),
    ("R3", "A box lighting up is switch: flush first, then change the state.", 1000),
    ("Z1", "The one line to remember: only two things cross a chunk: the state, and the held backticks.", 1500),
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
