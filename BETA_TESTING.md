# CIO Clearinghouse — Beta Testing Guide

Thanks for helping beta test the CIO Clearinghouse! This site helps UVA students discover, apply to, and manage Contracted Independent Organizations (CIOs).

Please work through the scenarios below and report anything that breaks, confuses you, or feels off via GitHub Issues (instructions at the bottom).

---

## Getting started

**Live site:** https://uva-cio-clearinghouse-29f66a8d423e.herokuapp.com/

> **Heads up:** Chrome may show a "Dangerous site" warning the first time — that's a false positive from Google Safe Browsing (common for brand-new Heroku domains with login forms). It's safe to proceed: click **Details** → **visit this unsafe site**. Or use Firefox/Safari, which don't flag it.

**How to sign in:** Two options.
1. **Google** — click "Sign in with Google" and use any Google account.
2. **Email/password** — use one of the pre-seeded test accounts below, OR create a new account with "Sign Up".

**Pre-seeded test accounts (all use password `testpass123`):**

> Sign in with the **email address**, not the username — this app only accepts email at login.

| Email                        | Role              | Use for                        |
|-----------------------------|-------------------|--------------------------------|
| member1@virginia.edu        | Prospective       | Scenarios 1, 2, 3, 4, 5        |
| officer1@virginia.edu       | CIO Officer       | Scenario 6                     |
| admin1@virginia.edu         | User Administrator| Scenario 7                     |

> After signing in once, you can sign out from the profile dropdown (top-right) before switching accounts.

---

## Scenario 1 — Sign up as a new member

**Goal:** Verify the sign-up flow works end-to-end.

1. Go to the live site, click **Sign Up**.
2. Enter a username, email, and password. Submit.
3. You should land on the home page, signed in.
4. Open the profile dropdown → **Settings** → fill in your bio, graduation year, and interests. Save.
5. Sign out. Sign back in using the credentials you just made.

**What to report:** Anything that errors out, any field that doesn't save, any weird redirect.

---

## Scenario 2 — Browse & discover CIOs (as `member1`)

**Goal:** Verify discovery features.

1. Sign in as `member1@virginia.edu`.
2. Click **Browse CIOs**. You should see several sample CIOs.
3. Filter by a category (e.g. Service, Technology). Confirm results change.
4. Open a CIO (e.g. HooHacks). Read description, check meeting time, announcements, reviews, upcoming events.
5. Go back to Browse. Use search (if present) to find a CIO by name.

**What to report:** Missing images, broken filters, wrong data, CIOs that won't load.

---

## Scenario 3 — Engage as a prospective member

**Goal:** Verify bookmarks, applications, events, and recommendations.

1. Still signed in as `member1`.
2. From a CIO's page, click **Bookmark**. Go to **Bookmarks** in the nav — the CIO should appear.
3. Find a CIO whose applications are open (e.g. Madison House) and **Apply**. Fill out the form.
4. Click **For You** — the page should show recommendations based on your interests.
5. Click **My Events** — should list any events you've RSVPed to. Open an event from a CIO page and RSVP to test.

**What to report:** Apply form rejects valid input, bookmarks don't persist, recommendations empty when they shouldn't be, RSVP doesn't toggle.

---

## Scenario 4 — Propose a new CIO (gauge interest)

**Goal:** Verify the "Start a CIO" flow.

1. In the nav, click **Start a CIO**.
2. You should see a list of CIO proposals from other students.
3. Upvote one that interests you.
4. Create a new proposal of your own — give it a name, description, and category. Submit.
5. Confirm your new proposal appears in the list.

**What to report:** Vote doesn't register, proposal doesn't save, duplicate-proposal issues.

---

## Scenario 5 — Message a CIO officer

**Goal:** Verify in-app messaging.

1. As `member1`, open a CIO (e.g. HooHacks). Click **Message Officer** (or equivalent button on the CIO page).
2. Send a short message.
3. Sign out. Sign in as `officer1@virginia.edu`.
4. Open **Messages** in the nav — you should see the conversation.
5. Reply.
6. Sign back in as `member1` and confirm the reply appears.

**What to report:** Messages don't send/deliver, you can message yourself, unread counts wrong, conversation sort order wrong.

---

## Scenario 6 — Run a CIO (as an officer)

**Goal:** Verify the officer management workflow.

1. Sign in as `officer1@virginia.edu`. Officer1 already manages HooHacks.
2. Open **HooHacks** → click **Manage CIO**.
3. **Post an announcement:** add a title and body. Save. Confirm it appears on the public CIO page.
4. **Add an event:** go to the Events section, create one with a title, time, location. Confirm it appears.
5. **Upload a photo:** add a photo to the gallery. Confirm it renders (this tests Amazon S3 uploads).
6. **Toggle applications:** close applications, confirm the Apply button disappears for members. Reopen.
7. **Review an application:** if anyone's applied, accept or reject it.
8. **Create a new CIO:** from Browse, click "Create CIO". Fill in the form, submit. You should now manage a second CIO.

**What to report:** Anything that silently fails, uploaded photos that don't render (S3 issue), a form that won't submit.

---

## Scenario 7 — Administer users (as admin)

**Goal:** Verify the User Administrator dashboard.

1. Sign in as `admin1@virginia.edu`.
2. You should land in the Admin Panel automatically — the only page admins can access.
3. You'll see a list of all non-admin users and their current role.
4. Pick a prospective member and **promote** them to officer. Confirm the role changes.
5. Try to visit `/cios/` or `/messages/` directly — you should be redirected back to the admin panel (admins cannot use app features).
6. Sign out.

**What to report:** Admin somehow accessing app features, promotion doesn't save, list missing users you expect to see.

---

## Scenario 8 — Edge cases & polish

**Quick checks — whatever catches your eye:**

- Sign in with wrong password → should error gracefully (not crash).
- Hit a bad URL (e.g. `/cios/not-a-real-cio/`) → should 404, not 500.
- Try accessing `/cios/some-cio/manage/` while signed in as a member (not that CIO's officer) → should be blocked.
- Navigate on mobile (resize your browser) — does the layout hold up?
- Refresh the page mid-form — are you informed gracefully?

---

## Reporting bugs & feedback
1. Click **New Issue**.
2. Pick the **Beta Feedback** template if one is offered (otherwise write freely).
3. Label it `beta-feedback`.
4. Include:
   - Which scenario you were in (e.g. "Scenario 3, step 3")
   - Your browser + device (e.g. "Chrome on macOS", "Safari on iPhone")
   - What you expected vs. what happened
   - Screenshot if possible
   - Severity: 🔴 blocker / 🟡 annoying / 🟢 suggestion

Thanks! Even "this wording is confusing" counts as useful feedback — we'd rather over-hear than miss something.
