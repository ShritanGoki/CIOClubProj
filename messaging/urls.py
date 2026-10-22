from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('new/', views.new_conversation, name='new'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('<int:pk>/', views.conversation_detail, name='conversation'),
]
