import json
from django.http import HttpResponse, JsonResponse, Http404
from .models import *
from games.models import *
from .serializer import *
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.defaults import page_not_found
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
import names
from rest_framework.response import Response
from rest_framework import viewsets
from lobby.aux import *


import random


@csrf_exempt
@api_view(["GET"])
def list_room(request):
    try:
        rooms = Room.objects.all()
    except Room.DoesNotExist:
        return JsonResponse({}, safe=False)
    serializer = RoomSerializer(rooms, many=True)
    return JsonResponse(serializer.data, safe=False)


def get_lobby(request, id_room):
    try:
        lobby = Room.objects.get(pk=id_room)
    except Room.DoesNotExist:
        return JsonResponse({}, safe=False)
    serializer = RoomSerializer(lobby, many=False)

    return JsonResponse(serializer.data, safe=False)


def create(request, token):
    name = json.loads(request.body)['name']

    try:
        names = Room.objects.get(name=name)
        raise Http404("La room ya existe")
    except Room.DoesNotExist:
        board = json.loads(request.body)['board_id']
        try:
            the_board = Board.objects.get(id=board)
        except Board.DoesNotExist:
            raise Http404("El board no existe")

        owner = token.user
        new_room = Room(name=name, owner=owner, board=board)
        new_room.save()
        my_room = Room.objects.get(name=name)
        users = User_in_room(name=owner, room=new_room)
        users.room_id = my_room.pk
        users.save()

        serializer = RoomSerializer(new_room, many=False)
        response = JsonResponse(serializer.data, safe=False)
        return response


def join_lobby(request, id_room, token):
    try:
        room = Room.objects.get(pk=id_room, game_has_started=False)
    except Room.DoesNotExist:
        raise Http404(
            "No existe ninguna room con ese id o ya ha iniciado la partida!")
    try:
        user = User_in_room.objects.filter(room_id=id_room)
    except BaseException:
        raise Http404("La sala esta vacia, ni el owner esta presente!")
    current_players = len(user)

    if current_players < room.max_players:
        user = User_in_room(name=token.user.username)
        user.room_id = id_room
        user.save()
    else:
        raise Http404("La sala seleccionada esta llena")
    return HttpResponse('')


def start_game(request, id_room, token):
    user_start = token.user
    try:
        room = Room.objects.get(owner=user_start, pk=id_room)
        board_id = room.board

    except Room.DoesNotExist:
        raise Http404("No hay ninguna room con este usuario")
    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404("Board inexistente")

    if room.game_has_started:
        raise Http404("La room ya empezo")
    else:
        users = User_in_room.objects.filter(room_id=room.id)
        current_players = len(users)
        if current_players >= 3 and current_players <= 4:
            new_game = Game()
            new_game.save()
            create_vertex(new_game)
            create_hexgame(new_game, board)
            create_players(users, new_game)
            create_turns(users, new_game)

            room.game_has_started = True
            room.game_id = new_game.id
            room.save()

            return HttpResponse("Partida iniciada")
        else:
            raise Http404("Room no alcanza la cantidad minima de jugadores")


def cancel_lobby(request, id_room, token):
    user_start = token.user.username
    try:
        room = Room.objects.get(id=id_room, owner=user_start)
    except Room.DoesNotExist:
        raise Http404("Room no existe")

    if room.game_has_started == False:
        room.delete()
        return HttpResponse()
    else:
        raise Http404("La partida ya fue iniciada y no puede cancelarse")


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
def select(request, id_room=0):
    is_valid, token = validate(request)
    if is_valid:
        if id_room != 0:
            if request.method == "GET":
                return get_lobby(request, id_room)
            elif request.method == "PATCH":
                return start_game(request, id_room, token)

            elif request.method == "DELETE":
                return cancel_lobby(request, id_room, token)

            elif request.method == "PUT":
                return join_lobby(request, id_room, token)
        else:

            if request.method == "POST":
                return create(request, token)
            elif request.method == "GET":
                return list_room(request)
    else:
        return JsonResponse({'error': 'Invalid Credentials'},
                            status=HTTP_404_NOT_FOUND)
