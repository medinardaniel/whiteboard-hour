# Cache with a short TTL: lecture video (component 11)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component eleven: the cache with a short TTL.
2. `SD` A cache is a small, very fast memory, usually Redis, that holds recent answers so you don't have to look them up again. The TTL, or time to live, is how long a copy is kept before it's fetched fresh. *(pause)*
3. `SD2` It's fast. One Redis server handles about a hundred thousand reads a second, each in under a millisecond. *(pause)*
4. `S1` Why do you need it? Game day at a pizza shop. Twenty thousand fans keep refreshing slots left. That's about five hundred requests a second.
5. `S1b` Each one runs the same database query, for the same answer. Five hundred identical queries a second, and checkout slows down too. *(pause)*
6. `S2` So put a cache in between. The first request finds it empty. That's a cache miss. The API reads the database once, and saves the answer with a two-second TTL.
7. `S3` For the next two seconds, every request is a cache hit, answered from Redis in under a millisecond. The database sees none of them.
8. `S4` When the TTL runs out, the copy is gone. The next request misses and refreshes it, and the cycle repeats. *(pause)*
9. `S5` But what if the cache says three left, and they're already gone? That's fine. It's a hint. Checkout asks the database, and the conditional update says sold out. *(pause)*
10. `S6` So what belongs in it? Things read often, where a few seconds old is fine: slots left, the menu, the catalog.
11. `S6b` The checkout decision and payment status always come from the database. *(pause)*
12. `S7` Now the numbers. Without a cache, the database answers five hundred reads a second.
13. `S7b` With a two-second TTL, it's one read every two seconds. That's a thousand times fewer. *(pause)*
14. `S8` Here's where it sits: beside the API. Reads check Redis first.
15. `S8b` Anything that decides, like checkout, goes straight to Postgres. *(pause)*
16. `S9` Two things to know. A stampede: a hot copy expires, and thousands of requests hit the database at once. Let just one of them refresh it.
17. `S9b` And invalidation, deleting copies on every change, is harder than it sounds. A short TTL is simpler. *(pause)*
18. `S10` In the interview, say: cached for two seconds. It's a hint; the database is the truth.

## Pronunciation

| On screen | Spoken |
|---|---|
| TTL | T T L |
| Redis | reddis |
| API | A P I |
