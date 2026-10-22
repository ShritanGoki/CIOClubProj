from django import forms


class NewMessageForm(forms.Form):
    recipient = forms.CharField(max_length=150, help_text="Username of the recipient")
    subject = forms.CharField(max_length=200, required=False)
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message...'}))


class ReplyForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your reply...'}))
