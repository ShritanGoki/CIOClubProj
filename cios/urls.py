from django.urls import path
from . import views

app_name = 'cios'

urlpatterns = [
    path('', views.cio_list, name='list'),
    path('create/', views.cio_create, name='create'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('gauge-interest/', views.gauge_interest_list, name='gauge_list'),
    path('gauge-interest/create/', views.gauge_interest_create, name='gauge_create'),
    path('gauge-interest/<int:pk>/vote/', views.gauge_interest_vote, name='gauge_vote'),
    path('start-a-cio/', views.start_cio_guide, name='start_guide'),
    path('<slug:slug>/', views.cio_detail, name='detail'),
    path('<slug:slug>/edit/', views.cio_edit, name='edit'),
    path('<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('<slug:slug>/toggle-applications/', views.toggle_applications, name='toggle_applications'),
    path('<slug:slug>/apply/', views.apply_to_cio, name='apply'),
    path('<slug:slug>/manage/', views.manage_cio, name='manage'),
    path('<slug:slug>/manage/application/<int:app_id>/', views.review_application, name='review_application'),
    path('<slug:slug>/manage/announcement/', views.add_announcement, name='add_announcement'),
    path('<slug:slug>/manage/announcement/<int:ann_id>/delete/', views.delete_announcement, name='delete_announcement'),
    path('<slug:slug>/manage/review/', views.add_review, name='add_review'),
    path('<slug:slug>/manage/document/', views.add_document, name='add_document'),
    path('<slug:slug>/manage/document/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
    path('<slug:slug>/manage/photo/', views.add_photo, name='add_photo'),
    path('<slug:slug>/manage/photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('<slug:slug>/manage/officer/', views.add_officer, name='add_officer'),
    path('<slug:slug>/manage/officer/<int:officer_id>/remove/', views.remove_officer, name='remove_officer'),
]
