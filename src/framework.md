# The 60-minute framework

**TLDR.** Turn the vague ask into numbers. Build the simplest V1. Defend every choice. Add spike defenses cheapest first. Plan go-live. Close with trade-offs. Keep 2 minutes for questions.

```timeline
1|Clarify|6
2|Version 1|14
3|Decisions|6
4|Spike|14
5|Go-live|12
6|Wrap-up|6
```

::: phase 1 | Clarify | 0 to 6 min

**Leave with:** 5 to 7 numbers, 2 invariants (rules that must never break, like "never oversell"), and the real bottleneck.

- **Ask:** core action, normal vs spike (how big, how fast, how long), hard limit (seats, ovens, stock), what must never fail, what may degrade, team and time.
- **Math:** peak reads/s = peak-minute visitors / 60 x calls each. Writes are capped by the hard limit.

> "So the spike is a read problem. The write path is small but must be correct."

:::

::: phase 2 | Version 1 | 6 to 20 min

**Leave with:** a diagram, endpoints, schema, one request end to end.

```flow
Browser
CDN: static site, images
Load balancer
API: 2+ identical copies
Postgres | Stripe: webhook back | Sweeper job
```

- 4 to 6 endpoints. The one that writes gets an idempotency key (card 10), so a double tap can't create two orders.
- 2 or 3 database tables, each with a status column and a uniqueness rule.
- Walk one order through step by step, including what happens if a step fails.

> "At N writes a second, this fits on one database."

:::

::: phase 3 | Decisions | 20 to 26 min

**Leave with:** each choice and the alternative it beat.

> "X over Y, because Z at these numbers. I'd revisit if W."

- Postgres over DynamoDB (card 4) · conditional update over a Redis counter (8) · hold, then charge (9) · hosted checkout over your own card form (17) · one service over microservices (3) · a simple queue over Kafka (6) · managed containers over Kubernetes (3).

:::

::: phase 4 | Spike defenses | 26 to 40 min

**Leave with:** a cheapest-first list and "what breaks first".

1. CDN for static files (card 1)
2. Cache reads for 1 to 5 s (card 11)
3. Waiting room, behind a flag (card 13)
4. Rate limits per IP and per user (card 12)
5. Conditional update and expiring holds: **no oversell** (cards 8, 9)
6. Idempotency keys: **no double charge** (card 10)
7. Queue for work that can wait (card 6)
8. Connection pooler and provider limits (cards 15, 17)

:::

::: phase 5 | Go-live | 40 to 52 min

**Leave with:** a checklist you could run on launch day.

1. Load test at 2 to 3x peak, with a pass bar (card 20)
2. Pre-scale an hour early; autoscaling is too slow (card 16)
3. Kill switches, each one tested (card 19)
4. Canary release, then a code freeze before the event (card 21)
5. Dashboards: errors, p95 latency, queue length, held vs paid (card 22)
6. Runbook, on-call person, and a game day rehearsal (cards 20, 22)
7. Ask providers like Stripe to raise rate limits ahead of time (card 17)

> "If errors pass 2% for 2 minutes, I turn on the waiting room."

:::

::: phase 6 | Wrap-up | 52 to 58 min

**Leave with:** a 30-second summary and 3 or 4 trade-offs.

- **Summary:** the bottleneck, how the invariants hold, how the spike is absorbed, how go-live is de-risked.
- **Trade-offs:** stale cached reads, holds that lock stock, one region, less control with hosted checkout.

:::

## Habits that get scored

::: chips
- Talk the whole time
- Name each phase
- Check in every 5 to 10 min
- A reason for every choice
- Numbers, not adjectives
- Don't over-engineer
- One real story from your own work
:::

## Spot the shape early

| Shape | Must never fail | Key trick |
|---|---|---|
| **Limited inventory** | No oversell, no double charge | Conditional decrement, holds, waiting room |
| **Write-heavy counter** | Each event counted once | Send totals, not deltas; count async |
| **Job burst** | No job lost or run twice | Queue, workers, idempotent jobs, lanes |
| **Reservations** | No double booking | Unique (resource, slot) |
| **Notification fan-out** | Everyone told, once | Queue, batches, provider rate limits |

**Red flags:** Kafka and microservices for a small shop, no numbers, no "why not X", no plan for oversell or double charge, stopping at the diagram.

See [Components](components.html) for the 23 parts you need, drawn, and the numbers to know.
