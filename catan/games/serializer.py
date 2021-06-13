from rest_framework import serializers
from games.models import Cards, Resources, Game, Hex, Hex_Position, Vertex_Game, Hex_Game, Player,Board


class CardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cards
        fields = ['road_building', 'year_of_plenty',
                  'monopoly', 'victory_point', 'knight']


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = ('lumber', 'wool', 'grain', 'brick', 'ore')


class Hex_PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hex_Position
        fields = ['level', 'index']


class Vertex_GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertex_Game
        fields = ['level', 'index']


class Hex_GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hex_Game
        fields = ['level', 'index']


class Hex_GameSerializer2(serializers.ModelSerializer):

    class Meta:
        model = Hex_Game
        fields = ['terrain', 'token']


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['username']


class HexSerializer(serializers.ModelSerializer):
    position = Hex_PositionSerializer(read_only=True)

    class Meta:
        model = Hex
        fields = ['position', 'resource', 'token']


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ['winner']


class BoardSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Board
        fields = ['id','name']
