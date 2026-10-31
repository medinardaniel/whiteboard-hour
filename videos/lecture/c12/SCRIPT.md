# Rate limits: lecture video (component 12)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component twelve: rate limits.
2. `SD` A rate limit is a cap on how often one person or machine can call you, say ten requests a second. Anything over the cap gets an instant error that says: slow down. *(pause)*
3. `SD2` That error is HTTP status four twenty-nine: too many requests. You rarely build the first layer yourself. Your CDN or firewall offers it as a setting. *(pause)*
4. `S1` Why do you need it? An electronics sale opens. A reseller's script hits checkout three hundred times a second, from one IP address.
5. `S1b` It floods your servers, and buys the TVs before real customers can click.
6. `S1c` And it's not always on purpose. A buggy app that retries in a tight loop can turn one small hiccup into an outage. *(pause)*
7. `S2` The usual way to enforce a limit is a token bucket. Each IP address gets a bucket of ten tokens, refilled at ten a second. Every request spends one.
8. `S3` A normal customer spends a few, and the bucket refills. They never notice.
9. `S4` The script empties its bucket in a blink. Every request after that, with no token left, gets a four twenty-nine, without ever reaching your servers.
10. `S4b` A well-behaved client reads that error, waits, and tries again later. *(pause)*
11. `S5` So it protects you from bots, and from retry storms: the buggy loop gets errors, not your database.
12. `S5b` It also keeps you under other people's limits. Stripe allows about a hundred requests a second, so you cap your own calls. *(pause)*
13. `S6` Back to the sale. With an edge cap of ten a second per IP, two hundred and ninety of the script's three hundred requests are rejected before your servers.
14. `S6b` But the script can switch IP addresses. So the API also caps orders per customer: two per phone number, whatever the IP. *(pause)*
15. `S7` Here's where it sits. The per IP cap runs at the edge, in the CDN and its web application firewall, or WAF.
16. `S7b` The business cap lives in the API, where it knows who the customer is. *(pause)*
17. `S8` Two things to know. An office or a mobile carrier can put many real people behind one IP, so leave room in the cap.
18. `S8b` And per IP alone is easy to dodge, because scripts rotate addresses. The per-customer cap catches that. *(pause)*
19. `S9` In the interview, say: per IP at the edge, and two orders per phone in the API.

## Pronunciation

| On screen | Spoken |
|---|---|
| HTTP | H T T P |
| IP | I P |
| IPs | I Ps |
| API | A P I |
| AWS | A W S |
| WAF | waff |
| CDN | C D N |
| TVs | T Vs |
