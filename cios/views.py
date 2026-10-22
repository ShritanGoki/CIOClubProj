from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from accounts.views import ensure_profile
from .forms import (
    CIOForm, AnnouncementForm, ReviewForm, DocumentForm,
    PhotoForm, ApplicationForm, GaugeInterestForm, OfficerForm,
)
from .models import (
    CIO, Category, Officer, Bookmark, Application,
    Announcement, Review, CIODocument, CIOPhoto, ProfileView, GaugeInterest,
)


def cio_list(request):
    cios = CIO.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    # Search
    query = request.GET.get('q', '')
    if query:
        cios = cios.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Filter by category
    category_slug = request.GET.get('category', '')
    if category_slug:
        cios = cios.filter(category__slug=category_slug)

    # Filter by membership type
    membership = request.GET.get('membership', '')
    if membership:
        cios = cios.filter(membership_type=membership)

    # Filter by time commitment
    commitment = request.GET.get('commitment', '')
    if commitment:
        cios = cios.filter(time_commitment=commitment)

    # Filter by meeting day
    meeting_day = request.GET.get('meeting_day', '')
    if meeting_day:
        cios = cios.filter(meeting_day=meeting_day)

    # Sort
    sort = request.GET.get('sort', 'name')
    if sort == 'newest':
        cios = cios.order_by('-created_at')
    elif sort == 'popular':
        cios = cios.annotate(num_bookmarks=Count('bookmarks')).order_by('-num_bookmarks')
    else:
        cios = cios.order_by('name')

    # Annotate average rating
    cios = cios.annotate(avg_rating=Avg('reviews__rating'))

    # Bookmarked CIO IDs for current user
    bookmarked_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('cio_id', flat=True))

    return render(request, 'cios/cio_list.html', {
        'cios': cios,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'selected_membership': membership,
        'selected_commitment': commitment,
        'selected_meeting_day': meeting_day,
        'selected_sort': sort,
        'bookmarked_ids': bookmarked_ids,
    })


def cio_detail(request, slug):
    cio = get_object_or_404(CIO.objects.select_related('category', 'created_by'), slug=slug)
    officers = cio.officers.select_related('user')
    announcements = cio.announcements.all()[:5]
    upcoming_events = cio.events.filter(start_time__gte=timezone.now()).order_by('start_time')[:5]
    past_events = cio.events.filter(end_time__lt=timezone.now()).order_by('-start_time')[:5]
    reviews = cio.reviews.select_related('author')[:10]
    photos = cio.photos.all()[:12]
    documents = cio.documents.all()[:10]
    avg_rating = cio.reviews.aggregate(avg=Avg('rating'))['avg']

    # Track profile view
    if request.user.is_authenticated:
        ProfileView.objects.create(cio=cio, viewer=request.user)

    is_officer = False
    is_bookmarked = False
    has_applied = False
    user_review = None
    if request.user.is_authenticated:
        is_officer = officers.filter(user=request.user).exists()
        is_bookmarked = Bookmark.objects.filter(user=request.user, cio=cio).exists()
        has_applied = Application.objects.filter(applicant=request.user, cio=cio).exists()
        user_review = Review.objects.filter(author=request.user, cio=cio).first()

    return render(request, 'cios/cio_detail.html', {
        'cio': cio,
        'officers': officers,
        'announcements': announcements,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'reviews': reviews,
        'photos': photos,
        'documents': documents,
        'avg_rating': avg_rating,
        'is_officer': is_officer,
        'is_bookmarked': is_bookmarked,
        'has_applied': has_applied,
        'user_review': user_review,
        'review_form': ReviewForm(),
        'application_form': ApplicationForm(),
    })


@login_required
def cio_create(request):
    profile = ensure_profile(request.user)
    if request.method == 'POST':
        form = CIOForm(request.POST, request.FILES)
        if form.is_valid():
            cio = form.save(commit=False)
            cio.created_by = request.user
            cio.slug = slugify(cio.name)
            # Ensure unique slug
            base_slug = cio.slug
            counter = 1
            while CIO.objects.filter(slug=cio.slug).exists():
                cio.slug = f"{base_slug}-{counter}"
                counter += 1
            cio.save()
            Officer.objects.create(cio=cio, user=request.user, role='president', is_primary=True)
            # Make user an officer
            if profile.role == 'prospective':
                profile.role = 'officer'
                profile.save()
            messages.success(request, f'"{cio.name}" has been created!')
            return redirect('cios:detail', slug=cio.slug)
    else:
        form = CIOForm()
    return render(request, 'cios/cio_form.html', {'form': form, 'title': 'Create a New CIO'})


@login_required
def cio_edit(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'You are not an officer of this CIO.')
        return redirect('cios:detail', slug=slug)
    if request.method == 'POST':
        form = CIOForm(request.POST, request.FILES, instance=cio)
        if form.is_valid():
            form.save()
            messages.success(request, 'CIO updated successfully.')
            return redirect('cios:detail', slug=cio.slug)
    else:
        form = CIOForm(instance=cio)
    return render(request, 'cios/cio_form.html', {'form': form, 'title': f'Edit {cio.name}', 'cio': cio})


@login_required
def toggle_bookmark(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, cio=cio)
    if not created:
        bookmark.delete()
        messages.info(request, f'Removed "{cio.name}" from bookmarks.')
    else:
        messages.success(request, f'Added "{cio.name}" to bookmarks.')
    return redirect(request.META.get('HTTP_REFERER', 'cios:list'))


@login_required
def bookmarks(request):
    user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('cio', 'cio__category')
    return render(request, 'cios/bookmarks.html', {'bookmarks': user_bookmarks})


@login_required
def toggle_applications(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    cio.applications_open = not cio.applications_open
    cio.save()
    status = "opened" if cio.applications_open else "closed"
    messages.success(request, f'Applications {status} for {cio.name}.')
    return redirect('cios:manage', slug=slug)


@login_required
def apply_to_cio(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.applications_open:
        messages.error(request, 'Applications are not currently open.')
        return redirect('cios:detail', slug=slug)
    if Application.objects.filter(applicant=request.user, cio=cio).exists():
        messages.warning(request, 'You have already applied to this CIO.')
        return redirect('cios:detail', slug=slug)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.cio = cio
            app.applicant = request.user
            app.save()
            messages.success(request, 'Application submitted!')
            return redirect('cios:detail', slug=slug)
    return redirect('cios:detail', slug=slug)


@login_required
def manage_cio(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    applications = cio.applications.select_related('applicant').order_by('-submitted_at')
    officers = cio.officers.select_related('user')
    documents = cio.documents.all()
    photos = cio.photos.all()
    bookmarked_users = Bookmark.objects.filter(cio=cio).select_related('user').order_by('created_at')

    # Analytics
    total_views = cio.profile_views.count()
    views_this_week = cio.profile_views.filter(
        viewed_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    views_this_month = cio.profile_views.filter(
        viewed_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()

    return render(request, 'cios/manage_cio.html', {
        'cio': cio,
        'applications': applications,
        'officers': officers,
        'documents': documents,
        'photos': photos,
        'bookmarked_users': bookmarked_users,
        'officer_form': OfficerForm(),
        'announcement_form': AnnouncementForm(),
        'document_form': DocumentForm(),
        'photo_form': PhotoForm(),
        'total_views': total_views,
        'views_this_week': views_this_week,
        'views_this_month': views_this_month,
    })


@login_required
def review_application(request, slug, app_id):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    application = get_object_or_404(Application, id=app_id, cio=cio)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('accepted', 'denied'):
            application.status = action
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.save()
            messages.success(request, f'Application {action}.')
    return redirect('cios:manage', slug=slug)


@login_required
def add_announcement(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.cio = cio
            ann.author = request.user
            ann.save()
            messages.success(request, 'Announcement posted.')
    return redirect('cios:manage', slug=slug)


@login_required
def delete_announcement(request, slug, ann_id):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:detail', slug=slug)
    announcement = get_object_or_404(Announcement, id=ann_id, cio=cio)
    announcement.delete()
    messages.success(request, 'Announcement deleted.')
    return redirect('cios:manage', slug=slug)


@login_required
def add_review(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if Review.objects.filter(author=request.user, cio=cio).exists():
        messages.warning(request, 'You have already reviewed this CIO.')
        return redirect('cios:detail', slug=slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.cio = cio
            review.author = request.user
            review.save()
            messages.success(request, 'Review submitted.')
    return redirect('cios:detail', slug=slug)


@login_required
def add_document(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:manage', slug=slug)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.cio = cio
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, 'Document uploaded.')
    return redirect('cios:manage', slug=slug)


@login_required
def delete_document(request, slug, doc_id):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:manage', slug=slug)
    doc = get_object_or_404(CIODocument, id=doc_id, cio=cio)
    doc.delete()
    messages.success(request, 'Document deleted.')
    return redirect('cios:manage', slug=slug)


@login_required
def add_photo(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:manage', slug=slug)
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.cio = cio
            photo.uploaded_by = request.user
            photo.save()
            messages.success(request, 'Photo uploaded.')
    return redirect('cios:manage', slug=slug)


@login_required
def delete_photo(request, slug, photo_id):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:manage', slug=slug)
    photo = get_object_or_404(CIOPhoto, id=photo_id, cio=cio)
    photo.delete()
    messages.success(request, 'Photo deleted.')
    return redirect('cios:manage', slug=slug)


@login_required
def add_officer(request, slug):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:manage', slug=slug)
    if request.method == 'POST':
        form = OfficerForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['username'])
                officer, created = Officer.objects.get_or_create(
                    cio=cio, user=user,
                    defaults={'role': form.cleaned_data['role']}
                )
                if not created:
                    officer.role = form.cleaned_data['role']
                    officer.save()
                    messages.info(request, f"Updated {user.username}'s role.")
                else:
                    # Update user profile to officer
                    profile = ensure_profile(user)
                    if profile.role == 'prospective':
                        profile.role = 'officer'
                        profile.save()
                    messages.success(request, f"Added {user.username} as {officer.get_role_display()}.")
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    return redirect('cios:manage', slug=slug)


@login_required
def remove_officer(request, slug, officer_id):
    cio = get_object_or_404(CIO, slug=slug)
    if not cio.officers.filter(user=request.user).exists():
        messages.error(request, 'Permission denied.')
        return redirect('cios:manage', slug=slug)
    officer = get_object_or_404(Officer, id=officer_id, cio=cio)
    if officer.is_primary:
        messages.error(request, 'Cannot remove the primary officer.')
        return redirect('cios:manage', slug=slug)
    officer.delete()
    messages.success(request, 'Officer removed.')
    return redirect('cios:manage', slug=slug)


def recommendations(request):
    if not request.user.is_authenticated:
        return redirect('cios:list')
    profile = ensure_profile(request.user)
    interest_ids = profile.interests.values_list('id', flat=True)
    if interest_ids:
        cios = CIO.objects.filter(
            category_id__in=interest_ids, is_active=True
        ).exclude(
            bookmarks__user=request.user
        ).annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:12]
    else:
        cios = CIO.objects.filter(is_active=True).annotate(
            num_bookmarks=Count('bookmarks')
        ).order_by('-num_bookmarks')[:12]
    return render(request, 'cios/recommendations.html', {'cios': cios, 'profile': profile})


def gauge_interest_list(request):
    gauges = GaugeInterest.objects.filter(is_active=True).select_related('creator', 'category')
    voted_ids = set()
    if request.user.is_authenticated:
        voted_ids = set(request.user.voted_interests.values_list('id', flat=True))
    return render(request, 'cios/gauge_interest_list.html', {
        'gauges': gauges,
        'voted_ids': voted_ids,
        'form': GaugeInterestForm(),
    })


@login_required
def gauge_interest_create(request):
    if request.method == 'POST':
        form = GaugeInterestForm(request.POST)
        if form.is_valid():
            gauge = form.save(commit=False)
            gauge.creator = request.user
            gauge.save()
            messages.success(request, 'Interest gauge created!')
            return redirect('cios:gauge_list')
    return redirect('cios:gauge_list')


@login_required
def gauge_interest_vote(request, pk):
    gauge = get_object_or_404(GaugeInterest, pk=pk, is_active=True)
    if request.user in gauge.votes.all():
        gauge.votes.remove(request.user)
        messages.info(request, 'Vote removed.')
    else:
        gauge.votes.add(request.user)
        messages.success(request, 'Vote recorded!')
    return redirect('cios:gauge_list')


def start_cio_guide(request):
    return render(request, 'cios/start_cio_guide.html')
