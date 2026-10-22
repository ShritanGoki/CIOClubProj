# CIO Discovery & Officer Tools

## What is needed

The core of the product: prospective members need to be able to find CIOs that fit their interests and availability, and officers need tools to present their CIO well and run its membership pipeline.

## Plan

The `CIO` model will hold everything a prospective member filters on up front — `category`, `membership_type` (open vs. application-based), `time_commitment`, `meeting_day`/`meeting_time`, `dues`, and `application_deadline` — so the browse view can support search, category filtering, membership-type filtering, time-commitment filtering, and sorting entirely as query-set filters on existing fields, without a separate search index.

A `Bookmark` model (one row per user/CIO pair) will back the "Interested" feature and the Bookmarks page. `GaugeInterest` and its `votes` many-to-many will support the "Start a CIO" flow — someone can post an idea before a CIO formally exists and gauge whether there's enough traction to found it.

For officers, a CIO's management surface will cover:
- **Membership pipeline** — `Application` (with `pending`/`accepted`/`rejected` status and a `reviewed_by` audit trail) and `Officer` (linking a user to a CIO with their own role, supporting multiple officers per CIO).
- **Content** — `Announcement` (with a `pinned` flag for highlighting), `CIOPhoto` for the gallery, and `CIODocument` for persistent file storage that survives leadership turnover.
- **Events** — a separate `Event` model (own app) tied to a CIO, with `is_upcoming`/`is_past` derived from `start_time` rather than a stored flag, so events age out automatically instead of needing manual cleanup.
- **Analytics** — `ProfileView` will log each visit to a CIO's page (with `viewer` nullable so anonymous views still count), giving officers a lightweight view-count metric without a separate analytics service.

`Review` (rating + text, one per user per CIO via a unique-together constraint) will round out the member-facing trust signals on a CIO's page — testimonials from current and past members, visible to anyone evaluating whether to apply.
