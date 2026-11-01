# Connection pooler: lecture video (component 15)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component fifteen: the connection pooler.
2. `SD` A connection pooler is a small server that sits between your app and Postgres. It keeps a few real database connections open, and shares them among all your server copies. *(pause)*
3. `SD2` The classic one is PgBouncer. Clouds offer managed ones too, like Amazon RDS Proxy. *(pause)*
4. `S1` First, what's a connection? It's an open line from your app to the database. Postgres runs a separate process for each one, so it can only afford a few hundred. The default limit is one hundred.
5. `S1b` Each server copy keeps its own set open, say twenty, so it doesn't have to open a new one for every request. Add copies, and the count multiplies.
6. `S1c` Past the limit, Postgres refuses new connections. Copy six can't connect, and its requests fail. *(pause)*
7. `S2` The pooler fixes this. Every copy connects to the pooler instead, and those connections are cheap.
8. `S3` Behind it, the pooler keeps a small set of real connections to Postgres.
9. `S3b` When a copy runs a transaction, the pooler lends it a real connection, for just the milliseconds it takes, then puts it back. *(pause)*
10. `S3c` Why are a few enough? If a query takes five milliseconds, one connection can run two hundred a second. Fifty connections: ten thousand a second. *(pause)*
11. `S5` So you need one as soon as you add copies of your API.
12. `S5b` And whenever many short-lived workers or functions each want their own connection. *(pause)*
13. `S6` Now a real case. Before the game, the pizza shop scales from two copies to twenty, with twenty connections each. That's four hundred connections.
14. `S6b` Their database allows two hundred. Copies one to ten connect. Copies eleven to twenty can't, and fail right at kickoff. *(pause)*
15. `S6c` With a pooler, all twenty copies connect to it, and it keeps fifty real connections. The database stays well under its limit. *(pause)*
16. `S7` Here's where it sits: between your API copies and Postgres. Every query goes through it. *(pause)*
17. `S8` Two things to know. Keep transactions short. Never wait on Stripe while holding a connection, or the pool runs dry.
18. `S8b` And each transaction may get a different real connection, so don't rely on settings that live in one session. *(pause)*
19. `S9` In the interview, say: Postgres allows a few hundred connections. Without a pooler, scaling the API takes down the database.

## Pronunciation

| On screen | Spoken |
|---|---|
| PgBouncer | P G bouncer |
| RDS | R D S |
| API | A P I |
| 5 ms | five milliseconds |
