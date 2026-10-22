from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('admin-panel/', views.user_admin, name='user_admin'),
    path('admin-panel/change-role/<int:user_id>/', views.change_user_role, name='change_role'),
]
