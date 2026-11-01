# Hosted checkout + webhooks: lecture video (component 17)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component seventeen: hosted checkout and webhooks.
2. `SD` Hosted checkout is a pattern for taking payments. Customers pay on the payment provider's own page, not yours. The provider then calls your server, with a webhook, to say the payment worked. *(pause)*
3. `SD2` With Stripe, that's Stripe Checkout. You never build a card form at all. *(pause)*
4. `S1` Why not build your own card form? Then card numbers pass through your servers, and maybe into your logs and database.
5. `S1b` Anything that touches card numbers falls under PCI, the card industry's security rules. That means heavy audits for every server involved. *(pause)*
6. `S2` Instead, when the customer clicks pay, your server asks Stripe for a checkout session, with the order and amount. Stripe answers with a link.
7. `S2b` The browser is redirected to Stripe's page, and the customer types their card there. The card number never touches your servers. *(pause)*
8. `S3` When the payment succeeds, Stripe calls your server. That's a webhook: the provider calling a web address of yours when something happens.
9. `S3b` Why not just trust the redirect back to your site? The customer might close the tab first. The webhook comes either way. *(pause)*
10. `S4` Your webhook handler first checks the signature, proof the message came from Stripe. Then it saves the event's id.
11. `S4b` It marks the order paid, and replies OK fast. Slow work, like texting the customer, goes on a queue for later. *(pause)*
12. `S5` Use it for every payment. Refunds and disputes arrive as webhooks too, so the same handler covers them. *(pause)*
13. `S6` Now a real case: order forty-two, twenty-four dollars, at the pizza shop. The server creates a checkout session, and the customer pays on Stripe's page.
14. `S6b` Stripe sends the webhook: event one, order forty-two paid. The server marks it paid, and replies OK.
15. `S6c` Later, the same event arrives again. Its id is already saved, so it's ignored. Without that check, the kitchen could cook the order twice. *(pause)*
16. `S7` Here's where it sits: the API talks to Stripe, the customer pays on Stripe's page, and the webhook comes back. *(pause)*
17. `S8` Two things to know. Webhooks can repeat and arrive late, so ignore known ids, and never assume their order.
18. `S8b` And Stripe has rate limits, about a hundred requests a second by default. Ask for more before a big launch. *(pause)*
19. `S9` In the interview, say: card data never touches our servers, which shrinks our PCI scope.

## Pronunciation

| On screen | Spoken |
|---|---|
| PCI | P C I |
| API | A P I |
