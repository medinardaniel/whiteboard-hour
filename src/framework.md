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

**Leave with:** 5 to 7 numbers, 2 invariants, the real bottleneck.

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
API: 2+ stateless instances
Postgres | Stripe: webhook back | Sweeper job
```

- 4 to 6 endpoints. The write gets an idempotency key.
- 2 or 3 tables, each with a status and unique constraints.
- Walk the write through its transaction, including failure.

> "At N writes a second, this fits on one database."

:::

::: phase 3 | Decisions | 20 to 26 min

**Leave with:** each choice and the alternative it beat.

> "X over Y, because Z at these numbers. I'd revisit if W."

- Postgres over DynamoDB · conditional UPDATE over a Redis counter · hold, then charge · hosted checkout over a card form · one service over microservices · managed queue over Kafka · managed containers over Kubernetes.

:::

::: phase 4 | Spike defenses | 26 to 40 min

**Leave with:** a cheapest-first list and "what breaks first".

1. CDN for static content
2. Short cache (1 to 5 s) on reads
3. Waiting room, behind a flag
4. Rate limits per IP and per user
5. Atomic decrement or expiring holds: **no oversell**
6. Idempotency keys: **no double charge**
7. Queue for non-urgent work
8. Connection pooler and third-party limits

:::

::: phase 5 | Go-live | 40 to 52 min

**Leave with:** a checklist you could run on launch day.

1. Load test at 2 to 3x peak, with a pass bar
2. Pre-scale an hour early (autoscaling is too slow)
3. Kill switches, each one tested
4. Canary, then code freeze before the event
5. Dashboards: errors, p95, queue depth, held vs paid
6. Runbook, on-call, and a game day
7. Raise third-party rate limits ahead of time

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

See [Components](components.html) for every building block, drawn, and the numbers to know.
