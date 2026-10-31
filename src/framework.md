# System design interview framework

**TLDR.** Six phases in 60 minutes. Ask questions until you have numbers. Build the simplest version that works. Give a reason and a rejected alternative for every choice. Add spike defenses cheapest first. Spend real time on go-live. Finish with a summary and the trade-offs.

| # | Phase | Minutes | You leave this phase with |
|---|---|---|---|
| 1 | Clarify | 0 to 6 | 5 to 7 numbers, 2 invariants, the real bottleneck |
| 2 | Version 1 | 6 to 20 | A diagram, endpoints, schema, one request end to end |
| 3 | Decisions | 20 to 26 | Each choice with the alternative it beat and why |
| 4 | Spike defenses | 26 to 40 | A cheapest-first list, plus answers to "what breaks first" |
| 5 | Go-live prep | 40 to 52 | A checklist you could actually run on launch day |
| 6 | Wrap-up | 52 to 58 | A 30-second summary and 3 or 4 trade-offs |

Keep 2 minutes of buffer for the interviewer's questions. If a phase runs more than 3 minutes over, say so and move on: "I'll leave V1 there so we have time for the spike."

---

## The habits that get scored

1. **Talk the whole time.** Silence reads as stuck. Think out loud: "I'm deciding between X and Y. X is simpler, so..."
2. **Signpost.** Start each phase by naming it: "Now version one, the simple design for normal load."
3. **Check in.** Every 5 to 10 minutes: "Does this match what you had in mind, or should I go deeper anywhere?" The interviewer often steers you toward what they grade.
4. **A reason for every choice.** Never just "I'd use Postgres." Say "Postgres, not DynamoDB, because..."
5. **Don't over-engineer.** If you add a component, say what problem it solves at *these* numbers. If it doesn't solve one yet, leave it out or keep it behind a flag.
6. **Use numbers.** "Ten writes a second fits on one database," not "this scales."
7. **Bring your own experience in.** One real story per interview is worth more than any amount of theory (see "Your stories" below).

---

## Phase 1: Clarify (0 to 6 min)

**Goal:** turn a vague ask into numbers, find the hard limit, and name what must never break.

Open with: "Before I design anything, I'll spend about five minutes on questions."

### Question bank (ask 5 to 7, not all)

| Topic | Ask | Why it matters |
|---|---|---|
| Users and flow | Who uses it? Web, app, both? What's the one core action? | Defines the endpoints and the core write |
| Normal traffic | What's a normal day or hour? | Your baseline for V1 |
| The spike | How big, how fast does it arrive, how long does it last? (10x for 2 hours is a different problem from 1,000x for 5 minutes) | Decides whether autoscaling is enough or you must pre-scale |
| Hard limit | Is there a fixed supply? (seats, ovens, units, slots) | Often caps the writes, so the spike becomes a read problem |
| Must never fail | What would be a disaster? (oversell, double charge, lost order, lost booking) | Becomes your invariants, protected in the database |
| May degrade | What can be slow or missing for an hour? (photos, emails, status page) | Tells you what to put on a queue or switch off |
| Team, time, budget | How many engineers, how long, what's already in place? (payments, cloud) | Justifies keeping it simple |
| Read vs write | Are users mostly looking or mostly acting? | Picks the cache and DB strategy |
| Geography | One city, one country, global? | Usually one region is fine; say so |

### Then do the math out loud

- **Peak reads per second** = visitors at the peak minute / 60 x calls per visit.
- **Peak writes per second** = actions at the peak minute / 60. Cap it by the hard limit.
- **Data size** = rows x about 1 KB. Usually tiny, so say "the data fits in memory."
- **One-line conclusion:** "So the spike is a read problem, and the write path is small but has to be correct."

**Common mistakes:** asking questions without turning the answers into numbers; skipping "what must never fail"; spending 12 minutes here.

---

## Phase 2: Version 1 (6 to 20 min)

**Goal:** the simplest design that works at normal load, with one request traced end to end.

Say: "Version one is the simple design. I'll get one order working end to end, then harden it for the spike."

### The default V1 (start here, change only with a reason)

```flow
Browser
CDN: static site, images
Load balancer
API service: 2+ stateless instances
Postgres (managed) | Third party: Stripe, SMS, webhook back | Scheduled job: sweeper, reports
```

### Cover these four things

1. **Boxes and arrows.** Client, CDN, load balancer, API, one database, any third party, any background job.
2. **Endpoints.** 4 to 6 of them. Mark the one that writes, and give it an idempotency key.
3. **Schema.** The 2 or 3 core tables, with their key columns, a status field, and unique constraints.
4. **One request end to end.** Walk the core write step by step, including the transaction and what happens on failure.

### Say it out loud

"At about N writes a second and a few GB of data, **this fits on one database** with room to spare." Interviewers listen for this sentence because it shows you can tell when you don't need to scale.

**Common mistakes:** drawing 12 boxes before one request works; putting in Kafka, microservices or sharding at 10 writes a second; forgetting the schema.

---

## Phase 3: Decisions (20 to 26 min)

**Goal:** show judgment. Each choice gets a rejected alternative and a reason tied to the numbers.

### Template

> "I picked **X** over **Y** because **Z, at these numbers**. I'd revisit if **W**."

### Decisions that come up almost every time

| Decision | Usual pick | Usual rejected | Reason to give |
|---|---|---|---|
| Database | Postgres (managed) | DynamoDB / MongoDB | Transactions across rows; small scale; team knows SQL |
| Oversell guard | Conditional UPDATE in the DB | Redis counter / distributed lock | One source of truth; the DB handles the write rate easily |
| Payment timing | Hold, then charge | Charge, then check | No refunds when you run out |
| Payment UI | Stripe hosted checkout | Own card form | No card data on your servers (PCI scope) |
| Services | One service (modular monolith) | Microservices | Small team, short timeline |
| Async work | Managed queue (SQS, Service Bus) | Kafka | Simple task queue; no need to replay a stream |
| Hosting | Managed containers (ECS, Cloud Run, Container Apps) | Kubernetes / raw VMs | Nobody to run a cluster |

Expect "Why not X?" Answer in three parts: what X is good at, why you don't need it here (numbers), and when you'd switch.

---

## Phase 4: Spike defenses (26 to 40 min)

**Goal:** survive the spike without breaking the invariants. Add defenses **cheapest first**, and say which one you'd skip.

Say: "Now the spike. I'll add defenses cheapest first."

| # | Defense | Protects | Note |
|---|---|---|---|
| 1 | CDN for static content | API, bandwidth | Free win. Cache the menu or catalog JSON for 30 to 60 s too |
| 2 | Cache the read paths (short TTL) | DB reads | 1 to 5 s for availability; it's a hint, the DB write is the truth |
| 3 | Waiting room or queue in front of checkout | Everything behind it | Often keep it behind a flag; turn on only if traffic beats the plan |
| 4 | Rate limits per user and per IP | Fairness, bots, retry storms | At the edge (WAF) plus a business limit (2 per phone) |
| 5 | Atomic inventory decrement or expiring holds | **No oversell** | `UPDATE ... WHERE remaining >= n`; holds expire after N min |
| 6 | Idempotency keys on orders and payments | **No double charge** | Client key, provider key, webhook event id |
| 7 | Async queue for non-urgent work | Checkout latency | Emails, SMS, receipts, analytics |
| 8 | Connection limits and third-party limits | DB, payment provider | Connection pooler; call the provider only after a hold succeeds |

### Follow-ups to expect (and the answer shape)

| Interviewer asks | Answer shape |
|---|---|
| "The payment provider is slow or down." | The hold already protects inventory. Timeout plus retry with the same idempotency key. Kill switch to pause new orders. Reconcile with the provider before releasing a hold. |
| "The spike is 10x bigger. What breaks first?" | Name the first thing to fail and why (usually the read path or DB connections, not the capped writes). Then the defense: CDN, cache, waiting room on. |
| "The database goes down." | Managed failover (about 30 to 60 s), retries on the client, the waiting room absorbs it. RPO and RTO from backups. |
| "The cache goes down." | Reads fall through to the DB. Protect it with a connection cap and load shedding. Never let the cache be the source of truth. |
| "A webhook arrives twice, or late." | Dedupe on event id. The order status only moves forward. Reconcile job for late ones. |
| "Bots buy everything." | Rate limits, one per account or phone, CAPTCHA at the waiting room (vendor), and cancel abusive orders afterward. |
| "One hot item or key." | It's a single row: a conditional update serializes on it. That's fine at 10/s. At 1,000/s, split the counter into N buckets or pre-allocate in batches. |
| "How do you know it's working?" | Name the 3 or 4 metrics you'd watch (see go-live). |

---

## Phase 5: Go-live prep (40 to 52 min)

**Goal:** the part most candidates skip, and often what interviewers care about most. Be concrete: numbers, dates, pass criteria.

Say: "Go-live prep. This is where launches fail, so I'll be specific."

| # | Item | Make it concrete |
|---|---|---|
| 1 | **Load test at 2 to 3x peak** | Tool (k6, Locust), environment (staging, provider in test mode), pass bar: 0 oversold, 0 double charges, p95 < 500 ms |
| 2 | **Pre-scale** | "At T minus 1 hour, scale to N instances, bump the DB tier, warm the CDN." Autoscaling takes minutes; the spike takes seconds |
| 3 | **Feature flags and kill switches** | List them: pause orders, waiting room on, hide heavy features, close a slot. Test each one |
| 4 | **Staged rollout with tested rollback** | Canary before the freeze. Code freeze before the event. No deploys during the window |
| 5 | **Dashboards and alerts** | Errors, p95 latency, queue depth, inventory left, held vs paid, provider errors, DB connections |
| 6 | **Runbook, on-call, game day** | Owner per alert, a written "if X then Y", and a dry run: load test, flip every switch, fake a provider outage |
| 7 | **Raise third-party limits** | Ask the payment or SMS provider to raise rate limits ahead of time |

### "It's go-live morning. What are you watching?"

- **Before:** pre-scale done, CDN hit rate high, flags in the right state, on-call present.
- **During:** error rate, p95 latency, queue depth, held vs paid (a gap means payments are failing), inventory left vs the real world.
- **The trigger:** "If X crosses Y, I flip Z." For example, error rate over 2% for 2 minutes turns on the waiting room.

---

## Phase 6: Wrap-up (52 to 58 min)

**Summary (30 seconds):** the bottleneck, how the invariants are protected, how the spike is absorbed, how go-live is de-risked.

**Trade-offs (3 or 4):** what you knowingly gave up. Examples:
- Cached availability can be stale for a few seconds, so some users learn "sold out" at checkout.
- Holds lock inventory for N minutes even if unpaid.
- One region and one database: managed failover, not multi-region.
- Hosted checkout: less control over the payment page.

**What I'd do next with more time:** one or two items, such as multi-region or a better fairness system.

---

## Prompt archetypes

Most "small business plus spike" prompts are one of these. Recognize the shape early.

| Archetype | Examples | Invariant | Key trick |
|---|---|---|---|
| Limited inventory drop | Pizza promo, flash-sale doorbusters, sneaker drop | No oversell, no double charge | Conditional decrement plus expiring holds; waiting room; reads are the spike |
| Write-heavy counter | Likes, reactions, step-challenge leaderboards | Each event counted once, none lost | Send totals instead of deltas where you can; otherwise append events to a queue or log and count async; dedupe per user; show approximate totals |
| Job burst | Photo processing before a deadline, video encoding, report generation | No job lost, none run twice | Queue plus a worker pool; concurrency caps; retries with idempotency; backpressure; priority lanes |
| Reservations | Restaurant tables, appointments, classes | No double booking | Unique constraint on (resource, time slot); holds with expiry |
| Notifications fan-out | Flash-sale alert to 1M users | Delivered at most once, eventually | Queue, batch sends, provider rate limits, retries with backoff |

---

## Your stories (use one per interview)

Map one real reliability story from your own work to each phase. Keep each to two sentences: what happened, and what you changed. Prepare them before the interview so you are not inventing one under pressure.

| Story shape | Fits | Why it lands |
|---|---|---|
| You capped concurrency against a quota or pooled a scarce resource | Spike: third-party and connection limits | Shows you know limits live outside your own code |
| A retry duplicated work, and you made it idempotent | Follow-up: provider slow or down | Shows you know retries are only safe when repeats are no-ops |
| You built a dashboard that told on-call what to do, not just that something failed | Go-live: dashboards | Shows you think about the person reading the alert |
| A deploy broke in-flight work during a busy window | Go-live: code freeze, no deploys during the window | Shows you learned why freezes exist |

---

## Red flags (these get a no-hire)

- Drawing the "Netflix architecture" (Kafka, microservices, sharding) for a small business.
- No numbers anywhere.
- No answer to "why this and not that."
- Never mentioning how you stop overselling or double charging.
- Ending at the diagram, with nothing about load testing, rollout or monitoring.
- Long silences, or not answering the question that was asked.

---

## Rules of thumb for quick math

| Fact | Value |
|---|---|
| Seconds in a day | 86,400, about 10^5 |
| 1M events per day | about 12 per second on average |
| Normal peak vs average | 2 to 3x |
| One row | about 1 KB, so 1M rows is about 1 GB |
| Managed Postgres, one primary | thousands of simple writes/s, tens of thousands of indexed reads/s |
| Postgres connections | a few hundred max; use a pooler |
| Redis, one node | about 100,000 ops/s, under 1 ms |
| One stateless API instance | hundreds to a couple thousand simple requests/s |
| Container autoscaling reaction | 1 to 5 minutes |
| Payment provider call | 200 ms to over 1 s |
| Stripe default rate limit (live) | about 100 requests/s; ask to raise it before a launch |

See the [Components](components.html) page for what each building block is and when to use it.
