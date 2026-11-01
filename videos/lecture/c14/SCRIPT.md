# Replicas and failover: lecture video (component 14)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component fourteen: replicas and failover.
2. `SD` The primary is the one database that takes every write. Replicas are live, read-only copies of it, a fraction of a second behind. A standby is a spare copy that takes over if the primary dies. *(pause)*
3. `SD2` Every managed database offers both: you pick how many replicas, and switch the standby on. *(pause)*
4. `S1` Why do you need them? With one database, checkout and a heavy sales report share it. While the report runs, checkout slows down.
5. `S1b` And if that machine fails, you're down for hours, while someone rebuilds it from a backup. *(pause)*
6. `S2` Here's how it works. Every write goes to one place, the primary. Stock goes from five to four.
7. `S2b` The primary streams a log of its changes to the replicas, which replay it. The delay is called replication lag, usually well under a second. *(pause)*
8. `S3` Reads can go to any replica, so adding replicas adds read capacity. *(pause)*
9. `S4` The standby is kept fully in sync, in another data center. Now the primary's machine dies, and writes start failing.
10. `S4b` The cloud promotes the standby to be the new primary, usually within thirty to sixty seconds. That's failover. The app retries the writes that failed. *(pause)*
11. `S5` So, two uses. Replicas add read capacity, for reports and dashboards.
12. `S5b` And the standby turns a crashed machine from hours of downtime into about a minute. *(pause)*
13. `S6` Now a real case. A bike shop's morning sales report slows down checkout.
14. `S6b` Point the report at a replica, and checkout has the primary to itself. *(pause)*
15. `S6c` Then, at two AM, the primary's machine fails. Without a standby, the shop is down for hours.
16. `S6d` With a standby, it's promoted within a minute. A few writes are retried, and by morning, nobody knows. *(pause)*
17. `S7` Here's where it sits. Orders go to the primary, which keeps the standby in sync. Reports read from a replica. *(pause)*
18. `S8` Two things to know. A replica can be a moment behind, which is fine for a report, but wrong for "is this in stock?"
19. `S8b` And failover is a blip, not zero. The app must retry, and the standby roughly doubles the database bill. *(pause)*
20. `S9` In the interview, say: never read stock you're about to sell from a replica. It can be a moment behind.

## Pronunciation

| On screen | Spoken |
|---|---|
| Multi-AZ | multi A Z |
| API | A P I |
