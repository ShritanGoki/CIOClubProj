from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Max, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import NewMessageForm, ReplyForm
from .models import Conversation, Message


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_msg_time=Max('messages__sent_at'),
        msg_count=Count('messages'),
    ).order_by('-last_msg_time')

    # Count unread
    for conv in conversations:
        conv.unread_count = conv.messages.exclude(
            read_by=request.user
        ).exclude(sender=request.user).count()
        last = conv.last_message
        conv.last_msg = last
        conv.other_users = conv.other_participants(request.user)

    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    msgs = conversation.messages.select_related('sender').order_by('sent_at')

    # Mark messages as read
    unread = msgs.exclude(read_by=request.user).exclude(sender=request.user)
    for msg in unread:
        msg.read_by.add(request.user)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=form.cleaned_data['body'],
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            return redirect('messaging:conversation', pk=pk)
    else:
        form = ReplyForm()

    other_users = conversation.other_participants(request.user)
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages_list': msgs,
        'form': form,
        'other_users': other_users,
    })


@login_required
def new_conversation(request):
    recipient_username = request.GET.get('to', '')
    if request.method == 'POST':
        form = NewMessageForm(request.POST)
        if form.is_valid():
            try:
                recipient = User.objects.get(username=form.cleaned_data['recipient'])
            except User.DoesNotExist:
                django_messages.error(request, 'User not found.')
                return render(request, 'messaging/new_conversation.html', {'form': form})

            if recipient == request.user:
                django_messages.error(request, 'You cannot message yourself.')
                return render(request, 'messaging/new_conversation.html', {'form': form})

            # Check for existing conversation between the two users
            existing = Conversation.objects.filter(
                participants=request.user
            ).filter(
                participants=recipient
            ).first()

            if existing:
                conversation = existing
            else:
                conversation = Conversation.objects.create(
                    subject=form.cleaned_data.get('subject', '')
                )
                conversation.participants.add(request.user, recipient)

            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=form.cleaned_data['body'],
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            return redirect('messaging:conversation', pk=conversation.pk)
    else:
        form = NewMessageForm(initial={'recipient': recipient_username})
    return render(request, 'messaging/new_conversation.html', {'form': form})


@login_required
def unread_count(request):
    count = Message.objects.filter(
        conversation__participants=request.user
    ).exclude(
        read_by=request.user
    ).exclude(sender=request.user).count()
    from django.http import JsonResponse
    return JsonResponse({'count': count})
