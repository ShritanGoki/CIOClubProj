# Account Management

## What is needed

Users need to be able to create an account (with a profile) and delete it themselves at any time, and higher-level users need some ability to manage membership (approve, deny, or remove members).

## Plan

Account creation will run through Django login or Google OAuth (see [Authentication & User Roles](01-authentication-and-roles.md)); either path will land the user on `profile_edit` to fill in their bio, picture, graduation year, field of study, and interests.

Self-deletion will be a single confirmation step: `delete_account` will log the user out and delete the `User` row directly, which cascades to the `UserProfile` and everything else tied to it by foreign key (bookmarks, applications, reviews, etc.) — there will be no soft-delete or recovery window, matching the requirement that users can remove their own account outright.

CIO-level membership approval will live with the officer tools rather than as a separate system: officers will accept or reject `Application` rows (see [CIO Discovery & Officer Tools](05-cio-discovery-and-officer-tools.md)), which is the CIO-specific version of "approve/deny users" — approving an application is what makes someone a member of that CIO.
