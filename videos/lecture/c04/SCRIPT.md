# Postgres (managed): lecture video (component 4)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component four: Postgres, the managed relational database.
2. `SD` Postgres is the standard relational database. It stores your data as tables of rows, and lets many users change them at the same time without corrupting anything. It's your source of truth. *(pause)*
3. `SD2` And managed means you rent it. The cloud handles backups, patches and recovery for you. *(pause)*
4. `S1` Why do you need its guarantees? Booking a tire bay takes two writes: save the booking, and mark the bay as taken.
5. `S1b` If the server crashes between them, the booking exists, but the bay still looks free.
6. `S1c` And if two customers click the same slot at the same instant, both can get it. *(pause)*
7. `S2` Postgres fixes the first problem with a transaction: a group of changes that succeed or fail as a unit. When it commits, both are kept.
8. `S2b` If anything fails halfway, the database rolls back, as if nothing had happened. *(pause)*
9. `S3` It fixes the second with a constraint: a rule the database itself enforces. Here, every email must be unique.
10. `S3b` Two sign-ups with the same email arrive together. The first insert wins. The second breaks the rule, so Postgres rejects it. *(pause)*
11. `S4` So what goes in it? The facts that must never be wrong: orders, payments, stock counts, bookings, accounts.
12. `S4b` Photos, slow work and hot reads belong elsewhere. *(pause)*
13. `S5` Now the real case. Saturday, nine in the morning: the tire shop has one bay left, and two customers click it at the same instant.
14. `S5b` Customer A's transaction commits. The booking is saved and the bay is marked taken, together.
15. `S5c` Customer B's insert breaks the unique rule on bay and time. It rolls back, and B is offered the next free slot, nine thirty. *(pause)*
16. `S5d` And the load? Even at peak, the shop makes a few writes a second. One Postgres handles thousands. One database is plenty. *(pause)*
17. `S6` Here's where it sits: behind the API. Every API copy, and every background job, uses this one database. *(pause)*
18. `S7` Two things to know. Why not DynamoDB? It's built for huge-scale lookups by ID, but changing two rows together is clunky.
19. `S7b` And every frequent query needs an index: a sorted lookup, so the query doesn't read every row. *(pause)*
20. `S8` In the interview, say: Postgres, not DynamoDB. My write changes two rows together, and one database is plenty at these numbers.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| DynamoDB | Dynamo D B |
| ID | I D |
