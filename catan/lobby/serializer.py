from rest_framework import serializers
from lobby.models import Room


class RoomSerializer(serializers.ModelSerializer):
    players = serializers.StringRelatedField(many=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'owner',
            'players',
            'max_players',
            'game_id',
            'game_has_started']
