# Authentication & User Roles

## What is needed

The app needs a login system that doesn't require every user to create a new password, plus a way to distinguish between two kinds of users with meaningfully different capabilities: people browsing for a CIO to join, and people running one.

## Plan

Google OAuth login will be integrated using `django-allauth`, configured as a social account provider alongside Django's own username/password login. Both paths will funnel into the same `User` model, so an account created with email/password and one created via Google resolve to the same user if the emails match — there will be no split between "Google users" and "local users."

A `UserProfile` model will be added as a one-to-one extension of Django's built-in `User`, holding:
- `role` — one of `prospective`, `officer`, or `admin`
- `bio`, `profile_picture`, `graduation_year`, `field_of_study`
- `interests` — a many-to-many link to CIO categories, to be used later for recommendations

Every profile will be created lazily the first time a user logs in (`ensure_profile`), defaulting to the `prospective` role, so there's no separate "pick your role" step during signup — users start as prospective members and get promoted to officer when they create or get added to a CIO.

The two roles will diverge in practice, not just in a database field:
- **Prospective Member** gets the discovery-oriented UI — browse, filter, search, bookmark, apply.
- **CIO Officer** gets management views scoped to the CIOs they officer — creating/editing a CIO, posting announcements, reviewing applications, viewing analytics.

Role checks will be implemented as properties on `UserProfile` (`is_officer`, `is_prospective`, `is_admin`) rather than scattered string comparisons, so view logic reads as `if profile.is_officer` instead of `if profile.role == 'officer'`.
