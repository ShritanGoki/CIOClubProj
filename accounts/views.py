from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserProfileForm
from .models import UserProfile


def ensure_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


@login_required
def profile_view(request):
    profile = ensure_profile(request.user)
    if profile.is_admin:
        return redirect('accounts:user_admin')
    bookmarks = request.user.bookmarks.select_related('cio')[:5]
    applications = request.user.applications.select_related('cio')[:5]
    officer_roles = request.user.officer_roles.select_related('cio')[:10]
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'bookmarks': bookmarks,
        'applications': applications,
        'officer_roles': officer_roles,
    })


@login_required
def profile_edit(request):
    profile = ensure_profile(request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = ensure_profile(user)
    officer_roles = user.officer_roles.select_related('cio')
    return render(request, 'accounts/public_profile.html', {
        'profile_user': user,
        'profile': profile,
        'officer_roles': officer_roles,
    })


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return render(request, 'accounts/delete_account.html')


@login_required
def user_admin(request):
    profile = ensure_profile(request.user)
    if not profile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    users = UserProfile.objects.exclude(role='admin').select_related('user').order_by('user__username')
    return render(request, 'accounts/user_admin.html', {'users': users})


@login_required
def change_user_role(request, user_id):
    admin_profile = ensure_profile(request.user)
    if not admin_profile.is_admin:
        messages.error(request, 'Permission denied.')
        return redirect('home')
    if request.method == 'POST':
        target_profile = get_object_or_404(UserProfile, user_id=user_id)
        new_role = request.POST.get('role')
        if new_role in ('prospective', 'officer'):
            target_profile.role = new_role
            target_profile.save()
            messages.success(request, f"Role updated for {target_profile.user.username}.")
        else:
            messages.error(request, 'Invalid role.')
    return redirect('accounts:user_admin')
