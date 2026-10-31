# System design components: what each one is and when to use it

**TLDR.** Most small-business designs need only about eight parts: CDN, load balancer, a stateless API, one managed Postgres, a cache, a queue with workers, a scheduled job, and a third-party payment provider. Everything else is an answer to a specific number or failure. For each part, know what it is, when to use it, what it costs you, and the one sentence to say in the interview.

Product names are listed as AWS / Azure / GCP / others.

---

## 1. Edge: everything before your servers

| Component | What it is | When to use it | Trade-off / interview line | Products |
|---|---|---|---|---|
| **DNS** | Turns `pizza.com` into an IP address | Always | Low TTL before a launch, so you can redirect traffic fast | Route 53 / Azure DNS / Cloud DNS / Cloudflare |
| **CDN** (content delivery network) | Servers around the world that cache your static files (HTML, JS, images) and serve them close to users | Always for static content; also short-TTL caching of public JSON (menu, catalog) | Cheapest spike defense. Takes most traffic off your API. "Cached content can be stale for up to the TTL." | CloudFront / Azure Front Door / Cloud CDN / Cloudflare, Fastly |
| **WAF** (web application firewall) | Filters bad requests at the edge: bots, SQL injection, known attack patterns | Public sites, launches that attract bots | Can block real users if rules are too strict | AWS WAF / Front Door WAF / Cloud Armor / Cloudflare |
| **DDoS protection** | Absorbs floods of junk traffic | Usually included with the CDN or cloud | Mention it in one line; don't design it | AWS Shield / Azure DDoS Protection / Cloudflare |
| **Rate limiter** | Caps requests per IP, user or API key in a time window (token bucket or sliding window) | Spikes, bots, retry storms, protecting third-party quotas | Edge limits per IP; business limits per account ("2 orders per phone") in the API | WAF rules, API gateway, Redis counters |
| **Waiting room / virtual queue** | Holds users on a "you're in line" page and lets them in at a fixed rate | When demand far exceeds what you can serve (big launches) | Protects everything behind it, but it's a worse experience. Often keep it behind a flag. | Cloudflare Waiting Room, Queue-it, Akamai |
| **API gateway** | One front door for APIs: auth, rate limits, routing, API keys | Many APIs or external developers | Overkill for one small service; a load balancer is enough | API Gateway / Azure API Management / Apigee |
| **Load balancer** | Spreads requests across several API instances and skips unhealthy ones | As soon as you have 2+ instances (always, for availability) | L4 balances TCP connections (fast, simple). L7 understands HTTP (routes by path, ends TLS). Usually pick L7. | ALB, NLB / Azure Load Balancer, App Gateway / Cloud Load Balancing |
| **Reverse proxy** | A server in front of your app that handles TLS, compression and routing | Often built into the load balancer or platform | Nginx and Envoy are the classics | Nginx, Envoy, Traefik |

---

## 2. Compute: where your code runs

| Component | What it is | When to use it | Trade-off / interview line | Products |
|---|---|---|---|---|
| **API service (stateless)** | Your backend: handles requests, keeps no user state in memory, so any instance can serve any request | Always | "Stateless, so I scale it by adding instances." State goes in the DB or cache. | Any web framework |
| **Monolith (modular)** | One deployable service with clear internal modules | Small teams, short timelines: the default | Simple to build, deploy and debug. Splitting later is fine. | |
| **Microservices** | Many small services, each owning its own data | Large teams that need to deploy independently | Network calls, distributed failures, more ops. Usually the wrong answer for a small business. | |
| **Managed containers** | Run Docker images without managing servers or a cluster | Default hosting for an API and workers | Good middle ground. Scale-out takes 1 to 5 minutes. | ECS Fargate / Azure Container Apps / Cloud Run |
| **Kubernetes** | A cluster that schedules containers | Many services, a platform team | Powerful, but heavy to run. Say why you're *not* using it. | EKS / AKS / GKE |
| **Serverless functions** | Code that runs per event; you pay per call | Spiky, short tasks; webhooks; glue code | Cold starts; concurrency limits (AWS: 1,000 per region by default); time limits | Lambda / Azure Functions / Cloud Functions |
| **Autoscaling** | Adds or removes instances based on CPU, requests or queue depth | Gradual traffic changes | **Too slow for a 5-minute surge.** That's why you pre-scale before a known event. | Built into each platform |
| **Background worker** | A process that pulls jobs from a queue and does slow work | Emails, SMS, image processing, report generation | Scale on queue depth. Make jobs idempotent, since they may run twice. | Same platforms as the API |
| **Scheduled job (cron)** | Code that runs on a timer | Nightly reports, cleanup, reconciliation | Make sure only one copy runs at a time (a lock or a single-instance job) | EventBridge Scheduler / Container Apps jobs, Logic Apps / Cloud Scheduler |
| **Sweeper job** | A scheduled job that finds stale state and fixes it: expired holds, stuck orders, abandoned carts | Any design with holds, reservations or timeouts | "Every minute, release holds past their expiry. Before releasing, check the provider in case payment succeeded." | A cron job plus a DB query on an indexed `expires_at` |
| **Reconciliation job** | Compares your records with the outside source of truth (Stripe, bank) and fixes gaps | Anything involving money or external state | Catches lost webhooks and partial failures. "Trust, but reconcile." | Scheduled job |

---

## 3. Databases

### 3a. Which kind of database

| Type | What it is | Good for | Weak at | Products |
|---|---|---|---|---|
| **Relational (SQL)** | Tables with rows, joins, **ACID transactions**, constraints | Orders, payments, inventory, users: anything where correctness matters. **The default.** | Huge write scale on one primary (you shard by hand) | Postgres, MySQL / RDS, Aurora / Azure Database for PostgreSQL / Cloud SQL |
| **Key-value** | Get and put by key, very fast, scales horizontally | Sessions, carts, counters, simple lookups at huge scale | Queries other than by key; multi-item transactions are limited | DynamoDB / Cosmos DB / Bigtable; Redis |
| **Document** | Stores JSON documents, flexible schema | Content, catalogs, data whose shape varies | Joins, strict cross-document consistency | MongoDB / Cosmos DB / Firestore |
| **Wide-column** | Huge tables partitioned by key, built for writes | Time series, event logs, massive write volume | Ad-hoc queries, transactions | Cassandra, ScyllaDB / Bigtable |
| **Search engine** | Inverted index for full-text and filtered search | Product search, log search | Being the source of truth; it's eventually consistent | Elasticsearch, OpenSearch / Azure AI Search |
| **Time-series** | Optimized for timestamped metrics | Monitoring, IoT | General app data | Prometheus, InfluxDB, TimescaleDB |
| **Graph** | Nodes and edges | Social graphs, recommendations | Most business apps | Neo4j / Neptune / Cosmos DB Gremlin |
| **Object storage** | Files (blobs) by key, nearly unlimited, cheap | Images, videos, exports, backups, recordings | Querying, small frequent updates | S3 / Azure Blob Storage / GCS |
| **Data warehouse** | Columnar store for analytics over large data | Reports, dashboards, BI | Serving live user requests | Redshift / Synapse, Fabric / BigQuery; Snowflake |

**Interview line for picking Postgres:** "My core write touches two rows that must change together, and Postgres does that in one transaction. At N writes a second it fits on one instance. I'd consider DynamoDB if writes grew past what one primary handles or I needed single-digit-ms reads at huge scale."

**Interview line for DynamoDB:** "Great at massive scale with predictable key lookups, and it has conditional writes. But each partition is limited (about 1,000 writes/s), so one hot item is a bottleneck, and multi-item transactions cost more and have limits."

### 3b. Database concepts to know

| Concept | What it is | Why it matters |
|---|---|---|
| **ACID transaction** | Several changes that all happen or none do (Atomic, Consistent, Isolated, Durable) | "Reserve inventory and create the order in one transaction." |
| **Isolation levels** | How much concurrent transactions see each other (read committed, repeatable read, serializable) | Default read committed is fine if you use conditional updates or row locks |
| **Index** | A sorted lookup structure on a column | Every query in the hot path needs one. The sweeper needs one on `expires_at`. |
| **Unique constraint** | The DB rejects duplicate values | Idempotency keys, "one booking per seat per time slot" |
| **Primary / replica** | Writes go to the primary; replicas copy it for reads | Scale reads, survive failure. Replicas lag slightly, so never read inventory you're about to sell from a replica. |
| **Failover** | A replica is promoted when the primary dies | Managed DBs do it in about 30 to 60 s. Clients must retry. |
| **Sharding / partitioning** | Split data across several DBs by a key | Only when one primary can't keep up. Hard to undo; avoid in V1. |
| **Connection pooling** | A pooler holds a small set of DB connections shared by many app instances | Postgres allows only a few hundred connections. Without a pooler, scaling out the API exhausts the DB. |
| **Backups / point-in-time restore** | Restore the DB to any moment in the last N days | Defines your RPO |
| **RPO / RTO** | RPO: how much data you can lose. RTO: how long you can be down. | "RPO 5 minutes, RTO 1 hour" makes multi-region a choice you can argue, not a default. |
| **CAP / consistency** | In a network split, a distributed system chooses between consistency and availability | Money and inventory need strong consistency; likes and view counts can be eventual |
| **Eventual consistency** | Readers may see old data for a short while | Fine for caches, search and counters; never for "is this seat taken" |

---

## 4. Caching

| Concept | What it is | Note |
|---|---|---|
| **Cache** | A fast copy of data, usually in memory | Cuts DB reads and latency. Never the source of truth for money or inventory. |
| **In-memory store** | Redis (data structures, persistence, atomic ops) or Memcached (simple, pure cache) | Redis is the usual pick. Products: ElastiCache / Azure Cache for Redis / Memorystore. |
| **Cache-aside** | The app checks the cache, on a miss reads the DB and fills the cache | The most common pattern |
| **Write-through** | Every write updates the DB and the cache together | Fresher cache, slower writes |
| **TTL** | How long a cached value lives | Short TTL (1 to 5 s) during a spike is a big win with little staleness |
| **Invalidation** | Removing a cached value when the data changes | Hard. A short TTL is often simpler. |
| **Cache stampede** | A popular key expires and thousands of requests hit the DB at once | Fixes: one request refreshes while others wait (request coalescing), or serve stale while refreshing |
| **Hot key** | One key gets most of the traffic | Replicate it, or cache it locally in each API instance for a second |
| **Local (in-process) cache** | Cache in the API's own memory | Fastest, but each instance has its own copy |

---

## 5. Async: queues, streams and events

| Component | What it is | When to use it | Products |
|---|---|---|---|
| **Message queue** | A list of jobs; workers take one, do it, and delete it | Non-urgent work (emails, SMS), smoothing bursts, job processing | SQS / Azure Service Bus, Storage Queues / Cloud Tasks, Pub/Sub; RabbitMQ |
| **Log / stream** | An append-only log many consumers can read and replay | Event sourcing, analytics pipelines, very high throughput, replays | Kafka / Kinesis / Event Hubs / Pub/Sub |
| **Pub/sub** | One message, many subscribers | Fan-out: "order paid" goes to the kitchen, email and analytics | SNS / Event Grid, Service Bus topics / Pub/Sub |
| **Dead-letter queue (DLQ)** | Where messages go after N failed attempts | Always pair it with a queue, and alert on DLQ depth | Built into most queues |
| **At-least-once delivery** | The queue may deliver a message twice | So consumers **must be idempotent** | |
| **Exactly-once** | Mostly a myth end to end | Say: "at-least-once delivery plus idempotent consumers" | |
| **Backpressure** | Slowing producers when consumers can't keep up | Queue depth as a signal; cap worker concurrency so downstream systems survive | |
| **Outbox pattern** | Write the event to an `outbox` table in the same DB transaction, and a relay publishes it | Avoids "DB committed but the message was never sent" | |

**Queue vs stream, in one line:** "A queue is a to-do list where each job is done once. A stream is a log that many readers can replay. For sending texts I need a queue, not Kafka."

---

## 6. Correctness patterns (the invariants)

| Pattern | What it is | Example |
|---|---|---|
| **Atomic conditional update** | Change a row only if a condition holds, in one statement | `UPDATE slots SET reserved = reserved + 2 WHERE id = 7 AND reserved + 2 <= capacity`. 0 rows updated means sold out. |
| **Pessimistic lock** | Lock the row while you work: `SELECT ... FOR UPDATE` | When the logic is too complex for one statement. Keep the transaction short. |
| **Optimistic lock** | Read a version number, update only if it hasn't changed, retry otherwise | Low contention, such as editing a profile |
| **Holds / reservations with expiry** | Reserve the inventory first, pay within N minutes, a sweeper frees expired holds | Seats, limited stock, time slots |
| **Idempotency key** | A unique id per user action. Repeating the request returns the first result instead of doing it again. | Client sends `Idempotency-Key`; unique constraint in the DB; same key passed to Stripe |
| **Webhook dedupe** | Store each provider event id; ignore repeats | Stripe can send the same event more than once |
| **State machine** | A status that only moves forward: held, then paid or expired | A late or duplicate event can't move an order backward |
| **Saga** | A multi-step process where each step has an undo step | Booking a flight and a hotel; refund if the second step fails |
| **Distributed lock** | A lock shared across machines (Redis, ZooKeeper) | Usually avoid. A DB constraint or conditional update is simpler and safer. |
| **Reconciliation** | Periodically compare with the source of truth and fix gaps | Nightly or every few minutes against Stripe |

---

## 7. Third-party services

| Service | What it does | What to know | Products |
|---|---|---|---|
| **Payment provider** | Charges cards, handles fraud checks, 3-D Secure and payouts | **Hosted checkout** keeps card data off your servers (much smaller PCI scope). Flow: create a session or PaymentIntent, user pays on the provider's page, the provider sends a **webhook**. Use **idempotency keys** on every call. **Test mode** for load tests. Rate limit about 100 requests/s by default in live mode; ask to raise it before a launch. | Stripe, Adyen, Square, PayPal |
| **Webhook** | The provider calls *your* URL when something happens | Verify the signature, return 200 fast, process async, dedupe on event id, and expect it late or twice | |
| **SMS / voice** | Sends texts and calls | Per-number and per-account rate limits; carrier filtering; async plus retries | Twilio, Azure Communication Services, Vonage |
| **Email** | Sends transactional email | Async, with retries; watch bounces | SendGrid, SES, Postmark |
| **Auth / identity** | Login, OAuth, social sign-in, tokens | Don't build your own. Guest checkout often skips login entirely. | Auth0, Cognito, Entra ID, Firebase Auth |
| **Feature flags** | Turn features on or off at runtime without a deploy | Kill switches, staged rollouts, waiting room toggle | LaunchDarkly, Azure App Configuration, Unleash, or a DB table |
| **Maps / geo** | Addresses, distance, delivery zones | Cache results; per-call cost | Google Maps, Mapbox, Azure Maps |

---

## 8. Reliability patterns

| Pattern | What it is | Interview line |
|---|---|---|
| **Timeout** | Give up on a call after N ms | "Every outbound call has a timeout. The default is often infinite." |
| **Retry with exponential backoff and jitter** | Retry after 100 ms, 200, 400..., with randomness | Jitter stops all clients retrying at the same instant. Retry only idempotent calls. |
| **Circuit breaker** | After repeated failures, stop calling a dependency for a while and fail fast | Protects your threads and the struggling dependency |
| **Bulkhead** | Separate resource pools per dependency | A slow Stripe can't eat all the threads checkout needs |
| **Graceful degradation** | Turn off non-essential features under load | Hide photos, recommendations, the live status page |
| **Load shedding** | Reject some requests early (HTTP 429/503) to keep the rest fast | Better than everyone timing out |
| **Kill switch** | A flag that turns off a feature instantly | "Pause new orders" when payments are down |
| **Health checks** | The load balancer pings `/health` and removes bad instances | Liveness (is it running) vs readiness (can it take traffic) |
| **Multi-AZ** | Instances in several data centers in one region | Cheap and usually managed: do it |
| **Multi-region** | A full copy in another region | Expensive and complex. Justify with RTO/RPO, or say no. |
| **Pre-scaling / pre-warming** | Scale up before a known event | Autoscaling reacts in minutes; a promo spike arrives in seconds |

---

## 9. Observability

| Component | What it is | Products |
|---|---|---|
| **Metrics** | Numbers over time: request rate, errors, latency, queue depth | Prometheus, CloudWatch, Azure Monitor, Datadog |
| **Logs** | Event records; structured JSON is searchable | CloudWatch Logs, Log Analytics, ELK |
| **Traces** | One request followed across services, with timings | OpenTelemetry, X-Ray, Application Insights |
| **Dashboards** | The metrics you watch on launch day | Grafana, Azure dashboards, Datadog |
| **Alerts** | Page someone when a metric crosses a threshold | PagerDuty, Opsgenie, Azure Monitor alerts |
| **Percentiles** | p50 = typical, p95 / p99 = the slow tail | "p95 under 500 ms" beats "average 200 ms" |
| **Golden signals** | Latency, traffic, errors, saturation | The default dashboard |
| **Business metrics** | Orders/min, held vs paid, inventory left | Often the first sign something is wrong |
| **SLI / SLO / error budget** | SLI: a measured indicator. SLO: the target (99.9%). Error budget: how much failure is allowed. | "Our SLO is 99.9% of checkouts under 1 s during the event." |
| **Runbook** | A written "if this alert fires, do this" | Every alert gets an owner and a runbook entry |

---

## 10. Release and launch operations

| Practice | What it is | Note |
|---|---|---|
| **CI/CD** | Automatic build, test and deploy on merge | GitHub Actions, Azure DevOps |
| **Rolling deploy** | Replace instances a few at a time | The default on most platforms. Kills in-flight work unless shutdown is graceful. |
| **Blue-green** | Run the new version next to the old and switch traffic at once | Instant rollback by switching back |
| **Canary** | Send 1 to 5% of traffic to the new version first and watch metrics | Catches bad releases early |
| **Rollback** | Return to the last good version | Only real if you've practiced it |
| **Code freeze** | No deploys for a window around the event | "Nothing ships during the game." |
| **Load test** | Simulate expected traffic at 2 to 3x the peak | k6, Locust, JMeter, Azure Load Testing. Needs a pass bar. |
| **Game day** | A rehearsal: run the load test, flip every switch, fake an outage | Finds the gaps in the runbook |
| **Chaos testing** | Kill things on purpose to see what breaks | A game day is the small-business version |
| **Capacity planning** | The math from peak load to instance counts and DB size | Your back-of-envelope numbers, written down |

---

## 11. Security basics (one line each in an interview)

| Topic | What to say |
|---|---|
| **TLS** | HTTPS everywhere, ended at the load balancer or CDN |
| **Authn vs authz** | Authentication = who you are; authorization = what you're allowed to do |
| **Secrets** | Keys in a secrets manager (Key Vault, Secrets Manager), never in code |
| **PCI** | Hosted checkout keeps card data off your servers, which shrinks PCI scope a lot |
| **PII** | Store as little as possible; encrypt at rest (managed DBs do it by default) |
| **Least privilege** | Each service gets only the permissions it needs (managed identities) |

---

## 12. The pizza-shop design, mapped to these parts

| Part | Used for |
|---|---|
| CDN | Static site, photos, menu JSON cached 30 s |
| WAF + rate limits | Per-IP limits at the edge; 2 orders per phone in the API |
| Waiting room | Behind a flag, off by default |
| Load balancer + stateless API | 2 instances normally, pre-scaled for the game |
| Managed Postgres | Menu, slots, orders; conditional update guards capacity |
| Connection pooler | Keeps scaled-out API instances from exhausting Postgres |
| Cache | Slot availability, 2 s TTL |
| Stripe hosted checkout + webhooks | Payment, with idempotency keys and event-id dedupe |
| Queue + worker | Confirmation texts and emails |
| Sweeper job | Releases expired holds, after checking Stripe |
| Feature flags | Pause orders, waiting room, hide photos, close a slot |
| Dashboards + alerts | Errors, p95, held vs paid, slots left, Stripe errors, DB connections |

See the [Framework](index.html) page for how to run the 60 minutes.
