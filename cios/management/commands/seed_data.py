from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import UserProfile
from cios.models import Category, CIO, Officer, Announcement, Review, GaugeInterest
from events.models import Event


class Command(BaseCommand):
    help = 'Seed the database with sample categories, CIOs, events, and users'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Categories
        categories_data = [
            ('Professional', 'professional', 'bi-briefcase'),
            ('Service', 'service', 'bi-heart'),
            ('Academic', 'academic', 'bi-book'),
            ('Recreational', 'recreational', 'bi-controller'),
            ('Cultural', 'cultural', 'bi-globe'),
            ('Religious', 'religious', 'bi-building'),
            ('Political', 'political', 'bi-megaphone'),
            ('Media & Arts', 'media-arts', 'bi-palette'),
            ('Sports & Fitness', 'sports-fitness', 'bi-trophy'),
            ('Technology', 'technology', 'bi-laptop'),
        ]
        categories = {}
        for name, slug, icon in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'slug': slug, 'icon': icon})
            categories[slug] = cat

        # Create sample users — one of every role so beta testers can exercise
        # every workflow. Passwords are all `testpass123`.
        users = {}
        sample_users = [
            ('admin1', 'admin1@virginia.edu', 'Admin', 'User', 'admin'),
            ('officer1', 'officer1@virginia.edu', 'Alice', 'Johnson', 'officer'),
            ('officer2', 'officer2@virginia.edu', 'Bob', 'Smith', 'officer'),
            ('member1', 'member1@virginia.edu', 'Charlie', 'Brown', 'prospective'),
            ('member2', 'member2@virginia.edu', 'Diana', 'Lee', 'prospective'),
        ]
        for username, email, first, last, role in sample_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': first, 'last_name': last}
            )
            if created:
                user.set_password('testpass123')
                user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': role})
            if profile.role != role:
                profile.role = role
                profile.save(update_fields=['role'])
            users[username] = user

        # CIOs
        cios_data = [
            {
                'name': 'HooHacks',
                'slug': 'hoohacks',
                'description': 'UVA\'s premier hackathon organization. We organize an annual 24-hour hackathon bringing together hundreds of students to build innovative projects. Open to all skill levels!',
                'short_description': 'UVA\'s premier hackathon — building innovation one hack at a time.',
                'category': categories['technology'],
                'membership_type': 'open',
                'time_commitment': 'medium',
                'meeting_day': 'wednesday',
                'meeting_time': '19:00',
                'meeting_location': 'Rice Hall 130',
                'contact_email': 'hoohacks@virginia.edu',
                'created_by': users['officer1'],
            },
            {
                'name': 'Madison House',
                'slug': 'madison-house',
                'description': 'Madison House is UVA\'s hub for student volunteering. We connect thousands of students with community organizations in Charlottesville through dozens of volunteer programs.',
                'short_description': 'UVA\'s center for student civic engagement and volunteerism.',
                'category': categories['service'],
                'membership_type': 'application',
                'time_commitment': 'medium',
                'meeting_day': 'monday',
                'meeting_time': '18:00',
                'meeting_location': 'Madison House',
                'contact_email': 'madisonhouse@virginia.edu',
                'applications_open': True,
                'created_by': users['officer1'],
            },
            {
                'name': 'Entrepreneurship Club',
                'slug': 'entrepreneurship-club',
                'description': 'Connect with fellow entrepreneurs, attend speaker events, pitch competitions, and startup workshops. Whether you have an idea or just want to learn, we welcome all Hoos!',
                'short_description': 'Fostering the next generation of Hoo-preneurs.',
                'category': categories['professional'],
                'membership_type': 'open',
                'time_commitment': 'low',
                'meeting_day': 'thursday',
                'meeting_time': '18:30',
                'meeting_location': 'Darden School, Room 120',
                'contact_email': 'eclub@virginia.edu',
                'created_by': users['officer2'],
            },
            {
                'name': 'Club Running',
                'slug': 'club-running',
                'description': 'Join fellow Wahoos for group runs, trail adventures, and road races! All paces welcome. We run together 5 days a week with fun social events on weekends.',
                'short_description': 'Running together on Grounds and beyond. All paces welcome!',
                'category': categories['sports-fitness'],
                'membership_type': 'open',
                'time_commitment': 'medium',
                'meeting_day': 'tuesday',
                'meeting_time': '17:00',
                'meeting_location': 'Nameless Field',
                'dues': 20.00,
                'created_by': users['officer2'],
            },
            {
                'name': 'Hoos Reading',
                'slug': 'hoos-reading',
                'description': 'A book club for UVA students who love to read! We pick a new book each month and meet to discuss. Genres range from fiction to philosophy to current affairs.',
                'short_description': 'Monthly book club for curious Hoos.',
                'category': categories['academic'],
                'membership_type': 'open',
                'time_commitment': 'low',
                'meeting_day': 'friday',
                'meeting_time': '16:00',
                'meeting_location': 'Alderman Library, Room 421',
                'created_by': users['officer1'],
            },
            {
                'name': 'South Asian Student Association',
                'slug': 'sasa',
                'description': 'Celebrating South Asian culture at UVA through Diwali shows, Holi celebrations, cultural performances, and community building events throughout the year.',
                'short_description': 'Celebrating South Asian culture and community at UVA.',
                'category': categories['cultural'],
                'membership_type': 'open',
                'time_commitment': 'medium',
                'meeting_day': 'wednesday',
                'meeting_time': '19:30',
                'meeting_location': 'Newcomb Hall Ballroom',
                'contact_email': 'sasa@virginia.edu',
                'created_by': users['officer2'],
            },
        ]

        for data in cios_data:
            cio, created = CIO.objects.get_or_create(
                slug=data['slug'],
                defaults=data,
            )
            if created:
                Officer.objects.get_or_create(
                    cio=cio, user=data['created_by'],
                    defaults={'role': 'president', 'is_primary': True}
                )

        # Sample events
        now = timezone.now()
        cio_hoohacks = CIO.objects.filter(slug='hoohacks').first()
        cio_madison = CIO.objects.filter(slug='madison-house').first()
        if cio_hoohacks:
            Event.objects.get_or_create(
                cio=cio_hoohacks, title='HooHacks 2026',
                defaults={
                    'description': 'Our annual 24-hour hackathon! Food, prizes, and workshops included.',
                    'event_type': 'other',
                    'start_time': now + timezone.timedelta(days=14),
                    'end_time': now + timezone.timedelta(days=15),
                    'location': 'Rice Hall',
                    'created_by': users['officer1'],
                }
            )
            Event.objects.get_or_create(
                cio=cio_hoohacks, title='Weekly Workshop: Intro to React',
                defaults={
                    'description': 'Learn the basics of React.js in this beginner-friendly workshop.',
                    'event_type': 'workshop',
                    'start_time': now + timezone.timedelta(days=3),
                    'end_time': now + timezone.timedelta(days=3, hours=2),
                    'location': 'Rice Hall 130',
                    'created_by': users['officer1'],
                }
            )

        if cio_madison:
            Event.objects.get_or_create(
                cio=cio_madison, title='Spring Volunteer Fair',
                defaults={
                    'description': 'Come learn about all our volunteer programs!',
                    'event_type': 'info',
                    'start_time': now + timezone.timedelta(days=7),
                    'end_time': now + timezone.timedelta(days=7, hours=3),
                    'location': 'Madison House',
                    'created_by': users['officer1'],
                }
            )

        # Sample announcements
        if cio_hoohacks:
            Announcement.objects.get_or_create(
                cio=cio_hoohacks, title='HooHacks 2026 Registration Open!',
                defaults={
                    'content': 'Registration for HooHacks 2026 is now live! Sign up on our website. Early bird registration closes in 2 weeks.',
                    'author': users['officer1'],
                    'pinned': True,
                }
            )

        # Sample reviews
        if cio_hoohacks:
            Review.objects.get_or_create(
                cio=cio_hoohacks, author=users['member1'],
                defaults={
                    'rating': 5,
                    'content': 'Amazing community! HooHacks was the highlight of my first year. Met great people and learned so much.',
                }
            )
            Review.objects.get_or_create(
                cio=cio_hoohacks, author=users['member2'],
                defaults={
                    'rating': 4,
                    'content': 'Really well organized hackathon. The workshops throughout the year are super helpful too.',
                }
            )

        # Gauge interest
        GaugeInterest.objects.get_or_create(
            title='UVA Board Game Club',
            defaults={
                'description': 'Would anyone be interested in a club focused on board games and tabletop RPGs? Weekly game nights, tournaments, etc.',
                'creator': users['member1'],
                'category': categories['recreational'],
            }
        )

        self.stdout.write(self.style.SUCCESS('Data seeded successfully!'))
