from django.test import TestCase
from rest_framework.test import APIClient
from .models import *
from rest_framework.test import APIRequestFactory
from django.test.client import RequestFactory
from .views import *
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from copy import copy

from django.test import Client


class BoardTest(TestCase):
    def setUp(self):
        self.game = Game()
        self.game.save()

        self.board = Board(name='board_test')
        self.board.save()

        self.hex = Hex(resource='ore', token='1', board=self.board)
        self.hex.save()

        self.hex_pos = Hex_Position(hex=self.hex, index=1, level=1)
        self.hex_pos.save()

    def test_Fields(self):
        newHex = Hex(resource='wool', token='10', board=self.board)
        newHex.save()
        record = Hex.objects.get(id=newHex.id)
        self.assertEqual(record.token, 10)

    def test_newHex(self):
        newHex = Hex()
        newHex.board = self.board
        newHex.resource = 'grain'
        newHex.save()

        record = Hex.objects.get(id=newHex.id)
        self.assertEqual(record, newHex)

    def test_anotherBoard(self):
        otherGame = Game()
        otherGame.save()
        otherBoard = Board(name='board_test')
        otherBoard.save()
        newHex = Hex(resource='lumber', token=5, board=otherBoard)
        newHex.save()
        newPos = Hex_Position(level=2, index=0, hex=newHex)
        newPos.save()

        otherHexes = Hex.objects.filter(board=otherBoard)
        isOre = otherHexes.filter(resource='ore').exists()
        isLumber = otherHexes.filter(resource='lumber').exists()
        self.assertTrue(isLumber & (not isOre))


class ResourcesTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.client = APIClient()
        user = User.objects.create(username='test', password='ivi')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)
        self.player = Player.objects.create(username='test', game=self.game)
        self.resource = Resources.objects.create(
            lumber=1, wool=1, grain=1, brick=1, ore=1, player=self.player)
        Cards.objects.create(player=self.player)
        self.factory = RequestFactory()

    def test_resource(self):
        resource = Resources.objects.get(player=self.player)
        self.assertEqual(resource.lumber, 1)

    def test_list_resources(self):

        response = ListResources(self.player.id)

        self.assertEqual(response, ["lumber", "wool", "grain", "brick", "ore"])


class CardsTestCase(TestCase):

    def setUp(self):
        self.game = Game.objects.create()
        self.client = APIClient()
        user = User.objects.create(username='test', password='ivi')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)
        self.player = Player.objects.create(
            username='test', colour='red', game=self.game)
        Cards.objects.create(
            road_building=1,
            year_of_plenty=2,
            monopoly=3,
            victory_point=4,
            knight=5,
            player=self.player)
        Resources.objects.create(player=self.player)
        self.factory = RequestFactory()

    def test_list_cards(self):

        response = ListCards(self.player.id)
        self.assertEqual(response, ["road_building", "year_of_plenty",
                                    "year_of_plenty", "monopoly", "monopoly", "monopoly", "victory_point",
                                    "victory_point", "victory_point", "victory_point", "knight",
                                    "knight", "knight", "knight", "knight"])


class BankTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.player = Player.objects.create(
            username='banktest', game=self.game)
        self.resources = Resources.objects.create(player=self.player)
        self.player_two = Player.objects.create(
            username='player_two', game=self.game)
        self.player_three = Player.objects.create(
            username='player_three', game=self.game)
        self.player_four = Player.objects.create(
            username='player_four', game=self.game)
        self.turns = Turns.objects.create(
            game=self.game,
            first_turn=self.player,
            second_turn=self.player_two,
            third_turn=self.player_three,
            fourth_turn=self.player_four
        )
        self.factory = RequestFactory()

    def test_correct_params(self):
        game_id = self.game.id
        player = Player.objects.get(id=self.player.id)
        resources = player.resources
        resources.lumber = 4
        resources.grain = 0
        resources.save()
        payload = {"give": "lumber", "receive": "grain"}
        bank_trade(payload, game_id, player.username, 'post')
        changed_player = Player.objects.get(id=self.player.id)
        changed_resources = changed_player.resources
        self.assertEqual(changed_resources.lumber, 0)
        self.assertEqual(changed_resources.grain, 1)


class PlayRoadBuildingCardTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()

        self.client = APIClient()
        user = User.objects.create(
            username='PlayRoadBuildingcardtest',
            password='ivi')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        self.player = Player.objects.create(
            username='PlayRoadBuildingcardtest', game=self.game)
        self.player_two = Player.objects.create(
            username='player_two', game=self.game)
        self.player_three = Player.objects.create(
            username='player_three', game=self.game)
        self.player_four = Player.objects.create(
            username='player_four', game=self.game)
        self.turns = Turns.objects.create(
            game=self.game,
            first_turn=self.player,
            second_turn=self.player_two,
            third_turn=self.player_three,
            fourth_turn=self.player_four
        )

        cards = Cards.objects.create(player=self.player)
        self.factory = RequestFactory()
        self.vertex_game1 = Vertex_Game(level=2, index=25, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game1.save()
        self.vertex_game2 = Vertex_Game(level=2, index=24, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game2.save()
        self.vertex_game3 = Vertex_Game(level=2, index=23, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game3.save()
        self.vertex_game4 = Vertex_Game(level=2, index=22, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game4.save()
        self.vertex_game5 = Vertex_Game(level=2, index=26, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game5.save()
        self.vertex_game6 = Vertex_Game(level=1, index=14, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game6.save()
        self.vertex_game7 = Vertex_Game(level=2, index=21, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game7.save()
        self.resources = Resources.objects.create(player=self.player)

        cards.road_building = 11

        cards.save()


# falta corregir asentamientos en vertices

    def test_play_build_road_card(self):
        payload = [[{"level": "2", "index": "25"},
                    {"level": "2", "index": "24"}], [{"level": "2", "index": "23"},
                                                     {"level": "2", "index": "22"}]]
        id = self.game.id
        player = self.player.username
        result = play_road_building_card(payload, id, player, 'post')

        self.assertEqual(result, [1, 1])
        cards = Cards.objects.get(player=self.player)
        self.assertEqual(cards.road_building, 10)

    def test_correct_params(self):
        game_id = self.game.id
        player = Player.objects.get(id=self.player.id)

        username = player.username

        path = '/games/' + str(game_id) + '/player/actions/'
        data = {
            'type': 'play_road_building_card',
            'payload': [[{'level': 2, "index": 25}, {'level': 2, 'index': 24}], [{'level': 2, 'index': 23},
                                                                                 {'level': 2, 'index': 22}]]}

        response = self.client.post(
            path, data, format="json")

        self.assertEqual(response.content, b'[1, 1]')
        cards = Cards.objects.get(player=self.player)
        roads = Road.objects.filter(player=player)
        self.assertEqual(len(roads), 2)
        self.assertEqual(cards.road_building, 10)


class EndTurnTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create(turn_number=4)

        self.client = APIClient()
        user = User.objects.create(username='ivi', password='ivi')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        self.player_one = Player.objects.create(
            username='player_one', game=self.game)
        self.resources_one = Resources.objects.create(player=self.player_one)
        self.player_two = Player.objects.create(
            username='player_two', game=self.game)
        self.resources_two = Resources.objects.create(player=self.player_two)
        self.player_three = Player.objects.create(
            username='player_three', game=self.game)
        resources_three = Resources.objects.create(player=self.player_three)
        self.player_four = Player.objects.create(
            username='player_four', game=self.game)
        resources_four = Resources.objects.create(player=self.player_four)
        self.turns = Turns.objects.create(
            game=self.game,
            first_turn=self.player_one,
            second_turn=self.player_two,
            third_turn=self.player_three,
            fourth_turn=self.player_four
        )

        HEX_LIST = [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
        for (l, i) in HEX_LIST:
            random_resource = random.choice(RESOURCE_TYPES)
            random_token = random.randrange(2, 12)
            Hex_Game.objects.create(
                game=self.game,
                level=l,
                index=i,
                token=random_token,
                resource=random_resource
            )
        for n in range(0, 2):
            if n == 0:
                bound = 6 * (n + 1)
            else:
                bound = 6 * (n + 2)
            for m in range(0, bound):
                Vertex_Game.objects.create(game=self.game, level=n, index=m)
        position_one = Vertex_Game.objects.get(level=0, index=0)
        position_one.is_available_for_building = False
        position_one.save()
        self.settlement_one = Settlement.objects.create(
            player=self.player_two, position=position_one)
        position_two = Vertex_Game.objects.get(level=0, index=2)
        position_two.is_available_for_building = False
        position_two.save()
        self.settlement_two = Settlement.objects.create(
            player=self.player_one, position=position_two)
        self.factory = RequestFactory()

    def test_normal_resource_distribution(self):
        P1_HEXES = [(0, 0), (1, 1), (1, 2)]
        p1_prev_resources = copy(self.resources_one)
        hex_gain = Hex_Game.objects.filter(game=self.game, token=6)
        p1_gains = set()
        for h in hex_gain:
            position = (h.level, h.index)
            if position in P1_HEXES:
                p1_gains.add(h.resource)
        distribute_resources(6, self.game)
        p1 = Player.objects.get(id=self.player_one.id)
        p1_curr_resources = p1.resources
        for resource in p1_gains:
            p1_prev_amount = getattr(p1_prev_resources, resource)
            p1_curr_amount = getattr(p1_curr_resources, resource)
            self.assertNotEqual(p1_prev_amount, p1_curr_amount)

    def test_desert_token_distribution(self):
        P2_HEXES = [(0, 0), (1, 0), (1, 5)]
        hex_zero = Hex_Game.objects.get(level=0, index=0)
        hex_zero.resource = 'desert'
        hex_zero.token = 5
        hex_zero.save()
        p2_prev_resources = copy(self.resources_two)
        hex_gain = Hex_Game.objects.filter(game=self.game, token=5)
        p2_gains = set()
        for h in hex_gain:
            position = (h.level, h.index)
            if position in P2_HEXES:
                if h.resource in RESOURCE_TYPES:
                    p2_gains.add(h.resource)
        distribute_resources(5, self.game)
        p2 = Player.objects.get(id=self.player_two.id)
        p2_curr_resources = p2.resources
        for resource in p2_gains:
            p2_prev_amount = getattr(p2_prev_resources, resource)
            p2_curr_amount = getattr(p2_curr_resources, resource)
            self.assertNotEqual(p2_prev_amount, p2_curr_amount)

    def test_endpoint(self):
        game_id = self.game.id

        path = '/games/' + str(game_id) + '/player/actions/'
        data = {
            'type': 'end_turn',
            'payload': {}
        }

        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, 200)


class PlayKnightCardTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.client = APIClient()
        user = User.objects.create(username='knightTest', password='ivi')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

        self.player = Player.objects.create(
            username='knightTest', game=self.game)
        resources = Resources.objects.create(player=self.player)
        self.player_two = Player.objects.create(
            username='player_two', game=self.game)
        self.player_three = Player.objects.create(
            username='player_three', game=self.game)
        self.player_four = Player.objects.create(
            username='player_four', game=self.game)
        self.turns = Turns.objects.create(
            game=self.game,
            first_turn=self.player,
            second_turn=self.player_two,
            third_turn=self.player_three,
            fourth_turn=self.player_four
        )

        cards = Cards.objects.create(player=self.player)
        self.playerTarget = Player.objects.create(
            username='knightTestTarget', game=self.game)
        resourcesTarget = Resources.objects.create(player=self.playerTarget)
        self.factory = RequestFactory()
        # hex_object
        self.hex_gameTarget = Hex_Game(level=2, index=9, token=5, has_robber=False, game=self.game,
                                       resource='grain')
        self.hex_gameTarget.save()
        # hex_robber
        self.hex_gameRobber = Hex_Game(level=2, index=5, token=4, has_robber=True, game=self.game,
                                       resource='grain')
        self.hex_gameRobber.save()

        # vertex_object
        self.vertex_game1 = Vertex_Game(level=2, index=24, is_available_for_road=True,
                                        is_available_for_building=False, game=self.game)
        self.vertex_game1.save()
        self.vertex_game2 = Vertex_Game(level=2, index=23, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game2.save()
        self.vertex_game3 = Vertex_Game(level=2, index=22, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game3.save()
        self.vertex_game4 = Vertex_Game(level=2, index=21, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game4.save()
        self.vertex_game5 = Vertex_Game(level=1, index=13, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game5.save()
        self.vertex_game6 = Vertex_Game(level=1, index=14, is_available_for_road=True,
                                        is_available_for_building=True, game=self.game)
        self.vertex_game6.save()

        self.settlementTarget = Settlement(
            position=self.vertex_game1,
            player=self.playerTarget)
        self.settlementTarget.save()

        cards.knight = 1
        cards.save()
        resourcesTarget.lumber = 1
        resourcesTarget.save()

    def test_play_knight_road_card(self):
        payload = {
            "position": {
                "level": "2",
                "index": "9"},
            "player": "knightTestTarget"}
        id = self.game.id
        player = self.player.username
        play_knight_card(payload, id, player, 'post')
        cards = Cards.objects.get(player=self.player)
        self.assertEqual(cards.knight, 0)

    def test_KnightCard_correct_params(self):
        game_id = self.game.id
        player = Player.objects.get(id=self.player.id)
        cards = Cards.objects.get(player=player)
        username = player.username
        playerTarget = Player.objects.get(username='knightTestTarget')

        path = '/games/' + str(game_id) + '/player/actions/'
        data = {
            'type': 'play_knight_card',
            'payload': {'position': {'level': 2, 'index': 9}, 'player': 'knightTestTarget'}}
        #json_data = json.dumps(data)

        response = self.client.post(
            path, data, format="json")

        hex_robber_new = Hex_Game.objects.get(has_robber=True)
        self.assertEqual(hex_robber_new.index, 9)
        cards = Cards.objects.get(player=self.player)
        resources = Resources.objects.get(player=self.player)
        self.assertEqual(resources.lumber, 1)
        self.assertEqual(cards.knight, 0)
