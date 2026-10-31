# Stateless API, one service: lecture video (component 3)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component three: the stateless API, one service.
2. `SD` The API is your backend program: it takes a request, like add a pizza to my cart, and answers it. Stateless means you run several identical copies, and no copy remembers a user between requests. Carts and logins live in the database, so any copy can serve any request. *(pause)*
3. `SD2` One service means it's a single program, not dozens of small ones. A managed container service runs the copies for you. *(pause)*
4. `S1` Why does stateless matter? Suppose copy one keeps your cart in its own memory.
5. `S1b` Your next click lands on copy two. Copy two has never seen you, so your cart looks empty.
6. `S1c` And if copy one crashes, the cart is simply gone. *(pause)*
7. `S2` The fix: no copy keeps anything between requests. Copy one gets add pizza, saves the cart to the database, and forgets it.
8. `S2b` Your next click lands on copy three. It reads the cart back from the database, and carries on.
9. `S2c` How does copy three know it's you? Every request carries a session token, a hard-to-guess ID in a cookie. The copy looks it up in the database. *(pause)*
10. `S3` So the copies are interchangeable. Add a fourth, and it's useful on its very first request. *(pause)*
11. `S4` What does that buy you? First, you scale out: add copies when traffic grows.
12. `S4b` Second, a copy can crash, and no user loses anything.
13. `S4c` Third, deploys are easy: you replace copies one at a time. *(pause)*
14. `S5` Now a real case. An hour before kickoff, the pizza shop goes from two copies to eight.
15. `S5b` If carts live in memory, each fan is stuck on the copy holding their cart. Copies one and two overload, while six new copies sit idle.
16. `S5c` With carts in the database, the load balancer spreads every click across all eight copies, from the first minute. *(pause)*
17. `S6` Here's where it sits: behind the load balancer. Every copy talks to the same database and cache.
18. `S6b` So the API is the part you multiply. Anything that must be remembered lives to its right. *(pause)*
19. `S7` Two things to know. The load moves to the database: every request reads state there, so it has to keep up.
20. `S7b` And keep it one service. Microservices, many small programs calling each other, solve big-company problems, not small-team ones. *(pause)*
21. `S8` In the interview, say: one service, run as several identical copies. Stateless, so I scale by adding copies.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| AWS | A W S |
| ECS | E C S |
