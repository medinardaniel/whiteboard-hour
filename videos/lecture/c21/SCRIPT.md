# Safe deploys: lecture video (component 21)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component twenty-one: safe deploys.
2. `SD` A safe deploy is a way of releasing new code. You send it to a few users first, keep a tested way back, and stop releasing around the event. *(pause)*
3. `SD2` Three tools do that: the canary, the rollback, and the code freeze. *(pause)*
4. `S1` Why does it matter? Most outages come from changes. A plain release replaces the code on every copy at once.
5. `S1b` If it's broken, every customer is hit, until someone notices and undoes it. *(pause)*
6. `S2` So first, you release a canary: about five percent of traffic gets the new version. The name comes from the canary that miners carried, because it showed trouble first.
7. `S3` You compare its error rate with the old version's. If it's no worse, you widen it step by step: twenty-five, fifty, then a hundred percent.
8. `S3b` If it is worse, you roll back. A rollback is a tested, one-step return to the last version. *(pause)*
9. `S3c` And around the event itself, you stop releasing completely. That's a code freeze. *(pause)*
10. `S5` Think of it this way: each tool limits something. The canary limits who sees a bad release.
11. `S5b` The rollback limits how long it lasts: minutes, not hours.
12. `S5c` And the freeze removes the risk while it matters most. *(pause)*
13. `S6` Now a real case. On the Wednesday before a snowy weekend, the tire shop ships a bug fix.
14. `S6b` Without a canary, the fix goes to everyone at once. If it's bad, booking breaks for every customer.
15. `S6c` With a canary, one customer in twenty gets it first. Their error rate jumps from zero point one percent to four percent.
16. `S6d` So you roll back with one click. The proper fix ships Thursday morning, and then the code freezes until Monday. *(pause)*
17. `S7` Here's where it sits: the load balancer sends five percent of requests to the new API copies, and the rest to the old ones. *(pause)*
18. `S8` Two other styles you'll hear. A rolling deploy replaces copies a few at a time, and can cut off work in progress.
19. `S8b` Blue-green runs old and new side by side, and switches all traffic at once. Switching back is just as fast. *(pause)*
20. `S9` In the interview, say: nothing ships during the window.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
