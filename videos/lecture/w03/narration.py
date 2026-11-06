"""Narration for the hierarchical rate limiter walkthrough: writes cues.json and SCRIPT.md here.

Each line: (scene function or "", narration, pause after in ms).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
TITLE = "Hierarchical rate limiter"
PRONOUNCE = {"popleft": "pop left", "defaultdict": "default dict", "deque": "deck", "Redis": "Reddiss", "Lua": "Loo-ah"}
CUES = [
    ("", "Hierarchical rate limiter. We'll build it from the ground up: what the words mean, what the problem asks, the idea in pictures, and then every line of code, tied back to its picture.", 1000),
    # the words
    ("D1", "First, the words. A notification is a message an app sends you: an email, a text, a push alert. Send too many, and people get annoyed. And a single bug can spam everyone.", 500),
    ("D2", "A rate limiter is the code that says no. Before each send, it answers one question: yes, send this one, or no, too many have gone out already.", 500),
    ("D3", "A limit always has two parts: how many, and over how long. For example, three notifications per ten minutes. The over how long part is called the window.", 700),
    ("D4", "Hierarchical means there are levels, nested inside each other. A user belongs to a team, and a team belongs to a company. Each level has its own limit. All the users on a team share the team's limit, and all the teams in a company share the company's.", 500),
    ("D5", "So a send goes through only if every level allows it. Here, the user has room, but the team is full. So the answer is no.", 1000),
    # the problem
    ("P1", "Now the problem, the way candidates report it. You write one method. It takes a user and a timestamp, which is just the time as a number of seconds. It returns true if the notification may be sent, and false if not.", 500),
    ("P2", "You're given two dictionaries: one from a user to their team, and one from a team to its company.", 400),
    ("P3", "The limits are three per user, ten per team, and twenty per company, within any six hundred seconds. That's ten minutes.", 400),
    ("P4", "And two details matter. A refused send counts nowhere, at any level. And timestamps never go backward.", 1000),
    ("E1", "Let's make that concrete. One user sends at times one, two, and three. All allowed. That's the user's limit of three.", 400),
    ("E2", "At time four, the answer is no. Three are already inside the last six hundred seconds.", 400),
    ("E3", "At time six oh one, the send from time one is exactly six hundred seconds old. That counts as expired, so there's room again. The answer is yes, and yes again at six oh two.", 700),
    ("E4", "A second example. Five users on one team each send twice, from time one to time ten. That's all ten of the team's sends. So at time eleven, user one is refused, even though that user has only sent two. The team is full.", 400),
    ("E5", "At time six oh one, the send from time one has expired, so the team has room, and user two is allowed.", 1000),
    # why
    ("B1", "Why is this harder than a counter? The obvious way to count is called a fixed window: keep one counter, and reset it to zero every ten minutes. With a limit of three, the fourth send is refused. Looks fine.", 400),
    ("B2", "But look at the reset. Three sends just before it, and three just after. That's six in about a minute, with a limit of three in ten minutes.", 800),
    ("B3", "The fix is a sliding window. Don't reset anything. At each send, look back exactly six hundred seconds from now, and count only what's inside. To do that, keep the time of every accepted send.", 500),
    ("B4", "As time moves on, the window slides, and old sends fall out on the left. The time stamps are already in order, so the oldest is always first.", 400),
    ("B5", "So we need a list that adds on the right, and removes from the left. In Python, that's a deque, short for double ended queue. Both of those moves take one step. A plain list has to shift every element when you remove the first one.", 1000),
    ("C1", "Before coding, ask a few questions, because each answer changes the code. Does a refused send count? No, at no level.", 400),
    ("C2", "Is something exactly six hundred seconds old still inside? No, it has expired.", 400),
    ("C3", "Do many threads call this at once? Assume yes, which we'll come back to. And is an unknown user possible? Assume it's an error.", 1000),
    # the plan
    ("L1", "Now the plan. The obvious loop goes level by level, checking and adding as it goes. Here's the bug. The user has room, so add one. The team is full, so refuse. But the user's count already went up.", 500),
    ("L2", "Try again, and again. The user is now blocked, and not one notification was ever sent.", 800),
    ("L3", "So split it into two moves. First, look: is there room at every level? Change nothing while you look.", 400),
    ("L4", "Second, commit: only if all three said yes, add to all three together. It's all or nothing.", 1000),
    # setup
    ("N1", "Now the code, starting with the setup. On the left is the picture, and on the right is the code for it. The limits and the window are constants on the class.", 500),
    ("N2", "The constructor stores the two dictionaries we're given. This is how we walk from a user, up to a team, up to a company.", 500),
    ("N3", "Self dot sent holds one log per level. Its key is a pair: the level, and the id. So there's a log for user U one, one for team T one, and one for company C one. A defaultdict creates the empty deque the first time a key is used, so we never check whether it exists.", 500),
    ("N4", "And there's a lock, which we'll get to.", 800),
    # walk
    ("W1", "Now the method, with the very first call: user one, at time one. These two lines walk up the hierarchy, with one dictionary lookup each.", 400),
    ("W2", "Then we build the list of three keys. Each one names a log.", 500),
    ("W3", "Now the first move, look. For each key, get its log. The while loop removes expired sends, and there are none yet. Then the check: is the log already at its limit? The limit comes from the first part of the key, here user, which is three. Zero isn't, so we go on.", 400),
    ("W4", "Team: zero of ten. Company: zero of twenty. All three said yes.", 400),
    ("W5", "So the second move, commit. This loop adds the time to all three logs, and we return true.", 800),
    ("W6", "Times two and three go exactly the same way. Each log grows by one.", 600),
    ("W7", "Now time four. The user's log has three entries, and three is at the limit. So we return false, right there. The commit loop never runs, so nothing changes anywhere. That's the bug fixed.", 800),
    ("W8", "Now time six oh one, and the while loop finally does something. Log zero is the oldest send. Six oh one minus one is six hundred, which is at least the window. So it's expired, and pop left removes it.", 500),
    ("W9", "Check the next oldest. Six oh one minus two is five ninety nine. That's still inside, so the loop stops. It only looks at the front, because the log is in time order.", 500),
    ("W10", "Now the user's log has two, so there's room. The team and company logs get pruned the same way, all three say yes, and we commit. True.", 800),
    ("W11", "Watch the second example run, with the team's log filling up. Every call adds to all three levels.", 400),
    ("W12", "Now user one at time eleven. The user's own log has two, so it passes. The team's log has ten, so we return false. Look at the user's log: it's still two. The look never changes the count.", 500),
    ("W13", "And user two at time six oh one. The oldest send falls out of the team's log, so there's room, and the answer is true.", 1000),
    # threads
    ("H1", "Now that lock. A thread is a separate line of work inside one program, and a server runs many at once. Say the company is at nineteen of twenty, with one slot left. Two threads look at the same moment, and both see room. Both add. Now it's twenty one. That's called a race condition.", 500),
    ("H2", "The fix is a lock. Only one thread can hold it at a time, and any other thread waits. So thread A looks and commits, and only then can thread B look, and it sees the company is full.", 500),
    ("H3", "In code, it's this with block. It takes the lock on the way in, and releases it on the way out, even when we return from the middle. Everything inside now happens as one step, which is called atomic. No other thread can see it half done.", 1000),
    # tests
    ("Q1", "Now tests. Start with the reported examples, as asserts. Then one for a refused send leaving no trace, one for the company limit, and one for the exact boundary: five ninety nine is still inside, and six hundred has expired.", 500),
    ("Q2", "And one for threads: fifty threads send at the same moment against a company limit of twenty, and exactly twenty get through.", 800),
    ("Q3", "Here's how that fits in the hour, in the order you'd type it. Five minutes to clarify. Then one level with a sliding window. Then all three levels, look then commit, with the reported examples as tests. Then the lock. That leaves a good twenty minutes for the design follow-ups.", 1100),
    # scale
    ("U1", "Those follow-ups usually start here: what about many servers? A lock only protects one program. Each server has its own logs, so each thinks it's at seven of twenty, and together they've sent twenty one.", 500),
    ("U2", "So move the logs out to one shared store, like Redis, an in-memory database. Redis can run a small Lua script as one step, with nothing else running in between. So the script does what our method does: prune, look at all three, and add to all or none. It's the same look and commit, in a different place.", 500),
    ("U3", "Next: Redis itself gets split across machines, and one script must reach all its keys on one machine. So put all of a company's keys together. A very busy company can then overload that machine, so be ready to talk about that.", 500),
    ("U4", "What about retries? If a server retries the same send, it shouldn't count twice. So give each send a request id, and if you've seen that id, return the first answer.", 400),
    ("U5", "And if Redis is down? Either allow the send, or refuse it, and that's a product choice. Say which one you'd pick and why. And if limits grow into the thousands, a log per level gets big, so switch to approximate counters.", 1000),
    # the full solution
    ("S1", "Here's the full solution, all on one screen. You've now seen every line of it. Pause here if you want to read it through.", 2500),
    ("S2", "At a high level, it has four pieces. The constants are the limits and the window. The constructor stores the dictionaries, one log per level, and a lock.", 500),
    ("S3", "The method first works out the three keys, by walking up from the user.", 500),
    ("S4", "Then, under the lock, it looks at every level: drop what's expired from the front, and if a log is at its limit, return false.", 500),
    ("S5", "And if all three had room, it commits: add the time to all three logs, and return true.", 800),
    ("S6", "As for cost: each call removes at most what was added earlier, so it averages out to a few steps per call. And no log ever holds more than its limit: three, ten, or twenty.", 1000),
    # recap
    ("R1", "Let's tie the pictures to the code. The window sliding, and old sends falling out, is the while loop with pop left.", 400),
    ("R2", "A level refusing is the return false in the first loop. And all levels going up together is the second loop.", 400),
    ("R3", "Two threads taking turns is the with block.", 1000),
    ("Z1", "The one line to remember: look at every level, then commit to every level, inside one atomic step.", 1500),
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
