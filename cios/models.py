from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class")

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class CIO(models.Model):
    MEMBERSHIP_CHOICES = [
        ('open', 'Open Membership'),
        ('application', 'Application Required'),
    ]

    COMMITMENT_CHOICES = [
        ('low', 'Low (1-2 hrs/week)'),
        ('medium', 'Medium (3-5 hrs/week)'),
        ('high', 'High (6-10 hrs/week)'),
        ('very_high', 'Very High (10+ hrs/week)'),
    ]

    MEETING_DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='cio_logos/', blank=True)
    banner_image = models.ImageField(upload_to='cio_banners/', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='cios')
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='open')
    time_commitment = models.CharField(max_length=20, choices=COMMITMENT_CHOICES, default='medium')
    meeting_day = models.CharField(max_length=10, choices=MEETING_DAY_CHOICES, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    meeting_location = models.CharField(max_length=200, blank=True)
    dues = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    requirements = models.TextField(blank=True, help_text="Membership requirements, dues, deadlines")
    contact_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    applications_open = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_cios')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CIO"
        verbose_name_plural = "CIOs"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def officer_count(self):
        return self.officers.count()

    @property
    def bookmark_count(self):
        return self.bookmarks.count()

    def get_officers(self):
        return self.officers.select_related('user')


class Officer(models.Model):
    ROLE_CHOICES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('treasurer', 'Treasurer'),
        ('secretary', 'Secretary'),
        ('social_chair', 'Social Chair'),
        ('membership', 'Membership Chair'),
        ('officer', 'Officer'),
    ]

    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='officers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='officer_roles')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='officer')
    is_primary = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cio', 'user')
        ordering = ['role']

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} of {self.cio.name}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cio')

    def __str__(self):
        return f"{self.user.username} -> {self.cio.name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
    ]

    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    statement = models.TextField(help_text="Why do you want to join?")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications'
    )

    class Meta:
        unique_together = ('cio', 'applicant')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.applicant.username} -> {self.cio.name} ({self.status})"


class Announcement(models.Model):
    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pinned', '-created_at']

    def __str__(self):
        return f"{self.cio.name}: {self.title}"


class Review(models.Model):
    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cio', 'author')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review of {self.cio.name} by {self.author.username}"


class CIODocument(models.Model):
    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='cio_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.cio.name}: {self.title}"


class CIOPhoto(models.Model):
    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='cio_photos/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.cio.name} photo: {self.caption or 'No caption'}"


class ProfileView(models.Model):
    cio = models.ForeignKey(CIO, on_delete=models.CASCADE, related_name='profile_views')
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']


class GaugeInterest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interest_gauges')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    votes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='voted_interests')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "gauge interests"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def vote_count(self):
        return self.votes.count()
