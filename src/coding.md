**TLDR.** This is a pairing round: a backend problem, built in stages. Set a 45-minute timer. Read the prompt and Stage 1 only. Out loud, restate it, ask your questions, and propose method signatures. Then code Stage 1 with a few quick asserts, and only then open the next stage. The answer key is one good solution, written the way you'd write it in the interview: plain Python, standard library only.

**Questions**

1. [Library lending desk](#k-library) (dict state, a queue per key)
2. [Parking garage](#k-parking) (allocation, money in cents)
3. [Puzzle game leaderboard](#k-leaderboard) (top k, rank, ties)
4. [Code editor file system](#k-files) (a tree of dicts)
5. [Config store with history](#k-config) (as-of reads with bisect)
6. [Meeting room booking](#k-rooms) (interval overlap)
7. [Feature flags](#k-flags) (stable percentage rollout)
8. [Nightly eval results](#k-evals) (regressions between runs)

With a video walkthrough. Try each one first, because the video shows a full solution. These prompts are rebuilt from public candidate reports, so the real wording may differ:

9. [Repository Merkle tree](#k-merkle) (hash bottom up, compare top down)
10. [Streaming text parser](#k-stream) (state across chunks)
11. [Hierarchical rate limiter](#k-limiter) (check every level, then commit)

The quick tests in every answer use this helper:

```python
def raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False
```

---

## 1. Library lending desk {#k-library}

> Our neighborhood library tracks loans on paper. Build the service behind a small lending desk app.

**Stage 1.** Members check books out and give them back. A book can't be out to two people at once.

::: reveal Stage 2
Loans are due 14 days after checkout. List the overdue books for a given day. When a book comes back late, charge 25 cents per late day.
:::

::: reveal Stage 3
A member can place a hold on a book that's out. When it comes back, it goes straight to the first member waiting: checked out to them automatically.
:::

::: reveal Stage 4
New rule from the librarian: a member can have at most 3 books out at once.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Can a book have several copies? *Treat each copy as its own book id.*
- How do we represent time? *Integer day numbers. The caller passes today.*
- What if someone returns a book that isn't out? *That's an error. Make it clear.*
- One desk or several? *One app for now, but tell me what changes with several.*

### 2. API

- `checkout(book_id, member, today) -> None`. Raises `AlreadyOut`, `LimitReached`.
- `give_back(book_id, today) -> int`: the late fee in cents. Raises `NotOut`.
- `overdue(today) -> list[str]`: book ids, sorted.
- `place_hold(book_id, member) -> int`: the member's place in line, from 1.

### 3. Code

```python
from collections import defaultdict, deque
from dataclasses import dataclass


class LibraryError(Exception): pass
class AlreadyOut(LibraryError): pass
class NotOut(LibraryError): pass
class LimitReached(LibraryError): pass


@dataclass
class Loan:
    member: str
    due: int                                  # a day number


class Library:
    LOAN_DAYS = 14
    FEE_PER_DAY = 25                          # cents
    MAX_LOANS = 3

    def __init__(self):
        self.loans = {}                       # book_id -> Loan
        self.count = defaultdict(int)         # member -> books out
        self.holds = defaultdict(deque)       # book_id -> members waiting

    def checkout(self, book_id: str, member: str, today: int) -> None:
        if book_id in self.loans:
            raise AlreadyOut(book_id)
        if self.count[member] >= self.MAX_LOANS:
            raise LimitReached(member)
        self.loans[book_id] = Loan(member, today + self.LOAN_DAYS)
        self.count[member] += 1

    def give_back(self, book_id: str, today: int) -> int:
        loan = self.loans.pop(book_id, None)
        if loan is None:
            raise NotOut(book_id)
        self.count[loan.member] -= 1
        fee = max(0, today - loan.due) * self.FEE_PER_DAY
        self._fill_hold(book_id, today)
        return fee

    def overdue(self, today: int) -> list[str]:
        return sorted(b for b, loan in self.loans.items() if loan.due < today)

    def place_hold(self, book_id: str, member: str) -> int:
        if book_id not in self.loans:
            raise NotOut(book_id)             # it's on the shelf: just check it out
        line = self.holds[book_id]
        if member not in line:
            line.append(member)
        return list(line).index(member) + 1

    def _fill_hold(self, book_id: str, today: int) -> None:
        line = self.holds.get(book_id)
        while line:
            member = line.popleft()
            try:
                self.checkout(book_id, member, today)
                return
            except LimitReached:
                continue                      # at their limit: skip to the next member
```

### 4. Quick tests

```python
lib = Library()
lib.checkout("b1", "ana", today=0)
assert raises(AlreadyOut, lib.checkout, "b1", "bo", today=0)
assert lib.overdue(today=15) == ["b1"]
assert lib.place_hold("b1", "bo") == 1
assert lib.give_back("b1", today=16) == 50            # 2 days late
assert lib.loans["b1"].member == "bo"                  # the hold was filled
for b in ("x", "y", "z"):
    lib.checkout(b, "cy", today=0)
assert raises(LimitReached, lib.checkout, "w", "cy", today=0)
assert raises(NotOut, lib.give_back, "w", today=0)
```

### 5. Follow-ups

- **Why a dict?** Checkout and give back are lookups by book id: constant time, and a key can't repeat, so "one loan per book" holds by construction.
- **Complexity:** checkout and give back are O(1). `overdue` scans and sorts, O(n log n). If it's called often, keep a heap keyed by due date.
- **Two desks at once:** both pass the `in` check, then both write. Hold one `threading.Lock` around the check and the write.
- **A decision to say out loud:** a member at their limit loses their hold. The alternative is to keep them in line and try the next member.
- **How it evolves:** a loans table in Postgres with a unique index on `book_id` where `returned_at is null`. The database then enforces "one loan per book" for every desk.
:::

---

## 2. Parking garage {#k-parking}

> A parking garage wants to replace its ticket machine. Build the service that assigns spots and charges at the exit.

**Stage 1.** The garage has small, medium and large spots, a set number of each. A car arrives with a plate and a size: give it a spot of that size, or say the garage is full. Free the spot when the car leaves.

::: reveal Stage 2
If its size is full, a car can take a bigger spot (small, then medium, then large). Never a smaller one.
:::

::: reveal Stage 3
Charge at the exit: $3 per started hour, the first 15 minutes free, capped at $20 a visit. Times are minutes, passed in.
:::

::: reveal Stage 4
The display at the entrance shows how many spots of each size are free. It refreshes every second, so make it cheap.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Do spots have ids? *Yes, like S1, M2. The ticket shows it.*
- Can the same plate arrive twice? *Not while it's inside. That's an error.*
- Which spot when several are free? *Any spot of the right size.*
- Money format? *Return cents as an integer.*

### 2. API

- `Garage(counts: dict[str, int])`
- `arrive(plate, size, now) -> str`: the spot id. Raises `GarageFull`, `AlreadyParked`.
- `leave(plate, now) -> int`: the fee in cents. Raises `UnknownCar`.
- `free_count() -> dict[str, int]`

### 3. Code

```python
SIZES = ["small", "medium", "large"]


class GarageError(Exception): pass
class GarageFull(GarageError): pass
class AlreadyParked(GarageError): pass
class UnknownCar(GarageError): pass


class Garage:
    RATE = 300                                # cents per started hour
    FREE_MINUTES = 15
    CAP = 2000                                # cents per visit

    def __init__(self, counts: dict[str, int]):
        # free spot ids per size, used as a stack: pop() gives S1 first
        self.free = {s: [f"{s[0].upper()}{i}" for i in range(counts.get(s, 0), 0, -1)] for s in SIZES}
        self.parked = {}                      # plate -> (size used, spot, arrived)

    def arrive(self, plate: str, size: str, now: int) -> str:
        if size not in SIZES:
            raise ValueError(size)
        if plate in self.parked:
            raise AlreadyParked(plate)
        for s in SIZES[SIZES.index(size):]:   # its own size first, then bigger
            if self.free[s]:
                spot = self.free[s].pop()
                self.parked[plate] = (s, spot, now)
                return spot
        raise GarageFull(size)

    def leave(self, plate: str, now: int) -> int:
        if plate not in self.parked:
            raise UnknownCar(plate)
        size, spot, arrived = self.parked.pop(plate)
        self.free[size].append(spot)
        return self.fee(now - arrived)

    def fee(self, minutes: int) -> int:
        if minutes <= self.FREE_MINUTES:
            return 0
        hours = -(-minutes // 60)             # ceiling division
        return min(self.CAP, hours * self.RATE)

    def free_count(self) -> dict[str, int]:
        return {s: len(self.free[s]) for s in SIZES}
```

### 4. Quick tests

```python
g = Garage({"small": 1, "medium": 1, "large": 0})
assert g.arrive("A", "small", 0) == "S1"
assert g.arrive("B", "small", 0) == "M1"               # moved up a size
assert raises(GarageFull, g.arrive, "C", "small", 0)
assert raises(AlreadyParked, g.arrive, "A", "small", 0)
assert g.leave("A", 10) == 0                            # under 15 minutes
assert g.free_count() == {"small": 1, "medium": 0, "large": 0}
assert g.leave("B", 61) == 600                          # 2 started hours
assert g.fee(60 * 24) == 2000                           # capped
assert raises(UnknownCar, g.leave, "B", 70)
```

### 5. Follow-ups

- **Why a list as a stack?** `pop()` and `append()` at the end are O(1). If they want the lowest-numbered free spot, use a heap (`heapq`) instead.
- **Complexity:** everything is O(1) (three sizes at most). `free_count` is just three `len` calls, so the display can call it every second.
- **Money:** integer cents, never floats. `0.1 + 0.2 != 0.3`.
- **Two gates at once:** two cars can grab the last spot. Lock around "find a spot and take it".
- **How it evolves:** a spots table, taking a spot with one conditional update (`UPDATE ... WHERE taken = false`), so two gates can't take the same spot.
:::

---

## 3. Puzzle game leaderboard {#k-leaderboard}

> We run a weekly puzzle game. Build the leaderboard service.

**Stage 1.** Record a player's score for a game. A player's total is the sum of their scores this week. Get a player's total.

::: reveal Stage 2
Show the top k players by total, highest first. Ties go to the name that comes first alphabetically.
:::

::: reveal Stage 3
Show any player's rank (1 is the best), with the same tie rule.
:::

::: reveal Stage 4
Start a new week: every total goes back to zero, but keep last week's top 3 and return them.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Can scores be negative? *No. Reject them.*
- A player we've never seen? *Asking for their total is an error.*
- How many players? *A few thousand. Rank is shown on every profile view.*
- Are ties common? *Yes, scores are small integers.*

### 2. API

- `add_score(player, score) -> int`: the new total.
- `total(player) -> int`. Raises `UnknownPlayer`.
- `top(k) -> list[tuple[str, int]]`
- `rank(player) -> int`
- `new_week() -> list[tuple[str, int]]`: last week's top 3.

### 3. Code

```python
import heapq
from collections import defaultdict


class UnknownPlayer(Exception): pass


class Leaderboard:
    def __init__(self):
        self.totals = defaultdict(int)        # player -> total this week
        self.history = []                     # each past week's top 3

    def add_score(self, player: str, score: int) -> int:
        if score < 0:
            raise ValueError("score must be >= 0")
        self.totals[player] += score
        return self.totals[player]

    def total(self, player: str) -> int:
        if player not in self.totals:
            raise UnknownPlayer(player)
        return self.totals[player]

    @staticmethod
    def _order(item):
        player, total = item
        return (-total, player)               # highest total first, then name A to Z

    def top(self, k: int) -> list[tuple[str, int]]:
        return heapq.nsmallest(k, self.totals.items(), key=self._order)

    def rank(self, player: str) -> int:
        mine = self._order((player, self.total(player)))
        return 1 + sum(self._order(item) < mine for item in self.totals.items())

    def new_week(self) -> list[tuple[str, int]]:
        podium = self.top(3)
        self.history.append(podium)
        self.totals.clear()
        return podium
```

### 4. Quick tests

```python
lb = Leaderboard()
lb.add_score("cy", 5); lb.add_score("ana", 7); lb.add_score("bo", 7)
assert lb.add_score("cy", 4) == 9
assert lb.top(2) == [("cy", 9), ("ana", 7)]
assert lb.rank("bo") == 3                               # ties with ana, loses on name
assert raises(ValueError, lb.add_score, "cy", -1)
assert lb.new_week() == [("cy", 9), ("ana", 7), ("bo", 7)]
assert raises(UnknownPlayer, lb.total, "cy")
```

### 5. Follow-ups

- **One sort key for both:** `(-total, name)` gives "highest first, ties by name" for top and rank, so they can't disagree.
- **Complexity:** `top(k)` is O(n log k) with a heap. `rank` is O(n). Fine for thousands of players.
- **If rank gets hot:** keep a sorted list of `(-total, name)` and use `bisect` (O(log n) to find, O(n) to update), or in production a Redis sorted set (`ZINCRBY`, `ZREVRANK`), which is built for exactly this.
- **Two threads:** `totals[p] += s` is a read, then a write. Two updates can lose one. Lock it.
:::

---

## 4. Code editor file system {#k-files}

> Build an in-memory file system for a web-based code editor.

**Stage 1.** `mkdir(path)` creates a folder and any missing parents. `write(path, text)` creates or overwrites a file; its folder must already exist. `read(path)` returns the text.

::: reveal Stage 2
`ls(path)`: the names in a folder, sorted. On a file, just the file's name.
:::

::: reveal Stage 3
`size(path)`: a file's size is the length of its text. A folder's size is the total of everything under it.
:::

::: reveal Stage 4
`move(src, dst)` for files and folders. Moving a folder into itself is an error.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Path format? *Absolute, slash-separated, like `/src/app/main.py`.*
- What if the parent folder is missing on write? *Error. Only mkdir creates parents.*
- Can a file and a folder share a name in one folder? *No.*
- How big? *Thousands of files. Paths are short.*

### 2. API

- `mkdir(path)`, `write(path, text)`, `read(path) -> str`
- `ls(path) -> list[str]`, `size(path) -> int`, `move(src, dst)`
- Errors: `NotFound`, `NotADir`, `NotAFile`, `Exists`, `BadMove`.

### 3. Code

```python
class FSError(Exception): pass
class NotFound(FSError): pass
class NotADir(FSError): pass
class NotAFile(FSError): pass
class Exists(FSError): pass
class BadMove(FSError): pass


class FileSystem:
    def __init__(self):
        self.root = {}                        # a folder is a dict of name -> child; a file is a str

    @staticmethod
    def _parts(path: str) -> list[str]:
        return [p for p in path.split("/") if p]

    def _get(self, parts: list[str]):
        node = self.root
        for p in parts:
            if not isinstance(node, dict) or p not in node:
                raise NotFound("/" + "/".join(parts))
            node = node[p]
        return node

    def _dir(self, parts: list[str]) -> dict:
        node = self._get(parts)
        if not isinstance(node, dict):
            raise NotADir("/" + "/".join(parts))
        return node

    def mkdir(self, path: str) -> None:
        node = self.root
        for p in self._parts(path):
            node = node.setdefault(p, {})
            if not isinstance(node, dict):
                raise NotADir(p)

    def write(self, path: str, text: str) -> None:
        *folder, name = self._parts(path)
        parent = self._dir(folder)
        if isinstance(parent.get(name), dict):
            raise Exists(path)                # a folder already has that name
        parent[name] = text

    def read(self, path: str) -> str:
        node = self._get(self._parts(path))
        if isinstance(node, dict):
            raise NotAFile(path)
        return node

    def ls(self, path: str) -> list[str]:
        parts = self._parts(path)
        node = self._get(parts)
        return sorted(node) if isinstance(node, dict) else [parts[-1]]

    def size(self, path: str) -> int:
        def total(node):
            return len(node) if isinstance(node, str) else sum(total(c) for c in node.values())
        return total(self._get(self._parts(path)))

    def move(self, src: str, dst: str) -> None:
        s, d = self._parts(src), self._parts(dst)
        if d[:len(s)] == s:
            raise BadMove(f"{dst} is inside {src}")
        node = self._get(s)
        *dst_folder, dst_name = d
        dest = self._dir(dst_folder)
        if dst_name in dest:
            raise Exists(dst)
        *src_folder, src_name = s
        del self._dir(src_folder)[src_name]
        dest[dst_name] = node
```

### 4. Quick tests

```python
fs = FileSystem()
fs.mkdir("/src/app")
fs.write("/src/app/main.py", "print(1)")
fs.write("/src/README", "hi")
assert fs.read("/src/app/main.py") == "print(1)"
assert fs.ls("/src") == ["README", "app"]
assert fs.ls("/src/README") == ["README"]
assert fs.size("/src") == 10
assert raises(NotFound, fs.write, "/nope/x.py", "")
assert raises(NotAFile, fs.read, "/src")
fs.move("/src/app", "/app")
assert fs.ls("/") == ["app", "src"]
assert raises(BadMove, fs.move, "/src", "/src/inner")
```

### 5. Follow-ups

- **Why nested dicts?** Each step down a path is one O(1) lookup, so every operation is O(depth), plus O(subtree) for `size` and O(k log k) for `ls`.
- **If size gets hot:** store a size on each folder and update every ancestor on write and move. That makes writes O(depth) and size O(1).
- **Two threads:** one lock for the whole tree is simple and correct. Per-folder locks are faster, but `move` takes two of them, so always lock in the same order to avoid deadlock.
- **How it evolves:** file contents go to object storage; the tree becomes a table `(id, parent_id, name)` with a unique index on `(parent_id, name)`. Then a move is one row update.
:::

---

## 5. Config store with history {#k-config}

> Our services read settings, like timeouts and model names, from a config store. When something breaks, we need to know what a setting was at any past moment.

**Stage 1.** `set(key, value, ts)` and `get(key)` for the latest value. For each key, timestamps only go up.

::: reveal Stage 2
`get(key, at=ts)`: the value as of that time, meaning the last set at or before it. Before the first set, the key is missing.
:::

::: reveal Stage 3
`delete(key, ts)`: from then on the key is missing, but its history before that stays readable.
:::

::: reveal Stage 4
`changes(since, until)`: every key whose value at `until` differs from its value at `since`, sorted.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What does "missing" return? *None by default. Let callers pass a default.*
- What if a write comes with an older timestamp? *Reject it. It's a bug upstream.*
- Reads vs writes? *Reads all day, a few writes an hour. History grows forever.*
- What can a value be? *Anything: numbers, strings, None.*

### 2. API

- `set(key, value, ts)`, `delete(key, ts)`. Raise `StaleWrite` on an old timestamp.
- `get(key, at=None, default=None)`
- `changes(since, until) -> list[str]`

### 3. Code

```python
from bisect import bisect_right
from collections import defaultdict


class StaleWrite(Exception): pass


_DELETED = object()                           # marks a delete in the history


class ConfigStore:
    def __init__(self):
        self.times = defaultdict(list)        # key -> [ts, ...], increasing
        self.values = defaultdict(list)       # key -> [value, ...], same order

    def set(self, key: str, value, ts: int) -> None:
        self._append(key, value, ts)

    def delete(self, key: str, ts: int) -> None:
        self._append(key, _DELETED, ts)

    def _append(self, key: str, value, ts: int) -> None:
        times = self.times[key]
        if times and ts <= times[-1]:
            raise StaleWrite(f"{key}: {ts} <= {times[-1]}")
        times.append(ts)
        self.values[key].append(value)

    def get(self, key: str, at: int | None = None, default=None):
        times = self.times.get(key)
        if not times:
            return default
        i = len(times) if at is None else bisect_right(times, at)
        if i == 0:
            return default                    # asked before the first set
        value = self.values[key][i - 1]
        return default if value is _DELETED else value

    def changes(self, since: int, until: int) -> list[str]:
        missing = object()
        return sorted(k for k in self.times
                      if self.get(k, since, missing) != self.get(k, until, missing))
```

### 4. Quick tests

```python
c = ConfigStore()
c.set("timeout", 30, ts=10)
c.set("timeout", 45, ts=20)
c.set("model", "small", ts=15)
assert c.get("timeout") == 45
assert c.get("timeout", at=19) == 30
assert c.get("timeout", at=5) is None
c.delete("model", ts=25)
assert c.get("model") is None and c.get("model", at=24) == "small"
assert c.changes(since=16, until=30) == ["model", "timeout"]
assert c.changes(since=21, until=24) == []
assert raises(StaleWrite, c.set, "timeout", 1, 20)
```

### 5. Follow-ups

- **Why bisect?** Timestamps arrive in order, so each key's list is already sorted. "As of" is a binary search: O(log n). Writes are O(1) appends.
- **Why a sentinel for delete?** None is a legal value. A private `object()` can't be confused with anything a caller stores.
- **Complexity of changes:** O(K log n) for K keys. Fine for config, which has hundreds of keys.
- **Two threads:** the stale check and the append must happen together. Lock per key, or one lock.
- **How it evolves:** an append-only table `(key, ts, value)` with an index on `(key, ts)`. "As of" becomes `WHERE key = ? AND ts <= ? ORDER BY ts DESC LIMIT 1`.
:::

---

## 6. Meeting room booking {#k-rooms}

> A coworking space wants online booking for its meeting rooms.

**Stage 1.** `book(room, start, end)` returns a booking id, or rejects the booking if it overlaps another one in that room. Times are minutes, and the end is exclusive, so 9:00 to 10:00 and 10:00 to 11:00 both fit.

::: reveal Stage 2
`cancel(booking_id)`.
:::

::: reveal Stage 3
`free_rooms(start, end)`: the rooms that are free for the whole range, sorted.
:::

::: reveal Stage 4
Rooms have a capacity. `book_any(people, start, end)` books the smallest free room that fits everyone.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Is touching allowed (one ends at 10:00, the next starts at 10:00)? *Yes.*
- Unknown room or start after end? *Errors.*
- How many bookings? *Tens of rooms, a few hundred bookings per room.*
- Ties in book_any? *Smallest capacity, then room name.*

### 2. API

- `Rooms(capacity: dict[str, int])`
- `book(room, start, end) -> int`. Raises `Conflict`.
- `cancel(booking_id)`. Raises `UnknownBooking`.
- `free_rooms(start, end) -> list[str]`
- `book_any(people, start, end) -> tuple[str, int]`. Raises `NoRoom`.

### 3. Code

```python
from bisect import bisect_left, insort
from itertools import count


class BookingError(Exception): pass
class Conflict(BookingError): pass
class UnknownBooking(BookingError): pass
class NoRoom(BookingError): pass


class Rooms:
    def __init__(self, capacity: dict[str, int]):
        self.capacity = capacity
        self.slots = {r: [] for r in capacity}    # room -> sorted [(start, end, id)]
        self.by_id = {}                           # id -> (room, start, end)
        self.next_id = count(1)

    def _free(self, room: str, start: int, end: int) -> bool:
        s = self.slots[room]
        i = bisect_left(s, (start,))              # first booking starting at or after start
        if i < len(s) and s[i][0] < end:          # it starts before we end
            return False
        if i > 0 and s[i - 1][1] > start:         # the one before ends after we start
            return False
        return True

    def book(self, room: str, start: int, end: int) -> int:
        if room not in self.slots:
            raise KeyError(room)
        if start >= end:
            raise ValueError("start must be before end")
        if not self._free(room, start, end):
            raise Conflict(room)
        bid = next(self.next_id)
        insort(self.slots[room], (start, end, bid))
        self.by_id[bid] = (room, start, end)
        return bid

    def cancel(self, bid: int) -> None:
        if bid not in self.by_id:
            raise UnknownBooking(bid)
        room, start, end = self.by_id.pop(bid)
        self.slots[room].remove((start, end, bid))

    def free_rooms(self, start: int, end: int) -> list[str]:
        return sorted(r for r in self.slots if self._free(r, start, end))

    def book_any(self, people: int, start: int, end: int) -> tuple[str, int]:
        fits = [r for r in self.free_rooms(start, end) if self.capacity[r] >= people]
        if not fits:
            raise NoRoom(people)
        room = min(fits, key=lambda r: (self.capacity[r], r))
        return room, self.book(room, start, end)
```

### 4. Quick tests

```python
r = Rooms({"oak": 4, "elm": 10})
a = r.book("oak", 540, 600)
assert r.book("oak", 600, 660)                          # back to back is fine
assert raises(Conflict, r.book, "oak", 570, 630)
assert raises(Conflict, r.book, "oak", 500, 550)
assert r.free_rooms(550, 580) == ["elm"]
r.cancel(a)
assert r.free_rooms(550, 580) == ["elm", "oak"]
assert r.book_any(3, 550, 580)[0] == "oak"              # smallest that fits
assert r.book_any(3, 550, 580)[0] == "elm"
assert raises(NoRoom, r.book_any, 3, 550, 580)
assert raises(UnknownBooking, r.cancel, a)
```

### 5. Follow-ups

- **Why keep bookings sorted?** A new booking can only clash with its two neighbors, so the check is one binary search, O(log n), instead of a scan of every booking.
- **Complexity:** `book` is O(log n) to check plus O(n) to insert into the list (a fast memory shift). `free_rooms` is O(R log n).
- **Two people, same slot:** both pass `_free`, both insert. Lock per room around check and insert.
- **How it evolves:** Postgres can enforce this itself with an exclusion constraint: `EXCLUDE USING gist (room WITH =, tsrange(start_at, end_at) WITH &&)`. Then no two overlapping rows can ever commit.
:::

---

## 7. Feature flags {#k-flags}

> Our team ships features behind flags. Build the flag service our backend checks on every request.

**Stage 1.** Create a flag, turn it on or off for everyone, and check `is_on(flag, user)`. An unknown flag is an error.

::: reveal Stage 2
Allow lists: turn a flag on for specific users, even while it's off for everyone else.
:::

::: reveal Stage 3
Percentage rollout: on for N% of users. A user must always get the same answer, and raising N from 10 to 20 must keep the first 10% on.
:::

::: reveal Stage 4
A user reported a bug in the new feature. Add a deny list that wins over everything else.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- How often is is_on called? *On every request. It has to be fast.*
- What's a user? *A string id.*
- Does "always the same answer" hold across restarts and servers? *Yes. Every server must agree.*
- Percent granularity? *Whole numbers, 0 to 100.*

### 2. API

- `create(name)`, `set_on(name, on)`, `allow(name, user)`, `deny(name, user)`, `rollout(name, percent)`
- `is_on(name, user) -> bool`. Raises `UnknownFlag`.

### 3. Code

```python
import hashlib
from dataclasses import dataclass, field


class UnknownFlag(Exception): pass


@dataclass
class Flag:
    on: bool = False
    percent: int = 0                          # 0 to 100
    allow: set = field(default_factory=set)
    deny: set = field(default_factory=set)


def bucket(flag: str, user: str) -> int:
    """A stable number from 0 to 99 for each (flag, user). Not hash(): it changes between runs."""
    digest = hashlib.sha256(f"{flag}:{user}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 100


class Flags:
    def __init__(self):
        self.flags = {}                       # name -> Flag

    def create(self, name: str) -> None:
        if name in self.flags:
            raise ValueError(f"{name} already exists")
        self.flags[name] = Flag()

    def _get(self, name: str) -> Flag:
        if name not in self.flags:
            raise UnknownFlag(name)
        return self.flags[name]

    def set_on(self, name: str, on: bool) -> None:
        self._get(name).on = on

    def allow(self, name: str, user: str) -> None:
        self._get(name).allow.add(user)

    def deny(self, name: str, user: str) -> None:
        self._get(name).deny.add(user)

    def rollout(self, name: str, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError(percent)
        self._get(name).percent = percent

    def is_on(self, name: str, user: str) -> bool:
        f = self._get(name)
        if user in f.deny:
            return False
        if f.on or user in f.allow:
            return True
        return bucket(name, user) < f.percent
```

### 4. Quick tests

```python
fl = Flags()
fl.create("new_ui")
assert not fl.is_on("new_ui", "u1")
fl.allow("new_ui", "u1")
assert fl.is_on("new_ui", "u1") and not fl.is_on("new_ui", "u2")
users = [f"u{i}" for i in range(1000)]
fl.rollout("new_ui", 10)
ten = {u for u in users if fl.is_on("new_ui", u)}
fl.rollout("new_ui", 20)
twenty = {u for u in users if fl.is_on("new_ui", u)}
assert ten <= twenty                                    # the first 10% stay on
assert 50 < len(ten) < 160 and 150 < len(twenty) < 260
fl.deny("new_ui", "u1"); fl.set_on("new_ui", True)
assert not fl.is_on("new_ui", "u1") and fl.is_on("new_ui", "u2")
assert raises(UnknownFlag, fl.is_on, "nope", "u1")
```

### 5. Follow-ups

- **Why a hash bucket?** It's stable with no stored state: any server computes the same bucket. Raising the percent only adds users, because a user's bucket never changes.
- **Why put the flag name in the hash?** Otherwise the same 10% of users land in every rollout.
- **Complexity:** `is_on` is O(1): two set lookups and one hash. No network call on the request path.
- **Many servers:** each server keeps flags in memory and refreshes every few seconds, or gets pushed changes. Writes replace a whole `Flag` object, so a reader never sees half an update.
- **How it evolves:** rules on user attributes (country, plan) checked in order, with the percentage as the last rule.
:::

---

## 8. Nightly eval results {#k-evals}

> Our team runs a model against a fixed set of test cases every night. Build the service that stores the results and tells us whether the new model got worse.

**Stage 1.** `record(run_id, case_id, passed)`. `summary(run_id)` returns how many passed, the total, and the pass rate.

::: reveal Stage 2
Some cases are retried within a run. The last result for a case counts, and nothing is counted twice.
:::

::: reveal Stage 3
`compare(base_run, new_run)`: the cases that passed in base and fail in new (regressions), and the reverse (fixes), sorted. A case in only one run doesn't count.
:::

::: reveal Stage 4
`flaky(run_ids)`: the cases that passed in some of those runs and failed in others.
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What's a result? *Pass or fail for now. Scores later.*
- Do runs arrive all at once? *No. Workers record results as they finish, in any order.*
- How big? *About 2,000 cases a run, one run a night per model.*
- An unknown run id? *Error.*

### 2. API

- `record(run_id, case_id, passed)`
- `summary(run_id) -> Summary` with `passed`, `total`, `rate`. Raises `UnknownRun`.
- `compare(base, new) -> dict[str, list[str]]` with `regressions` and `fixes`.
- `flaky(run_ids) -> list[str]`

### 3. Code

```python
from collections import defaultdict
from dataclasses import dataclass


class UnknownRun(Exception): pass


@dataclass(frozen=True)
class Summary:
    passed: int
    total: int

    @property
    def rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


class EvalTracker:
    def __init__(self):
        self.runs = defaultdict(dict)         # run_id -> {case_id: passed}; a retry overwrites

    def record(self, run_id: str, case_id: str, passed: bool) -> None:
        self.runs[run_id][case_id] = passed

    def _run(self, run_id: str) -> dict:
        if run_id not in self.runs:
            raise UnknownRun(run_id)
        return self.runs[run_id]

    def summary(self, run_id: str) -> Summary:
        results = self._run(run_id)
        return Summary(sum(results.values()), len(results))

    def compare(self, base: str, new: str) -> dict[str, list[str]]:
        b, n = self._run(base), self._run(new)
        both = b.keys() & n.keys()
        return {
            "regressions": sorted(c for c in both if b[c] and not n[c]),
            "fixes": sorted(c for c in both if not b[c] and n[c]),
        }

    def flaky(self, run_ids: list[str]) -> list[str]:
        seen = defaultdict(set)               # case -> the outcomes it had
        for rid in run_ids:
            for case, passed in self._run(rid).items():
                seen[case].add(passed)
        return sorted(c for c, outcomes in seen.items() if len(outcomes) == 2)
```

### 4. Quick tests

```python
ev = EvalTracker()
for case, ok in [("c1", True), ("c2", False), ("c3", True)]:
    ev.record("mon", case, ok)
ev.record("tue", "c1", False)
ev.record("tue", "c2", False); ev.record("tue", "c2", True)   # c2 retried, passed
ev.record("tue", "c4", True)
assert ev.summary("mon") == Summary(2, 3)
assert ev.summary("tue").rate == 2 / 3
assert ev.compare("mon", "tue") == {"regressions": ["c1"], "fixes": ["c2"]}
assert ev.flaky(["mon", "tue"]) == ["c1", "c2"]
assert raises(UnknownRun, ev.summary, "wed")
```

### 5. Follow-ups

- **The dict absorbed Stage 2:** keying results by case id means a retry overwrites, so "last result wins" and "never count twice" come for free. A list of results would have needed a rewrite.
- **Complexity:** `record` is O(1); `summary` and `compare` are O(cases); `flaky` is O(runs × cases).
- **Is a drop real?** On 2,000 cases, a few regressions can be noise. Report the regression and fix counts, and use a paired test on just the cases that changed (McNemar's test) before calling it worse.
- **Parallel workers:** a single dict write is safe in CPython, but `summary` can iterate while a worker inserts ("dictionary changed size"). Take a lock, or snapshot the dict first.
- **How it evolves:** a results table `(run_id, case_id, attempt, passed)` with a unique index, and the latest attempt per case picked in the query.
:::

---

## 9. Repository Merkle tree {#k-merkle}

> You're working on the part of a code editor that keeps a repository in sync with a server. A repo can hold hundreds of thousands of files, and comparing them one by one is too slow. Build a Merkle tree over a real folder on disk, so two snapshots of the folder can be compared quickly.

Implement this class:

```python
class MerkleTree:
    def build(self, path):
        """Read the folder at path. Return a tree of your own design."""

    def get_hash(self, path, tree):
        """Return the hash stored for a relative path, like "src/db.py"."""

    def diff(self, tree_a, tree_b):
        """Return the changes from tree_a to tree_b: a list of (path, status)."""
```

**Requirements**

- A file's hash comes from its content. A folder's hash comes from what's directly inside it.
- `status` is `"ADDED"`, `"REMOVED"` or `"MODIFIED"`. Report files, not folders.
- `diff` must not look inside a folder whose hash didn't change.
- Write your own tests, using real temporary folders.

**Example**

```text
Monday            Tuesday
src/app.py        src/app.py
src/db.py         src/db.py
src/util/io.py    src/util/io.py   (edited)
docs/a.md         docs/a.md
docs/b.md         docs/c.md        (b.md deleted, c.md is new)
lib/x.py          lib/x.py
lib/y.py          lib/y.py

diff(monday, tuesday) ==
  [("docs/b.md", "REMOVED"), ("docs/c.md", "ADDED"), ("src/util/io.py", "MODIFIED")]
```

**Walkthrough** (12:50)

::: video w01
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What counts as a change? *Content and names. Not timestamps, or identical folders would look different.*
- Is a rename special? *Not at first. It's one removed file and one added file.*
- Can files be huge? *Assume yes, so read them in pieces.*
- Symbolic links? *Assume none. Say you'd skip them, so a link can't trap you in a loop.*
- A path that isn't in the tree? *Raise `KeyError`.*

### 2. The idea

Two moves. Hash bottom up: a folder's hash needs its children's hashes first, and recursion gives you that order. Compare top down: if two hashes match, everything below them matches, so skip the whole subtree.

### 3. Code

```python
import hashlib
import os
from dataclasses import dataclass


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
```

### 4. Quick tests

```python
import tempfile
from pathlib import Path


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

m = MerkleTree()
a, b = tree(MONDAY), tree(TUESDAY)
assert m.diff(a, b) == [("docs/b.md", "REMOVED"), ("docs/c.md", "ADDED"), ("src/util/io.py", "MODIFIED")]
assert m.diff(a, tree(MONDAY)) == []                                  # identical folders, different paths
assert m.get_hash("src/util/io.py", a) == a.children["src"].children["util"].children["io.py"].hash
assert raises(KeyError, m.get_hash, "src/nope.py", a)
assert raises(KeyError, m.get_hash, "src/app.py/x", a)
assert m.diff(tree({"x": "1"}), tree({"y": "1"})) == [("x", "REMOVED"), ("y", "ADDED")]         # a rename
assert m.diff(tree({"p": "1"}), tree({"p/q": "1"})) == [("p", "REMOVED"), ("p/q", "ADDED")]     # file to folder
assert tree({"p": ""}).hash != tree({}, dirs=["p"]).hash              # empty file, empty folder
```

### 5. Follow-ups

- **Complexity:** `build` reads every byte once. `get_hash` takes one step per level. `diff` only walks the branches that changed.
- **One file changes after build:** don't rebuild. Rehash that file, then only its parents, up to the root.
- **Two machines:** send the root hash first. If it differs, ask for the children's hashes, and go down only where they differ. It's the same diff, with a network call at each step.
- **Renames:** a file's hash comes only from its content, so a removed file and an added file with the same hash are a move.
- **Millions of files:** store the tree on disk, and use a file's size and modified time to skip rehashing files that can't have changed.
:::

---

## 10. Streaming text parser {#k-stream}

> A language model's reply reaches the editor in chunks, and the editor shows it as it arrives. A chunk can be cut anywhere, even in the middle of a delimiter. Build a parser that takes the chunks one at a time, and marks each part of the reply as plain text, inline code or a code block.

Here's one interface. Propose another if you prefer:

```python
class StreamParser:
    def feed(self, chunk):
        """Take the next chunk. Return the (kind, text) events ready to show."""

    def finish(self):
        """The stream ended. Return any events still waiting."""
```

**Requirements**

- `kind` is `"text"`, `"inline"` or `"fence"`.
- One backtick opens and closes inline code. Three backticks in a row open and close a code block, also called a fence.
- The result can't depend on where the cuts land. Pieces may be sized differently, but every character must get the same kind.
- Style it as soon as you can. Once you know you're in code, send it as code, even before the closing delimiter arrives.
- Never take back what you've sent. A reader can be selecting text while the reply is still arriving.

**Example**

```text
feed("Use `x` th")   -> [("text", "Use "), ("inline", "x"), ("text", " th")]
feed("en `")         -> [("text", "en ")]
feed("``py\npr")     -> [("fence", "py\npr")]
feed("int(1)\n`")    -> [("fence", "int(1)\n")]
feed("``")           -> []
feed(" done")        -> [("text", " done")]
finish()             -> []
```

**Walkthrough** (12:32)

::: video w02
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What if the stream ends inside code? *It stays code. It's already on screen.*
- Two backticks on their own? *Ordinary characters.*
- One backtick inside a code block? *Ordinary code. Only three in a row close it.*
- The language name after the opening fence, or a fence in the middle of a line? *Keep it simple first. They're follow-ups.*

### 2. The idea

A state machine with three states: text, inline and fence. The catch is that one backtick can't be decided yet: it may open inline code, start a fence, or be an ordinary character. So hold it and keep a count, and decide when a different character arrives or the count hits three. Between chunks, the parser only has to remember the state and the held count.

### 3. Code

```python
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
```

### 4. Quick tests

```python
import random


def merged(events):                  # cuts change the piece sizes, so glue neighbors of the same kind
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
WANT = [("text", "Use "), ("inline", "x"), ("text", " then "), ("fence", "py\nprint(1)\n"), ("text", " done")]
assert run(["Use `x` th", "en `", "``py\npr", "int(1)\n`", "``", " done"]) == WANT
assert run(list(SAMPLE)) == WANT
for s in [SAMPLE, "a``b", "`a", "```a", "a`", "a``", "```a``b```c", "````", "`a``b`", "```a`b```", "", "``````", "x```"]:
    for _ in range(300):
        assert run(random_cuts(s)) == run([s]), s
assert run(["a``b"]) == [("text", "a``b")]
assert run(["```a`b```c"]) == [("fence", "a`b"), ("text", "c")]
assert run(["a``"]) == [("text", "a``")]
assert StreamParser().feed('`print("hello wor') == [("inline", 'print("hello wor')]    # styled before it closes
```

### 5. Follow-ups

- **Complexity:** one step per character. Between chunks, it holds at most two backticks.
- **The language name:** add a fourth state after the opening fence, which collects characters up to the newline.
- **Fences only at the start of a line:** remember whether the last character was a newline. Anywhere else, three backticks are ordinary characters.
- **Other marks, like bold:** the same trick. A star might be the first of two stars, so hold it until you can tell.
- **On the screen:** each event adds to the last block, or opens a new one. Old text is never touched, which is what keeps a selection working.
:::

---

## 11. Hierarchical rate limiter {#k-limiter}

> We send notifications to users, and too many of them annoy people. Every user belongs to one team, and every team belongs to one company. Before each send, decide whether it may go out.

Implement this class:

```python
class NotificationLimiter:
    def __init__(self, user_to_team, team_to_company):
        """Two dicts: a user id to a team id, and a team id to a company id."""

    def should_send_notifications(self, user_id, timestamp):
        """Return True if this notification may be sent, and False if not."""
```

**Requirements**

- In any sliding window of 600 seconds, allow at most 3 sends per user, 10 per team and 20 per company.
- An earlier send at time `s` counts at time `t` only if `t - s < 600`.
- A send goes through only if every level has room. A refused send counts nowhere, at any level.
- Timestamps are in seconds, and never go backward.

**Example 1: one user**

```text
should_send_notifications("u1", 1)    -> True
should_send_notifications("u1", 2)    -> True
should_send_notifications("u1", 3)    -> True
should_send_notifications("u1", 4)    -> False   (the user's limit)
should_send_notifications("u1", 601)  -> True    (the send at time 1 has expired)
should_send_notifications("u1", 602)  -> True
```

**Example 2: five users on one team**

```text
u1 to u5 at times 1 to 5    -> True, five times
u1 to u5 at times 6 to 10   -> True, five times
u1 at time 11               -> False   (the team's limit, though u1 has sent only 2)
u2 at time 601              -> True    (the send at time 1 has expired)
```

**Walkthrough** (11:57)

::: video w03
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Is something exactly 600 seconds old still inside? *No, it has expired.*
- Do many threads call this at once? *Assume yes.*
- An unknown user? *Assume it's an error.*
- Is this one server or many? *One for the code. We'll talk about many afterward.*

### 2. The idea

Keep the time of every accepted send, in one deque per level, so old sends can fall off the left in one step. Then make two moves. Look: drop what's expired, and check every level for room, changing no counts. Commit: only if all three said yes, add the time to all three. Hold one lock around both moves.

### 3. Code

```python
import threading
from collections import defaultdict, deque


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
```

### 4. Quick tests

```python
T, F = True, False
L = NotificationLimiter({"u1": "t1"}, {"t1": "c1"})
ask = L.should_send_notifications
times = (1, 2, 3, 4, 601, 602)
assert [ask("u1", t) for t in times] == [T, T, T, F, T, T]

five = {f"u{i}": "t1" for i in range(1, 6)}
L = NotificationLimiter(five, {"t1": "c1"})
ask = L.should_send_notifications
calls = [(f"u{i}", i) for i in range(1, 6)] + [(f"u{i}", i + 5) for i in range(1, 6)] + [("u1", 11), ("u2", 601)]
assert [ask(u, t) for u, t in calls] == [T] * 10 + [F, T]

# a refused send leaves no trace
L = NotificationLimiter({**five, "z": "t1"}, {"t1": "c1"})
ask = L.should_send_notifications
for i in range(1, 6):
    ask(f"u{i}", 0)
    ask(f"u{i}", 1)
assert ask("z", 2) is False
assert len(L.sent[("user", "z")]) == 0

# the company limit: two full teams, then a third team is refused
org = {f"a{i}": "ta" for i in range(4)} | {f"b{i}": "tb" for i in range(4)} | {"c0": "tc"}
L = NotificationLimiter(org, {"ta": "c", "tb": "c", "tc": "c"})
ask = L.should_send_notifications
for u in [f"{t}{i}" for t in "ab" for i in range(4)]:
    for _ in range(3):
        ask(u, 0)
assert ask("c0", 1) is False

# the exact boundary
L = NotificationLimiter({"u1": "t1"}, {"t1": "c1"})
ask = L.should_send_notifications
for _ in range(3):
    ask("u1", 0)
assert ask("u1", 599) is False
assert ask("u1", 600) is True

# 50 threads: exactly 20 get through
org = {f"u{i}": f"t{i}" for i in range(50)}
L = NotificationLimiter(org, {f"t{i}": "c" for i in range(50)})
res = []


def worker(i):
    for _ in range(3):
        res.append(L.should_send_notifications(f"u{i}", 0))


threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
[t.start() for t in threads]
[t.join() for t in threads]
assert sum(res) == 20
```

### 5. Follow-ups

- **Complexity:** a few steps per call, on average, since each send is removed at most once. No log ever holds more than its limit: 3, 10 or 20.
- **Why not a fixed window?** One counter reset every 10 minutes allows a burst around the reset: 3 just before and 3 just after, with a limit of 3.
- **Many servers:** a lock only protects one program. Move the logs to a shared store like Redis, and run a Lua script that prunes, looks at all three, and adds to all or none. Redis runs it as one step.
- **Redis split across machines:** one script must reach all its keys on one machine, so put all of a company's keys together with a hash tag. A very busy company can then overload its machine.
- **Retries:** give each send a request id. If you've seen that id, return the first answer, and count nothing.
- **Redis is down:** allow the send or refuse it. It's a product choice, so say which one and why.
- **Limits in the thousands:** a log per level gets big, so switch to approximate counters.
:::
