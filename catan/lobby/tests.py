from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework.test import APIRequestFactory
from .models import *
from django.contrib.auth.models import User
from .views import list_room
from django.views.generic import TemplateView
from django.test import Client
from logueo.views import *
import json
from rest_framework.test import APIClient
from django.db import models
import random
from games.models import *


class RoomTestCase(TestCase):
    def setUp(self):
        Room.objects.create(name='test-room', owner='agustina')

    def test_get_name(self):
        name = Room.objects.get(name='test-room').name
        self.assertEqual(name, 'test-room')

    def test_get_owner(self):
        owner = Room.objects.get(owner='agustina').owner
        self.assertEqual(owner, 'agustina')

    def test_get_max_players(self):
        max_players = Room.objects.get(name='test-room').max_players
        self.assertEqual(max_players, 4)


class User_in_roomTestCase(TestCase):

    def setUp(self):
        Room.objects.create(name='test-room', owner='ivanovich')
        User_in_room.objects.create(
            name='tester', room=Room.objects.get(
                name='test-room'))

    def test_get_name(self):
        name = User_in_room.objects.get(name='tester').name
        self.assertEqual(name, 'tester')

    def test_get_name_of_room_from_user_relation(self):
        name = User_in_room.objects.get(name='tester').room.name
        self.assertEqual(name, 'test-room')


class listTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        Room.objects.create(name='test-room', owner='agustina')

    def test_list_room(self):
        request = self.factory.get('/rooms')
        response = list_room(request)
        self.assertEqual(response.status_code, 200)


class listVoidTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_room(self):
        request = self.factory.get('/rooms')
        response = list_room(request)
        self.assertEqual(response.status_code, 200)


class unirse_no_roomTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_room(self):
        request = self.factory.get('/rooms/-1/')
        response = list_room(request)
        self.assertRaises(Room.DoesNotExist)


class PlayerTestCase(TestCase):

    def setUp(self):
        Room.objects.create(name='test-room', owner='ivi')
        self.factory = RequestFactory()

    def test_add_players(self):
        id_room = (Room.objects.get(name='test-room')).id
        for x in range(
            1, (Room.objects.get(
                name='test-room').max_players) * 50):
            request = self.factory.get('/rooms/%d/' % id_room)
        user = len(User_in_room.objects.filter(room_id=id_room))
        self.assertLessEqual(
            user, Room.objects.get(
                name='test-room').max_players)


class CancelLobbyTestCase(TestCase):
    def setUp(self):
        Room.objects.create(name='test-room', owner='ivi')
        self.client = APIClient()
        user = User.objects.create(username='ivi', password='ivi')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

    def test_cancel_lobby_not_inited(self):
        id_room = Room.objects.get(name='test-room').id
        response = self.client.delete('/rooms/%d/' % id_room)
        self.assertEqual(response.status_code, 200)

    def test_cancel_lobby_inited(self):

        room = Room.objects.get(name='test-room', owner='ivi')
        room.game_has_started = True
        room.save()

        response = self.client.delete('/rooms/%d/' % room.id)

        self.assertEqual(response.status_code, 404)


def random_resource():
    rand = random.randrange(1, 5)
    if rand == 1:
        return 'brick'
    elif rand == 2:
        return 'lumber'
    elif rand == 3:
        return 'wool'
    elif rand == 4:
        return 'grain'
    elif rand == 5:
        return 'ore'


class StartGameTestCase(TestCase):

    def setUp(self):
        name = 'Board 1'
        board = Board(name=name)
        board.save()
        choice = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12]
        resource_choice = ['brick', 'lumber', 'wool', 'grain', 'ore']
        for i in range(1, 20):
            if i == 7 or i == 19 or i == 12:
                hex = Hex(board=board, token=random.choice(choice),
                          resource=random.choice(resource_choice))
                hex.save()
            hex = Hex(
                board=board, token=i %
                12, resource=random.choice(resource_choice))
            hex.save()

        hexes = Hex.objects.filter(board=board)
        hex = random.choice(hexes)
        hex.resource = 'desert'
        hex.save()

        hex = Hex.objects.get(board=board, resource='desert')
        hex.has_robber = True
        hex.save()

        hexes = Hex.objects.filter(board=board.id)
        hexp = Hex_Position(level=0, index=0, hex=hexes[0])
        hexp.save()
        for i in range(1, 7):
            hexp = Hex_Position(level=1, index=i - 1, hex=hexes[i])
            hexp.save()
        for i in range(7, 19):
            hexp = Hex_Position(level=2, index=i - 7, hex=hexes[i])
            hexp.save()

        self.client = APIClient()
        user = User.objects.create(username='ivi', password='ivi')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)
        self.test_room = {
            "name": "test-room",
            "board_id": 1}
        create = self.client.post(
            "/rooms/", self.test_room, format="json")
        board = Board.objects.all().first()
        self.assertEqual(board.id, 1)
        self.assertEqual(create.status_code, 200)
        room = Room.objects.get(name='test-room')
        User_in_room.objects.create(room=room, name='tester2')
        User_in_room.objects.create(room=room, name='tester3')

    def test_start_game(self):
        id_room = Room.objects.get(name='test-room').id
        response = self.client.patch('/rooms/%d/' % id_room)
        self.assertEqual(response.status_code, 200)
