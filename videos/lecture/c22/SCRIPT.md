# Dashboards and alerts: lecture video (component 22)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component twenty-two: dashboards and alerts.
2. `SD` Dashboards are live charts of your system's health. Alerts watch those numbers, and automatically page the on-call person when one crosses a line. *(pause)*
3. `SD2` Think of a car dashboard: gauges you glance at, and warning lights that demand attention. *(pause)*
4. `S1` Without them, your customers find out first. Checkout fails, people give up, and the on-call engineer has no idea. *(pause)*
5. `S2` So what do you chart? Start with the four golden signals. Latency, usually as p95: the time that ninety-five percent of requests beat. Traffic. Errors. And saturation: how full a resource is.
6. `S3` Then add business metrics: orders a minute, held versus paid, stock left. They show what customers are actually getting. *(pause)*
7. `S3b` An alert is a rule on one number: above a line, for some time. Say, errors above two percent for two minutes. The duration means a short blip doesn't wake anyone.
8. `S3c` And every alert links to a runbook: a written 'if this fires, do this', with an owner. *(pause)*
9. `S5` Good alerts give you three things. You hear about trouble before customers tell you.
10. `S5b` You know what's wrong, not just that something is.
11. `S5c` And you know what to do, like which switch to flip. *(pause)*
12. `S6` Now game day at the pizza shop. At three forty PM, held orders keep climbing, but paid orders go flat. A held order has a slot reserved, waiting for payment.
13. `S6b` If you only watch errors and latency, both look normal. Customers can't pay, and nobody knows.
14. `S6c` So you alert on the gap: held minus paid above fifty, for three minutes. It pages the on-call engineer.
15. `S6d` The runbook says: check Stripe's status. If it's down, pause orders. *(pause)*
16. `S7` Here's where it sits: every part reports its numbers to one dashboard, and the alerts watch them there. *(pause)*
17. `S8` Two things to know. Too many alerts get ignored, so page only for what needs a person right now.
18. `S8b` And every alert needs an owner and a runbook, or the page wakes someone who can't act. *(pause)*
19. `S9` In the interview, say: if errors pass two percent for two minutes, I turn on the waiting room.

## Pronunciation

| On screen | Spoken |
|---|---|
| p95 | p ninety-five |
| PM | P M |
