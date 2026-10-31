# Sweeper and reconciliation jobs: lecture video (component 7)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component seven: sweeper and reconciliation jobs.
2. `SD` These are small programs that run on a timer and clean up. A sweeper releases things that got stuck. A reconciliation job compares your records with an outside source, and fixes any gaps. *(pause)*
3. `SD2` Like closing time at a shop, when you count the till against the receipts. Running a program on a schedule is classically called cron. *(pause)*
4. `S1` Why do you need them? At the pizza shop, checkout puts a hold on the pizzas, then sends the customer to Stripe's payment page.
5. `S1b` Fifty customers abandon that page. Their pizzas stay held, and nobody else can buy them.
6. `S1c` Worse, one customer pays, but Stripe's webhook, the message that says paid, never arrives. That order is never cooked. *(pause)*
7. `S2` The sweeper runs every minute, and finds the holds that have expired.
8. `S2b` Before releasing one, it asks Stripe: was this paid? If not, the pizzas go back on sale. If it was, the order goes to the kitchen. That catches the lost webhook. *(pause)*
9. `S3` Reconciliation is the nightly safety net. It lists Stripe's payments, and compares them with your orders, one by one.
10. `S3b` Here's a payment with no matching paid order. The job marks the order paid, so nothing is left hanging. *(pause)*
11. `S4` You use them for expired holds, on stock, seats or bookings,
12. `S4b` for stuck orders, like one that's been sending for an hour,
13. `S4c` and for matching payments against an outside record. *(pause)*
14. `S5` Now the real case. Kickoff night: fifty customers abandon the Stripe page, and one paid order's webhook is lost.
15. `S5b` Without these jobs, those pizzas stay held all night, and the paying customer never gets dinner.
16. `S5c` With them, within a minute of the holds expiring, all fifty carts are released and back on sale, and the paid order reaches the kitchen. *(pause)*
17. `S6` Here's where it sits: off to the side, on a timer. The jobs read the database and ask Stripe, but no customer ever waits on them. *(pause)*
18. `S7` Two things to know. Run one copy of each job at a time, so two sweepers don't fight over the same hold.
19. `S7b` And make every fix safe to repeat. If a job dies halfway, the next run simply does it again. *(pause)*
20. `S8` In the interview, say: every minute, release expired holds, after asking Stripe whether they were paid.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
