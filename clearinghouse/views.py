from django.db.models import Avg, Count
from django.shortcuts import render
from django.utils import timezone

from cios.models import CIO, Category
from events.models import Event


def home(request):
    categories = Category.objects.annotate(cio_count=Count('cios'))
    featured_cios = CIO.objects.filter(is_active=True).annotate(
        num_bookmarks=Count('bookmarks')
    ).order_by('-num_bookmarks')[:6]
    upcoming_events = Event.objects.filter(
        start_time__gte=timezone.now(), is_public=True
    ).select_related('cio').order_by('start_time')[:5]

    return render(request, 'home.html', {
        'categories': categories,
        'featured_cios': featured_cios,
        'upcoming_events': upcoming_events,
    })
