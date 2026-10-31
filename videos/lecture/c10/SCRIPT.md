# Idempotency key: lecture video (component 10)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component ten: the idempotency key.
2. `SD` An idempotency key is a random ID that the app attaches to each user action. The server saves it with a uniqueness rule. If the same key arrives again, the server returns the first result, instead of doing the work twice. *(pause)*
3. `SD2` Idempotent means doing it twice has the same effect as doing it once. Like a numbered ticket: show it twice, get served once. *(pause)*
4. `S1` Why do you need it? A customer on a train taps Place order. The server creates the order and charges the card.
5. `S1b` But the reply is lost in a tunnel. The phone never hears back.
6. `S1c` So the app retries, which is right: networks fail. But the server can't tell it's a repeat. It creates a second order, and charges again. *(pause)*
7. `S2` Here's the fix. When the customer taps, the app makes a random key, say a7f3, and sends it with every try of that one action.
8. `S3` On the first try, the server saves a7f3 with the result: order one thousand and one. The key column has a unique constraint, a rule that rejects duplicates.
9. `S3b` The reply is lost again. The app retries, with the same key.
10. `S3c` This time the server finds a7f3 already saved. It skips the work and returns the original order. One order, one charge. *(pause)*
11. `S4` One more layer. The server passes the order ID to Stripe as Stripe's own idempotency key. If the charge call repeats, Stripe returns the first charge. *(pause)*
12. `S5` Use it on every action that creates something, or charges money.
13. `S5b` And on the receiving side too. Stripe can deliver the same webhook event twice, so save its event ID and ignore repeats. *(pause)*
14. `S6` How often does this bite? Say a print shop's app takes five thousand orders a day, and two percent lose the reply and retry. That's a hundred double charges a day.
15. `S6b` With idempotency keys, it's zero. The retries still happen. They just do no harm. *(pause)*
16. `S7` Here's where it sits. The app makes the key, and the API checks it against a unique column in Postgres.
17. `S7b` It passes a key on to Stripe, and dedupes Stripe's webhook events on the way back. *(pause)*
18. `S8` Two things to know. One key per action: a retry reuses it, and a new order gets a new one.
19. `S8b` And exactly once isn't possible on a real network. You get at least once, with repeats made harmless. *(pause)*
20. `S9` In the interview, say: a client key with a unique constraint, the same key passed to Stripe, and webhook event IDs deduped.

## Pronunciation

| On screen | Spoken |
|---|---|
| ID | I D |
| IDs | I Ds |
| a7f3 | A seven F three |
| API | A P I |
