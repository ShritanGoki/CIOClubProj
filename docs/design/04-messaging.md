# In-App Messaging

## What is needed

Prospective members need a way to reach CIO officers directly without leaving the app, and officers need to be able to reply and follow up — the primary communication channel has to live inside the product, not depend on email.

## Plan

Two models will cover it: `Conversation`, a many-to-many thread between participants, and `Message`, each belonging to one conversation with a sender, body, and timestamp. A `read_by` many-to-many on `Message` will track which participants have seen a given message, which will drive the unread-count badge in the nav.

Starting a conversation will check for an existing one between the same two users first, so messaging the same officer twice doesn't fork into duplicate threads — it will reopen the existing conversation and append to it.

This will be built as the sole primary communication mechanism (direct messages between a member and a CIO's officers), with the option to extend to broader thread/board-style messaging later without changing the underlying `Conversation`/`Message` structure.
