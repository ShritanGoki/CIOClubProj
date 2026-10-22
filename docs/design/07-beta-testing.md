# Beta Testing

## What is needed

Before calling the app done, real people need to exercise every workflow — sign-up, discovery, applying, messaging, officer management, and admin role management — to catch bugs and confusing flows that wouldn't show up from just reading the code.

## Plan

A `seed_data` management command will populate the database with sample users covering every role (prospective member, officer, admin), sample CIOs, events, announcements, and reviews, all under a shared test password — so testers can sign in and immediately exercise real workflows instead of building up data from scratch.

A beta testing guide (see [BETA_TESTING.md](../../BETA_TESTING.md)) will be written with eight scenarios, one per major workflow: sign-up, discovery/browsing, bookmarking and applying, proposing a new CIO, messaging an officer, running a CIO as an officer, administering users, and a sweep of edge cases (bad URLs, wrong permissions, mobile layout). Each scenario will name the account to sign in as and what to check, so feedback comes back scoped to a specific step rather than a vague "something's broken."

Bug reports and feedback will be tracked as GitHub Issues using a dedicated issue template (`.github/ISSUE_TEMPLATE/beta-feedback.md`) capturing the scenario, expected vs. actual behavior, browser/device, and severity — which will keep beta feedback in the same place as the rest of the project's issue tracking rather than scattered across chat threads.
