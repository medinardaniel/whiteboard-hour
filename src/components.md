# The 23 components you need

**TLDR.** Learn these 23 well and you can design any small-business-plus-spike prompt. They're in the order you use them in the interview. Each card shows a diagram, what the part is, an analogy, a real scenario with and without it, the line to say, and the related terms as tiles. Everything else is in the [optional reference](reference.html); skip it for now.

**One-sheet view:** [all the cards plus a worked framework (PDF)](cards-sheet.pdf), 2 landscape pages.

**Study plan**

- **Day 1:** cards 1 to 10. Then draw the pizza-shop V1 from memory.
- **Day 2:** cards 11 to 18. Then answer 2 sample questions out loud.
- **Day 3:** cards 19 to 23 and the numbers. Then 2 more questions and 10 drills.

## Draw these in V1

[[cards:v1]]

## Protect the invariants

An invariant is a rule that must never break, like "never sell more pizzas than the ovens can make".

[[cards:invariants]]

## Survive the spike

[[cards:spike]]

## Call third parties safely

[[cards:third]]

## Go-live

[[cards:golive]]

## Put together: the pizza shop

```flow
Browser
CDN: site, photos, menu JSON for 30 s
WAF and rate limits: per IP, 2 orders per phone
Load balancer
API: 2 copies, more added before the game
Redis cache: slots, 2 s | Postgres: menu, slots, orders | Stripe checkout: webhooks, idempotency keys
Queue + worker: texts and emails | Sweeper job: expired holds, checks Stripe first
```

Behind flags: a waiting room (off by default), pause orders, hide photos, close a slot.

## Numbers to know

| Fact | Value |
|---|---|
| 1M events a day | about 12 a second on average; the busiest hour is 2 to 3x that |
| One row | about 1 KB, so 1M rows is about 1 GB: "it all fits in memory" |
| One Postgres database | thousands of simple writes a second |
| Postgres connections | a few hundred at most, so use a pooler (card 15) |
| Redis, one server | about 100,000 reads or writes a second, each under 1 ms |
| One API copy | hundreds to a couple of thousand requests a second |
| Autoscaling | reacts in 1 to 5 minutes |
| A payment call | 200 ms to over 1 s; Stripe allows about 100 requests a second by default |

## Skipped for now

You can name these if they come up, but don't study them: API gateway, Kubernetes details, search engines, time-series, graph and wide-column databases, data warehouses, isolation levels, CAP theorem, optimistic locks, sagas, distributed locks, write-through caching, maps, auth providers, multi-region design, traces and SLO math, CI/CD, chaos tooling. They're all drawn in the [optional reference](reference.html).
