from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path(
        '<int:id>/<slug:player>/actions/',
        views.actions,
        name='player_actions'),

    path(
        '<int:id>/',
        views.games_status),

    path(
        '<int:id>/board/',
        views.board_status,
        name='board_status'),
    path(
        '<int:id>/<slug:player>/',
        views.ListInfo,
        name='list_info'),
]
