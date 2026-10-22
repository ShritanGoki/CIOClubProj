"""
Shared test factories and fixtures used across every app's test suite.

Centralizing object creation here means a model field rename only
requires an update in one place instead of in every test file that
builds a User/CIO/etc.
"""
import itertools

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from cios.models import CIO, Category, Officer

# Smallest possible valid GIF, used wherever a real image file is needed
# (e.g. forms.ImageField runs PIL validation on the upload).
_TINY_GIF = (
    b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,'
    b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)

_username_counter = itertools.count(1)


def unique_username(prefix='user'):
    return f'{prefix}{next(_username_counter)}'


def make_user(username=None, password='testpass123', **extra):
    username = username or unique_username()
    email = extra.pop('email', f'{username}@example.com')
    user = User.objects.create_user(username=username, email=email, password=password, **extra)
    return user


def set_role(user, role):
    """Set the role on a user's profile, creating the profile if needed."""
    profile = user.profile
    profile.role = role
    profile.save()
    return profile


def make_officer_user(cio=None, **extra):
    user = make_user(**extra)
    set_role(user, 'officer')
    if cio is not None:
        Officer.objects.create(cio=cio, user=user, role='officer')
    return user


def make_admin_user(**extra):
    user = make_user(**extra)
    set_role(user, 'admin')
    return user


def make_category(name='Technology', slug=None):
    slug = slug or name.lower().replace(' ', '-')
    return Category.objects.create(name=name, slug=slug)


def make_cio(created_by, name='Test CIO', slug=None, category=None, **extra):
    slug = slug or name.lower().replace(' ', '-')
    defaults = {
        'description': 'A CIO used for testing.',
        'applications_open': False,
        'is_active': True,
    }
    defaults.update(extra)
    cio = CIO.objects.create(
        name=name, slug=slug, category=category, created_by=created_by, **defaults
    )
    Officer.objects.create(cio=cio, user=created_by, role='president', is_primary=True)
    return cio


def tiny_image(name='test.gif'):
    return SimpleUploadedFile(name, _TINY_GIF, content_type='image/gif')


def tiny_file(name='doc.txt', content=b'hello world'):
    return SimpleUploadedFile(name, content, content_type='text/plain')
