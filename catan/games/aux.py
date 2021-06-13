import random

from games.models import *


def generate_dices():
    return random.randrange(1, 6), random.randrange(1, 6)


VERTICES_BY_HEX = {
    (0, 0): [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],
    (1, 0): [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (1, 3)],
    (1, 1): [(0, 1), (0, 2), (1, 3), (1, 4), (1, 5), (1, 6)],
    (1, 2): [(0, 2), (0, 3), (1, 6), (1, 7), (1, 8), (1, 9)],
    (1, 3): [(0, 3), (0, 4), (1, 9), (1, 10), (1, 11), (1, 12)],
    (1, 4): [(0, 4), (0, 5), (1, 12), (1, 13), (1, 14), (1, 15)],
    (1, 5): [(0, 0), (0, 5), (1, 0), (1, 15), (1, 16), (1, 17)],
    (2, 0): [(1, 0), (1, 1), (1, 17), (2, 0), (2, 1), (2, 29)],
    (2, 1): [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (2, 4)],
    (2, 2): [(1, 2), (1, 3), (1, 4), (2, 4), (2, 5), (2, 6)],
    (2, 3): [(1, 4), (1, 5), (2, 6), (2, 7), (2, 8), (2, 9)],
    (2, 4): [(1, 5), (1, 6), (1, 7), (2, 9), (2, 10), (2, 11)],
    (2, 5): [(1, 7), (1, 8), (2, 11), (2, 12), (2, 13), (2, 14)],
    (2, 6): [(1, 8), (1, 9), (1, 10), (2, 14), (2, 15), (2, 16)],
    (2, 7): [(1, 10), (1, 11), (2, 16), (2, 17), (2, 18), (2, 19)],
    (2, 8): [(1, 11), (1, 12), (1, 13), (2, 19), (2, 20), (2, 21)],
    (2, 9): [(1, 13), (1, 14), (2, 21), (2, 22), (2, 23), (2, 24)],
    (2, 10): [(1, 14), (1, 15), (1, 16), (2, 24), (2, 25), (2, 26)],
    (2, 11): [(1, 16), (1, 17), (2, 26), (2, 27), (2, 28), (2, 29)]
}


def random_resource():
    rand = random.randrange(1, 6)
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


def random_desert(board):
    hexes = Hex.objects.filter(board=board)
    hex = random.choice(hexes)
    hex.resource = 'desert'
    hex.save()


def place_robber(board):
    hex = Hex.objects.get(board=board, resource='desert')
    hex.has_robber = True
    hex.save()


def assign_hex_position(board):
    hexes = Hex.objects.filter(board=board.id)
    hexp = Hex_Position(level=0, index=0, hex=hexes[0])
    hexp.save()
    for i in range(1, 7):
        hexp = Hex_Position(level=1, index=i - 1, hex=hexes[i])
        hexp.save()
    for i in range(7, 19):
        hexp = Hex_Position(level=2, index=i - 7, hex=hexes[i])
        hexp.save()


def create_board(name):
    board = Board(name=name)
    board.save()
    choice = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]
    for i in range(1, 20):
        if i == 7 or i == 19 or i == 12 or i == 1 or i == 13:
            hex = Hex(
                board=board,
                token=random.choice(choice),
                resource=random_resource())
            hex.save()
        else:
            hex = Hex(board=board, token=i % 12, resource=random_resource())
            hex.save()
    random_desert(board)
    place_robber(board)
    assign_hex_position(board)


def list_hex(value):

    if value == 0:
        values_of_index = [0, 1, 2, 3]
    elif value == 1:

        values_of_index = [3, 4, 5, 6]
    elif value == 2:

        values_of_index = [6, 7, 8, 9]

    elif value == 3:

        values_of_index = [9, 10, 11, 12]

    elif value == 4:

        values_of_index = [12, 13, 14, 15]
    elif value == 5:

        values_of_index = [15, 16, 17, 0]

    return values_of_index


def list_hex2(value):

    if value == 0:
        values_of_index = [0, 1]
    elif value == 1:

        values_of_index = [1, 2]
    elif value == 2:

        values_of_index = [2, 3]

    elif value == 3:

        values_of_index = [3, 4]

    elif value == 4:

        values_of_index = [4, 5]
    elif value == 5:

        values_of_index = [5, 0]

    return values_of_index


def list_hex3(value):
    if value == 0:
        value_of_index = [29, 0, 1]
    elif value == 2:
        value_of_index = [4, 5, 6]
    elif value == 4:
        value_of_index = [9, 10, 11]
    elif value == 6:
        value_of_index = [14, 15, 16]
    elif value == 8:
        value_of_index = [19, 20, 21]
    elif value == 10:
        value_of_index = [24, 25, 26]
    return value_of_index


def list_hex4(value):
    if value == 0:
        value_of_index = [17, 0, 1]
    elif value == 2:
        value_of_index = [2, 3, 4]
    elif value == 4:
        value_of_index = [5, 6, 7]
    elif value == 6:
        value_of_index = [8, 9, 10]
    elif value == 8:
        value_of_index = [11, 12, 13]
    elif value == 10:
        value_of_index = [14, 15, 16]
    return value_of_index


def list_hex5(value):
    if value == 1:
        value_of_index = [1, 2, 3, 4]
    elif value == 3:
        value_of_index = [6, 7, 8, 9]
    elif value == 5:
        value_of_index = [11, 12, 13, 14]
    elif value == 7:
        value_of_index = [16, 17, 18, 19]
    elif value == 9:
        value_of_index = [21, 22, 23, 24]
    elif value == 11:
        value_of_index = [26, 27, 28, 29]
    return value_of_index


def list_hex6(value):
    if value == 1:
        value_of_index = [1, 2]
    elif value == 3:
        value_of_index = [4, 5]
    elif value == 5:
        value_of_index = [7, 8]
    elif value == 7:
        value_of_index = [10, 11]
    elif value == 9:
        value_of_index = [13, 14]
    elif value == 11:
        value_of_index = [16, 17]
    return value_of_index
