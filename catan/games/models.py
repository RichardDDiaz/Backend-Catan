from django.db import models
from django.contrib.auth.models import User
from .aux import VERTICES_BY_HEX

RESOURCE_TYPES = [
    'brick',
    'lumber',
    'wool',
    'grain',
    'ore',
]


class Game(models.Model):
    winner = models.CharField(default=None, blank=True, max_length=20,null=True)
    dice_1 = models.IntegerField(default=0)
    dice_2 = models.IntegerField(default=0)
    turn_number = models.IntegerField(default=1)
    has_finished = models.BooleanField(default=False)
    robber_has_moved = models.BooleanField(default = False)


class Vertex_Game(models.Model):
    level = models.IntegerField()
    index = models.IntegerField()
    is_available_for_road = models.BooleanField(default=False)
    is_available_for_building = models.BooleanField(default=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class Hex_Game(models.Model):
    level = models.IntegerField()
    index = models.IntegerField()
    token = models.IntegerField(default=0)
    has_robber = models.BooleanField(default=False)
    resource_types = (
        ('brick', 'brick'),
        ('lumber', 'lumber'),
        ('wool', 'wool'),
        ('grain', 'grain'),
        ('ore', 'ore'),
        ('desert', 'desert')
    )
    resource = models.CharField(
        choices=resource_types,
        max_length=10,
        default=None,
    )
    game = models.ForeignKey(Game, default=None, on_delete=models.CASCADE)

    def get_vertices(self):
        position_tuple = (self.level, self.index)
        result = VERTICES_BY_HEX.get(position_tuple)
        return (result)


class Player(models.Model):
    username = models.CharField(max_length=30)
    colour = models.CharField(max_length=20)
    development_cards = models.IntegerField(default=0)
    resources_cards = models.IntegerField(default=0)
    victory_points = models.IntegerField(default=0)
    #last_gained = models.OneToOneField(Resources,on_delete=models.CASCADE,primary_key=True,default = None)

    game = models.ForeignKey(
        Game,
        default=None,
        related_name='players',
        on_delete=models.CASCADE
    )


class Settlement(models.Model):
    position = models.OneToOneField(
        Vertex_Game,
        on_delete=models.CASCADE,
        primary_key=True)
    player = models.ForeignKey(
        Player, related_name='settlements', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['player', 'position']


class City(models.Model):
    position = models.OneToOneField(
        Vertex_Game,
        on_delete=models.CASCADE,
        primary_key=True)
    player = models.ForeignKey(
        Player, related_name='cities', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['player', 'position']


class Road(models.Model):
    position1 = models.ForeignKey(
        Vertex_Game,
        related_name='position1',
        on_delete=models.CASCADE)
    position2 = models.ForeignKey(
        Vertex_Game,
        related_name='position2',
        on_delete=models.CASCADE)
    player = models.ForeignKey(
        Player, related_name='road', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['player', 'position1', 'position2']


class Cards(models.Model):
    road_building = models.PositiveIntegerField(default=0)
    year_of_plenty = models.PositiveIntegerField(default=0)
    monopoly = models.PositiveIntegerField(default=0)
    victory_point = models.PositiveIntegerField(default=0)
    knight = models.PositiveIntegerField(default=0)
    player = models.OneToOneField(
        Player, on_delete=models.CASCADE, primary_key=True)


class Resources(models.Model):
    lumber = models.PositiveIntegerField(default=0)
    wool = models.PositiveIntegerField(default=0)
    grain = models.PositiveIntegerField(default=0)
    brick = models.PositiveIntegerField(default=0)
    ore = models.PositiveIntegerField(default=0)
    player = models.OneToOneField(
        Player, on_delete=models.CASCADE, primary_key=True)


class Board(models.Model):
    name = models.CharField(max_length=100)


class Hex(models.Model):
    board = models.ForeignKey(Board, default=None, on_delete=models.CASCADE)
    token = models.IntegerField(default=0)
    has_robber = models.BooleanField(default=False)
    resource_types = (
        ('brick', 'brick'),
        ('lumber', 'lumber'),
        ('wool', 'wool'),
        ('grain', 'grain'),
        ('ore', 'ore'),
    )
    resource = models.CharField(
        choices=resource_types,
        max_length=10,
        default=None,
    )

    class Meta:
        verbose_name_plural = 'hexes'


class Hex_Position(models.Model):
    level = models.IntegerField()
    index = models.IntegerField()
    hex = models.OneToOneField(
        Hex,
        related_name='position',
        default=None,
        on_delete=models.CASCADE
    )


class Turns (models.Model):
    game = models.OneToOneField(Game,

                                default=None,
                                on_delete=models.CASCADE
                                )
    first_turn = models.OneToOneField(Player,
                                      related_name='first4',
                                      default=None,
                                      on_delete=models.CASCADE
                                      )
    second_turn = models.OneToOneField(Player,
                                       related_name='second4',
                                       default=None,
                                       on_delete=models.CASCADE
                                       )
    third_turn = models.OneToOneField(Player,
                                      related_name='third4',
                                      default=None,
                                      on_delete=models.CASCADE
                                      )
    fourth_turn = models.OneToOneField(Player,
                                       related_name='fourth4',
                                       default=None,
                                       on_delete=models.CASCADE
                                       )


class Turns3 (models.Model):
    game = models.OneToOneField(Game,
                                default=None,
                                on_delete=models.CASCADE
                                )
    first_turn = models.OneToOneField(Player,
                                      related_name='first3',
                                      default=None,
                                      on_delete=models.CASCADE
                                      )
    second_turn = models.OneToOneField(Player,
                                       related_name='second3',
                                       default=None,
                                       on_delete=models.CASCADE
                                       )
    third_turn = models.OneToOneField(Player,
                                      related_name='third3',
                                      default=None,
                                      on_delete=models.CASCADE
                                      )
