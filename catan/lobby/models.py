from django.db import models

from games.models import Game


class Room(models.Model):
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    max_players = models.PositiveIntegerField(default=4)
    game_has_started = models.BooleanField(default=False)
    game_id = models.IntegerField(default=None, null = True)
    board = models.IntegerField(default=0)


class User_in_room(models.Model):
    name = models.CharField(max_length=100)
    room = models.ForeignKey(
        Room,
        related_name='players',
        on_delete=models.CASCADE)

    class Meta:
        unique_together = ['room', 'name']
        ordering = ['name']

    def __str__(self):
        return '%s' % (self.name)
