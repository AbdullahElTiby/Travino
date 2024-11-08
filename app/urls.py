from django.urls import path
from . import views
from .views import logout_view

urlpatterns = [
    path('', views.home, name='home'),
    path('aitg/', views.aitg, name='aitg'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact', views.contact_view, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('settings/', views.settings, name='settings'),
    path('tr_in_blocks/', views.tr_in_blocks, name='tr_in_blocks'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('place/<int:pk>/', views.place_detail, name='place_detail'),
    path('delete-profile-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('change-profile-picture/', views.change_profile_picture, name='change_profile_picture'),
    
]