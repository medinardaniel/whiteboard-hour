# The 23 components you need

**TLDR.** Learn these 23 well and you can design any small-business-plus-spike prompt. They're in the order you use them in the interview. Each card folds in its close cousins under "Also covers", so you know the word if the interviewer says it. Everything else is in the [optional reference](reference.html); skip it for now.

**Study plan**

- **Day 1:** cards 1 to 10. Then draw the pizza-shop V1 from memory.
- **Day 2:** cards 11 to 18. Then answer 2 sample questions out loud.
- **Day 3:** cards 19 to 23 and the numbers. Then 2 more questions and 10 drills.

## Draw these in V1

| # | Part | What it is | Use it for | Say this | Also covers |
|---|---|---|---|---|---|
| 1 | CDN | Copies of your static files, and short-lived public JSON, on servers near users | Every design. It's the first spike defense | "The CDN takes most of the read spike before it reaches us." | DNS: lower its TTL before launch so you can redirect fast |
| 2 | Load balancer | Spreads requests over 2+ API instances and skips unhealthy ones | Every design, for availability | "Two instances behind a load balancer, so one can die." | Health checks; HTTPS ends here; a reverse proxy is the same idea |
| 3 | Stateless API, one service | Your backend. It keeps no user state in memory, so any instance can serve any request | Every design | "One service with clear modules on managed containers. Stateless, so I scale by adding instances." | Monolith over microservices (small team); managed containers over Kubernetes (nobody to run a cluster); serverless is fine for webhooks and glue |
| 4 | Postgres (managed) | A relational database with transactions, unique constraints and indexes. Your source of truth | Orders, payments, stock, bookings | "Postgres, not DynamoDB: my write changes two rows together, and at these numbers one primary is plenty." | ACID transaction (all or nothing); an index on every hot query; DynamoDB is for huge scale and key lookups, with a hot partition limit of about 1,000 writes/s; sharding: avoid in V1 |
| 5 | Object storage | Files by key: photos, PDFs, exports. Cheap and nearly unlimited | Anything bigger than a row | "Browsers upload straight to storage with a signed URL, so files never touch the API." | Serve the files through the CDN |
| 6 | Queue + workers | Jobs wait in a queue, and workers take them one at a time | Emails, texts, renders: anything that can lag | "At-least-once delivery, plus workers that are safe to run twice." | Dead-letter queue after N failures; scale workers on queue depth; Kafka is a replayable log for many readers, not needed here; pub/sub sends one event to many; outbox: write the event in the same transaction |
| 7 | Sweeper and reconciliation jobs | Code on a timer that finds stale state and fixes it | Expired holds, stuck orders, checking against Stripe | "Every minute, release expired holds, after asking Stripe whether they were paid." | Cron; make sure only one copy runs at a time |

## Protect the invariants

| # | Part | What it is | Use it for | Say this | Also covers |
|---|---|---|---|---|---|
| 8 | Conditional update | `UPDATE stock SET left = left - n WHERE id = ? AND left >= n`. Zero rows updated means sold out | Any limited stock, seats or slots: **no oversell** | "One statement, so the database refuses to go below zero." | `SELECT ... FOR UPDATE` when the logic doesn't fit in one statement; avoid a Redis counter or distributed lock (two sources of truth) |
| 9 | Holds that expire | Reserve first, pay within N minutes. The status only moves forward: held, then paid or expired | Anything reserved before payment | "Hold, then charge, so we never take money for something we can't deliver." | State machine: a late webhook can't move an order backward; the sweeper (card 7) frees expired holds |
| 10 | Idempotency key | A unique id per user action. A repeat returns the first result instead of doing it again | Every write endpoint, payment call and webhook: **no double charge** | "A client key with a unique constraint, the same key passed to Stripe, and webhook event ids deduped." | Unique constraint: the same trick stops double booking (unique bay and slot); "exactly once" really means at-least-once plus idempotent |

## Survive the spike

| # | Part | What it is | Use it for | Say this | Also covers |
|---|---|---|---|---|---|
| 11 | Cache with a short TTL | A fast in-memory copy (Redis). Check the cache; on a miss, read the DB and fill the cache | Hot reads: availability, menus, catalogs | "Cached for 2 s. It's a hint; the database is the truth." | A short TTL beats invalidation; stampede: one request refreshes while others wait; hot key: a 1 s copy in each instance |
| 12 | Rate limits | Caps on requests per IP at the edge, and per user or phone in the API | Bots, retry storms, protecting provider quotas | "Per IP at the edge, and 2 orders per phone in the API." | WAF and DDoS protection usually come with the CDN |
| 13 | Waiting room | Holds users in line and lets them in at a fixed rate | Demand far above capacity, or a sale that starts at one instant | "Behind a flag. On only if traffic beats the plan." | Fairness: randomize everyone who arrived before the start |
| 14 | Replicas and failover | The primary takes writes. Replicas copy it for reads, and a standby takes over if it dies (30 to 60 s) | Read scale, surviving a DB failure | "Never read stock you're about to sell from a replica. It lags." | Multi-AZ: always; multi-region: only if RTO demands it; backups with point-in-time restore; RPO is the data you can lose, RTO is the time you're down |
| 15 | Connection pooler | Shares a small set of DB connections across many API instances | As soon as you scale out the API | "Postgres allows a few hundred connections. Without a pooler, scaling the API takes down the DB." | Keep transactions short; never call Stripe inside one |
| 16 | Pre-scaling | Scale up before a known event | Every planned spike | "Autoscaling reacts in minutes. The spike arrives in seconds." | Autoscaling stays on as the safety net; scale workers on queue depth |

## Call third parties safely

| # | Part | What it is | Use it for | Say this | Also covers |
|---|---|---|---|---|---|
| 17 | Hosted checkout + webhooks | The provider's payment page. The provider calls your URL when the payment succeeds | Every payment | "Card data never touches our servers, which shrinks PCI scope." | Webhooks: check the signature, return 200 fast, dedupe, expect them late; test mode for load tests; ask to raise the rate limit (about 100/s) before launch; SMS and email providers work the same way, through a queue |
| 18 | Timeouts, retries, circuit breaker | Every outbound call has a timeout, retries with backoff and jitter, and stops after repeated failures | Stripe, SMS, any dependency | "Retries are safe only because the call carries an idempotency key." | Bulkhead: separate pools, so a slow Stripe can't eat the threads checkout needs |

## Go-live

| # | Part | What it is | Use it for | Say this | Also covers |
|---|---|---|---|---|---|
| 19 | Flags and kill switches | Turn features on or off at runtime, with no deploy | Pause orders, waiting room on, hide photos, close a slot | "Every switch is tested on game day." | Graceful degradation (turn off extras); load shedding: a fast 503 beats everyone timing out |
| 20 | Load test and game day | Simulate 2 to 3x the peak with a pass bar, then rehearse: flip every switch, fake an outage | Before every launch | "Pass means 0 oversold, 0 double charges, p95 under 500 ms." | Chaos testing is the big-company version; capacity planning is your Clarify math written down |
| 21 | Safe deploys | Send a new version to 1 to 5% of traffic first, keep a rollback you've practiced, and freeze before the event | Every release near the event | "Nothing ships during the window." | A rolling deploy kills in-flight work unless shutdown is graceful; blue-green means an instant switch back |
| 22 | Dashboards and alerts | Latency (p95), traffic, errors and saturation, plus business numbers like held vs paid and stock left | Launch day, and every day after | "If errors pass 2% for 2 minutes, I turn on the waiting room." | p95, not the average; every alert has an owner and a runbook; logs and traces for debugging; the SLO is the target |
| 23 | Security basics | HTTPS everywhere, secrets in a vault, hosted checkout for cards, least privilege, little personal data | When asked, in one breath | "HTTPS, secrets in a vault, no card data on our servers, each service gets only what it needs." | Authentication is who you are; authorization is what you may do |

## Put together: the pizza shop

```flow
Browser
CDN: site, photos, menu JSON for 30 s
WAF and rate limits: per IP, 2 orders per phone
Load balancer
API: 2 instances, pre-scaled for the game
Redis cache: slots, 2 s | Postgres: menu, slots, orders | Stripe checkout: webhooks, idempotency keys
Queue + worker: texts and emails | Sweeper job: expired holds, checks Stripe first
```

Behind flags: a waiting room (off by default), pause orders, hide photos, close a slot.

## Numbers to know

| Fact | Value |
|---|---|
| 1M events a day | about 12 a second on average; the peak is 2 to 3x that |
| One row | about 1 KB, so 1M rows is about 1 GB: "it fits in memory" |
| One Postgres primary | thousands of simple writes a second |
| Postgres connections | a few hundred at most: use a pooler |
| Redis, one node | about 100,000 operations a second, under 1 ms |
| One API instance | hundreds to a couple of thousand requests a second |
| Autoscaling | reacts in 1 to 5 minutes |
| Payment call | 200 ms to over 1 s; Stripe allows about 100 requests a second by default |

## Skipped for now

You can name these if they come up, but don't study them: API gateway, Kubernetes details, search engines, time-series, graph and wide-column databases, data warehouses, isolation levels, CAP theorem, optimistic locks, sagas, distributed locks, write-through caching, maps, auth providers, multi-region design, traces and SLO math, CI/CD, chaos tooling. They're all drawn in the [optional reference](reference.html).
