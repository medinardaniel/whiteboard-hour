# Load balancer: lecture video (component 2)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component two: the load balancer.
2. `SD` A load balancer is a server that sits in front of your app and spreads incoming requests across several identical copies of it. It also checks that each copy is healthy, and stops sending traffic to any copy that isn't. *(pause)*
3. `SD2` You rarely build one. Every cloud offers it as a managed service. *(pause)*
4. `S1` Why do you need it? Start with a single server. Every request lands on that one machine, and as traffic grows, it slows down.
5. `S1b` Worse, when it crashes, or when you deploy new code, the whole site goes down. *(pause)*
6. `S2` So you run two or more copies. But your users only know one address. The load balancer is that address.
7. `S3` Each request goes to the next copy in turn. That's called round robin. Smarter balancers pick the copy with the fewest open requests. *(pause)*
8. `S4` Every few seconds, it pings each copy at a health endpoint. Two answer. One times out.
9. `S4b` So it stops sending traffic there, and users never notice. When the copy recovers, it rejoins. *(pause)*
10. `S5` You use it in every design, for three reasons. First, capacity: more copies handle more traffic.
11. `S5b` Second, availability: one copy can die, and the site stays up.
12. `S5c` Third, it ends HTTPS, so your copies don't each manage certificates. *(pause)*
13. `S6` Now a real case. A tire shop's booking site, at nine in the morning. One server crashes on a bug.
14. `S6b` Without a load balancer, every customer on that server sees errors until someone restarts it.
15. `S6c` With one, the health check catches it within seconds, and every request goes to the healthy copy. Customers keep booking. *(pause)*
16. `S7` Here's where it sits: right behind the CDN, in front of your API copies. Every request that isn't a static file passes through it.
17. `S7b` Before a spike, you add copies behind it. It can also send a few users to a new release first. *(pause)*
18. `S8` Two things to know. It's the front door, so the managed service runs it across several data centers.
19. `S8b` And your copies must be stateless, or a user's next request may land on a copy that doesn't know them. *(pause)*
20. `S9` In the interview, say: two copies behind a load balancer, so one can die.
