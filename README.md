# CIO Clearinghouse

> **Tech Stack:** Python 3 · Django · PostgreSQL · Heroku · Amazon S3 · GitHub Actions CI

## Overview

Many student organizations at universities operate as **Contracted Independent Organizations (CIOs)** — student-run groups that are independent of the university but can access benefits like reserving meeting space, requesting storage, advertising at activities fairs, and applying for activity-fee funding. Because CIOs are student-run, day-to-day operations (member communication, tracking participation, managing documents, coordinating events, and handling leadership turnover) fall entirely on student officers.

**CIO Clearinghouse** is a platform where CIO leaders can create and post their organization so prospective members can search, filter, and apply to join, with officer tools for managing applications, announcements, events, and membership.

## Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Language       | Python 3                             |
| Framework      | Django (Django templates)            |
| Database       | PostgreSQL (production & CI), SQLite (local dev) |
| CI/CD          | GitHub Actions                       |
| Hosting        | Heroku                               |
| File Storage   | Amazon S3                            |
| UI             | Django templates + Bootstrap         |

## User Roles

- **Prospective Member** — Browses, searches, filters, bookmarks, and applies to CIOs.
- **CIO Officer** — Creates and manages a CIO profile, posts announcements, manages applications, views analytics, and assigns officer roles.
- **User Administrator** — Manages user role assignments only. Cannot access any other app feature, maintain a profile, or grant the Administrator role to anyone. Created only through Django's admin tools, never through the app UI.

All users authenticate via Google login (Django login is also available and links to the same account). Basic users maintain a profile with a picture and other information.

## Features

### Prospective Member
- Sort and filter CIOs by time commitment or meeting time
- Filter by category (Professional, Service, Academic, Recreational, etc.)
- Search CIOs by name
- Bookmark CIOs as "Interested"
- View a calendar of past and upcoming events per CIO
- Contact CIO officers via in-app messaging
- View officer contact info and names/roles
- Filter by open vs. application-based membership
- See dues, deadlines, and other requirements up front
- Get personalized CIO recommendations based on interests
- Read testimonials and reviews from members

### Current Member
- Receive reminders for joined/bookmarked CIOs
- See an aggregated view of upcoming events across joined/interested CIOs

### CIO Officer
- Display photos and videos on the CIO profile
- Post announcements and newsletters
- Post interest meetings / info sessions ahead of recruitment
- Edit or remove outdated events
- Toggle whether applications are open or closed
- View profile view analytics
- Send follow-up messages to interested prospects
- Store CIO documents persistently until explicitly deleted
- Assign officer roles to other accounts within the CIO

### Starting a CIO
- Gauge interest for a new CIO idea before committing
- Step-by-step guide for how to start a CIO

### User Administrator
- View all users and their current role
- Reassign a user between Prospective Member and CIO Officer
- Restricted to the admin dashboard — no profile, no other app features, cannot grant the Administrator role

## Design Docs

See [docs/design/](docs/design/) for the plan behind how each part of the system is designed and built.
