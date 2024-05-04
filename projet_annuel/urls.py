from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
    path('signin', views.connection, name='signin'),
    path('signup', views.inscription, name='signup'),
]