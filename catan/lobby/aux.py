
from .models import *
from games.models import *


def new_colour(a):
    if a == 0:
        return 'red'
    elif a == 1:
        return 'blue'
    elif a == 2:
        return 'yellow'
    elif a == 3:
        return 'white'


def create_vertex(game):
    for i in range(0, 6):
        vg = Vertex_Game(level=0, index=i, game=game)
        vg.save()

    for i in range(0, 18):
        vg = Vertex_Game(level=1, index=i, game=game)
        vg.save()

    for i in range(0, 30):
        vg = Vertex_Game(level=2, index=i, game=game)
        vg.save()


def create_hexgame(game, board):

    for each in Hex_Position.objects.filter(level=0, index=0):
        if each.hex.board == board:
            my_hex = each.hex

    hg = Hex_Game(level=0, index=0, token=my_hex.token,
                  has_robber=my_hex.has_robber, resource=my_hex.resource, game=game)
    hg.save()

    for i in range(1, 7):
        for each in Hex_Position.objects.filter(level=1, index=i - 1):
            if each.hex.board == board:
                my_hex = each.hex

        hg = Hex_Game(level=1, index=i - 1, token=my_hex.token,
                      has_robber=my_hex.has_robber, resource=my_hex.resource, game=game)
        hg.save()
    for i in range(7, 19):
        for each in Hex_Position.objects.filter(level=2, index=i - 7):
            if each.hex.board == board:
                my_hex = each.hex
        hg = Hex_Game(level=2, index=i - 7, token=my_hex.token,
                      has_robber=my_hex.has_robber, resource=my_hex.resource, game=game)
        hg.save()


def create_players(users, game):
    current_players = len(users)
    for i in range(0, current_players):
        new_player = Player(
            game=game,
            username=users[i].name,
            colour=new_colour(i))
        new_player.save()
        cards = Cards(player=new_player)
        cards.save()
        resources = Resources(player=new_player)
        resources.save()


def create_turns(users, game):

    players = Player.objects.filter(game=game)
    current_players = len(users)

    if current_players == 3:
        turn = Turns3(
            game=game,
            first_turn=players[0],
            second_turn=players[1],
            third_turn=players[2])
        turn.save()
    elif current_players == 4:
        turn = Turns(
            game=game,
            first_turn=players[0],
            second_turn=players[1],
            third_turn=players[2],
            fourth_turn=players[3])
        turn.save()
