# Waiting room: lecture video (component 13)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component thirteen: the waiting room.
2. `SD` A waiting room is a holding page that sits in front of your site. When demand is too high, visitors wait there in line, and they're let into the real site at a fixed rate. *(pause)*
3. `SD2` You don't build it. You switch it on at your CDN, or buy it from a vendor like Queue-it. *(pause)*
4. `S1` Why do you need one? Picture a sale that starts at an exact minute. Thousands of people sit on the page, pressing refresh.
5. `S1b` At the start, they all hit the servers in the same second, and the site falls over for everyone.
6. `S1c` And even if it survives, it isn't fair. Whoever has the fastest connection, or a bot, gets in first. *(pause)*
7. `S2` So instead, every visitor lands on the line page first, and gets a place in line.
8. `S3` Everyone who arrived before the start is shuffled, so being early, or fast, doesn't put you first. *(pause)*
9. `S4` Then the waiting room lets people in at a fixed rate, the rate your site was load tested for. Everyone else watches their place count down.
10. `S4b` Each person let in gets a pass, stored in a cookie, so they can move around the site without queueing again. *(pause)*
11. `S5` When do you use one? First, when demand is far above what you can serve, even after adding servers.
12. `S5b` Second, when a sale starts at an exact minute, and everyone arrives at once. *(pause)*
13. `S6` Now a real case. An electronics shop's sale starts at exactly six AM. Forty thousand people are refreshing, and checkout was tested for three hundred a second.
14. `S6b` Without a waiting room, forty thousand requests land at once, and checkout falls over at six o'clock.
15. `S6c` With one, it lets in three hundred a second, so checkout runs at the load it was tested for. The last person in line gets in a little after six oh two. *(pause)*
16. `S7` It sits at the edge, in front of everything, often as a CDN feature. Visitors with a pass go straight through.
17. `S7b` On a normal day it's off, behind a feature flag: a switch you flip without deploying code. *(pause)*
18. `S8` Two trade-offs. Waiting is a real cost to your customers, so only turn it on when traffic beats the plan.
19. `S8b` And the rate is only as good as your load test. Let in more than you tested, and the site falls over anyway. *(pause)*
20. `S9` In the interview, say: the waiting room is behind a flag, on only if traffic beats the plan.

## Pronunciation

| On screen | Spoken |
|---|---|
| CDN | C D N |
| Queue-it | queue it |
