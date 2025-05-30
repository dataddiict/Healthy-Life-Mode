from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
    path('signin', views.connection, name='signin'),
    path('signup', views.inscription, name='signup'),
    path('profile/', views.user_profile, name='user_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('user-update/', views.update_user, name='user_update'),
    path('logout/', views.logout_view, name='logout'),
    path('predict/', views.predict_sleep_disorder_view, name='predict_sleep_disorder'),
]