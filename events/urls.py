from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('my-events/', views.my_events, name='my_events'),
    path('<slug:slug>/create/', views.event_create, name='create'),
    path('<slug:slug>/<int:event_id>/edit/', views.event_edit, name='edit'),
    path('<slug:slug>/<int:event_id>/delete/', views.event_delete, name='delete'),
    path('reminder/<int:event_id>/', views.toggle_reminder, name='toggle_reminder'),
]
