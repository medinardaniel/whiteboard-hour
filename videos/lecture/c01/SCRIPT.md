# CDN: lecture video (component 1)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component one: the CDN.
2. `SD` A CDN, or content delivery network, is a network of servers spread across hundreds of cities. Each one keeps copies of your website's files, and serves every visitor from the closest one. *(pause)*
3. `SD2` You don't build it. You rent it, from a provider like Cloudflare, Akamai or Amazon CloudFront. *(pause)*
4. `S1` Why does it matter? Picture your site on two servers in Virginia. A visitor in Sydney loads your homepage, and every file crosses the Pacific and back.
5. `title` Multiply that by fifty thousand visitors, all pulling the same files from two servers. *(pause)*
6. `S2` With a CDN, copies sit on edge servers near your users. Your servers become the origin, the source of the copies. *(pause)*
7. `S3` The first visitor in Sydney asks the nearby edge for a photo. The edge doesn't have it yet. That's a cache miss.
8. `S3b` So it fetches the photo from the origin once, keeps a copy, and passes it on. *(pause)*
9. `S4` Everyone after that is a cache hit, served nearby in about twenty milliseconds. The origin never sees them. *(pause)*
10. `S5` Each copy has a time to live, or TTL. When it runs out, the edge checks with the origin for a fresh copy.
11. `S5b` Need a change out right now? You purge the copy. *(pause)*
12. `S6` So what belongs on a CDN? Anything that's the same for every visitor: pages, scripts, images, video, even a menu cached for thirty seconds.
13. `S6b` Anything personal or that writes, like the cart or checkout, passes straight through. *(pause)*
14. `S7` Now a real case. A bike shop gets shared on a forum: fifty thousand visitors in an hour, two megabytes each. That's a hundred gigabytes. *(pause)*
15. `S8` Without a CDN, all of it comes from two servers, and the site crawls for everyone, buyers included.
16. `S8b` With a CDN at a ninety-five percent hit rate, the edges send ninety-five gigabytes. The origin sends just five. *(pause)*
17. `S9` Here's where it sits. DNS points the browser at the CDN, and static files are answered at the edge.
18. `S9b` An order passes through to the load balancer, the API and the database.
19. `title` That's why it's spike defense number one: nearly free, and it removes most traffic first. *(pause)*
20. `S10` Two trade-offs to name. Visitors can see content up to one TTL old.
21. `S10b` And never cache personal pages, or the next visitor could see someone else's cart. *(pause)*
22. `S11` In the interview, say it in one line: the CDN takes most of the read spike before it reaches us.

## Pronunciation

| On screen | Spoken |
|---|---|
| CDN | C D N |
| TTL | T T L |
| DNS | D N S |
| API | A P I |
