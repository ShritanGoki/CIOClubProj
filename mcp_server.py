#!/usr/bin/env python
"""
MCP server exposing read-only CIO Clearinghouse data to AI assistants.

Lets a connected AI look up CIOs (clubs) by name, category, meeting time,
or membership type, and pull full details for one — the same data a
prospective member would see browsing the site, nothing more. No writes,
no authenticated/officer-only data (documents, applications, messages).

Run directly (stdio transport, what Claude Desktop/Code expect locally):
    python mcp_server.py
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearinghouse.settings')

import django  # noqa: E402

django.setup()

from mcp.server.mcpserver import MCPServer  # noqa: E402

from django.db.models import Q  # noqa: E402
from cios.models import CIO, Category  # noqa: E402

mcp = MCPServer(
    name='cio-clearinghouse',
    instructions=(
        'Look up student organizations (CIOs) at UVA by name, category, '
        'meeting day, or membership type. Use search_cios to find candidates, '
        'then get_cio_details for the full specification of one.'
    ),
)


def _cio_summary(cio: CIO) -> dict:
    return {
        'slug': cio.slug,
        'name': cio.name,
        'short_description': cio.short_description,
        'category': cio.category.name if cio.category else None,
        'membership_type': cio.get_membership_type_display(),
        'time_commitment': cio.get_time_commitment_display(),
        'meeting_day': cio.get_meeting_day_display() if cio.meeting_day else None,
        'applications_open': cio.applications_open,
    }


@mcp.tool()
def list_categories() -> list[dict]:
    """List every CIO category (e.g. Professional, Service, Academic) with its slug."""
    return [{'name': c.name, 'slug': c.slug} for c in Category.objects.all()]


@mcp.tool()
def search_cios(
    query: str = '',
    category: str = '',
    membership_type: str = '',
    time_commitment: str = '',
    meeting_day: str = '',
) -> list[dict]:
    """
    Search active CIOs by name/description, and optionally filter by
    category slug, membership_type ('open' or 'application'),
    time_commitment ('low', 'medium', 'high', 'very_high'), or
    meeting_day (e.g. 'monday'). Returns up to 25 summaries.
    """
    cios = CIO.objects.filter(is_active=True).select_related('category')

    if query:
        cios = cios.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        cios = cios.filter(category__slug=category)
    if membership_type:
        cios = cios.filter(membership_type=membership_type)
    if time_commitment:
        cios = cios.filter(time_commitment=time_commitment)
    if meeting_day:
        cios = cios.filter(meeting_day=meeting_day)

    return [_cio_summary(cio) for cio in cios.order_by('name')[:25]]


@mcp.tool()
def get_cio_details(slug: str) -> dict:
    """
    Get the full specification for one CIO by its slug (as returned by
    search_cios): description, requirements, dues, deadline, meeting
    info, contact info, and officer names/roles.
    """
    try:
        cio = CIO.objects.select_related('category').get(slug=slug, is_active=True)
    except CIO.DoesNotExist:
        return {'error': f'No active CIO found with slug "{slug}"'}

    return {
        'slug': cio.slug,
        'name': cio.name,
        'description': cio.description,
        'category': cio.category.name if cio.category else None,
        'membership_type': cio.get_membership_type_display(),
        'time_commitment': cio.get_time_commitment_display(),
        'meeting_day': cio.get_meeting_day_display() if cio.meeting_day else None,
        'meeting_time': cio.meeting_time.isoformat() if cio.meeting_time else None,
        'meeting_location': cio.meeting_location,
        'dues': str(cio.dues) if cio.dues is not None else None,
        'application_deadline': cio.application_deadline.isoformat() if cio.application_deadline else None,
        'requirements': cio.requirements,
        'contact_email': cio.contact_email,
        'website': cio.website,
        'applications_open': cio.applications_open,
        'officers': [
            {'name': o.user.get_full_name() or o.user.username, 'role': o.get_role_display()}
            for o in cio.get_officers()
        ],
    }


if __name__ == '__main__':
    mcp.run(transport='stdio')
