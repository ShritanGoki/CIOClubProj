# User Administrator Role

## What is needed

A third role is needed, separate from the original two, whose only job is managing role assignments — promoting or demoting users between Prospective Member and CIO Officer. It needs to be deliberately boxed in: no profile, no access to any other feature, and no way to create another administrator through the app itself.

## Plan

A third value, `admin`, will be added to `UserProfile.role`. Rather than bolting admin checks onto every existing view, the routing will be inverted: when an admin's profile loads, they'll be redirected straight to a dedicated `user_admin` view instead of the normal profile page, and that view will be the only screen an admin can reach — any other URL will redirect them back out.

The admin dashboard itself will do two things:
- List every non-admin user (`UserProfile.objects.exclude(role='admin')`) with their current role.
- Let the admin reassign a user between `prospective` and `officer` via `change_user_role`, which will explicitly reject any attempt to set a role to `admin` — the Administrator role won't be grantable through the UI at all.

Because admin accounts won't be creatable through sign-up or any in-app flow, they will only exist by being set directly through Django's admin site or a management command — a deliberate gap, not an oversight, so that administrator access stays outside the normal account-creation surface.

This will be layered on top of the existing two-role system without changing how Prospective Member and CIO Officer work — `admin` is just a third branch that short-circuits to its own isolated view before any of the regular app logic runs.
