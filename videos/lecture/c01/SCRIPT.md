# CDN: lecture video (component 1)

Target: under 3 minutes. Each section is one animated scene; *(italics)* says what moves on screen.

## 0 · Title
*(Title card: "CDN, content delivery network".)*
This is the **CDN**, the content delivery network. It's usually the first box you draw after the browser, and it's the **CHEAPEST** way to survive a traffic spike.

## 1 · The problem
*(World map. One origin server in Virginia. Requests stream out to users on every continent; the server's load bar climbs into the red.)*
Start with the problem. Your site runs on two servers in Virginia. A visitor in Sydney opens the homepage, about two megabytes of pages, scripts and photos, and every file crosses the Pacific and back. Now picture fifty thousand visitors, and your two servers sending the **SAME** files to every one.

## 2 · Edge servers
*(Edge servers pop up next to each group of users.)*
A CDN puts copies of your files **CLOSE** to your users. It's a network of edge servers in hundreds of cities. Your own servers become the **ORIGIN**, the source those copies come from.

## 3 · Cache miss
*(Sydney: user asks the edge, edge flashes MISS, fetches from Virginia once, keeps a copy, returns it.)*
The first visitor in Sydney asks the nearby edge for a photo. It doesn't have it yet. That's a **cache miss**. So the edge fetches it from the origin once, keeps a copy, and passes it on.

## 4 · Cache hits
*(Short green hops at every edge; the hit counter climbs; the origin's load bar drops to green.)*
Everyone after that is a **cache hit**: served from a few miles away in about twenty milliseconds, and your origin never sees the request.

## 5 · TTL and purge
*(A countdown ring drains around Sydney's cached copy; at zero the edge re-checks with the origin and the ring refills.)*
Each copy has a time to live, or **TTL**. When it runs out, the edge checks with the origin again. Long TTL, fewer origin trips. Short TTL, fresher content. Need it gone right now? **Purge** it.

## 6 · What goes on a CDN
*(File chips sort themselves into two bins: "cache at the edge" and "pass through to your servers".)*
So what goes on a CDN? Anything that's the **SAME** for every visitor: pages, scripts, images, video, and slow-changing public data like a menu, cached for thirty seconds. Anything **PERSONAL** or that writes, like the cart or checkout, passes straight through.

## 7 · The scenario
*(Counters: 50,000 visitors × 2 MB = 100 GB.)*
Now a real case. A bike shop gets shared on a forum: fifty thousand visitors in an hour, two megabytes each. That's a hundred gigabytes.

## 8 · With and without
*(Two bar charts grow: without a CDN, one red bar maxes out; with a CDN, 95 GB green from the edges and 5 GB from the origin.)*
Without a CDN, all hundred gigabytes come from two servers, and the site crawls for everyone, buyers included. With a CDN at a ninety-five percent hit rate, the edges send ninety-five gigabytes, and the origin just **FIVE**: only the cart and checkout.

## 9 · Where it fits
*(Full schematic: Browser, DNS, CDN, load balancer, API, database. A photo request bounces back at the CDN; an order request travels all the way to the database and back.)*
Here's where it fits. DNS points the browser at the CDN. Static files are answered right at the edge. An order passes through to the load balancer, the API servers and the database. That's why it's spike defense **NUMBER ONE**: nearly free, and it removes most traffic before anything you have to scale.

## 10 · Trade-offs
*(Three cards appear in turn.)*
Two trade-offs to name. Visitors can see content up to one TTL old. And never cache personal pages, or the next visitor could see someone else's cart. One tip: lower your DNS TTL before a launch, so you can redirect traffic fast.

## 11 · The line to say
*(Speech bubble.)*
In the interview, say it in one line: the CDN takes most of the read spike before it reaches us.

## Pronunciation
| On screen | Spoken |
|---|---|
| CDN | C D N |
| TTL | T T L |
| DNS | D N S |
| API | A P I |
| GB / MB | gigabytes / megabytes |
| ms | milliseconds |
