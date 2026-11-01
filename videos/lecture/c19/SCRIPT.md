# Flags and kill switches: lecture video (component 19)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component nineteen: flags and kill switches.
2. `SD` A feature flag is a setting you flip while the site is running, with no code release. A kill switch is a flag for emergencies: it turns something off, fast. *(pause)*
3. `SD2` Your app re-reads the flags every few seconds, from a database table or a config service. So a flip takes effect in seconds. *(pause)*
4. `S1` Why does that matter? Without a switch, changing what the site does means changing code. You write it, review it, test it and release it, in the middle of an incident.
5. `S1b` That's twenty minutes or more of failed checkouts, at the worst possible moment. *(pause)*
6. `S2` A flag is just a named setting, like pause orders, stored outside your code. Every API copy reads it every few seconds.
7. `S3` The code checks it before it acts. If orders are paused, show a friendly message instead of the order button.
8. `S3b` You flip it in an admin page. Seconds later, every copy has the new value, and the button changes. Orders that are already paid still finish. *(pause)*
9. `S3c` A kill switch turns off an extra, like photos, so the core keeps working. That's called graceful degradation. *(pause)*
10. `S5` So install your switches before the event. Pause orders when payments fail. A waiting room when traffic is too much. Hide photos when the database is busy. Close a time slot when the ovens are full. *(pause)*
11. `S6` Now game day at the pizza shop. At four ten PM, payment errors spike.
12. `S6b` Without a switch, someone writes, reviews and releases a fix mid-incident. Twenty minutes or more of failed checkouts.
13. `S6c` With one, you flip pause new orders. Seconds later, the button says paused for a few minutes, and paid orders keep flowing.
14. `S6d` At four twenty-five, payments recover, and you flip it back. Later, if the database gets busy, you flip hide photos. *(pause)*
15. `S7` Here's where it sits. The flags live in a small table, and every API copy reads them every few seconds.
16. `S7b` Flipping one changes what the API does. Nothing is deployed. *(pause)*
17. `S8` Two things to know. Test every switch: one that nobody has flipped may not work when you need it. So flip each one on game day.
18. `S8b` And clean them up after the event, because old flags pile up and make the code hard to follow. *(pause)*
19. `S9` In the interview, say: every switch is tested on game day.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| PM | P M |
