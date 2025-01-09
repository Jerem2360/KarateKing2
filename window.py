import pygame
from os import PathLike


class Window:
    def __init__(self, default_title: str):
        self.screen = pygame.display.set_mode((720, 480))
        self.title(default_title)

    @staticmethod
    def title(title: str, icon: str or PathLike = None):
        if icon is not None:
            pygame.display.set_caption(title, icon)
            return
        pygame.display.set_caption(title)
