"""The code shown in the rate limiter walkthrough. API, limits and window as candidates report them.

    python solution.py          run the tests
    python solution.py --data   also write data.js: the real trace and source the video shows
"""
import json
import sys
import threading
from collections import defaultdict, deque
from pathlib import Path


class NotificationLimiter:
    LIMITS = {"user": 3, "team": 10, "company": 20}
    WINDOW = 600

    def __init__(self, user_to_team, team_to_company):
        self.user_to_team = user_to_team
        self.team_to_company = team_to_company
        self.sent = defaultdict(deque)    # (level, id) -> times
        self.lock = threading.Lock()

    def should_send_notifications(self, user_id, timestamp):
        team = self.user_to_team[user_id]
        company = self.team_to_company[team]
        keys = [("user", user_id),
                ("team", team),
                ("company", company)]
        with self.lock:
            for key in keys:
                log = self.sent[key]
                while log and timestamp - log[0] >= self.WINDOW:
                    log.popleft()
                if len(log) >= self.LIMITS[key[0]]:
                    return False
            for key in keys:
                self.sent[key].append(timestamp)
            return True


def trace(calls, user_to_team, team_to_company):
    """What the real limiter does on each call: a snapshot of each level as it is looked at."""
    L = NotificationLimiter(user_to_team, team_to_company)
    out = []
    for user, t in calls:
        team = user_to_team[user]
        company = team_to_company[team]
        keys = [("user", user), ("team", team), ("company", company)]
        before = {k[0]: list(L.sent[k]) for k in keys}
        looks = []
        for k in keys:
            log = list(L.sent[k])
            kept = [x for x in log if t - x < L.WINDOW]
            looks.append({"level": k[0], "id": k[1], "log": log, "popped": log[:len(log) - len(kept)], "kept": kept, "full": len(kept) >= L.LIMITS[k[0]]})
            if looks[-1]["full"]:
                break
        ok = L.should_send_notifications(user, t)
        out.append({"user": user, "t": t, "team": team, "company": company, "ok": ok, "before": before, "looks": looks,
                    "after": {k[0]: list(L.sent[k]) for k in keys}})
    return out


if __name__ == "__main__":
    T, F = True, False
    # reported example 1
    ONE = ({"u1": "t1"}, {"t1": "c1"})
    calls1 = [("u1", t) for t in (1, 2, 3, 4, 601, 602)]
    L = NotificationLimiter(*ONE)
    ask = L.should_send_notifications
    times = (1, 2, 3, 4, 601, 602)
    assert [ask("u1", t) for t in times] == [T, T, T, F, T, T]

    # reported example 2: five users on one team
    FIVE = ({f"u{i}": "t1" for i in range(1, 6)}, {"t1": "c1"})
    calls2 = [(f"u{i}", i) for i in range(1, 6)] + [(f"u{i}", i + 5) for i in range(1, 6)] + [("u1", 11), ("u2", 601)]
    L = NotificationLimiter(*FIVE)
    ask = L.should_send_notifications
    assert [ask(u, t) for u, t in calls2] == [T] * 10 + [F, T]

    # a refused send counts nowhere: the team refused z, and z's own log has no trace of it
    L = NotificationLimiter({**FIVE[0], "z": "t1"}, FIVE[1])
    for i in range(1, 6):
        L.should_send_notifications(f"u{i}", 0)
        L.should_send_notifications(f"u{i}", 1)
    ask = L.should_send_notifications
    assert ask("z", 2) is False
    assert len(L.sent[("user", "z")]) == 0

    # the company limit: two full teams, then a third team is refused
    org = {f"a{i}": "ta" for i in range(4)} | {f"b{i}": "tb" for i in range(4)} | {"c0": "tc"}
    L = NotificationLimiter(org, {"ta": "c", "tb": "c", "tc": "c"})
    for team in "ab":
        for i in range(4):
            for j in range(3):
                L.should_send_notifications(f"{team}{i}", 0)
    assert len(L.sent[("company", "c")]) == 20
    ask = L.should_send_notifications
    assert ask("c0", 1) is False

    # exactly 600 seconds old has expired, and 599 has not
    L = NotificationLimiter(*ONE)
    for t in (0, 0, 0):
        L.should_send_notifications("u1", t)
    ask = L.should_send_notifications
    assert ask("u1", 599) is False
    assert ask("u1", 600) is True

    # threads never exceed the limit
    org = {f"u{i}": f"t{i}" for i in range(50)}
    L = NotificationLimiter(org, {f"t{i}": "c" for i in range(50)})
    res = []

    def w(i):
        for _ in range(3):
            res.append(L.should_send_notifications(f"u{i}", 0))

    ts = [threading.Thread(target=w, args=(i,)) for i in range(50)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert sum(res) == 20
    print("limiter ok")

    if "--data" in sys.argv:
        src = Path(__file__).read_text(encoding="utf-8").split("\n")
        start, end = src.index("class NotificationLimiter:"), src.index("def trace(calls, user_to_team, team_to_company):")
        body = src[start:end]
        while not body[-1].strip():
            body.pop()
        cut = body.index("    def should_send_notifications(self, user_id, timestamp):")
        left = ["import threading", "from collections import defaultdict, deque", "", ""] + body[:cut]
        while not left[-1].strip():
            left.pop()
        data = {"T1": trace(calls1, *ONE), "T2": trace(calls2, *FIVE), "FULL": {"left": left, "right": body[cut:]}}
        js = "".join(f"window.{k} = {json.dumps(v)};\n" for k, v in data.items())
        Path(__file__).with_name("data.js").write_text(js, encoding="utf-8")
        print("data.js:", len(data["T1"]), "+", len(data["T2"]), "calls; full solution", len(left), "+", len(body) - cut, "lines")
