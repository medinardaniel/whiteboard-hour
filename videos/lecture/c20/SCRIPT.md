# Load test and game day: lecture video (component 20)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component twenty: the load test and the game day.
2. `SD` Two practices before a launch. A load test fires fake traffic, two to three times the expected peak, at a test copy, against a pass bar. A game day is a rehearsal: flip switches, fake outages. *(pause)*
3. `SD2` Tools like k6 or Locust play the fake users. *(pause)*
4. `S1` Why bother? Otherwise you find problems on sale day. At six AM, checkout crawls: a missing index. An index lets the database jump to the rows it needs, instead of reading every row.
5. `S1b` Then payments fail, and nobody has practiced pausing orders. *(pause)*
6. `S2` A load test starts with a script of one user: open the deal, add the TV, and pay, with Stripe in test mode. The tool runs thousands at once.
7. `S3` It ramps traffic past the expected peak, to two or three times it, aimed at staging: a test copy, never real customers.
8. `S3b` And you write the pass bar first. Zero TVs oversold, zero double charges, and p95 under five hundred milliseconds.
9. `S3c` P95 means ninety-five percent of requests are faster than that. It shows the slow tail. *(pause)*
10. `S4` A game day is the rehearsal: flip every switch, fake Stripe errors, check that alerts fire, and time each response. *(pause)*
11. `S5` The load test finds slow queries, missing indexes, and too few copies.
12. `S5b` The game day finds switches that don't work, and alerts that don't fire. *(pause)*
13. `S6` Now a real case, two days before a doorbuster sale. k6 simulates a hundred and twenty thousand visitors. A thousand try to buy one TV deal, with fifty in stock.
14. `S6b` Run one sells exactly fifty, with no double charges, but fails the p95 bar: a missing index.
15. `S6c` Add the index, rerun, and it passes. Found two days early, not at six AM on sale day. *(pause)*
16. `S6d` Then the game day: every switch flipped, Stripe errors faked, the response timed. *(pause)*
17. `S7` It sits outside your system, aimed at a full copy of it, with Stripe in test mode. *(pause)*
18. `S8` Two things to know. Size staging like production, or the numbers lie.
19. `S8b` And fake traffic is a guess, so model real users: most browse, a few buy. *(pause)*
20. `S9` In the interview, say: pass means zero oversold, zero double charges, and p95 under five hundred milliseconds.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| p95 | p ninety-five |
| P95 | P ninety-five |
| AM | A M |
| k6 | k six |
