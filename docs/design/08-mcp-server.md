# MCP Server (AI Assistant Access)

## What is needed

AI assistants (like Claude) need a way to look up CIOs — searching by name, category, meeting day, or membership type, and pulling full details for one — without scraping the website or needing API credentials. This should expose the same public data a prospective member sees browsing the site, nothing from behind a login.

## Plan

A standalone `mcp_server.py` will sit at the project root alongside `manage.py`, calling `django.setup()` the same way `manage.py` does so it can use the existing Django ORM and models directly rather than duplicating query logic.

It will expose three read-only tools via the Model Context Protocol:
- `list_categories` — every CIO category and its slug.
- `search_cios` — filters active CIOs by free-text query, category, membership type, time commitment, and meeting day, mirroring the exact filtering logic already in `cios/views.py:cio_list`.
- `get_cio_details` — the full specification for one CIO by slug: description, requirements, dues, deadline, meeting info, contact info, and officer names/roles.

It will run over stdio transport (`python mcp_server.py`), which is what Claude Desktop/Code expect for a locally-run MCP server — no separate hosting or network exposure needed. It will not expose anything requiring authentication (documents, applications, messages, officer-only analytics) — only what `cio_list`/`cio_detail` already show to an anonymous visitor.

Write actions (an AI applying to a CIO, bookmarking, messaging on a user's behalf) are deliberately out of scope for this first version, since MCP has no built-in notion of "which Django user is this" — that would need its own auth design before being safe to add.
