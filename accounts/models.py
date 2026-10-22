from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('prospective', 'Prospective Member'),
        ('officer', 'CIO Officer'),
        ('admin', 'User Administrator'),
    ]

    FIELD_OF_STUDY_CHOICES = [
        ('cs', 'Computer Science'),
        ('engineering', 'Engineering'),
        ('business', 'Business'),
        ('arts', 'Arts & Humanities'),
        ('sciences', 'Sciences'),
        ('social_sciences', 'Social Sciences'),
        ('education', 'Education'),
        ('nursing', 'Nursing'),
        ('architecture', 'Architecture'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='prospective')
    bio = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    field_of_study = models.CharField(max_length=30, choices=FIELD_OF_STUDY_CHOICES, blank=True)
    interests = models.ManyToManyField('cios.Category', blank=True, related_name='interested_users')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_officer(self):
        return self.role == 'officer'

    @property
    def is_prospective(self):
        return self.role == 'prospective'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None
