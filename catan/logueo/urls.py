from django.urls import path
from .views import login, register, logout

urlpatterns = [
    path('', register),
    path('login/', login),
    path('logout/', logout),

]
