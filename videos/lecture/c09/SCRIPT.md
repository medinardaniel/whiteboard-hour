# Holds that expire: lecture video (component 9)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component nine: holds that expire.
2. `SD` A hold is a pattern for selling something you can run out of. You reserve the item first, and take payment second. If the payment doesn't arrive in time, the hold expires, and the item goes back. *(pause)*
3. `SD2` Think of a store setting an item aside for ten minutes while you get your wallet. *(pause)*
4. `S1` Why not just charge first? A customer picks two pizzas for the six o'clock slot, and pays.
5. `S1b` Meanwhile, other orders filled the slot. Now you've taken money for pizza you can't make. That's a refund, and an angry customer. *(pause)*
6. `S2` So flip the order. Step one: reserve. Two of the slot's hundred and fifty pizzas are held, and the hold expires in ten minutes. *(pause)*
7. `S3` Step two: the customer pays on Stripe's page. Stripe sends your server a webhook, a message saying the payment went through. The hold flips to paid, and the kitchen gets the order. *(pause)*
8. `S4` But say another customer walks away. Ten minutes pass with no payment.
9. `S4b` A sweeper, a small job that runs every minute, asks Stripe whether it was paid, just in case. It wasn't, so the hold expires, and the two pizzas go back to the slot. *(pause)*
10. `S5` These statuses form a state machine: a fixed set of statuses, and fixed moves between them. Held can become paid, or expired.
11. `S5b` And it only moves forward. So a late message from Stripe can't turn a paid order back into held. *(pause)*
12. `S6` Use it for anything you reserve before payment: time slots, seats at a show, a hotel room. *(pause)*
13. `S7` Now a real case. Game night at a pizza shop. The six o'clock slot fits a hundred and fifty pizzas.
14. `S7b` Charge first, and in the rush, payments for a hundred and sixty go through. Ten pizzas get refunded.
15. `S7c` Hold first, and the hold itself is a conditional update, so it stops at a hundred and fifty. The next order sees slot full before paying. *(pause)*
16. `S8` Here's where it sits. The API writes the hold to Postgres, then sends the customer to Stripe.
17. `S8b` Stripe's webhook marks it paid, and the sweeper job expires the rest, every minute. *(pause)*
18. `S9` Two things to know. Pick the hold time with care. Too short, and slow payers lose their slot. Too long, and stock sits locked up.
19. `S9b` And a payment can still land just after a hold expires. If the slot is gone by then, refund it automatically. *(pause)*
20. `S10` In the interview, say: hold, then charge, so we never take money for something we can't deliver.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
