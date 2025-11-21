from django.contrib import admin
from django.urls import path, include
from socialmedia import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logoutt, name='logout'),
    path('upload',views.upload, name='upload'),
    path('like-post/<uuid:id>/', views.like, name='like-post'),
    path('post/<uuid:id>', views.post_details, name='post_details'),
    path('explore/', views.explore, name='explore'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit-profile/<str:username>/', views.edit_profile, name='edit_profile'),
    path('delete-post/<uuid:id>/', views.delete_post, name='delete_post'),
    path('follower/<str:username>/', views.follower, name='follow'),
    path('search/', views.search_results, name='search_results'),
    path('post/<uuid:id>/comments/', views.comments, name='comments'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)