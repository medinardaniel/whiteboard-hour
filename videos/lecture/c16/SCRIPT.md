# Pre-scaling: lecture video (component 16)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component sixteen: pre-scaling.
2. `SD` Pre-scaling is a practice, not a product. You add server copies and upgrade the database before a spike you know is coming, instead of waiting for the system to react. *(pause)*
3. `SD2` You can do it by hand, from a checklist, or set it up as a scheduled scaling rule in your cloud. *(pause)*
4. `S1` Why not just rely on autoscaling? Autoscaling means the cloud watches a number, like CPU, and adds copies when your servers get busy.
5. `S1b` But it's slow on purpose. It waits until servers have been busy for a few minutes, so it doesn't react to a blip. Then new copies take minutes to boot and pass health checks.
6. `S1c` Meanwhile, the spike is already here, and customers see errors. The new copies arrive too late. *(pause)*
7. `S2` Pre-scaling flips the order. You know when the spike is coming, so you get ready an hour before.
8. `S3` Add server copies, say from two to six.
9. `S3b` Upgrade the database to a bigger size. That often means a short restart, so do it early, in a quiet hour.
10. `S3c` Warm the CDN, so your busiest pages are already cached.
11. `S3d` And keep autoscaling on, as a safety net, in case the spike is bigger than you planned. *(pause)*
12. `S5` Use it for any spike you can see coming: a sale you scheduled, an email to every customer, a TV mention or a big game. *(pause)*
13. `S6` Now a real case. The snow forecast airs on the six PM news, and tire shop traffic jumps twenty times in two minutes.
14. `S6b` Without pre-scaling, autoscaling notices the busy servers at six oh six, and new copies are ready at six oh nine. That's four minutes of errors, at the worst possible moment. *(pause)*
15. `S6c` With pre-scaling, at five PM the shop goes from two copies to six, upgrades the database, and warms the CDN. The spike arrives at six oh five, and the system is already sized. *(pause)*
16. `S7` This applies to every busy part: more API copies, a bigger database, a warm CDN. Workers scale too, but on queue length, not CPU. *(pause)*
17. `S8` Two trade-offs. You pay for idle copies for a few hours. That's cheap next to four minutes of errors.
18. `S8b` And it only works for spikes you can see coming. Surprises still need autoscaling, rate limits and a waiting room. *(pause)*
19. `S9` In the interview, say: autoscaling reacts in minutes. The spike arrives in seconds.

## Pronunciation

| On screen | Spoken |
|---|---|
| CDN | C D N |
| API | A P I |
| CPU | C P U |
