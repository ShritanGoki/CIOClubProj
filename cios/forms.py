from django import forms
from .models import CIO, Announcement, Review, CIODocument, CIOPhoto, Application, GaugeInterest, Officer


class CIOForm(forms.ModelForm):
    class Meta:
        model = CIO
        fields = [
            'name', 'description', 'short_description', 'logo', 'banner_image',
            'category', 'membership_type', 'time_commitment',
            'meeting_day', 'meeting_time', 'meeting_location',
            'dues', 'application_deadline', 'requirements',
            'contact_email', 'website', 'instagram',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            'meeting_time': forms.TimeInput(attrs={'type': 'time'}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'pinned']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your experience...'}),
            'rating': forms.RadioSelect,
        }


class DocumentForm(forms.ModelForm):
    class Meta:
        model = CIODocument
        fields = ['title', 'file']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = CIOPhoto
        fields = ['image', 'caption']


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['statement']
        widgets = {
            'statement': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us why you want to join...'}),
        }


class GaugeInterestForm(forms.ModelForm):
    class Meta:
        model = GaugeInterest
        fields = ['title', 'description', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class OfficerForm(forms.Form):
    username = forms.CharField(max_length=150, help_text="Username of the person to add as officer")
    role = forms.ChoiceField(choices=Officer.ROLE_CHOICES)
