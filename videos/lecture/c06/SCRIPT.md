# Queue + workers: lecture video (component 6)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component six: the queue and workers.
2. `SD` A queue is a to-do list for slow work. Your server writes a note, called a message, and replies to the user at once. Background programs called workers pick up the messages and do the work. *(pause)*
3. `SD2` Think of order tickets on a kitchen rail: the cashier doesn't cook. *(pause)*
4. `S1` Why do you need it? After each paid pizza order, the shop sends a confirmation text. The text provider takes one to two seconds, and the customer waits.
5. `S1b` Worse, when the provider times out, a paid order shows a checkout error. *(pause)*
6. `S2` With a queue, the API writes one message, text order forty-two, and confirms the order instantly.
7. `S2b` A worker takes the message and sends the text. If the provider fails, the message goes back on the queue, and is retried later. *(pause)*
8. `S3` Here's the catch. Delivery is at least once: if a worker is slow to confirm it finished, the queue can hand the same message to another worker.
9. `S3b` So jobs must be idempotent: running one twice has the same effect as once. Worker two sees the text was already sent, and skips it. *(pause)*
10. `S4` And a message that fails five times goes to a dead-letter queue, a side list for messages that keep failing. You alert on it. *(pause)*
11. `S5` So what goes on a queue? Anything that can lag a little. Emails and texts,
12. `S5b` image processing, like resizing uploaded photos,
13. `S5c` and reports or exports, which nobody needs in the same second. *(pause)*
14. `S6` Now a real case. At kickoff, nine hundred orders arrive in thirty minutes. Each one queues a text, and the list grows.
15. `S6b` The workers drain it at their own pace. Texts lag a few minutes, but checkout stays instant, and no text is lost.
16. `S6c` If the queue keeps growing, add workers. Queue length is the signal to watch. *(pause)*
17. `S7` Here's where it sits: the API writes to the queue, and workers call slow outside services, like text providers. *(pause)*
18. `S8` Two things to know. Save the message in the same transaction as the order, a pattern called the outbox. Otherwise a crash between the two can lose it.
19. `S8b` And you don't need Kafka, a replayable log for many readers. A simple queue is enough here. *(pause)*
20. `S9` In the interview, say: at-least-once delivery, plus workers that are safe to run twice.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| SQS | S Q S |
