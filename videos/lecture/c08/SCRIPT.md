# Conditional update: lecture video (component 8)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component eight: the conditional update.
2. `SD` A conditional update is a database command that checks a condition and changes a row in one step. For example: subtract one from the stock, but only if at least one is left. *(pause)*
3. `SD2` It's built into every SQL database. Nothing can sneak in between the check and the change. *(pause)*
4. `S1` Why does that matter? One TV is left on sale. Alice and Bob click Buy in the same millisecond.
5. `S1b` The naive code reads first. Both ask the database how many are left, and both hear: one. Each thinks it's theirs.
6. `S1c` Then both write zero. Two orders, two charges, one TV in the warehouse. That's an oversell. *(pause)*
7. `S2` The fix is to put the check inside the write. One update statement: subtract one, where the id matches and at least one is left. *(pause)*
8. `S3` Both send it at the same time. The database changes a row for only one statement at a time, so Bob's waits.
9. `S3b` Alice's runs first. At least one is left, so the row changes. Left is now zero.
10. `S3c` Then Bob's runs and checks the condition again, on the new value. Nothing is left, so zero rows change. *(pause)*
11. `S4` So the row count is your answer. One row means you got it. Zero means sold out. *(pause)*
12. `S5` Use it for anything you can run out of: items in stock, and seats.
13. `S5b` And time slots: add two pizzas only if the slot stays at or under a hundred and fifty. *(pause)*
14. `S6` Now scale it up. An electronics sale: fifty TVs, and three thousand clicks in the first second.
15. `S6b` With read, then write, every pair of clicks that lands in that gap oversells. Say you sell fifty-three, and refund three angry customers.
16. `S6c` With the conditional update, you sell exactly fifty. The other two thousand nine hundred and fifty see sold out. *(pause)*
17. `S7` Here's where it sits: inside the API's checkout code, as one statement sent to Postgres.
18. `S7b` There's no new box to run. The database already does the hard part. *(pause)*
19. `S8` Two things to know. If the logic is too complex for one statement, lock the row with select for update. Others wait their turn.
20. `S8b` And don't move the count into a Redis counter or a distributed lock. Then two places hold the truth. *(pause)*
21. `S9` In the interview, say: one statement, so the database refuses to go below zero.

## Pronunciation

| On screen | Spoken |
|---|---|
| SQL | sequel |
| UPDATE | update |
| SELECT | select |
| MySQL | my sequel |
| TV | T V |
| TVs | T Vs |
