# Sample questions

**TLDR.** Read the one-line prompt, set a 60-minute timer, and answer out loud. Then tap "See answer" and compare. Every answer follows the six phases. The interviewer's replies in Clarify are made up: in a real interview, ask and use whatever numbers you get.

**Questions**

1. [Pizza shop, game day](#q-pizza) (limited inventory)
2. [Weekend step challenge](#q-steps) (write-heavy counter)
3. [Holiday photo cards](#q-cards) (job burst)
4. [Tire shop, first snow](#q-tires) (reservations)
5. [Youth soccer storm alert](#q-soccer) (notification fan-out)
6. [Electronics shop doorbusters](#q-doorbusters) (inventory drop with carts)
7. [City marathon live tracking](#q-marathon) (event ingest plus read spike)
8. [Travel blog goes viral](#q-blog) (read spike, happening now)
9. [Hat drop, one famous post](#q-hats) (limited stock, spike at an unknown minute)

Then the [Follow-up drills](#drills): 20 questions interviewers ask after the design.

---

## 1. Pizza shop, game day {#q-pizza}

> You run a small pizza shop and want to take online orders for the big game on Sunday.

::: mock pizza-mock | Watch the full mock (11 min)
- 0:00 Intro
- 0:17 Clarify
- 2:38 Version 1
- 4:37 Decisions
- 5:52 Spike
- 8:26 Go-live
- 10:18 Wrap-up
- 11:07 Debrief
:::

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Who orders, and how? *Web and phone browsers. Pickup only, paid online.*
- Normal Sunday vs this Sunday? *Normal is about 200 orders. A radio host is promoting half-price pizza at kickoff, 3:30. Expect 20,000 people on the site in the half hour before.*
- What is the real limit? *Four ovens, about 600 pizzas an hour.*
- What must never fail, and what can degrade? *Never take money for a pizza we can't make. Never charge twice. Photos and confirmation texts can be slow.*
- Team, time, payments? *Two engineers, two weeks. The shop already uses Stripe for its card reader.*

**Numbers**

- Spike: 100x normal, in 30 minutes.
- Supply: 15-minute pickup slots of 150 pizzas. Kickoff to 6:30 is 1,800 pizzas, about 900 orders.
- Reads: 20,000 visitors in 30 min, front loaded, peaks near 100 visitors/s. At 5 API calls each, about 500 requests/s, almost all reads.
- Writes: capped by the ovens at 900 orders, about 10/s at the peak.
- Invariants: no oversold slot, no double charge.
- **Conclusion:** the spike is a read problem. The write path is small and must be correct.

### 2. Version 1

```flow
Browser
CDN: static site, photos, menu JSON
Load balancer
API: 2 stateless instances
Postgres (managed) | Stripe hosted checkout: webhook back | Sweeper job: every minute
```

**Endpoints**

- `GET /menu`
- `GET /slots`: capacity left per slot
- `POST /orders`: **the write**, with an `Idempotency-Key`
- `POST /webhooks/stripe`
- `GET /orders/{id}`: status page

**Schema**

- `menu_items`: id, name, price, photo_url
- `slots`: id, starts_at, capacity (150), reserved
- `orders`: id, slot_id, phone, items, status (held, paid, expired), expires_at, idempotency_key (unique), stripe_session_id

**One order, end to end**

1. The checkout page creates an idempotency key and posts the order.
2. One transaction: `UPDATE slots SET reserved = reserved + n WHERE id = ? AND reserved + n <= capacity`. Zero rows updated means the slot is full, and we say so. Otherwise insert the order as held, expiring in 10 minutes.
3. Create a Stripe checkout session with the order id as Stripe's idempotency key, and redirect.
4. Stripe's webhook marks the order paid, and it shows up on the kitchen screen. The sweeper releases expired unpaid holds.

At 10 writes/s and a few MB of data, **this fits on one database** with lots of room.

### 3. Decisions

- **Postgres over DynamoDB.** Reserving and creating the order happen together in one transaction. The ovens cap writes at 10/s, so DynamoDB's scale buys nothing, and a cross-item DynamoDB transaction is more to get right in two weeks.
- **Conditional UPDATE over a Redis counter.** One source of truth. Redis is faster, but then there are two sources to reconcile.
- **Hold, then charge, over charge, then check.** No refunds when a slot is full.
- **Stripe hosted checkout over our own card form.** No card data on our servers, and the shop already uses Stripe.
- **One service over microservices.** Two engineers, two weeks.

### 4. Spike defenses, cheapest first

1. **CDN:** site, photos, and the menu JSON cached 30 s, since it only changes when we edit it.
2. **Cache slot availability for 2 s.** It's a hint; the conditional update is the truth. Show a sold-out banner when every slot is full.
3. **Waiting room behind a flag.** Ship without one: a full slot is rejected cheaply in the database. Turn it on only if traffic is far above plan.
4. **Rate limits:** per IP at the edge, and at most 2 orders per phone.
5. **Atomic reserve** (already in V1): no oversell.
6. **Idempotency** (already in V1): a double tap returns the same order, Stripe dedupes on the order id, the webhook ignores event ids it has seen.
7. **Queue for texts and emails.** They can lag; checkout can't.
8. **Connection pooler**, and call Stripe only after a hold succeeds, so people who miss out never touch Stripe's rate limit.

### 5. Go-live checklist

1. **Load test at 3x:** 60,000 visitors in 30 min, against staging, with Stripe mocked using latencies sampled from live calls. Stripe's sandbox limits are lower than live, so a test against it would measure those limits, not our system. Pass: 0 oversold slots, 0 double charges, p95 under 500 ms.
2. **Pre-scale at 2:00 Sunday:** more API instances, a bigger DB tier, a warm CDN. Autoscaling takes minutes; this surge takes seconds.
3. **Kill switches, each tested:** pause orders, close a slot (an oven breaks), waiting room on, hide photos.
4. **Code freeze Friday.** Before that, canary releases with a rollback we've actually run. No deploys during the game.
5. **Dashboards:** errors, p95, slots left, held vs paid, Stripe errors, webhook lag, DB connections.
6. **Runbook and game day:** an owner per alert. On Saturday, run the load test, flip every switch, and fake a Stripe outage.
7. **Go-live morning:** before kickoff, check the pre-scale and CDN hit rate. During, watch errors and p95, then held vs paid (holds climbing while paid stays flat means payments are failing), and slots left against the kitchen screen.

### 6. Wrap-up

**Summary.** The ovens cap writes, so the spike is reads. One Postgres with a conditional update means no oversold slot. Idempotency keys end to end mean no double charge. The CDN, a 2 s cache and a waiting-room flag absorb the reads. Go-live is pre-scale, freeze, kill switches and a game day.

**Trade-offs**

- Availability can lag 2 s, so a few people learn "sold out" at checkout.
- An unpaid hold blocks pizzas for up to 10 minutes.
- Hosted checkout gives less control over the payment page.
- One database: managed failover and backups, not a second region.

:::

---

## 2. Weekend step challenge {#q-steps}

> A small fitness app runs a weekend team step challenge with a live leaderboard and prizes for the top teams.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Who, and how? *Phone app only. The app reads step counts from the phone's health data and syncs them to us.*
- Normal traffic? *About 20,000 daily users, each phone syncs every 15 minutes.*
- The spike? *150,000 people in 10,000 teams. It runs Friday 6 PM to Sunday 8 PM. In the last hour, everyone has the app open, syncing and watching the leaderboard.*
- Must never fail? *Every step counted once: none lost, none double counted. The final standings must be right, because there are prizes.*
- May degrade? *The leaderboard can lag 30 s. The feed and profile photos can go away.*
- Team, time, existing stack? *Three engineers, four weeks. The app already has a Postgres backend.*

**Numbers**

- During the weekend: 150,000 users syncing every 5 min is about 500 writes/s.
- Last hour: 100,000 active phones syncing every 30 s is about 3,300 writes/s.
- Leaderboard reads: 100,000 users refreshing every 10 s is 10,000 reads/s.
- Data: one row per user per day, 450,000 rows. Tiny.
- **Conclusion:** a write-heavy counter, but the trick is in the shape of the write. If phones send their **daily total** instead of "+500 steps", every sync is an idempotent upsert, and retries can't double count.

### 2. Version 1

```flow
Phone app
Load balancer
API: stateless instances
Postgres: users, teams, daily steps
Leaderboard job: every 15 s
Object storage + CDN: leaderboard and per-team JSON
```

**Endpoints**

- `POST /sync`: **the write**. Body: date, steps_total for that day, recorded_at
- `GET /leaderboard`: static JSON on the CDN, 15 s TTL
- `GET /teams/{id}`: static JSON on the CDN, 15 s TTL
- `POST /teams/{id}/join`
- `GET /me`

**Schema**

- `users`: id, team_id
- `teams`: id, name
- `user_day_steps`: primary key (user_id, date), steps, updated_at
- `final_standings`: team_id, rank, steps, snapshot_at

**One sync, end to end**

1. The phone reads today's cumulative steps, say 8,412, and posts them.
2. The API checks caps (at most 60,000 a day, at most about 250 steps a minute since the last sync), then runs `INSERT ... ON CONFLICT (user_id, date) DO UPDATE SET steps = excluded.steps WHERE excluded.steps > user_day_steps.steps`. A retried or duplicate sync changes nothing, and an older total that arrives late can't lower the count.
3. Every 15 s, the leaderboard job sums steps by team and writes the leaderboard JSON and changed team files to object storage. The CDN serves them.
4. At 8:00 PM, syncs with recorded_at after 8:00 stop counting. Phones that were offline get a 15-minute grace window for steps recorded before 8:00. The final snapshot is taken at 8:15.

3,300 single-row upserts by primary key **fit on one Postgres primary** with a pooler. We'll prove it in the load test.

### 3. Decisions

- **Daily totals over deltas.** A total is idempotent and order-independent. Deltas ("+500") would need a unique id per event and dedupe on every one.
- **Aggregate every 15 s over incrementing team counters.** The top teams' rows would be hot, and every increment would need dedupe. A sum over 450,000 rows every 15 s is cheap.
- **Postgres over a Redis sorted set.** A sorted set is the textbook leaderboard and my pick at 10x this size or for real-time ranks. Here a 15 s sum is enough, and Postgres is already the source of truth.
- **Static JSON on a CDN over API reads.** 10,000 reads/s become a few origin fetches per edge.
- **A grace window keyed on recorded_at over a hard cutoff on arrival time.** Fair to phones that were offline, while the caps limit abuse.

### 4. Spike defenses, cheapest first

1. **CDN** for the leaderboard and team JSON.
2. **Server-controlled sync interval.** Each response says `next_sync_in`: 30 s normally, 120 s under load, with jitter so phones don't sync in lockstep. This is the cheapest throttle there is.
3. **Rate limit per user:** one sync per 20 s, extras dropped.
4. **Connection pooler and pre-scaled API.**
5. **If writes still bite:** put syncs on a queue and apply only the latest total per user every few seconds. Last value wins, so the queue collapses.
6. **Degrade:** feed and photos off in the last hour.
7. **Anti-cheat:** the caps plus anomaly flags reviewed before prizes.

### 5. Go-live checklist

1. **Load test at 3x the last hour:** 10,000 syncs/s, with duplicates and out-of-order totals, plus 30,000 leaderboard requests/s. Pass: final standings equal a truth computed offline, sync p95 under 300 ms, no step lost.
2. **Pre-scale Sunday at 6 PM.**
3. **Flags:** the sync-interval knob, freeze the leaderboard, extend the grace window.
4. **Freeze Friday.** No deploys during the challenge.
5. **Dashboards:** syncs/s, rejected syncs (cap hits), leaderboard JSON age, DB write latency, pool saturation.
6. **Rehearse the cutoff:** run the snapshot job in staging twice and confirm it gives the same answer.
7. **Prizes come from the 8:15 snapshot** after a manual check of the top 10 teams.

### 6. Wrap-up

**Summary.** Phones send totals, not deltas, so every sync is an idempotent upsert and retries can't double count. Team totals are summed every 15 s into static JSON on a CDN. A server-controlled sync interval is the throttle, and a grace window keeps the cutoff fair.

**Trade-offs**

- The leaderboard lags 15 to 30 s.
- Late phones get 15 minutes, then they're out.
- Caps may flag a real ultramarathoner, so prizes wait for a manual check.
- One region and one database.

:::

---

## 3. Holiday photo cards {#q-cards}

> A small print shop lets customers upload photos and design holiday cards. The week before the shipping cutoff, orders jump 50x.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What's the flow? *Upload 1 to 20 photos, pick a template, see a preview, pay. The shop prints and ships.*
- What has to happen to each order? *Thumbnails, a preview image, and a print-ready PDF at 300 dpi.*
- Normal traffic? *About 300 orders a day.*
- The spike? *15,000 orders a day for the last 5 days. The busiest hour is the evening before the cutoff: about 2,500 orders.*
- Must never fail? *Never lose an uploaded photo or a paid order. Never print an order twice, and never print the wrong photos.*
- May degrade? *The preview can take 30 s. The print PDF can take hours, as long as it's ready before its print slot.*
- Team and stack? *Three engineers, six weeks. Payments through Stripe.*

**Numbers**

- Orders: 2,500 in the peak hour is under 1 order/s. Tiny.
- Uploads: 8 photos x 4 MB = 32 MB an order, so 80 GB in the peak hour, about 22 MB/s coming in.
- Compute: thumbnails 8 s, preview 5 s, print PDF 60 s of CPU per order. Peak hour: 2,500 x 73 s is about 180,000 CPU seconds, so about 50 cores busy. Normal days need less than one.
- Storage: about 500 GB of photos a day, in object storage. DB rows are tiny.
- **Conclusion:** this is a compute burst and an upload-bandwidth problem, not a database problem. Fast jobs that a customer is waiting on and slow print jobs need separate lanes.

### 2. Version 1

```flow
Browser
API: stateless, hands out upload URLs | Object storage: photos and PDFs, browser uploads directly
Postgres: orders, photos, jobs | Queue: fast lane and slow lane
Fast workers: thumbnails, preview | Slow workers: print PDF
Print-shop screen
```

**Endpoints**

- `POST /uploads`: returns a pre-signed upload URL per photo
- `POST /orders`: **the write**, with an `Idempotency-Key`
- `GET /orders/{id}/preview`: status plus the preview URL
- `POST /webhooks/stripe`
- `GET /print-queue`: staff view of paid orders with a ready PDF
- `POST /print-queue/{id}/printed`

**Schema**

- `orders`: id, status (draft, paid, rendered, printed, shipped), template_id, idempotency_key (unique)
- `photos`: id, order_id, storage_key
- `jobs`: id, order_id, kind (thumb, preview, print_pdf), status (queued, running, done, failed), attempts, output_key; unique (order_id, kind)
- `prints`: order_id as the primary key, printed_at. One row per order, so a second print is refused.

**One order, end to end**

1. The browser gets upload URLs and sends each photo straight to object storage.
2. The upload-complete call enqueues thumbnail jobs on the fast lane.
3. The customer picks a template. The API enqueues a preview job, and the page polls ("rendering, about 20 s").
4. The customer pays on Stripe. The webhook (deduped on event id) marks the order paid and enqueues the print_pdf job on the slow lane.
5. A worker takes the message and checks the jobs row. If it's already done, it acks and skips. Otherwise it renders, writes the PDF to a fixed key like `orders/{id}/print.pdf` (so a re-render just overwrites), marks the job done, and acks.
6. Staff print from the queue. Marking an order printed inserts into `prints`, so a second attempt fails loudly.

Under 1 order/s and a few hundred job updates/s **fit on one database** easily.

### 3. Decisions

- **Direct uploads with pre-signed URLs over uploading through the API.** 22 MB/s of photos never touches the API, and object storage scales on its own.
- **A managed queue over Kafka.** Each job runs once, nobody needs to replay a stream, and the dead-letter queue is built in.
- **Two lanes over one queue.** A 60 s print job must not sit in front of a 1 s thumbnail a customer is staring at.
- **Scale workers on queue depth over CPU.** Depth is the real backlog.
- **A jobs table next to the queue over the queue alone.** The queue says "do this"; the table says what's done. That gives idempotency and a staff view of stuck jobs.
- **Containers for workers over serverless functions.** Long renders with big image libraries, and a simple concurrency cap.

### 4. Spike defenses, cheapest first

1. **CDN** for the site, templates and thumbnails.
2. **Direct uploads** (already in V1).
3. **The queue absorbs the burst.** Work waits instead of failing. Show an honest ETA.
4. **Autoscale workers on depth, with a max:** say 20 cores for the fast lane and 60 for the slow lane, so cost is bounded and the fast lane never starves.
5. **Pre-scale** the worker pool for the last 5 days, more in the evenings.
6. **Retries with backoff, and a dead-letter queue after 5 attempts.** Alert on DLQ depth.
7. **Visibility timeout longer than the job** (5 min for a 60 s render) so a job isn't handed to a second worker mid-render.
8. **Alert on the oldest job's age** in each lane, not just the depth. A 2-hour-old print job threatens the print schedule.

### 5. Go-live checklist

1. **Load test at 3x the peak hour:** 7,500 orders an hour with real-size photos, in staging. Pass: every paid order has a PDF, no order printed twice, preview p95 under 30 s, oldest slow job under 1 hour.
2. **Raise cloud CPU quotas weeks ahead.** Quota requests can take days.
3. **Kill switches:** pause the slow lane to give every worker to previews, turn off slow templates, stop new orders at the cutoff.
4. **Freeze for the last week.** If you must deploy, workers shut down gracefully: finish the job or hand it back.
5. **Dashboards:** depth and oldest age per lane, DLQ depth, job failure rate, paid orders without a PDF, upload errors.
6. **Nightly reconciliation:** every paid order has a finished print job, and every PDF was printed once.
7. **Game day:** kill workers mid-render and confirm the job retries and the PDF comes out the same. Push a corrupt photo and watch it land in the DLQ.

### 6. Wrap-up

**Summary.** The spike is compute and bandwidth, not the database. Photos go straight to storage. Renders go through a queue with a fast and a slow lane and workers scaled on depth. Idempotent jobs plus a one-row-per-order `prints` table mean no lost order and no double print.

**Trade-offs**

- Previews can take 30 s at peak.
- The worker cap bounds cost, so a backlog can build in the slow lane.
- Fixed output keys mean a re-render overwrites the old file.
- One region.

:::

---

## 4. Tire shop, first snow {#q-tires}

> A tire shop with 3 locations lets customers book winter-tire swaps online. The first snow is forecast for Friday.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What's the flow? *Pick a location and a 45-minute slot, enter phone and plate. No payment: they pay in the store. They can cancel by link.*
- Normal traffic? *About 100 bookings a week.*
- The spike? *When the forecast hits the local news on Tuesday, we expect 20,000 visitors in the first hour and 8,000 booking attempts over two days.*
- The hard limit? *Each location has 4 bays, open 10 hours a day.*
- Must never fail? *Never two cars in one bay at one time. Never lose a booking we confirmed.*
- May degrade? *Reminder texts can lag.*
- Team and stack? *One contractor, three weeks. Today it's a paper calendar.*

**Numbers**

- Supply: 13 slots a day x 4 bays x 3 locations x 6 days is about 940 appointments. Most of the 8,000 attempts will miss.
- Reads: 1,000 visitors in the peak minute is about 17/s, x 6 availability calls is about 100 requests/s.
- Writes: capped at 940 bookings, under 5/s.
- **Conclusion:** load is easy. The real problems are races on the popular slots (Saturday 9 AM), one person hoarding slots, and demand far above supply. Don't over-build.

Also say: "An off-the-shelf booking tool might do this for a small monthly fee. I'll assume they need it tied to their own system."

### 2. Version 1

```flow
Browser
CDN: static site
Load balancer
API: 2 instances
Postgres | Queue + SMS provider | Reminder job: hourly
```

**Endpoints**

- `GET /locations`
- `GET /locations/{id}/availability?date=`: free bays per slot
- `POST /bookings`: **the write**, with an `Idempotency-Key`
- `POST /bookings/{id}/cancel`: uses a token from the text message
- `GET /schedule?location=&date=`: staff view

**Schema**

- `bays`: id, location_id
- `bookings`: id, location_id, bay_id, slot_start, phone, plate, status (confirmed, completed, cancelled, no_show), cancel_token, idempotency_key (unique)
- Unique index on (bay_id, slot_start) where status is confirmed: **the database refuses a double booking.**
- Unique index on (phone, location_id) where status is confirmed: one upcoming booking per phone per location.

**One booking, end to end**

1. The customer picks a slot. The page posts with an idempotency key.
2. In one transaction, the API picks a bay with no confirmed booking at that time and inserts the booking.
3. If two requests race for the last bay, the unique index rejects one. That request retries once with the next free bay, or returns "just taken" plus the next 3 free slots.
4. Commit, then queue the confirmation text with a cancel link. A cancel frees the bay at once.

### 3. Decisions

- **Unique constraint over a check in code.** "Check, then insert" in the app races. The DB is the referee.
- **No holds.** There's no payment step, so book in one step. Holds with expiry come back only if they add deposits.
- **SMS through a queue over sending inline.** A slow SMS provider must not fail a booking.
- **Phone check over accounts.** One booking per phone stops most hoarding without a login. A one-time SMS code sits behind a flag, on only if bots show up.
- **Waitlist over a waiting room.** The problem is demand above supply, not load. A waitlist turns cancellations into bookings.

### 4. Spike defenses, cheapest first

1. **CDN** for the site.
2. **Cache availability for 5 s.** A hint; the insert is the truth.
3. **Rate limits per IP**, plus one booking per phone per location (already a unique index).
4. **SMS code on booking, behind a flag**, for bots.
5. **Waitlist:** when a day fills, take "text me if a slot opens". A cancellation texts the next person.
6. **Ask the SMS provider for higher throughput** ahead of time.
7. **Say what you're skipping:** no waiting room, no read replicas, no Redis. 100 requests/s doesn't need them.

### 5. Go-live checklist

1. **Load test at 3x:** 300 requests/s, with 200 concurrent bookings for the same Saturday 9 AM slot. Pass: exactly 4 bookings for that slot, everyone else gets a clean "taken" with alternatives, p95 under 300 ms.
2. **Import the paper calendar before launch,** or the first car through the door double books a bay. Give staff a tool to block a bay.
3. **Kill switches:** close online booking for one location, block a day, turn on the SMS code, pause texts.
4. **A paper fallback:** a printed daily schedule if the site is down.
5. **Dashboards:** bookings an hour per location, "slot taken" rate (high is expected), 500 errors (a bug), SMS failures, cancellations.
6. **When the news story runs:** scale to 4 instances and watch errors and the 500 rate.

### 6. Wrap-up

**Summary.** Supply caps writes at about 940 bookings, so load is easy. A unique index on (bay, slot) makes double booking impossible. One booking per phone and an SMS-code flag stop hoarding. A waitlist handles demand above supply.

**Trade-offs**

- Cached availability means some "just taken" messages.
- No deposit means no-shows. Reminders reduce them.
- First come, first served favors fast users.
- One region.

:::

---

## 5. Youth soccer storm alert {#q-soccer}

> A youth soccer league's app has 300,000 parents. When lightning cancels games, everyone must be told within 10 minutes.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Which channels? *Push notifications for everyone. SMS for the 100,000 parents who opted in. Email as a backup.*
- Who triggers it? *A league admin presses "cancel games in a region".*
- Normal traffic? *A few thousand notifications a week, per-team schedule changes.*
- The spike? *A storm cancels a whole region on Saturday morning. Everyone is told at once, and most parents open the app within 5 minutes.*
- Must never fail? *No parent misses a cancellation. Never cancel the wrong games.*
- May degrade? *Email can lag 30 minutes. Standings and photos can go away.*
- Team and stack? *Two volunteers and a contractor. The app uses Firebase for push and Twilio for SMS.*

**Numbers**

- Fan-out: 300,000 push, 100,000 SMS and 300,000 emails within 10 minutes.
- Push: batches of 500 tokens is 600 calls. Done in under a minute.
- SMS: 100,000 in 10 minutes is about 170/s. A single ordinary phone number sends about 1/s, so we need a high-throughput sender, raised with the provider in advance. **This is the bottleneck.**
- Reads afterward: 180,000 parents in 5 minutes is 600 app opens/s, x 3 calls is about 1,800 requests/s, all asking "is my game on?"
- **Conclusion:** a fan-out limited by SMS throughput, then a read spike with one answer per game. Both are queue-and-cache problems.

### 2. Version 1

```flow
Admin console
API
Postgres: games, recipients, deliveries | Outbox table
Queue: fan-out jobs
Push workers | SMS workers | Email workers
CDN: game status JSON for the app
```

**Endpoints**

- `POST /admin/cancellations`: **the write**. Region and date, with an `Idempotency-Key`
- `GET /games?team=`: CDN cached 30 s, purged on a cancellation
- `GET /announcements/{id}`
- `POST /webhooks/sms-status`: delivery receipts
- `POST /devices`, `PUT /preferences`

**Schema**

- `games`: id, team_ids, starts_at, field, status (scheduled, cancelled)
- `recipients`: parent_id, team_id, push_token, phone, email, sms_opt_in
- `announcements`: id, region, created_by, idempotency_key (unique)
- `deliveries`: primary key (announcement_id, parent_id, channel), status (queued, sent, delivered, failed), provider_id. **One send per parent per channel.**

**One cancellation, end to end**

1. The admin presses cancel. The confirm dialog shows the count: "112 games, 300,000 parents."
2. One transaction: mark the games cancelled, insert the announcement, insert an outbox row. Then purge those games from the CDN.
3. A fan-out worker pages through recipients 1,000 at a time, inserts delivery rows (on conflict, do nothing) and enqueues batches per channel.
4. Channel workers skip rows already sent, send, and record the provider id.
5. Delivery receipts mark rows delivered or failed. Failed SMS retry with backoff. A failed push falls back to SMS or email.

### 3. Decisions

- **Queue and batch workers over sending in the admin's request.** 700,000 sends take minutes; the request returns in a second.
- **Outbox over "commit, then publish".** If the process dies between the two, games would be cancelled and nobody told.
- **A deliveries key over trusting the queue.** Queues deliver at least once; the key makes a resend a no-op and gives a per-parent audit.
- **A high-throughput SMS sender over a few ordinary numbers.** 170/s is impossible otherwise. It takes weeks to set up, so it goes in the plan now.
- **Push first, SMS second, email last.** The free, fast channel shouldn't wait behind the throttled one.
- **Managed queue over Kafka.** Each send is a task done once; nothing needs replaying.

### 4. Spike defenses, cheapest first

1. **CDN with purge** for game status: the 1,800 requests/s are served at the edge.
2. **Priority lanes:** push, then SMS, then email.
3. **SMS workers rate limited to the provider's limit** (a token bucket at about 150/s), with backoff and jitter on 429s.
4. **Recipient lists per region built nightly,** so the fan-out doesn't run heavy joins on a Saturday morning.
5. **Turn off standings and photos** during the event.
6. **Idempotent sends** (the deliveries key) and deduped delivery receipts.
7. **A 30 s undo window** before the fan-out starts. A wrong-region cancellation is the costliest mistake, and 30 s of a 10-minute budget is cheap.

### 5. Go-live checklist

1. **Load test at 3x:** a fan-out to 900,000 fake recipients with providers in test mode. Pass: all push within 2 minutes, SMS at the provider limit, 0 duplicates per parent and channel, status p95 under 300 ms at 5,000 requests/s.
2. **Raise provider limits weeks ahead.**
3. **Kill switches:** pause the fan-out mid-send, stop the SMS lane, hide heavy app features.
4. **Dry run:** a real test announcement sent only to staff.
5. **Dashboards:** deliveries by channel and status, send rate vs provider limit, queue depth and oldest age, provider errors, and time until 95% delivered.
6. **Runbook:** a wrong-region cancellation gets a correction announcement, never a delete.

### 6. Wrap-up

**Summary.** The 10-minute promise depends on SMS throughput, so push goes first, SMS runs at a pre-raised limit, and email goes last. An outbox and a deliveries key make the fan-out at-least-once without duplicates. The read spike is one cached JSON per game, purged on change.

**Trade-offs**

- SMS costs money per message.
- A parent can get both a push and a text, by design.
- The 30 s undo window delays every alert.
- Status can be stale for the few seconds a CDN purge takes.

:::

---

## 6. Electronics shop doorbusters {#q-doorbusters}

> A small electronics shop runs online Black Friday doorbusters at 6 AM: 20 deal items, 50 units each, plus its normal catalog.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What's the flow? *Browse, build a cart with several items, pay, then ship or pick up.*
- Normal traffic? *1,500 visitors and 100 orders a day.*
- The spike? *An email goes to 80,000 subscribers. We expect 40,000 visitors in the first 10 minutes after 6 AM. The deals will sell out in about 5 minutes.*
- The hard limit? *1,000 deal units in total. The normal catalog has 3,000 items, with hundreds in stock.*
- Must never fail? *No oversell, no double charge, and the "1 per customer" limit on deals must hold.*
- May degrade? *Reviews, recommendations, search suggestions.*
- Team and stack? *Two engineers, four weeks, Stripe. The store's register uses the same stock.*

**Numbers**

- Reads: about 10,000 visitors in the peak minute is about 170/s, x 8 calls is about 1,300 requests/s.
- Writes: about 800 deal orders in 5 minutes, but most land in the first seconds: up to about 30 checkouts/s at 6:00:00.
- Hot rows: each deal is a single stock row hit by thousands of people at once.
- **Conclusion:** the reads are the bulk. The hard parts are 20 hot rows at 6:00 and carts that must reserve every item or none.

### 2. Version 1

```flow
Browser
CDN: site, images, catalog JSON
Load balancer
API: 2 instances
Postgres: products, stock, orders | Stripe hosted checkout | Sweeper job
```

**Endpoints**

- `GET /catalog`, `GET /deals`: cached
- Cart lives in the browser or session. **Adding to cart reserves nothing.**
- `POST /checkout`: **the write**, with an `Idempotency-Key`. Reserves every line, holds 10 minutes, returns the Stripe URL
- `POST /webhooks/stripe`
- `GET /orders/{id}`

**Schema**

- `products`: id, name, price, is_deal
- `stock`: product_id (primary key), available, with a check that available is never below 0
- `orders`: id, email, status (held, paid, expired), expires_at, idempotency_key (unique)
- `order_lines`: order_id, product_id, qty
- `deal_claims`: unique (product_id, customer_key). **The "1 per customer" rule.**

**One checkout, end to end**

1. The page posts the cart with an idempotency key.
2. One transaction. For each line, in product_id order: `UPDATE stock SET available = available - qty WHERE product_id = ? AND available >= qty`. If any line updates zero rows, roll back everything and say which item sold out. Insert the deal claims; a unique violation means "limit 1". Insert the held order and its lines.
3. Create the Stripe session with the order id as the idempotency key.
4. The webhook marks it paid. The sweeper returns stock from expired holds, after asking Stripe whether payment went through.

Roughly 30 transactions/s **fit on one Postgres** easily.

### 3. Decisions

- **Reserve at checkout over at add-to-cart.** Carts are cheap and often abandoned. Reserving them would lock stock for browsers.
- **One transaction, lines in a fixed order.** All or nothing, and a fixed lock order means two carts can't deadlock each other.
- **Conditional updates in Postgres over Redis.** 20 hot rows at about 30 updates/s each is fine for row locks of about a millisecond.
- **A deal-claims table over a check in code.** The unique key makes the limit race-proof.
- **Deals sold online only.** The register can't sell deal units, so there's no sync lag between store and site. Ask the business; it's their call.

### 4. Spike defenses, cheapest first

1. **CDN** for the catalog, images, deals JSON (30 s) and the stock badges (2 s).
2. **Flags off at 6 AM:** reviews and recommendations.
3. **Waiting room ON from 5:55 to 6:20.** Unlike a spread-out spike, this one starts at a single instant and sells out in minutes. Randomizing everyone who arrived before 6:00 is fairer than rewarding the fastest refresh, and it lets people into checkout at a fixed rate, say 300/s.
4. **Rate limits** per IP and session on checkout, and bot rules at the WAF.
5. **Atomic multi-line reserve and deal claims** (already in V1).
6. **Idempotency keys and webhook dedupe.**
7. **Connection pooler, with separate pools for browsing and checkout,** so a flood of browsing can't starve checkout.
8. **Confirmation emails on a queue.**

### 5. Go-live checklist

1. **Load test at 3x:** 120,000 visitors in 10 minutes and 1,000 concurrent checkouts on one deal at 6:00:00. Pass: exactly 50 units sold per deal, no negative stock, 0 double charges, no deadlocks, checkout p95 under 800 ms.
2. **Pre-scale at 5:30,** warm the CDN, configure the waiting room.
3. **Flags:** waiting room, pause checkout, hide reviews, end a deal early.
4. **Freeze on Wednesday.** No deploys on Friday.
5. **Dashboards:** stock per deal, held vs paid, sold-out responses vs 500s, lock wait time on stock rows, Stripe errors.
6. **Count the shelves Thursday night** and load the real numbers.
7. **At 6 AM, watch:** the waiting-room release rate, checkout p95, lock waits, held vs paid.

### 6. Wrap-up

**Summary.** Reads are served at the edge. Carts are free; stock is reserved at checkout in one transaction, a conditional update per line. The per-customer limit is a unique key. A waiting room makes the 6:00:00 start fair.

**Trade-offs**

- Stock can be gone by the time you check out.
- Holds lock units for 10 minutes.
- The waiting room adds friction for everyone.
- Deals are online only, so store shoppers can't buy them.

:::

---

## 7. City marathon live tracking {#q-marathon}

> A local running club times a 20,000-runner city marathon and wants live tracking so friends and family can follow runners online.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Where does the data come from? *Timing mats every 5 km, 9 in total. A chip on each runner is read when they cross. The mat readers send reads to us over cellular.*
- Are reads clean? *No. A chip is often read 2 or 3 times, and a reader that loses signal buffers and sends late.*
- Normal traffic? *None. Once a year. Other days, people look up results.*
- The spike? *Race morning, about 5 hours. 60,000 spectators each follow about 3 runners and refresh often. The finish is busiest.*
- Must never fail? *Never lose a timing read: the official results come from them. Final times must be right.*
- May degrade? *Live splits can lag 30 s. The map and photos can go away.*
- Team and stack? *Two volunteers. The timing vendor's readers can push over HTTPS.*

**Numbers**

- Ingest: 20,000 runners x 9 mats = 180,000 crossings, about 540,000 raw reads with duplicates. The busiest moment, the start, is 20,000 runners in 20 minutes: about 17 crossings/s, 50 reads/s with duplicates.
- Spectators: 60,000 people refreshing every 30 s is 2,000 requests/s, up to about 5,000/s at the finish.
- Data: 540,000 rows of about 200 bytes, about 100 MB.
- **Conclusion:** it sounds write-heavy, but ingest is about 50 reads/s. The job there is losing nothing and handling duplicates. The real load is spectators, and every runner's page is cacheable.

### 2. Version 1

```flow
Timing mat readers: buffer and retry
API: ingest endpoint
Postgres: raw reads, splits
Split builder: every 10 s
Object storage + CDN: one JSON per runner
Spectator browser
```

**Endpoints**

- `POST /ingest/reads`: **the write**. A batch of reads, each with reader_id, seq, chip_id, mat_id, timestamp. Each reader has its own API key
- `GET /runners/{bib}.json`: static file on the CDN
- `GET /search-index.json`: names and bibs, about 1 MB, searched in the browser
- `GET /leaderboard.json`
- `POST /admin/corrections`

**Schema**

- `raw_reads`: primary key (reader_id, seq), chip_id, mat_id, ts. **A resent batch is a no-op.**
- `runners`: bib, chip_id, name, wave, start_time
- `splits`: primary key (bib, mat_id), first_ts

**One read, end to end**

1. The reader batches reads every 2 s and posts them. It keeps them in its buffer until it gets a 200.
2. The API inserts the batch with "on conflict do nothing" and returns 200 only after the commit.
3. Every 10 s, the split builder upserts splits with **earliest read wins**: `first_ts = LEAST(existing, new)`. Duplicates and late reads give the same answer in any order.
4. For runners whose splits changed, the builder writes `runners/{bib}.json` to object storage. The CDN serves it, so spectators never hit the API.

### 3. Decisions

- **Postgres over Kafka, Cassandra or a time-series DB.** 50 reads/s is nothing, and corrections and dedupe are easy in SQL.
- **Keep raw reads and derive splits over updating splits directly.** The raw reads are the audit trail for official results and let us rebuild after a bug.
- **Earliest read wins over last write wins.** Duplicates and late batches can't corrupt a split.
- **Ack after commit, reader keeps its buffer until acked.** At-least-once from the mat plus an idempotent insert means no lost reads.
- **Static JSON on a CDN over an API with WebSockets.** 60,000 spectators are fine with 15 s freshness, and the origin does no work per spectator.

### 4. Spike defenses, cheapest first

1. **Static per-runner JSON on the CDN** (in V1). The spectator spike never reaches our servers.
2. **Search in the browser** from a 1 MB index file, instead of a search endpoint.
3. **Hide the map and photos** if anything strains.
4. **Bulkhead:** ingest runs on its own instance with its own DB pool. Nothing spectators do can slow the official timing.
5. **Readers retry with backoff, rate limited per reader.**

### 5. Go-live checklist

1. **Replay test:** 540,000 reads at 3x speed with extra duplicates, plus one reader that goes offline for 20 minutes and then dumps its buffer. Pass: splits exactly match a truth computed offline, ingest p99 under 1 s, zero lost reads.
2. **Spectator test:** 15,000 requests/s at the CDN; the origin should stay near zero.
3. **Field test Saturday:** every mat's reader sends a test read with its real key over real cellular.
4. **Kill switches:** freeze the leaderboard, hide the map, results read-only.
5. **Dashboards:** reads a minute per mat (a mat at zero means a reader is down), reader lag, split-builder lag, CDN hit rate.
6. **Fallback:** the vendor's local backup file at each mat. Reconcile against it before publishing official results.

### 6. Wrap-up

**Summary.** It sounds write-heavy, but ingest is about 50 reads/s; the job is losing nothing and deduping. Raw reads are keyed by (reader, seq), splits use "earliest read wins", and spectators read static JSON from a CDN.

**Trade-offs**

- Live splits lag up to about 25 s.
- Official results wait for reconciliation.
- One small file per runner means 20,000 files, which is cheap.
- One region.

:::

---

## 8. Travel blog goes viral {#q-blog}

> A one-person travel blog with a paid newsletter just went viral. Traffic is 100x and climbing, right now.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- What runs today? *A blogging CMS on one virtual machine with MySQL. Newsletter signups pay $5 a month through Stripe.*
- Normal traffic? *2,000 page views a day.*
- The spike? *One post is at 200,000 views an hour and may triple. It will probably last two days. The site is already slow.*
- Must never fail? *Paid signups charged once, and never lose the subscriber list.*
- May degrade? *Comments, related posts, search.*
- Team and budget? *The owner, plus you for a week. Small budget.*

**Numbers**

- Views: 200,000 an hour is 55/s, maybe 170/s if it triples. Each page loads about 30 files.
- The origin: one CMS server renders maybe 20 to 50 dynamic pages/s. That's why it's falling over.
- Signups: 1% of visitors is about 2,000 an hour, under 1/s.
- **Conclusion:** a pure read spike on one page. A CDN with full-page caching solves most of it within the hour. Don't rebuild the site during the spike.

### 2. Version 1 (the fix for the next hour)

```flow
Browser
CDN: full-page cache for logged-out visitors, images
One VM: the CMS, now the origin
MySQL | Stripe hosted checkout
```

**Endpoints**

- The existing pages, now cached at the CDN for 5 minutes
- `POST /subscribe`: **the write**, with an `Idempotency-Key`. Creates a Stripe checkout session
- `POST /webhooks/stripe`

**Schema**

- `subscribers`: email (unique), status (pending, active), stripe_customer_id
- `processed_events`: stripe_event_id (primary key)

**One request, end to end**

1. A visitor opens the viral post. The CDN serves it. On a miss, the CDN fetches from the VM once per 5 minutes per edge location.
2. Logged-in users, the admin pages and every POST bypass the cache.
3. A signup posts to `/subscribe`, the pending row is created (the unique email makes a retry return the same row), and the visitor pays on Stripe's page.
4. The webhook marks the subscriber active, deduped on event id.

### 3. Decisions

- **Put a CDN in front over adding servers or rebuilding as a static site.** It takes minutes and removes almost all origin load. A static rebuild is better long term, but not mid-spike.
- **Keep one VM, one size bigger, over a cluster.** Behind the CDN, the origin sees a few requests a second.
- **Stripe hosted checkout over a CMS card-form plugin.** No card data on the VM.
- **Comments off for 48 hours over scaling the database.**

### 4. Spike defenses, cheapest first

1. **Full-page CDN cache,** with "serve stale while refreshing" and "serve stale if the origin errors".
2. **Turn off comments, related posts and search:** the expensive queries.
3. **Resize the VM and database one tier.** Minutes, and cheap for two days.
4. **Resized images through the CDN.**
5. **Origin shield:** one CDN tier talks to the origin, so a cold cache doesn't stampede the VM.
6. **Rate limit `/subscribe`** and dedupe on email.
7. **Send the newsletter through the email provider,** never from this VM.

### 5. Go-live checklist

Here, "go-live" is the switch to the CDN, then the week after.

1. **Test the CDN config on a staging hostname first:** pages show a cache HIT, admin pages are never cached, signup works end to end.
2. **Back up the database now.** The subscriber list is the business.
3. **Load test the cached page at 3x (500 requests/s).** This tests the CDN config; the origin should stay flat.
4. **Watch:** origin requests/s, CDN hit rate (aim above 95%), error rate, signups vs Stripe.
5. **Kill switch:** a maintenance page served from the CDN if the origin dies, with stale pages still served.
6. **Next week:** plan the static rebuild and a proper staging site.

### 6. Wrap-up

**Summary.** A read spike on one page. Fix it with a full-page CDN cache, turn off the dynamic extras, and protect the one write, paid signups, with Stripe and idempotency.

**Trade-offs**

- Cached pages can be 5 minutes stale. Purge for an urgent edit.
- Comments are off for two days.
- The single VM is still a single point of failure, softened by "serve stale if error".

:::

---

## 9. Hat drop, one famous post {#q-hats}

> A small company is selling a limited run of branded hats. A very famous founder is going to post about them, so expect a traffic spike.

::: answer

### 1. Clarify

**Questions, with the interviewer's answers**

- Who buys, and how? *Anyone who follows the link, mostly on phones. No accounts. US shipping only. One hat, one size.*
- Normal traffic? *None. It's a new store.*
- The spike? *About 2M visitors in the first hour, half of them in the first 10 minutes.*
- Do we know when the post goes out? *We know the day, not the minute. Don't count on a heads-up.*
- The hard limit? *20,000 hats at a warehouse partner, with no restock for 8 weeks. At most 2 per order.*
- Must never fail? *No oversell, no double charge, no lost paid order. The site can't look down while the post is live.*
- May degrade? *Confirmation emails and the warehouse hand-off can lag by hours. Buyers can wait in line.*
- Team, time, stack? *Two engineers, two weeks, Stripe. The warehouse API takes 5 orders/s.*

**Numbers**

- Reads: about 200,000 visitors in the peak minute is about 3,300/s. At 5 requests each, about 17,000 requests/s, almost all static.
- Demand: if 5% try to buy, about 170 buy taps/s at peak and 100,000 buyers for 20,000 hats. It will sell out, and most buyers will hear no.
- Stripe: the default is 100 requests/s per account and 25/s per endpoint. Large increases need about 6 weeks' notice, and we have 2.
- Checkout rate: release 20/s to stay under Stripe's limit. If 80% pay, that's 16 sold/s, so 20,000 hats take about 21 minutes.
- Writes: 20 checkouts + 16 payment webhooks + 4 expiries is about 40 writes/s.
- Warehouse: 20,000 orders at 5/s is about 67 minutes.
- **Conclusion:** the reads are huge but static, and the CDN handles them. The real bottleneck is Stripe, not our database, so we choose the checkout rate and everyone else waits in line.

### 2. Version 1

```flow
Browser
CDN: hat page, images, stock flag
Waiting room: releases 20/s
Load balancer
API: 4 stateless instances
Postgres: stock, orders, outbox | Stripe hosted checkout: webhook back | Sweeper job: every minute | Warehouse worker: 5 orders/s
```

**Endpoints**

- `GET /hat`: static JSON on the CDN
- `GET /stock`: in stock or sold out, cached 2 s
- `POST /checkout`: **the write**, with an `Idempotency-Key` and a waiting-room token
- `POST /webhooks/stripe`
- `GET /orders/{id}`: status page

**Schema**

- `stock`: sku (primary key), available, with a check that available is never below 0
- `orders`: id, sku, qty, status (held, paid, expired), expires_at, idempotency_key (unique), stripe_session_id, email, address
- `stripe_events`: event_id (primary key)
- `outbox`: id, order_id (unique), sent_at

**One order, end to end**

1. The buyer taps Buy. Under 20/s, the waiting room passes them straight through. Above that, they see their place in line. Either way, they get a signed token good for 10 minutes.
2. The page posts the order with an idempotency key and the token.
3. One transaction: `UPDATE stock SET available = available - qty WHERE sku = ? AND available >= qty`. Zero rows updated means sold out, and we say so. Otherwise insert the order as held, expiring in 10 minutes, and commit.
4. Create a Stripe Checkout Session with the order id as Stripe's idempotency key, and redirect. Stripe collects the card and address.
5. On the webhook, one transaction: insert the event id (a duplicate stops here), mark the order paid, and insert an outbox row. The worker then sends it to the warehouse, with the order id as the dedupe key.
6. The sweeper finds overdue holds and expires their Stripe sessions. If that works, it returns the stock and marks the order expired. If Stripe says the order was paid, it marks it paid instead. A hold with no session is simply released.

About 40 writes/s and 20,000 orders **fit on one Postgres** easily.

### 3. Decisions

- **Waiting room always on over behind a flag.** We don't know the minute of the post, so nobody should have to flip a switch. It does nothing until demand passes 20/s.
- **Managed waiting room over building one.** Two engineers, two weeks. It also keeps working at the edge if our origin struggles.
- **Conditional UPDATE in Postgres over a Redis counter.** It's one hot row at 20 updates/s, so Redis adds a second source of truth for no gain. I'd revisit that only at thousands of updates/s.
- **Postgres over DynamoDB.** Reserving stock and creating the order happen in one transaction, and our write rate needs no extra scale.
- **Commit the hold, then call Stripe.** Holding a row lock across a network call would turn one slow Stripe response into a stalled store.
- **10-minute hold with an explicit expire over Stripe's own expiry.** Stripe's minimum session expiry is 30 minutes, which would lock scarce hats for too long. Expiring the session ourselves also means nobody can pay after their hold is released.
- **Outbox over calling the warehouse from the webhook.** The order and the hand-off commit together, and a warehouse outage can't block sales.
- **Hosted checkout over our own card form.** No card data on our servers, and wallets work well on phones.
- **One service over microservices.** Two engineers, two weeks.

### 4. Spike defenses, cheapest first

1. **CDN:** the page, images and product JSON are cached, and served stale if the origin errors. With an origin shield, the 2 s stock flag costs about one origin read every 2 s.
2. **Sold-out flag:** when stock hits 0, the Buy button goes away and the line ends. This is the biggest drop in load, because most buyers can't get a hat anyway.
3. **Waiting room at 20/s,** with the rate as a live knob.
4. **Rate limits and bot rules at the edge:** per IP on checkout, a challenge before the line, and 2 hats per order. Scarce hats attract resellers.
5. **Atomic reserve** (already in V1): no oversell.
6. **Idempotency** (already in V1): a double tap returns the same order, Stripe dedupes on the order id, and the webhook ignores events it has seen.
7. **Stripe guard:** a token bucket in the API, plus backoff with jitter on 429s. If 429s appear, lower the release rate.
8. **Queues for email and warehouse hand-off.** They can lag, but checkout can't.
9. **Connection pooler,** so a burst of instances can't exhaust database connections.

### 5. Go-live checklist

1. **Load test at 3x:** about 50,000 requests/s at the edge and 60/s at checkout, with Stripe mocked using latencies sampled from live calls. Stripe advises against load testing its sandbox. Pass: exactly 20,000 hats sold, stock never negative, 0 double charges, the page stays up, checkout p95 under 800 ms.
2. **Call Stripe today:** ask for a higher limit and warn them about the sale. The plan assumes no increase, and a higher limit just shortens the line.
3. **Pre-scale from the start of post day,** and stay scaled for hours after it. Autoscaling takes minutes, this surge takes seconds, and reposts can bring a second wave.
4. **Kill switches, each tested:** release rate, pause checkout, force sold out, and a static "back soon" page.
5. **Freeze two days before,** with a rollback we've actually run. No deploys on post day.
6. **Dashboards:** CDN hit rate, line length, release rate, stock left, held vs paid, Stripe 429s and errors, webhook lag, outbox backlog, DB latency.
7. **Game day and small real launch:** fake a Stripe outage (stop releasing, keep the line and the page up). Sell 100 hats to employees on live Stripe, end to end, and confirm the warehouse ships them.
8. **Before the post:** confirm the warehouse count, load the real number, and ask whoever controls the post to wait for our green light if they can.

### 6. Wrap-up

**Summary.** The CDN absorbs the reads, including a cached sold-out flag. Stripe's limit sets the real checkout rate, so an always-on waiting room releases 20/s. One Postgres with a conditional update means no oversell, and idempotency keys end to end mean no double charge. An outbox gets every paid order to the warehouse. Go-live is pre-scaling for the whole day, tested kill switches, and a small real launch.

**Trade-offs**

- The line can run about 20 minutes, shorter if Stripe raises our limit.
- About 80,000 of the 100,000 buyers leave without a hat. If the business can make more, a preorder removes the scarcity, so ask them.
- An unpaid hold blocks hats for up to 10 minutes.
- The stock flag can lag 2 s, so a few people learn "sold out" at checkout.
- We depend on one CDN vendor and one region: managed failover and backups, not a second region.

:::

---

## Follow-up drills {#drills}

**TLDR.** Interviewers poke at the design after you draw it. Say the answer in three parts: what happens, what protects you, and what you'd change. Tap each to check yourself.

### 1. "The payment provider is slow, or down."

::: answer
The hold already protects inventory, so nothing oversells while we wait. Every provider call has a timeout (say 5 s) and retries with backoff and the **same** idempotency key, so a retry can't charge twice. A circuit breaker stops calling after repeated failures, and a kill switch pauses new orders with a clear message. Before the sweeper releases an expired hold, it asks the provider whether that payment went through, so a late success never gives away something paid for. Afterward, a reconciliation job compares our orders with the provider's records.
:::

### 2. "Why not DynamoDB? It scales better."

::: answer
It does, and it has conditional writes. But at these numbers (tens of writes a second) I don't need that scale. My core write touches two rows that must change together, which is one ordinary Postgres transaction and a more limited, more expensive transaction in DynamoDB. A single DynamoDB partition also tops out around 1,000 writes/s, so one hot item is still a bottleneck. I'd switch if writes outgrew one Postgres primary, or if access were pure key lookups at huge scale.
:::

### 3. "The spike is 10x bigger. What breaks first?"

::: answer
Name the first thing and why. Usually **not the writes**: they're capped by supply (ovens, seats, stock). What breaks first is the read path: API instances and their database connections. The CDN and a short cache absorb most reads. Next to go is DB connections, so the pooler and connection caps matter. Then I turn on the waiting room flag, so the system behind it sees the traffic it was tested for. The invariants still hold, because they live in the database, not in the capacity plan.
:::

### 4. "The database fails over."

::: answer
Managed Postgres promotes a standby in about 30 to 60 s. During that window, writes fail. The API retries with backoff and the same idempotency keys, so a retry that lands after failover can't duplicate an order. The waiting room or a "try again in a minute" message absorbs users. With synchronous replication to the standby, committed data isn't lost. Our RPO and RTO come from that and from point-in-time backups. We rehearse a failover on game day, so we know the real number.
:::

### 5. "The cache dies."

::: answer
Reads fall through to the database, so the DB has to survive that. A connection cap and load shedding (fast 503s for the excess) protect it, and the CDN still holds the static content. Because the cache was only ever a hint, correctness is untouched: the conditional update in the DB is still the truth. To avoid a stampede when it comes back, one request refreshes each key while others wait or get the stale value.
:::

### 6. "A webhook arrives twice, or late."

::: answer
Twice: we store each provider event id with a unique key and ignore repeats. Late: the order status only moves forward (held, then paid or expired), so a late or out-of-order event can't move it backward. If a payment succeeds after the hold expired, the sweeper already asked the provider before releasing, and the reconciliation job catches anything left over (then we either honor it or refund). The handler checks the signature, returns 200 fast, and does the work asynchronously.
:::

### 7. "One key is hot."

::: answer
In the DB, a hot item is one row, and conditional updates on it run one at a time. Each takes about a millisecond, so that's fine up to a few hundred a second. Past that, split the counter into N bucket rows and pick one at random (sold out only when all are empty), or hand out stock in batches. In the cache, a hot key is fixed by a short local in-memory cache in each API instance (say 1 s), or by replicating the key.
:::

### 8. "It's go-live morning. What are you watching?"

::: answer
**Before:** pre-scale done, CDN hit rate high, flags in the right state, on-call in the room. **During:** error rate, p95 latency, queue depth, and the business metric that matches the invariant: held vs paid (a gap means payments are failing), stock left vs the real world. And a trigger written down in advance: "If errors pass 2% for 2 minutes, I turn on the waiting room."
:::

### 9. "Bots are buying everything."

::: answer
Layers, cheapest first: rate limits per IP at the edge and bot rules in the WAF; a business limit (one per account, phone or card); a waiting room that randomizes everyone who arrived before the start; a CAPTCHA at the waiting room, from a vendor. Afterward, cancel orders that break the rules, because the limit table makes them easy to find. Don't build your own bot detection.
:::

### 10. "Why not microservices and Kubernetes?"

::: answer
Microservices buy independent deploys for many teams. We have two engineers and a few weeks, so they'd buy network calls, distributed failures and more to run, for nothing. One service with clear modules can be split later. Kubernetes is the same: powerful, but someone has to run the cluster. Managed containers give us scaling and rolling deploys without that. I'd revisit with several teams shipping independently.
:::

### 11. "Why not Kafka?"

::: answer
Kafka is a log that many consumers can replay, built for very high throughput. Here I need a to-do list: each job done once, retried on failure, with a dead-letter queue. A managed queue does exactly that with nothing to run. I'd pick Kafka if several consumers needed the same events, we needed replay, or we were at hundreds of thousands of events a second.
:::

### 12. "How exactly does the idempotency key work?"

::: answer
The client makes a random key per user action (not per request) and sends it as a header. The server stores it with a unique constraint, plus a hash of the request body and the response. If the same key comes again, return the stored response, and do nothing new. If the same key comes with a **different** body, return an error, because that's a client bug. If the first request is still running, return "in progress" (409) so the client waits. Keys expire after about 24 hours. We pass our order id to the payment provider as its idempotency key, too.
:::

### 13. "A deploy goes bad in the middle of the event."

::: answer
First, there shouldn't be one: code freeze before the event, no deploys during the window. If an emergency fix is needed, roll back first (to the last good version, which we've practiced) and fix later. Rolling deploys can kill in-flight work, so workers shut down gracefully: finish the job or hand it back to the queue. A canary at 1 to 5% of traffic catches most bad releases before they reach everyone.
:::

### 14. "The queue is backing up."

::: answer
That's the queue doing its job: work waits instead of failing. Check the oldest message's age, not just the depth: does the delay break a promise? If yes, add workers, but only up to what the downstream system can take (DB connections, provider rate limits), or you just move the failure. Pause or deprioritize low-value work (analytics, emails) to make room. If a few messages keep failing, they go to the dead-letter queue after N tries so they don't block the rest.
:::

### 15. "How do you know you won't oversell? Prove it."

::: answer
Two ways. By design: the only path that sells is one conditional UPDATE (`WHERE remaining >= n`) in a transaction, so the database refuses to go below zero, plus a check constraint as a backstop. By test: a load test with 1,000 concurrent buyers for 50 units, run several times. Pass bar: exactly 50 sold, every time, and 0 double charges. Then a reconciliation after the real event: units sold vs stock vs payments.
:::

### 16. "Autoscaling will handle the spike, right?"

::: answer
Not on its own. Container autoscaling reacts in 1 to 5 minutes; a promo spike arrives in seconds. It also doesn't scale the database or raise a provider's rate limit. So for a known event I pre-scale an hour early: instances, DB tier, CDN warm-up, and provider limits raised weeks ahead. Autoscaling stays on as the safety net for whatever the plan missed.
:::

### 17. "What if the whole region goes down?"

::: answer
Start with RPO and RTO. Ask the business: "Is it OK to be down for an hour during a region outage, if we lose no paid orders?" For most small businesses, yes. Then: multi-AZ (cheap, managed), backups copied to another region, and a written restore plan. Full multi-region is expensive and makes the invariants harder (two databases that both sell the same stock). I'd add it only if an hour's outage costs more than running it.
:::

### 18. "The page said 'available', but checkout says sold out. Is that a bug?"

::: answer
No. It's a trade-off I chose. Availability is cached for a few seconds as a hint, so under a spike a few people learn "sold out" at checkout. The alternative, reading live stock on every page view, would send the whole read spike to the database. The fix for the experience is a clear message and an alternative: the next slot, a waitlist, a similar item.
:::

### 19. "The database runs out of connections."

::: answer
Postgres allows a few hundred connections, and each new API instance opens its own pool, so scaling out the API can exhaust it. Fixes: a connection pooler in transaction mode between the API and the DB, a small fixed pool per instance, and short transactions (no provider calls inside a transaction). Separate pools for checkout and browsing, so browsing can't starve checkout. Alert on connection use above 80%.
:::

### 20. "You get half the time. What do you cut?"

::: answer
Keep the invariants and the go-live basics. Cut the features. Keep: the conditional update, idempotency keys, hosted checkout, the CDN, a load test with a pass bar, a pause switch, and a code freeze. Cut: the waiting room (just a flag that shows a "come back later" page), custom dashboards (use the platform's defaults plus 3 alerts), the waitlist, and anything nice to have. Say it out loud: "I'm cutting features, not correctness."
:::
