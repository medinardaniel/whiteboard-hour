# Security basics: lecture video (component 23)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component twenty-three: security basics.
2. `SD` Security basics are five habits you can name in one breath. HTTPS everywhere. Secrets in a vault. Let the payment provider handle cards. Least privilege. And keep little personal data. *(pause)*
3. `SD2` In a design interview, that takes about twenty seconds. Then you go back to the design. *(pause)*
4. `S1` Why do they matter? Small shops get hurt by simple mistakes: a password left in the code, card numbers in their own database, or a worker that can read everything.
5. `S1b` One attacker finds one hole, and everything behind it is exposed. *(pause)*
6. `S2` First, HTTPS everywhere. It encrypts traffic between the browser and your servers, so someone on the same cafÃ© Wi-Fi sees only noise.
7. `S3` Second, secrets in a vault. The Stripe key and the database password live in a secrets manager, not in the code. The API fetches them when it starts.
8. `S3b` Third, hosted checkout. Customers type their card on Stripe's page, so card numbers never touch your servers. Stripe just tells you: order forty-two is paid.
9. `S3c` Fourth, least privilege: each part gets only what it needs. The text worker can read the queue, but not the database.
10. `S3d` Fifth, keep little personal data. A name and a phone number are enough. What you never store can't leak. *(pause)*
11. `S5` So in the interview, name these five, quickly and plainly.
12. `S5b` And skip the deep cuts, like cipher suites and key lengths, unless you're asked. *(pause)*
13. `S6` Here's how it plays out. The interviewer asks: what about security?
14. `S6b` The weak answer spends ten minutes on encryption algorithms, and there's no time left for go-live.
15. `S6c` The strong answer names the five, with your design's details, in about twenty seconds.
16. `S6d` Then you move on to go-live, with time to spare. *(pause)*
17. `S7` Here's where it sits: across the whole system. HTTPS at the front, keys from a vault, cards at Stripe, and narrow access for each part. *(pause)*
18. `S8` Two words to keep straight. Authentication is proving who you are, like a login.
19. `S8b` Authorization is what you're allowed to do once you're in. *(pause)*
20. `S9` In the interview, say: HTTPS everywhere, secrets in a vault, no card data on our servers, and each service gets only what it needs.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| HTTPS | H T T P S |
| PCI | P C I |
