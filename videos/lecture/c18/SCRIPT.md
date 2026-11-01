# Timeouts, retries, circuit breaker: lecture video (component 18)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component eighteen: timeouts, retries, and the circuit breaker.
2. `SD` Three rules for any call to an outside service, like Stripe: give up after a few seconds, retry with growing waits, and stop calling for a while after repeated failures. *(pause)*
3. `SD2` It's a pattern, not a product: a few settings in your HTTP client. *(pause)*
4. `S1` Why does it matter? On game day, Stripe slows from three hundred milliseconds to eight seconds, and each checkout holds a thread while it waits.
5. `S1b` Soon every thread is waiting, and even the menu stops loading. *(pause)*
6. `S2` Rule one, the timeout: the longest you'll wait. Say two seconds, then give up and free the thread. *(pause)*
7. `S3` Rule two: retry, waiting longer each time. That's backoff: a hundred milliseconds, then two hundred, then four hundred.
8. `S3b` Add a small random wait, called jitter, so clients don't retry in sync. And reuse the same idempotency key, so Stripe charges once. *(pause)*
9. `S4` Rule three, the circuit breaker. It starts closed: calls flow through. After five failures in a row, it opens.
10. `S4b` While it's open, calls fail instantly for thirty seconds. Checkout says: try again in a minute.
11. `S4c` Then it goes half-open: one test call. If it works, it closes. If not, it opens again. *(pause)*
12. `S5` Wrap every call that leaves your system: payments to Stripe,
13. `S5b` texts and email, retried by a worker so the order never waits,
14. `S5c` and anything else outside your system, like shipping rates or maps. *(pause)*
15. `S6` Now the pizza shop on game day, with Stripe at eight seconds.
16. `S6b` Without the rules, each checkout holds a thread for eight seconds. The threads fill up, and the site stalls.
17. `S6c` With them, each call gives up at two seconds and retries once. Five failures in a row, and the circuit opens for thirty seconds.
18. `S6d` Checkout says try again in a minute. The threads stay free, and the menu stays fast. *(pause)*
19. `S7` It sits inside the API, around every call to Stripe.
20. `S7b` And in the workers, around every text they send. *(pause)*
21. `S8` Two things to watch. Retries add load, so retry only a few times, with backoff.
22. `S8b` And only retry what's safe: a payment retried without the same key can be charged twice. *(pause)*
23. `S9` In the interview, say: retries are safe only because the call carries an idempotency key.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| HTTP | H T T P |
| SMS | S M S |
