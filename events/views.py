from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cios.models import CIO, Bookmark
from .forms import EventForm
from .models import Event, Reminder


@login_required
def event_create(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.cio = cio
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created.')
            return redirect('cios:detail', slug=slug)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'cio': cio, 'title': 'Create Event'})


@login_required
def event_edit(request, slug, event_id):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    event = get_object_or_404(Event, id=event_id, cio=cio)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated.')
            return redirect('cios:detail', slug=slug)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'cio': cio, 'title': 'Edit Event'})


@login_required
def event_delete(request, slug, event_id):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    event = get_object_or_404(Event, id=event_id, cio=cio)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted.')
    return redirect('cios:manage', slug=slug)


@login_required
def toggle_reminder(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reminder, created = Reminder.objects.get_or_create(user=request.user, event=event)
    if not created:
        reminder.delete()
        messages.info(request, 'Reminder removed.')
    else:
        messages.success(request, 'Reminder set!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def my_events(request):
    now = timezone.now()
    # Events from bookmarked CIOs and CIOs where user is officer
    bookmarked_cio_ids = Bookmark.objects.filter(user=request.user).values_list('cio_id', flat=True)
    officer_cio_ids = request.user.officer_roles.values_list('cio_id', flat=True)
    all_cio_ids = set(list(bookmarked_cio_ids) + list(officer_cio_ids))

    upcoming_events = Event.objects.filter(
        cio_id__in=all_cio_ids, start_time__gte=now
    ).select_related('cio').order_by('start_time')[:20]

    past_events = Event.objects.filter(
        cio_id__in=all_cio_ids, end_time__lt=now
    ).select_related('cio').order_by('-start_time')[:10]

    reminders = Reminder.objects.filter(user=request.user).select_related('event', 'event__cio')
    reminder_event_ids = set(reminders.values_list('event_id', flat=True))

    return render(request, 'events/my_events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'reminder_event_ids': reminder_event_ids,
    })
