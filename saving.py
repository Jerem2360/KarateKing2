from typing import Any
from tools import Registry
import pickle


class Data:
    def __init__(self, player: Registry, ERegistry: Registry, MapStatus: Registry):
        self.player = player
        self.entities = ERegistry
        self.map = MapStatus

    def save(self, directory):
        with open(directory + "/map.txt", mode="w+") as text_io:
            pickle.dump(self.map, text_io)
        with open(directory + "/entities.txt", mode="w+") as text_io:
            pickle.dump(self.entities, text_io)
        with open(directory + "/player.txt", mode="w+") as text_io:
            pickle.dump(self.player, text_io)

    @classmethod
    def load(cls, directory):

        map_ = cls._openload(directory + "/map.txt")
        entities = cls._openload(directory + "/entities.txt")
        player = cls._openload(directory + "/player.txt")
        return map_, entities, player

    @staticmethod
    def _openload(file):
        try:
            text_io = open(file, "r+")
        except FileNotFoundError:
            raise FileNotFoundError(f"Unknown file or directory '{file}'.")
        try:
            result = pickle.load(text_io)
        except pickle.UnpicklingError:
            raise ValueError("Object can't be saved correctly.")
        finally:
            text_io.close()

        return result




