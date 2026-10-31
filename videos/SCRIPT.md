# Component videos: narration script

One video per component. Each cue is one visual step; the voice reads the line while it is on screen.

## 1 · CDN  (~199 words, 13 steps)

1. Component 1: CDN. Servers around the world that keep copies of your site's files (pages, images, scripts) and serve each visitor from one nearby. You'll bring this up during version one, when you draw the basic design.
2. Think of it as: Local warehouses stocking your product, so not every order ships from the factory. Use it for every design, first spike defense, and files that rarely change.
3. Here's a real scenario. A bike shop's site gets shared on a forum: 50,000 visitors in an hour, about 2 megabytes each.
4. Without it: Every page, photo and script comes from the shop's 2 servers.
5. They max out, and pages crawl.
6. With it: First visitor per region: 1 fetch from the shop.
7. Everyone after: served by a nearby CDN server.
8. Shop servers only see cart and checkout.
9. Why it works: The files are the same for everyone, so don't make your servers send them every time.
10. In the interview, say: The CDN takes most of the read spike before it reaches us.
11. A few related terms you may hear.
12. DNS: The internet's phone book: pizza.com to a server address.
13. Low DNS TTL: Set it before launch, so you can redirect traffic fast.

## 2 · Load balancer  (~184 words, 14 steps)

1. Component 2: Load balancer. Sits in front of two or more identical copies of your backend, hands each request to one, and skips any copy that stops answering. You'll bring this up during version one, when you draw the basic design.
2. Think of it as: A traffic cop sending cars to open lanes. Use it for every design, and surviving a crashed copy.
3. Here's a real scenario. A tire shop's booking site runs 2 copies. At 9 AM, one crashes on a bug.
4. Without it: Only one copy: the site is down.
5. Every customer sees errors until someone restarts it.
6. With it: Health check gets no answer within seconds.
7. All traffic goes to the healthy copy.
8. Restarted copy passes the check and rejoins.
9. Why it works: One crash shouldn't take the whole site down.
10. In the interview, say: Two copies behind a load balancer, so one can die.
11. A few related terms you may hear.
12. Health check: The are you alive? ping, every few seconds.
13. HTTPS: Encryption usually ends at the load balancer.
14. Reverse proxy: Same idea: a server in front that forwards requests.

## 3 · Stateless API, one service  (~246 words, 17 steps)

1. Component 3: Stateless API, one service. Each copy of your backend forgets the user between requests. Carts, orders and logins live in the database, so any copy can serve any request. You'll bring this up during version one, when you draw the basic design.
2. Think of it as: Bank tellers: any teller can help you, because your account is in the bank's system, not in one teller's head. Use it for every design, and scaling by adding copies.
3. Here's a real scenario. The pizza shop goes from 2 copies to 8 an hour before kickoff.
4. Without it: The cart lives in copy 1's memory.
5. The customer is stuck on copy 1; new copies sit idle.
6. Copy 1 crashes: the cart is gone.
7. With it: Copy 1 saves the cart to the database.
8. The next click lands on copy 5, which reads it back.
9. All 8 copies are useful immediately.
10. Why it works: Stateless copies are interchangeable, so more copies means more capacity.
11. In the interview, say: One service, run as several identical copies. Stateless, so I scale by adding copies.
12. A few related terms you may hear.
13. Monolith: One program deployed as a unit. Right for a small team.
14. Microservices: Many small programs calling each other. For big orgs.
15. Managed containers: The cloud runs copies of your packaged app (Cloud Run, ECS, Container Apps).
16. Kubernetes: Your own cluster for that. Needs people to run it.
17. Serverless: Code that runs once per event. Fine for small glue.

## 4 · Postgres (managed)  (~245 words, 17 steps)

1. Component 4: Postgres (managed). The standard relational database: tables of rows that many users can change at once without corrupting anything. Your source of truth. You'll bring this up during version one, when you draw the basic design.
2. Think of it as: A shared spreadsheet that enforces its own rules. Use it for orders, payments, stock, and bookings.
3. Here's a real scenario. Two customers click the 9 AM Saturday slot at the tire shop at the same instant.
4. Without it: Booking saved, but the bay never marked taken (crash in between).
5. Both customers get the same bay.
6. With it: One transaction: mark bay taken and save booking, both or neither.
7. Unique rule on (bay, time) rejects the second insert.
8. Second customer is offered the next free slot.
9. Why it works: These facts must never be wrong, and the database guarantees them. A few writes a second is nothing for one database.
10. In the interview, say: Postgres, not Dynamodatabase: my write changes two rows together, and one database is plenty at these numbers.
11. A few related terms you may hear.
12. Transaction: Several changes succeed or fail together .
13. Constraint: A rule the database enforces, like unique (bay, time).
14. Index: A sorted lookup, so a query doesn't read every row. Every frequent query needs one.
15. Managed: The cloud handles backups, patches and recovery.
16. Dynamodatabase: Huge-scale lookups by id; clunky multi-row changes; about 1,000 writes a second per hot item.
17. Sharding: Splitting data across databases. Never in V1.

## 5 · Object storage  (~176 words, 13 steps)

1. Component 5: Object storage. Cloud storage for files, each saved under a name. Cheap and practically unlimited. The database keeps only the file's name. You'll bring this up during version one, when you draw the basic design.
2. Think of it as: Google Drive for your app. Use it for photos, PDFs, videos, and exports.
3. Here's a real scenario. A print-shop customer uploads 10 photos (4 megabytes each) for holiday cards.
4. Without it: 40 megabytes per order passes through the API servers.
5. Thousands of orders clog servers and bloat the database.
6. With it: API hands the browser 10 signed upload links.
7. Browser sends photos straight to storage.
8. Database keeps the names; a worker fetches photos to print.
9. Why it works: Storage is built for big files; your servers and database aren't.
10. In the interview, say: The browser uploads straight to storage with a signed URL, so photos never pass through our servers.
11. A few related terms you may hear.
12. Signed URL: A temporary link to upload or download one file directly.
13. CDN: Serve stored files through it.

## 6 · Queue + workers  (~244 words, 18 steps)

1. Component 6: Queue + workers. A to-do list for slow work. The server writes a note and replies at once; background workers pick up notes and do the work. You'll bring this up during version one, when you draw the basic design.
2. Think of it as: Order tickets on a kitchen rail: the cashier doesn't cook. Use it for emails, texts, image processing, and anything that can lag.
3. Here's a real scenario. Each paid pizza order sends a confirmation text. The SMS provider takes 1 to 2 seconds and sometimes times out.
4. Without it: The customer waits on the text before seeing confirmed.
5. A provider timeout becomes a checkout error.
6. With it: API queues text order 42 and confirms instantly.
7. A worker sends the text, retrying on failure.
8. After 5 failures: dead-letter queue and an alert.
9. 900 orders in 30 minutes: texts lag minutes, none lost.
10. Why it works: Checkout stays fast, and a slow provider can't break ordering.
11. In the interview, say: At-least-once delivery, plus workers that are safe to run twice.
12. A few related terms you may hear.
13. At-least-once: A note may be handed out twice, so jobs must be safe to repeat.
14. Dead-letter queue: Where a note goes after N failures. Alert on it.
15. Queue length: Add workers when the list gets long.
16. Kafka: A replayable event log for many readers. Overkill here.
17. Pub/sub: One message delivered to several listeners.
18. Outbox: Save the message in the same transaction as the order.

## 7 · Sweeper and reconciliation jobs  (~192 words, 13 steps)

1. Component 7: Sweeper and reconciliation jobs. Programs on a timer that clean up. The sweeper releases stuck things. Reconciliation compares your records with an outside source and fixes gaps. You'll bring this up during version one, when you draw the basic design.
2. Think of it as: Closing-time checks: count the till against the receipts. Use it for expired holds, stuck orders, and matching payments.
3. Here's a real scenario. 50 pizza customers reserve, then abandon the Stripe page. One paid order's webhook never arrives.
4. Without it: Abandoned pizzas stay reserved: lost sales.
5. The paid order is never cooked.
6. With it: Every minute, the sweeper finds expired holds.
7. It asks Stripe paid?; if not, the pizzas go back on sale.
8. Nightly: compare Stripe's payments with our orders, fix the missing one.
9. Why it works: Some messages always get lost. These jobs make the system end up correct anyway.
10. In the interview, say: Every minute, release expired holds, after asking Stripe whether they were paid.
11. A few related terms you may hear.
12. Cron: The classic name for run this on a schedule.
13. One runner: Only one copy runs at a time, so sweepers don't fight.

## 8 · Conditional update  (~204 words, 15 steps)

1. Component 8: Conditional update. Check and change in one database command: subtract 1 only if at least 1 is left. The database runs it as a single step. You'll bring this up during version one and the spike, to protect what must never break.
2. Think of it as: Grabbing the last item off a shelf: only one hand can take it. Use it for no oversell, stock, seats, and time slots.
3. Here's a real scenario. 1 TV left on sale. Alice and Bob click Buy in the same millisecond.
4. Without it: Both read left equals 1.
5. Both write left equals 0.
6. 2 TVs sold, 1 in stock.
7. With it: both run this one statement. It subtracts one only where at least one is left.
8. Alice: 1 row changed, left equals 0.
9. Bob: 0 rows changed, sees sold out.
10. Why it works: The database refuses to go below zero, no matter how close the clicks.
11. In the interview, say: One statement, so the database refuses to go below zero.
12. A few related terms you may hear.
13. SELECT ... FOR UPDATE: Lock the row for complex logic; others wait.
14. Redis counter: Avoid: then two places hold the truth.
15. Distributed lock: Avoid: the database already does this.

## 9 · Holds that expire  (~188 words, 13 steps)

1. Component 9: Holds that expire. Reserve the item first, then take payment. Unpaid holds expire. The status only moves forward: held, then paid or expired. You'll bring this up during version one and the spike, to protect what must never break.
2. Think of it as: A store setting an item aside for 10 minutes while you get your wallet. Use it for anything reserved before payment.
3. Here's a real scenario. A customer picks 2 pizzas for the 6:00 slot and clicks checkout.
4. Without it: Charge first, then find the slot is full.
5. Refunds and angry customers.
6. With it: Reserve 2 of the slot's 150: held, expires in 10 minutes.
7. Pays on Stripe: webhook flips it to paid, kitchen gets it.
8. No payment in 10 minutes: sweeper releases the 2.
9. Why it works: You only take money for pizza you can actually make.
10. In the interview, say: Hold, then charge, so we never take money for something we can't deliver.
11. A few related terms you may hear.
12. State machine: The fixed statuses and allowed moves between them.
13. Forward only: A late Stripe message can't turn paid back into held.

## 10 · Idempotency key  (~231 words, 15 steps)

1. Component 10: Idempotency key. A random id for each user action. The server saves it with a uniqueness rule; if it arrives again, it returns the first result instead of repeating. You'll bring this up during version one and the spike, to protect what must never break.
2. Think of it as: A numbered ticket: show it twice, get served once. Use it for no double charge, every create or charge, and every webhook.
3. Here's a real scenario. A customer on a train taps Place order. The order is created, but the reply is lost in a tunnel.
4. Without it: The app retries.
5. The server creates a second order and charges again.
6. With it: The app retries with the same key, a7f3.
7. Server finds a7f3 and returns the original order.
8. Order id also sent to Stripe as its key: one charge.
9. Why it works: Retries are unavoidable on real networks. Without the key, each one is a possible double charge.
10. In the interview, say: A client key with a unique constraint, the same key passed to Stripe, and webhook event ids deduped.
11. A few related terms you may hear.
12. Idempotent: Doing it twice has the same effect as doing it once.
13. Unique constraint: The rule that rejects duplicates. Also stops double booking.
14. Webhook dedupe: Save Stripe's event id and ignore repeats.
15. Exactly once: Not achievable. You get at least once, repeats harmless.

## 11 · Cache with a short TTL  (~212 words, 15 steps)

1. Component 11: Cache with a short TTL. A small, very fast memory (Redis) holding recent answers. The TTL is how long a copy lives before it's fetched again. You'll bring this up during the spike defenses.
2. Think of it as: A sticky note with today's specials, rewritten every 2 seconds. Use it for slots left, menu, and catalog.
3. Here's a real scenario. Game day: 20,000 people refresh slots left, about 500 requests a second.
4. Without it: 500 identical database queries every second.
5. With it: First request every 2 seconds reads the database and saves to Redis.
6. Everyone else gets the Redis copy in under 1 milliseconds.
7. Database load: 1 query per 2 seconds.
8. Stale 3 left? Checkout's conditional update says sold out.
9. Why it works: 2-second-old numbers are fine for browsing; the sale is still decided by the database.
10. In the interview, say: Cached for 2 seconds. It's a hint; the database is the truth.
11. A few related terms you may hear.
12. TTL: Time to live: how long a cached copy is kept.
13. Invalidation: Deleting copies on every change. Harder than a short TTL.
14. Stampede: A hot copy expires and thousands hit the database. Let one refresh.
15. Hot key: One item everyone reads. Also keep a 1 second copy in each server.

## 12 · Rate limits  (~202 words, 14 steps)

1. Component 12: Rate limits. A cap on how often one person or machine can call you. Extra requests get an instant slow down error. You'll bring this up during the spike defenses.
2. Think of it as: A bouncer letting each person through once a minute. Use it for bots, retry storms, and provider limits.
3. Here's a real scenario. A reseller's script hits checkout 300 times a second from one IP. A buggy app retries in a tight loop.
4. Without it: The script floods servers and buys the stock.
5. The retry loop turns a hiccup into an outage.
6. With it: Edge cap of 10 a second per IP: 290 rejected before the servers.
7. Business cap: 1 per customer per item, across IPs.
8. The retry loop gets slow down errors, not the database.
9. Why it works: It protects real customers fair share, and the servers.
10. In the interview, say: Per IP at the edge, and 2 orders per phone in the API.
11. A few related terms you may hear.
12. 429: The too many requests error code.
13. WAF: Web application firewall: blocks known attacks and bots.
14. DDoS protection: Absorbs floods of junk traffic. WAF and DDoS come with the CDN: mention them, don't design them.

## 13 · Waiting room  (~176 words, 13 steps)

1. Component 13: Waiting room. A you're in line page. Visitors wait there and are let into the real site at a fixed rate. You buy it from a vendor. You'll bring this up during the spike defenses.
2. Think of it as: A rope line outside a busy store. Use it for demand far above capacity, and A sale that starts at an exact minute.
3. Here's a real scenario. A sale starts at exactly 6:00 AM. 40,000 people are refreshing; checkout was tested for 300 a second.
4. Without it: 40,000 requests at once; the site falls over.
5. The fastest connection wins.
6. With it: Everyone lands on the line page.
7. Everyone who arrived before 6:00 is shuffled.
8. Let in 300 a second; each sees their place.
9. Why it works: The site runs at a load it was tested for, and the order is fair.
10. In the interview, say: Behind a flag. On only if traffic beats the plan.
11. A few related terms you may hear.
12. Fairness: Shuffle everyone who arrived before the start.
13. Vendors: Cloudflare Waiting Room, Queue-it.

## 14 · Replicas and failover  (~230 words, 17 steps)

1. Component 14: Replicas and failover. The primary database takes all writes. Replicas are live, read-only copies a fraction of a second behind. A standby takes over if the primary dies. You'll bring this up during the spike defenses.
2. Think of it as: A co-pilot ready to take the controls. Use it for more read capacity, and surviving a database crash.
3. Here's a real scenario. Heavy sales reports slow down checkout. Later, at 2 AM, the primary's machine fails.
4. Without it: Reports compete with checkout for the one database.
5. A hardware failure means hours of downtime.
6. With it: Reports read from a replica; checkout stays fast.
7. The cloud promotes the standby in 30 to 60 seconds.
8. Writes in that minute fail, and the app retries them.
9. Why it works: Replicas take read load off the one writer, and the standby turns a failure into a one-minute blip.
10. In the interview, say: Never read stock you're about to sell from a replica. It can be a moment behind.
11. A few related terms you may hear.
12. Failover: Promoting the standby when the primary dies.
13. Multi-AZ: Standby in another data center, same region. Always do it.
14. Multi-region: A full copy far away. Only if an hour down is unacceptable.
15. Point-in-time restore: Rewind to any minute, to undo a bad delete.
16. RPO: How much recent data you could lose.
17. RTO: How long you'd be down.

## 15 · Connection pooler  (~171 words, 13 steps)

1. Component 15: Connection pooler. Postgres handles only a few hundred connections. A pooler shares a small set of real connections among all your server copies. You'll bring this up during the spike defenses.
2. Think of it as: A few phone lines shared by a whole office. Use it for as soon as you add copies.
3. Here's a real scenario. Before the game, the pizza shop scales from 2 to 20 copies, 20 connections each.
4. Without it: 400 connections against a limit of 200.
5. Copies 11 to 20 can't connect and fail at kickoff.
6. With it: All 20 copies connect to the pooler.
7. The pooler keeps 50 real connections.
8. It lends one out for the milliseconds a query takes.
9. Why it works: Scaling out the API multiplies connections unless something shares them.
10. In the interview, say: Postgres allows a few hundred connections. Without a pooler, scaling the API takes down the database.
11. A few related terms you may hear.
12. PgBouncer: The classic pooler.
13. Short transactions: Never wait on Stripe while holding one.

## 16 · Pre-scaling  (~168 words, 13 steps)

1. Component 16: Pre-scaling. Add server copies and upgrade the database before a spike you know is coming. You'll bring this up during the spike defenses.
2. Think of it as: Calling in extra staff before the lunch rush, not during it. Use it for any planned event.
3. Here's a real scenario. The snow forecast airs on the 6 PM news. Tire-shop traffic will jump 20 times in 2 minutes.
4. Without it: Autoscaling notices the busy servers at 6:06.
5. New copies are ready at 6:09.
6. 4 minutes of errors at the worst moment.
7. With it: 5 PM: 2 to 6 copies, bigger database, CDN warmed.
8. 6:05: the spike arrives; the system is already sized.
9. Why it works: You know when the spike is coming, so use that.
10. In the interview, say: Autoscaling reacts in minutes. The spike arrives in seconds.
11. A few related terms you may hear.
12. Autoscaling: The cloud adds copies when servers get busy. Keep it as a safety net.
13. Workers: Scale them on queue length, not CPU.

## 17 · Hosted checkout + webhooks  (~229 words, 18 steps)

1. Component 17: Hosted checkout + webhooks. Customers pay on the payment provider's page. The provider then calls your server (a webhook) to say the payment worked. You'll bring this up during version one, wherever you call an outside service.
2. Think of it as: Letting the bank's own teller handle the cash. Use it for every payment.
3. Here's a real scenario. Order 42 (24 dollars) at the pizza shop.
4. Without it: Your own card form puts card numbers on your servers.
5. Heavy security audits (PCI).
6. With it: Create a Stripe Checkout session; the customer pays there.
7. Stripe calls /webhooks/stripe: order 42 paid.
8. Check signature, save event id, mark paid, reply OK fast.
9. Same event again later? Known id: ignore it.
10. Why it works: You never touch card numbers, and the webhook tells you about a payment on someone else's page.
11. In the interview, say: Card data never touches our servers, which shrinks our PCI scope.
12. A few related terms you may hear.
13. Webhook: The provider calling your URL when something happens.
14. Webhook rules: Check the signature (proof it's Stripe), reply OK fast, do the work later, ignore repeats, expect some late.
15. PCI: Security rules for handling card data.
16. Test mode: Fake payments, for load tests.
17. Rate limit: About 100 requests a second by default. Ask for more before launch.
18. SMS, email: Same pattern: call from a worker, respect the limits.

## 18 · Timeouts, retries, circuit breaker  (~220 words, 15 steps)

1. Component 18: Timeouts, retries, circuit breaker. Three rules for any outside call: give up after N seconds, retry with growing waits, and stop calling for a while after repeated failures. You'll bring this up during version one, wherever you call an outside service.
2. Think of it as: Hang up on hold music, call back later, and stop dialing if the line is clearly dead. Use it for stripe, SMS, and any outside service.
3. Here's a real scenario. Game day: Stripe calls slow down from 300 milliseconds to 8 seconds.
4. Without it: Each checkout ties up a server for 8 seconds.
5. Every server waits on Stripe; even the menu stops loading.
6. With it: 2 seconds timeout: fail fast, retry once with the same key.
7. 5 failures in a row: the circuit opens for 30 seconds.
8. Checkout says try again in a minute; the rest stays fast.
9. Why it works: One slow outside service shouldn't take down everything else.
10. In the interview, say: Retries are safe only because the call carries an idempotency key.
11. A few related terms you may hear.
12. Backoff: Wait longer each retry: 100, 200, 400 milliseconds.
13. Jitter: Random extra wait, so clients don't retry in sync.
14. Circuit breaker: Closed, then open (fail fast), then half-open (test one call).
15. Bulkhead: Separate connection pools per service, like a ship's compartments.

## 19 · Flags and kill switches  (~175 words, 15 steps)

1. Component 19: Flags and kill switches. Settings you flip while the site runs, with no code release. A kill switch is a flag for emergencies. You'll bring this up during go-live prep.
2. Think of it as: Light switches you install before the party. Use it for pause orders, waiting room on, hide photos, and close a slot.
3. Here's a real scenario. 4:10 PM on game day: payment errors spike.
4. Without it: Write code, review, release, mid-incident.
5. 20+ minutes of failed checkouts.
6. With it: Flip pause new orders.
7. Seconds later the button says paused for a few minutes.
8. Paid orders keep flowing; flip back at 4:25.
9. Database busy later? Flip hide photos.
10. Why it works: A switch takes seconds, and each one was tested the day before.
11. In the interview, say: Every switch is tested on game day.
12. A few related terms you may hear.
13. Feature flag: Turns a feature on or off at runtime.
14. Graceful degradation: Turn off extras so the core keeps working.
15. Load shedding: Reject some requests instantly so the rest stay fast.

## 20 · Load test and game day  (~201 words, 16 steps)

1. Component 20: Load test and game day. A load test fires fake traffic at 2 to 3 times the peak at a test copy, with a pass bar. A game day rehearses: flip switches, fake outages. You'll bring this up during go-live prep.
2. Think of it as: A dress rehearsal before opening night. Use it for before every launch.
3. Here's a real scenario. Two days before a doorbuster sale.
4. Without it: A missing index is found at 6 AM on sale day.
5. On-call has never practiced pausing orders.
6. With it: k6 simulates 120,000 visitors, 1,000 buying one TV.
7. Pass bar: 50 sold per deal, 0 double charges, p ninety-five under 800 milliseconds.
8. Run 1 fails (missing index); fix, rerun, pass.
9. Game day: flip every switch, fake Stripe errors, time the response.
10. Why it works: You find the missing index on Tuesday, not at 6 AM on Friday.
11. In the interview, say: Pass means 0 oversold, 0 double charges, and p ninety-five under 500 milliseconds.
12. A few related terms you may hear.
13. Staging: The test copy of your system.
14. k6, Locust: Load-testing tools.
15. Chaos testing: Breaking parts on purpose. Game day is the small version.
16. Capacity planning: Your Clarify math, written down.

## 21 · Safe deploys  (~201 words, 16 steps)

1. Component 21: Safe deploys. Release new code to a few users first, keep a tested way back, and stop releasing around the event. You'll bring this up during go-live prep.
2. Think of it as: Taste the soup before serving the whole room. Use it for any release near the event.
3. Here's a real scenario. Wednesday before the snowy weekend: the tire shop ships a bug fix.
4. Without it: The fix goes to 100% at once.
5. A bad release breaks booking for everyone.
6. With it: Canary: 5% of traffic gets the new version.
7. Errors on that 5% jump from 0.1% to 4%: one-click rollback.
8. Proper fix Thursday morning, then freeze until Monday.
9. Why it works: Most outages come from changes. A canary limits who, a rollback limits how long, a freeze removes the risk.
10. In the interview, say: Nothing ships during the window.
11. A few related terms you may hear.
12. Canary: New version to 1 to 5% of users first.
13. Rollback: A tested, one-step return to the last version.
14. Code freeze: No releases around the event.
15. Rolling deploy: Replace copies a few at a time; can kill work in progress.
16. Blue-green: Old and new side by side; switch all traffic at once.

## 22 · Dashboards and alerts  (~208 words, 17 steps)

1. Component 22: Dashboards and alerts. Live charts of the system's health, plus automatic pages to the on-call person when a number crosses a line. You'll bring this up during go-live prep.
2. Think of it as: A car dashboard, with warning lights. Use it for launch day, and every day after.
3. Here's a real scenario. Game day, 3:40 PM: held orders climb, but paid goes flat.
4. Without it: Only errors and latency watched: both look normal.
5. Customers can't pay, and nobody knows.
6. With it: Alert: held minus paid above 50 for 3 minutes.
7. It pages the on-call engineer.
8. Runbook: check Stripe's status; if it's down, pause orders.
9. Why it works: The right number tells on-call what's wrong, not just that something is.
10. In the interview, say: If errors pass 2% for 2 minutes, I turn on the waiting room.
11. A few related terms you may hear.
12. Golden signals: Latency, traffic, errors, saturation (how full).
13. Business metrics: Orders a minute, held versus paid, stock left.
14. p ninety-five: 95% of requests are faster than this. Shows the slow tail.
15. Runbook: A written if this fires, do this, with an owner.
16. Logs, traces: Event records, and one request followed step by step.
17. SLO: The target, like 99.9% of checkouts under 1 second.

## 23 · Security basics  (~175 words, 16 steps)

1. Component 23: Security basics. Five things in one breath: HTTPS, secrets in a vault, the provider handles cards, least privilege, little personal data. You'll bring this up during go-live prep.
2. Think of it as: Lock the doors, keep the keys in a safe, let the bank hold the cash. Use it for when asked.
3. Here's a real scenario. The interviewer asks: What about security?.
4. Weak answer: 10 minutes on encryption algorithms.
5. No time left for go-live.
6. Strong answer: HTTPS everywhere.
7. Stripe key and database password in a secrets manager.
8. No card numbers, thanks to hosted checkout.
9. Text worker can read the queue, not the database.
10. Store only a name and phone number.
11. Why it works: It shows you know the basics, in 20 seconds.
12. In the interview, say: HTTPS everywhere, secrets in a vault, no card data on our servers, and each service gets only what it needs.
13. A few related terms you may hear.
14. Authentication: Proving who you are.
15. Authorization: What you're allowed to do.
16. Least privilege: Each part gets only what it needs.

## Pronunciation

| On screen | Spoken |
|---|---|
| CDN | C D N |
| DNS | D N S |
| API | A P I |
| APIs | A P Is |
| SQL | sequel |
| HTTPS | H T T P S |
| WAF | waff |
| DDoS | D dos |
| PCI | P C I |
| RPO | R P O |
| RTO | R T O |
| SLO | S L O |
| TTL | T T L |
| k6 | K six |
| PgBouncer | P G bouncer |
| Redis | reddis |
| ECS | E C S |
| Multi-AZ | multi A Z |
| ACID | acid |
| 429 | four twenty-nine |
| SMS | S M S |
| a7f3 | A 7 F 3 |
| Pub/sub | pub sub |
| OK | okay |
| TVs | T Vs |
| TV | T V |
| IP | I P |
| IPs | I Ps |
| CPU | C P U |
| PDFs | P D Fs |
| URL | U R L |
| AM | A M |
| PM | P M |
| SELECT | select |
| UPDATE | update |
| FOR | for |
| id | I D |
| ids | I Ds |
| DynamoDB | Dynamo D B |
| Kubernetes | kubernetes |
| Cloud Run | Cloud Run |
| Locust | locust |
| Queue-it | queue it |
