from django.urls import path
from lobby import views


urlpatterns = [
    path('', views.select, name='select'),
    path('<int:id_room>/', views.select, name='unirse'),
]
