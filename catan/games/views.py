from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from games.serializer import *
from django.views.decorators.csrf import csrf_exempt
import json
import random
from games.aux import *
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED
)


def ListInfo(request, id, player):
    is_valid, token = validate(request)
    if is_valid:
        request.user = token.user
    try:
        game = Game.objects.get(id=id)
        username = Player.objects.get(
            game=game, username=request.user.username)
    except Player.DoesNotExist:
        raise Http404("El usuario no pertenece en un juego")
    user_id = username.id
    x = {}
    cards, resources = ListCards(
        user_id), ListResources(user_id)
    x['cards'] = cards
    x['resources'] = resources
    return HttpResponse(json.dumps(x))


def ListCards(user_id):
    try:
        cards = Cards.objects.get(player_id=user_id)
        l = []
        for i in range(0, cards.road_building):
            l.append("road_building")
        for i in range(0, cards.year_of_plenty):
            l.append("year_of_plenty")
        for i in range(0, cards.monopoly):
            l.append("monopoly")
        for i in range(0, cards.victory_point):
            l.append("victory_point")
        for i in range(0, cards.knight):
            l.append("knight")
    except Cards.DoesNotExist:
        raise Http404("Ese player no tiene instanciadas las cartas!")
    return (l)


def ListResources(user_id):
    try:
        resources = Resources.objects.get(player_id=user_id)
        h = []
        for i in range(0, resources.lumber):
            h.append("lumber")
        for i in range(0, resources.wool):
            h.append("wool")
        for i in range(0, resources.grain):
            h.append("grain")
        for i in range(0, resources.brick):
            h.append("brick")
        for i in range(0, resources.ore):
            h.append("ore")
    except Resources.DoesNotExist:
        raise Http404("Ese player no tiene instanciados los recursos!")
    return (h)


def ListBoard(request):
    try:
        boards = Board.objects.all()
        board_serialize = BoardSerializer(boards, many=True)
        return JsonResponse(board_serialize.data, safe=False)
    except Boards.DoesNotExist:
        raise Http404("No hay boards creados")


def board_status(request, id):
    try:
        game = Game.objects.get(id=id)
        hexes = Hex_Game.objects.filter(game=game)
        serializer = {}
        my_dict = {}
        list_of_hex_serializer = []
        for each in hexes:
            my_dict = {}
            position = {}
            position['level'] = each.level
            position['index'] = each.index
            my_dict['position'] = position
            my_dict['terrain'] = each.resource
            my_dict['token'] = each.token
            list_of_hex_serializer.append(my_dict)
        serializer['hexes'] = list_of_hex_serializer
        return JsonResponse(serializer, safe=False)
    except Game.DoesNotExist:
        raise Http404()


def count_resources(resource):
    count = 0
    count += resource.wool
    count += resource.brick
    count += resource.lumber
    count += resource.grain
    count += resource.ore
    return count


def discard_half(player):
    resources = Resources.objects.get(player=player)
    resources.wool = resources.wool // 2
    resources.brick = resources.brick // 2
    resources.lumber = resources.lumber // 2
    resources.grain = resources.grain // 2
    resources.ore = resources.ore // 2
    resources.save()


def discard(game):
    players = Player.objects.filter(game=game)
    resources = Resources.objects.filter(player=players)
    player_with_7_at_least = []
    for p in players:
        if(count_resources(Resources.objects.get(player=p)) > 7):
            player_with_7_at_least.append(p)
    for p in player_with_7_at_least:
        discard_half(p)


def get_player_building(position):
    if hasattr(position, 'city'):
        result = position.city.player
    else:
        result = position.settlement.player
    return result


def distribute_resources(dices_result, game):
    winner_hexes = game.hex_game_set.filter(
        token=dices_result).exclude(
        resource='desert')
    settlement_positions = game.vertex_game_set.filter(
        is_available_for_building=False)
    for h in winner_hexes:
        vertices = h.get_vertices()
        to_receive = set()
        for (l, i) in vertices:
            pos = settlement_positions.filter(level=l, index=i)
            if pos:
                player_to_receive = get_player_building(pos[0])
                to_receive.add(player_to_receive)
        for p in to_receive:
            player_resources = p.resources
            related_resource = getattr(player_resources, h.resource)
            related_resource += 1
            setattr(player_resources, h.resource, related_resource)
            player_resources.save()


def end_turn(payload, id, player, method):
    try:
        game = Game.objects.get(id=id)
    except Game.DoesNotExist:
        raise Http404("Game doesn't exist")
    if method == 'post':

        if game.has_finished:
            result = {}
            result['winner'] = game.winner
            return 1
        players = Player.objects.filter(game=game)
        for each in players:
            if (each.victory_points >= 5):
                game.winner = each.username
                game.has_finished = True
                game.save()
                return(1)

        game.turn_number += 1
        game.robber_has_moved = False
        if(game.turn_number > len(players)):
            game.dice_1, game.dice_2 = generate_dices()

        dices_result = game.dice_1 + game.dice_2
        if dices_result == 7:
            discard(game)
        distribute_resources(dices_result, game)
        game.save()

        return 1

    elif method == 'get':
        player_r = Player.objects.get(game=game, username=player)
        settles = Settlement.objects.filter(player=player_r)

        if (whos_turn(game) == player and count_settlement(
                id, player_r) >= 2 and count_roads(id, player_r) >= 2):
            return None
        else:
            return []


def whos_turn(game):
    players = Player.objects.filter(game=game)
    user_in_turn = game.turn_number % len(players)
    try:
        turns = Turns.objects.get(game=game)
    except Turns.DoesNotExist:
        try:
            turns = Turns3.objects.get(game=game)
        except Turns3.DoesNotExist:
            raise Http404("No hay turnos")

    if len(players) == 4:
        if(game.turn_number not in [5, 6, 7, 8]):
            if user_in_turn == 1:
                user = turns.first_turn.username
            elif user_in_turn == 2:
                user = turns.second_turn.username
            elif user_in_turn == 3:
                user = turns.third_turn.username
            elif user_in_turn == 0:
                user = turns.fourth_turn.username
        else:
            if user_in_turn == 0:
                user = turns.first_turn.username
            elif user_in_turn == 3:
                user = turns.second_turn.username
            elif user_in_turn == 2:
                user = turns.third_turn.username
            elif user_in_turn == 1:
                user = turns.fourth_turn.username

    else:
        if(game.turn_number not in [4, 5, 6]):
            if user_in_turn == 1:
                user = turns.first_turn.username
            elif user_in_turn == 2:
                user = turns.second_turn.username
            elif user_in_turn == 0:
                user = turns.third_turn.username
        else:
            if user_in_turn == 0:
                user = turns.first_turn.username
            elif user_in_turn == 2:
                user = turns.second_turn.username
            elif user_in_turn == 1:
                user = turns.third_turn.username

    return user


def games_status(request, id):
    try:
        game = Game.objects.get(id=id)
        robber = Hex_Game.objects.get(game=game, has_robber=True)
        winner = game.winner
        dice_1 = game.dice_1
        dice_2 = game.dice_2
        players = Player.objects.filter(game=game)
        user = whos_turn(game)
        current_turn = {}
        robber_position = {}
        list_of_players = []
        for each in players:
            player = {}
            player['username'] = each.username
            player['colour'] = each.colour
            settlements = Settlement.objects.filter(player=each)
            cities = City.objects.filter(player=each)
            roads = Road.objects.filter(player=each)
            list_of_settlements = []
            list_of_cities = []
            list_of_roads = []

            for settle in settlements:
                settlement = {
                    "level": settle.position.level,
                    "index": settle.position.index}
                list_of_settlements.append(settlement)
            for cy in cities:
                city = {"level": cy.position.level, "index": cy.position.index}
                list_of_cities.append(city)
            for rd in roads:
                road = [{"level": rd.position1.level, "index": rd.position1.index}, {
                    "level": rd.position2.level, "index": rd.position2.index}]
                list_of_roads.append(road)

            player['settlements'] = list_of_settlements
            player['cities'] = list_of_cities
            player['roads'] = list_of_roads
            player['development_cards'] = each.development_cards
            player['resources_cards'] = each.resources_cards
            player['victory_points'] = each.victory_points
            list_of_players.append(player)

        current_turn['user'] = user
        current_turn['dice'] = (dice_1, dice_2)
        response = {}
        response['players'] = list_of_players
        response['robber'] = {"level": robber.level, "index": robber.index}
        response['current_turn'] = current_turn
        response['winner'] = game.winner

        return HttpResponse(json.dumps(response))
        #serializer = GameSerializer(game)
        # return JsonResponse(serializer.data)
    except Game.DoesNotExist:
        raise Http404("El juego no existe")


def upgrade_city(payload, id, player, method):
    game = Game.objects.get(id=id)
    if(whos_turn(game) == player):
        return []
    return []


def bank_trade(payload, id, player, method):
    result = 0
    game = Game.objects.get(id=id)
    player_r = Player.objects.get(game=id, username=player)
    resources = Resources.objects.get(player=player_r)
    if method == 'post':

        give = payload.get('give')
        receive = payload.get('receive')
        try:
            if give not in RESOURCE_TYPES:
                raise ValueError
            if receive not in RESOURCE_TYPES:
                raise ValueError
            game = Game.objects.get(id=id)
            user = game.players.get(username=player)
            user_resources = user.resources
            given_total = getattr(user_resources, give)
            given_total -= 4
            if given_total < 0:
                raise ValueError
            received_total = getattr(user_resources, receive)
            received_total += 1
            setattr(user_resources, give, given_total)
            setattr(user_resources, receive, received_total)
            user_resources.save()
            result = 1
        except (Game.DoesNotExist, Player.DoesNotExist):
            raise Http404("Game DoesNotExist o Player DoesNotExist")
        except (ValueError):
            raise Http404("Value Error")
        return(result)
    elif method == 'get':

        if((resources.lumber >= 4 or resources.wool >= 4 or resources.grain >= 4 or resources.brick >= 4 or resources.ore >= 4) and whos_turn(game) == player):
            return None
        else:
            return []


def buy_card(payload, id, player, method):
    try:
        game = Game.objects.get(id=id)
        user = Player.objects.get(username=player, game=game)
        resources = user.resources
        cards = user.cards
    except (Game.DoesNotExist, Player.DoesNotExist):
        raise Http404("Incorrect data for action.")
    if method == 'post':
        if resources.wool > 0 and resources.grain > 0 and resources.ore > 0:
            random_card = random.randrange(0, 4)
            if random_card == 0:
                cards.road_building += 1
            elif random_card == 1:
                cards.year_of_plenty += 1
            elif random_card == 2:
                cards.monopoly += 1
            elif random_card == 3:
                cards.victory_point += 1
            elif random_card == 4:
                cards.knight += 1
            resources.wool -= 1
            resources.grain -= 1
            resources.ore -= 1
            cards.save()
            resources.save()
            return 1
        else:
            raise Http404("Insufficient resources for this action.")

    elif method == 'get':

        emptyList = []
        if resources.wool > 0 and resources.grain > 0 and resources.ore > 0 and whos_turn(
                game) == player:
            return None
        else:
            return emptyList


def compare_vertex(v1, v2):
    return ((v1.level == v2.level) and (v1.index == v2.index))


def resources_build_settlement(player, id):
    game = Game.objects.get(id=id)
    resource = Resources.objects.get(player=player)

    if(resource.wool > 0 and resource.brick > 0 and resource.lumber > 0 and resource.grain > 0):
        resource.wool -= 1
        resource.brick -= 1
        resource.lumber -= 1
        resource.grain -= 1
        resource.save()
        return True
    else:
        return False


def count_settlement(id, player):
    game = Game.objects.get(id=id)
    settlements = Settlement.objects.filter(player=player)
    return len(settlements)


def calculate_vertex_for_settlement(player, game):
    player_r = Player.objects.get(game=game, username=player)
    roads = Road.objects.filter(player=player_r)
    vertex = Vertex_Game.objects.filter(
        is_available_for_building=True, game=game)
    result = []
    result2 = []
    result3 = []
    for r in roads:
        response = {}
        response2 = {}
        response['level'] = r.position1.level
        response['index'] = r.position1.index
        response2['level'] = r.position2.level
        response2['index'] = r.position2.index
        result.append((response, response2))
    for v in vertex:
        for r in result:
            if(v.level == r[0].get('level') and v.index == r[0].get('index')):
                result2.append(r[0])
            elif(v.level == r[1].get('level') and v.index == r[1].get('index')):
                result2.append(r[1])
    for r in result2:
        if(r not in result3):
            result3.append(r)
    return(result3)


def build_settlement(payload, id, player, method):
    game = Game.objects.get(id=id)
    try:
        player_r = Player.objects.get(username=player, game=game)
    except Player.DoesNotExist:
        result = []
        return result

    if method == 'post':
        game = Game.objects.get(id=id)
        player_r = Player.objects.get(game=game, username=player)
        players = Player.objects.filter(game=game)

        level = payload.get('level')
        index = payload.get('index')
        try:
            vertex_wanted = Vertex_Game.objects.get(
                game=game, level=level, index=index)
        except Vertex_Game.DoesNotExist:
            raise Http404("Vertex_Game no existe")
        try:
            available_vertex = Vertex_Game.objects.filter(
                is_available_for_building=True, game=game)
        except Vertex_Game.DoesNotExist:
            raise Http404("Vertex_Game no existe")

        if(len(players) == 3 and game.turn_number < 4):
            for vg in available_vertex:
                if(compare_vertex(vertex_wanted, vg)):
                    if(count_settlement(id, player_r) < 2):
                        vg.is_available_for_building = False
                        settlement = Settlement(position=vg, player=player_r)
                        settlement.save()
                        vg.save()
                        vertex = colliding_vertex(vg)
                        for v in vertex:
                            v.is_available_for_road = True
                            v.save()
                        player_r.victory_points += 1
                        player_r.save()
                        return(1)

        elif(len(players) == 4 and game.turn_number < 5):
            for vg in available_vertex:
                if(compare_vertex(vertex_wanted, vg)):
                    if(count_settlement(id, player_r) < 2):
                        vg.is_available_for_building = False
                        settlement = Settlement(position=vg, player=player_r)
                        settlement.save()
                        vg.save()
                        vertex = colliding_vertex(vg)
                        for v in vertex:
                            v.is_available_for_road = True
                            v.save()

                        player_r.victory_points += 1
                        player_r.save()
                        return(1)

        else:
            for vg in available_vertex:
                if(compare_vertex(vertex_wanted, vg)):
                    if(count_settlement(id, player_r) < 5):
                        if (resources_build_settlement(player_r, id)):
                            vg.is_available_for_building = False
                            settlement = Settlement(
                                position=vg, player=player_r)
                            settlement.save()
                            vg.save()
                            vertex = colliding_vertex(vg)
                            for v in vertex:
                                v.is_available_for_road = True
                                v.save()
                            player_r.victory_points += 1
                            player_r.save()
                            return(1)

    elif method == 'get':
        result = []
        resources = Resources.objects.get(player=player_r)
        if(whos_turn(game) == player):
            if (resources.wool > 0 and resources.lumber > 0 and resources.grain > 0 and resources.brick >
                    0 and count_settlement(id, player_r) >= 2 and count_settlement(id, player_r) <= 5):
                result = calculate_vertex_for_settlement(player, game)
            elif(count_settlement(id, player_r) < 2):
                vertex = Vertex_Game.objects.filter(
                    is_available_for_building=True, game=game)
                for each in vertex:
                    response = {}
                    response['level'] = each.level
                    response['index'] = each.index
                    result.append(response)
        return(result)


def colliding_vertex(vertex):
    game = vertex.game
    colide_vertex = []
    colide_vertex.append(vertex)

    if vertex.level == 0:
        colide_vertex.append(
            Vertex_Game.objects.get(
                level=0, index=(
                    (vertex.index + 1) %
                    6), game=game))
        colide_vertex.append(
            Vertex_Game.objects.get(
                level=0, index=(
                    (vertex.index - 1) %
                    6), game=game))
        colide_vertex.append(
            Vertex_Game.objects.get(
                level=1, index=(
                    vertex.index * 3), game=game))

    elif vertex.level == 1:
        if (vertex.index % 3) == 0:

            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        (vertex.index + 1) %
                        18), game=game))
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        (vertex.index - 1) %
                        18), game=game))
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=0, index=(
                        vertex.index // 3), game=game))

        else:
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        (vertex.index + 1) %
                        18), game=game))
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        (vertex.index - 1) %
                        18), game=game))

            if(vertex.index == 1):
                colide_vertex.append(
                    Vertex_Game.objects.get(
                        level=2, index=vertex.index, game=game))

            elif(vertex.index == 2 or vertex.index == 4):
                colide_vertex.append(
                    Vertex_Game.objects.get(
                        level=2,
                        index=vertex.index + 2,
                        game=game))

            elif(vertex.index == 5 or vertex.index == 7):
                colide_vertex.append(
                    Vertex_Game.objects.get(
                        level=2,
                        index=vertex.index + 4,
                        game=game))

            elif(vertex.index == 8 or vertex.index == 10):
                colide_vertex.append(
                    Vertex_Game.objects.get(
                        level=2,
                        index=vertex.index + 6,
                        game=game))

            elif(vertex.index == 11 or vertex.index == 13):
                colide_vertex.append(
                    Vertex_Game.objects.get(
                        level=2,
                        index=vertex.index + 8,
                        game=game))

            elif(vertex.index == 14 or vertex.index == 16):
                colide_vertex.append(
                    Vertex_Game.objects.get(
                        level=2,
                        index=vertex.index + 10,
                        game=game))

            elif(vertex.index == 17):
                colide_vertex.append(
                    Vertex_Game.objects.get(
                        level=2,
                        index=vertex.index + 12,
                        game=game))

    elif vertex.level == 2:
        colide_vertex.append(
            Vertex_Game.objects.get(
                level=2,
                index=(
                    vertex.index +
                    1) %
                30,
                game=game))
        colide_vertex.append(
            Vertex_Game.objects.get(
                level=2,
                index=(
                    vertex.index -
                    1) %
                30,
                game=game))
        if(vertex.index == 1):
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1,
                    index=(
                        vertex.index %
                        18),
                    game=game))
        elif(vertex.index == 4 or vertex.index == 6):
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        vertex.index - 2) %
                    18, game=game))

        elif(vertex.index == 9 or vertex.index == 11):
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        vertex.index - 4) %
                    18, game=game))

        elif(vertex.index == 14 or vertex.index == 16):
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        vertex.index - 6) %
                    18, game=game))

        elif(vertex.index == 19or vertex.index == 21):
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        vertex.index - 8) %
                    18, game=game))

        elif(vertex.index == 24 or vertex.index == 26):
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        vertex.index - 10) %
                    18, game=game))

        elif(vertex.index == 29):
            colide_vertex.append(
                Vertex_Game.objects.get(
                    level=1, index=(
                        vertex.index - 12) %
                    18, game=game))

    return colide_vertex


def resources_build_roads(player, id):
    game = Game.objects.get(id=id)

    resources = Resources.objects.get(player=player)
    if(resources.lumber > 0 and resources.brick > 0):
        resources.brick -= 1
        resources.lumber -= 1
        resources.save()
        return True
    else:
        return False


def count_roads(id, player):
    game = Game.objects.get(id=id)
    roads = Road.objects.filter(player=player)
    return len(roads)


def colide_vertex_availables(colide_vertexs, game):
    cva = []
    for i in range(0, len(colide_vertexs)):
        if colide_vertexs[i].is_available_for_road:
            cva.append(colide_vertexs[i])

    return cva


def build_road(payload, id, player, method, fc=False):
    game = Game.objects.get(id=id)
    try:
        player_r = Player.objects.get(username=player, game=game)
    except Player.DoesNotExist:
        raise Http404("Player does not belong to the game")

    if method == 'post':
        game = Game.objects.get(id=id)
        player_r = Player.objects.get(game=game, username=player)
        players = Player.objects.filter(game=game)

        vertex = payload[0]
        vertex2 = payload[1]

        try:
            vertex1_wanted = Vertex_Game.objects.get(
                level=int(
                    vertex['level']), index=int(
                    vertex['index']), game=game)
            vertex2_wanted = Vertex_Game.objects.get(
                level=int(
                    vertex2['level']), index=int(
                    vertex2['index']), game=game)
        except Vertex_Game.DoesNotExist:
            raise Http404("Vertice inexistente")

        # if (vertex1_wanted.is_available_for_road):
        colide_vertexs = colliding_vertex(vertex1_wanted)

        if(len(players) == 3 and game.turn_number < 4):
            if vertex2_wanted in colide_vertexs and (
                    vertex2_wanted.is_available_for_road or vertex1_wanted.is_available_for_road):
                if (count_roads(id, player_r) < 2):
                    road = Road(
                        position1=vertex1_wanted,
                        position2=vertex2_wanted,
                        player=player_r)
                    road.save()
                    colide_vertexs2 = colliding_vertex(vertex2_wanted)
                    for cv in colide_vertexs2:
                        cv.is_available_for_road = True
                        cv.save()
                    return 1
        elif(len(players) == 4 and game.turn_number < 5):
            if vertex2_wanted in colide_vertexs and (
                    vertex2_wanted.is_available_for_road or vertex1_wanted.is_available_for_road):
                if (count_roads(id, player_r) < 2):
                    road = Road(
                        position1=vertex1_wanted,
                        position2=vertex2_wanted,
                        player=player_r)
                    road.save()
                    colide_vertexs2 = colliding_vertex(vertex2_wanted)
                    for cv in colide_vertexs2:
                        cv.is_available_for_road = True
                        cv.save()
                    return 1

        elif vertex2_wanted in colide_vertexs and (vertex2_wanted.is_available_for_road or vertex1_wanted.is_available_for_road):
            if (count_roads(id, player_r) < 15):
                if(fc):
                    road = Road(
                        position1=vertex1_wanted,
                        position2=vertex2_wanted,
                        player=player_r)
                    road.save()
                    colide_vertexs2 = colliding_vertex(vertex2_wanted)
                    for cv in colide_vertexs2:
                        cv.is_available_for_road = True
                        cv.save()
                    return (1)
                if (resources_build_roads(player_r, id)):
                    road = Road(
                        position1=vertex1_wanted,
                        position2=vertex2_wanted,
                        player=player_r)
                    road.save()
                    colide_vertexs2 = colliding_vertex(vertex2_wanted)
                    for cv in colide_vertexs2:
                        cv.is_available_for_road = True
                        cv.save()
                    return (1)
                return(2)
            return(3)
        return (0)

    elif method == 'get':
        result = []
        resources = Resources.objects.get(player=player_r)
        if(whos_turn(game) == player):
            if (count_settlement(game.id, player_r) > 0 and ((resources.lumber >=
                                                              1 and resources.brick >= 1) or (count_roads(game.id, player_r) < 2))):
                players = Player.objects.filter(game=game)
                if(len(players) == 3):
                    if(count_roads(game.id, player_r) >= 2 and game.turn_number < 4):
                        return result
                elif(len(players) == 4):
                    if(count_roads(game.id, player_r) >= 2 and game.turn_number < 5):
                        return result
                collide_vertex = []
                the_vertexs = []
                settles = Settlement.objects.filter(player=player_r)
                roads = Road.objects.filter(player=player_r)
                for s in settles:
                    collide_vertex = colliding_vertex(s.position)
                    for c in collide_vertex:
                        the_vertexs.append(
                            ((s.position.level, s.position.index), (c.level, c.index)))
                for r in roads:
                    collide_vertex = colliding_vertex(r.position1)
                    collide_vertex2 = colliding_vertex(r.position2)
                    for c in collide_vertex:
                        k1 = (
                            (r.position1.level, r.position1.index), (c.level, c.index))
                        k2 = (
                            (c.level, c.index), (r.position1.level, r.position1.index))
                        if (k1 not in the_vertexs and k2 not in the_vertexs):
                            the_vertexs.append(k1)
                    for d in collide_vertex2:
                        k1 = (
                            (r.position2.level, r.position2.index), (d.level, d.index))
                        k2 = (
                            (d.level, d.index), (r.position2.level, r.position2.index))
                        if (k1 not in the_vertexs and k2 not in the_vertexs):
                            the_vertexs.append(k1)

                the_vertexs = list(dict.fromkeys(the_vertexs))
                roads = (Road.objects.filter(player=player_r))
                if len(roads) > 0:
                    for r in roads:
                        road = ((r.position1.level, r.position1.index),
                                (r.position2.level, r.position2.index))
                        road_1 = ((r.position2.level, r.position2.index),
                                  (r.position1.level, r.position1.index))
                        if road in the_vertexs:
                            the_vertexs.remove(road)
                        elif road_1 in the_vertexs:
                            the_vertexs.remove(road_1)
                the_vertexs = remove_duplicates(the_vertexs)
                response = []
                for v in the_vertexs:
                    result = []
                    for v2 in v:
                        my_road = {}
                        my_road['level'] = v2[0]
                        my_road['index'] = v2[1]
                        result.append(my_road)
                    response.append(result)
                return response
            else:
                return result
        else:
            return result

        '''
        vertexs = Vertex_Game.objects.filter(game = game)
        collide_vertex = []
        the_vertexs = []
        if( whos_turn(game)==player):
            for each in vertexs:
                collide_vertex = colliding_vertex(each)
                for c in collide_vertex:
                    the_vertexs.append(((each.level,each.index),(c.level,c.index)))
            the_vertexs = list(dict.fromkeys(the_vertexs))
            roads = (Road.objects.filter(player = player_r))
            if len(roads)>0:
                for r in roads:
                    road = ((r.position1.level,r.position1.index),(r.position2.level,r.position2.index))
                    road_1 = ((r.position2.level,r.position2.index),(r.position1.level,r.position1.index))
                    if road in the_vertexs:
                        the_vertexs.remove(road)
                    elif road_1 in the_vertexs:
                        the_vertexs.remove(road_1)
            the_vertexs = remove_duplicates(the_vertexs)
            response = []
            for v in the_vertexs:
                result = []
                for v2 in v:
                    my_road={}
                    my_road['level'] = v2[0]
                    my_road['index'] = v2[1]
                    result.append(my_road)
                response.append(result)
            return response
        else:
            return []
        '''


def remove_duplicates(the_vertexs):
    for each in the_vertexs:
        for each2 in the_vertexs:
            if each[0] == each2[1] and each[1] == each2[0]:
                the_vertexs.remove(each2)
    return the_vertexs


def play_road_building_card(payload, id, player, method):
    game = Game.objects.get(id=id)
    try:
        player_r = Player.objects.get(username=player, game=game)
    except Player.DoesNotExist:
        raise Http404("Player does not belong to the game")

    if method == 'post':
        result1 = 0
        result2 = 0
        try:
            cards = Cards.objects.get(player=player_r)
            if cards.road_building > 0:
                result1 = 1
                result2 = 1
                payload1 = payload[0]
                payload2 = payload[1]
                result1 = build_road(payload1, id, player, method, True)
                result2 = build_road(payload2, id, player, method, True)
                cards.road_building -= 1
                cards.save()
        except(Game.DoesNotExist, User.DoesNotExist):
            raise Http404()
        return [result1, result2]
    elif method == 'get':

        result = []
        resources = Resources.objects.get(player=player_r)
        cards = Cards.objects.get(player=player_r)
        if(whos_turn(game) == player):
            if (count_settlement(game.id, player_r) > 0 and (
                    count_roads(game.id, player_r) < 15) and cards.road_building > 0):
                players = Player.objects.filter(game=game)
                if(len(players) == 3):
                    if(count_roads(game.id, player_r) >= 2 and game.turn_number < 4):
                        return result
                elif(len(players) == 4):
                    if(count_roads(game.id, player_r) >= 2 and game.turn_number < 5):
                        return result
                collide_vertex = []
                the_vertexs = []
                settles = Settlement.objects.filter(player=player_r)
                roads = Road.objects.filter(player=player_r)
                for s in settles:
                    collide_vertex = colliding_vertex(s.position)
                    for c in collide_vertex:
                        the_vertexs.append(
                            ((s.position.level, s.position.index), (c.level, c.index)))
                for r in roads:
                    collide_vertex = colliding_vertex(r.position1)
                    collide_vertex2 = colliding_vertex(r.position2)
                    for c in collide_vertex:
                        k1 = (
                            (r.position1.level, r.position1.index), (c.level, c.index))
                        k2 = (
                            (c.level, c.index), (r.position1.level, r.position1.index))
                        if (k1 not in the_vertexs and k2 not in the_vertexs):
                            the_vertexs.append(k1)
                    for d in collide_vertex2:
                        k1 = (
                            (r.position2.level, r.position2.index), (d.level, d.index))
                        k2 = (
                            (d.level, d.index), (r.position2.level, r.position2.index))
                        if (k1 not in the_vertexs and k2 not in the_vertexs):
                            the_vertexs.append(k1)

                the_vertexs = list(dict.fromkeys(the_vertexs))
                roads = (Road.objects.filter(player=player_r))
                if len(roads) > 0:
                    for r in roads:
                        road = ((r.position1.level, r.position1.index),
                                (r.position2.level, r.position2.index))
                        road_1 = ((r.position2.level, r.position2.index),
                                  (r.position1.level, r.position1.index))
                        if road in the_vertexs:
                            the_vertexs.remove(road)
                        elif road_1 in the_vertexs:
                            the_vertexs.remove(road_1)
                the_vertexs = remove_duplicates(the_vertexs)
                response = []
                for v in the_vertexs:
                    result = []
                    for v2 in v:
                        my_road = {}
                        my_road['level'] = v2[0]
                        my_road['index'] = v2[1]
                        result.append(my_road)
                    response.append(result)
                return response
            else:
                return result
        else:
            return result


def move_robber(payload, id, player, method):
    if method == 'post':
        game = Game.objects.get(id=id)
        player_r = Player.objects.get(username=player, game=game)

        try:
            position = payload.get('position')
            level = position.get('level')
            index = position.get('index')
            player_target = payload.get('player')

        except AttributeError:
            raise Http404("payload vacio")

        hex_origin = Hex_Game.objects.filter(has_robber=True, game=game)[0]
        hex_destiny = Hex_Game.objects.filter(
            level=level, index=index, game=game)[0]
        hex_origin.has_robber = False
        hex_destiny.has_robber = True
        try:
            hex_origin.save()
            hex_destiny.save()
        except BaseException:
            return 1
        game.robber_has_moved = True
        game.save()
        #vert = hex_to_vertex(hex_destiny)
        try:
            player_target = Player.objects.get(
                game=game, username=player_target)
        except BaseException:
            player_target = None

        if player_target is not None:
            #player_target = Player.objects.get(game=game,username=player_target)
            select_random = random.choice(ListResources(player_target.id))
            steal_resource(player_r, player_target, select_random)
            return 1
        else:
            return 1
        '''
        sorc = None

        for v in vert:
            try:
                sorc = Settlement.objects.get(position = v)
                continue
            except Settlement.DoesNotExist:
                try:
                    sorc = City.objects.get(position = v)
                    continue
                except City.DoesNotExist:
                    pass

        if sorc is not None:

            try:
                target_player = sorc.player
                select_random = random.choice(ListResources(target_player.id))
                steal_resource(player_r,target_player,select_random)
            except IndexError:
                pass
        '''

    elif method == 'get':

        game = Game.objects.get(id=id)
        if(whos_turn(game) == player):
            if(game.dice_1 + game.dice_2 == 7 and game.robber_has_moved == False):
                player_r = Player.objects.get(username=player, game=game)
                result = available_players_play_knight_card(game, player_r)
                return (result)
            else:
                return []
        else:
            return []


def steal_resource(player, target_player, resource):
    resources_player = Resources.objects.get(player=player)
    resources_target = Resources.objects.get(player=target_player)

    if resource == "lumber":
        resources_target.lumber -= 1
        resources_player.lumber += 1

    elif resource == "ore":
        resources_target.ore -= 1
        resources_player.ore += 1

    elif resource == "wool":
        resources_target.wool -= 1
        resources_player.wool += 1

    elif resource == "brick":
        resources_target.brick -= 1
        resources_player.brick += 1

    elif resource == "grain":
        resources_target.grain -= 1
        resources_player.grain += 1
    else:
        raise Http404("Fail to get resource")

    resources_target.save()
    resources_player.save()


def hex_to_vertex(hex_game):

    game = hex_game.game
    vertexs = []

    if hex_game.level == 0:
        for i in range(0, 6):
            vert = Vertex_Game.objects.get(level=0, index=i, game=game)
            vertexs.append(vert)

    elif hex_game.level == 1:
        list_hexone = list_hex(hex_game.index)
        list_hex2one = list_hex2(hex_game.index)

        for index in list_hexone:
            vertex_position = Vertex_Game.objects.get(
                level=1, index=index, game=game)
            vertexs.append(vertex_position)

        for index in list_hex2one:
            vertex_position = Vertex_Game.objects.get(
                level=0, index=index, game=game)
            vertexs.append(vertex_position)

    elif hex_game.level == 2:
        if hex_game.index % 2 == 0:
            list_hextwo = list_hex3(hex_game.index)
            list_hex2two = list_hex4(hex_game.index)

            for index in list_hextwo:
                vertex_position = Vertex_Game.objects.get(
                    level=2, index=index, game=game)
                vertexs.append(vertex_position)

            for index in list_hex2two:
                vertex_position = Vertex_Game.objects.get(
                    level=1, index=index, game=game)
                vertexs.append(vertex_position)

        else:
            list_hextwo1 = list_hex5(hex_game.index)
            list_hex2two2 = list_hex6(hex_game.index)

            for index in list_hextwo1:
                vertex_position = Vertex_Game.objects.get(
                    level=2, index=index, game=game)
                vertexs.append(vertex_position)

            for index in list_hex2two2:
                vertex_position = Vertex_Game.objects.get(
                    level=1, index=index, game=game)
                vertexs.append(vertex_position)

    return vertexs


def check_SorC(hex_pos, player_r, game):

    exists = False
    list_vert = hex_to_vertex(hex_pos)

    for vert in list_vert:

        try:
            settle = Settlement.objects.get(position=vert, player=player_r)
            exists = True

        except Settlement.DoesNotExist:
            try:
                cy = City.objects.get(position=vert, player=player_r)
                exists = True
            except City.DoesNotExist:
                pass

    return exists


def play_knight_card(payload, id, player, method):
    if method == 'post':
        result = 0
        game = Game.objects.get(id=id)
        target = payload.get('player')
        new_thief_pos = payload.get('position')
        pos_level_hex = int(new_thief_pos['level'])
        pos_index_hex = int(new_thief_pos['index'])
        try:
            old_hex_robber = Hex_Game.objects.get(has_robber=True, game=game)
            new_hex_robber = Hex_Game.objects.get(
                level=pos_level_hex, index=pos_index_hex, game=game)
        except Hex_Game.DoesNotExist:
            raise Http404("hexagono no existe")

        player_r = Player.objects.get(username=player, game=game)
        card_player = Cards.objects.get(player=player_r)
        if target is not None:
            try:
                target_player = Player.objects.get(username=target, game=game)

            except Player.DoesNotExist:
                raise Http404("target doesn't exist")

            if(card_player.knight == 0):
                raise Http404("no tienes cartas de caballero")

            select_random = random.choice(ListResources(target_player.id))
            steal_resource(player_r, target_player, select_random)
            old_hex_robber.has_robber = False
            new_hex_robber.has_robber = True
            old_hex_robber.save()
            new_hex_robber.save()
            card_player.knight -= 1
            card_player.save()
            return 1
        else:
            old_hex_robber.has_robber = False
            new_hex_robber.has_robber = True
            old_hex_robber.save()
            new_hex_robber.save()
            card_player.knight -= 1
            card_player.save()
            return 1

    elif method == 'get':

        game = Game.objects.get(id=id)
        player_r = Player.objects.get(username=player, game=game)
        cards = Cards.objects.get(player=player_r)
        result = []
        if(whos_turn(game) == player and cards.knight > 0):
            result = available_players_play_knight_card(game, player_r)
        return result


def available_players_play_knight_card(game, player):
    hexs = Hex_Game.objects.filter(game=game, has_robber=False)
    result = []

    for each in hexs:
        p_players = list_available_players(each, player)
        pos = {}
        hex_pos = {}
        hex_pos["level"] = each.level
        hex_pos["index"] = each.index
        pos["position"] = hex_pos

        list_of_players = []
        value = 1
        for i in p_players:
            if not (i.username in list_of_players):
                list_of_players.append(i.username)

        pos["players"] = list_of_players
        result.append(pos)

    return result


def filter_list_player(list_player, player):
    filtered = []
    for each in list_player:
        resource = Resources.objects.get(player=each)
        if count_resources(resource) > 0 and each.username != player.username:
            filtered.append(each)

    return filtered


def list_available_players(pos_hex, player):

    list_player = []
    list_vert = hex_to_vertex(pos_hex)

    for vert in list_vert:

        try:
            settlement = Settlement.objects.get(position=vert)
            pla = settlement.player
            list_player.append(pla)
        except Settlement.DoesNotExist:
            try:
                city = City.objects.get(position=vert)
                ple = city.player
                list_player.append(ple)
            except City.DoesNotExist:
                pass

    filtered_list = filter_list_player(list_player, player)
    return filtered_list


ACTION_TYPE = [('bank_trade', bank_trade), ('buy_card', buy_card),
               ('build_settlement', build_settlement), ('build_road', build_road),
               ('move_robber', move_robber), ('end_turn', end_turn),
               ('play_road_building_card', play_road_building_card),
               ('play_knight_card', play_knight_card)]

AVAILABLE_ACTIONS = [('build_settlement', build_settlement), ('build_road', build_road),
                     ('upgrade_city', upgrade_city),
                     ('move_robber', move_robber),
                     ('play_road_building_card', play_road_building_card),
                     ('play_knight_card', play_knight_card),
                     ('buy_card', buy_card), ('bank_trade', bank_trade), ('end_turn', end_turn)]


@csrf_exempt
def validate(request):
    token_post = request.META.get('HTTP_AUTHORIZATION')
    token_found = None
    for token in Token.objects.all():
        if "Bearer " + str(token.key) == token_post:
            token_found = token
            return True, token_found
    if token_found is None:
        return False, 0


@csrf_exempt
def actions(request, id, player):
    game = Game.objects.get(id=id)
    current_player = whos_turn(game)
    is_valid, token = validate(request)
    request.user = token.user
    player = request.user.username

    if (request.method == 'GET'):

        payload = {}
        response_final = []
        if(game.winner is None):
            for action, function in AVAILABLE_ACTIONS:
                result = {}
                response = function(payload, id, player, 'get')

                if action == 'move_robber':
                    if response != []:
                        response_final = []
                        result['type'] = action
                        result['payload'] = response
                        response_final.append(result)
                        return JsonResponse(response_final, safe=False)

                if response != []:
                    result['type'] = action
                    result['payload'] = response
                    response_final.append(result)

        return JsonResponse(response_final, safe=False)

    elif(request.method == 'POST'):
        json_request = json.loads(request.body)
        try:
            action_type = json_request.get('type')
            payload = json_request.get('payload')
        except AttributeError:
            raise Http404("Invalid request.")
        for action, function in ACTION_TYPE:
            if action_type == action:
                response = function(payload, id, player, 'post')
                if action == 'play_road_building_card':
                    if response[0] != 1 and response[1] != 1:
                        return JsonResponse(response, status=403, safe=False)
                    else:
                        return JsonResponse(response, safe=False)
                elif response != 1:
                    return JsonResponse(response, status=403, safe=False)
                else:
                    return JsonResponse(response, safe=False)
        raise Http404("Invalid Action")
