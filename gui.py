import pygame
import os
from tools import Registry
import logger
import time


class GUI:
    RegistryName = ("", "")
    component_type = 'menu'
    _active = False

    def __init__(self, game, function_unload):
        self._active = False
        self.game = game
        self.on_unload = function_unload

    def register(self, name: str, module):
        self.RegistryName = module, name
        menu_registry.register(f"{module}:{name}", self)
        logger.RenderThreadInfo.log(f"Registered name '{module}:{name}'.")

    def update(self, *args, **kwargs): pass

    def _register_update(self):
        module, name = self.RegistryName
        menu_registry.register(f"{module}:{name}", self)

    def state(self):
        result = {}
        for item in self.__dict__:
            result[item] = str(item.__class__.__name__) + str(item.__dict__)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value: bool):
        if (not value) and self._active:
            self.on_unload(self, self.game.win, self.game)
        self._active = value


menu_registry = Registry(GUI)


class Button(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], cut_ratio: tuple[float, float], image: str or os.PathLike, command: callable = None):
        super().__init__()

        self.image = pygame.image.load(image)
        new_pos = pos
        new_size = round(self.image.get_rect().width / cut_ratio[0]), round(self.image.get_rect().height / cut_ratio[1])
        new_rect = pygame.rect.Rect(*new_pos, *new_size)
        self.image = pygame.transform.chop(self.image, new_rect)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.command_args = ()
        self.command_kwargs = {}

        self.command = command
        if command is None:
            self.command = self.default_command

    def default_command(self, *args, **kwargs): pass

    def update(self, screen, *args, **kwargs) -> None:
        left, middle, right = pygame.mouse.get_pressed(3)
        if left and self._mouse_on_top():
            self.command(*self.command_args, **self.command_kwargs)

            time.sleep(0.5)

    def _mouse_on_top(self):
        return bool(self.rect.collidepoint(*pygame.mouse.get_pos()))


class Menu(GUI):
    def __init__(self, bg: str or os.PathLike, game, on_unload):
        super().__init__(game, on_unload)
        self.background = pygame.image.load(bg)
        self.background = pygame.transform.scale(self.background, game.screen.get_size())

        self.widgets = pygame.sprite.Group()

    def update(self, screen, *args, **kwargs) -> None:
        if self._active:
            screen.blit(self.background, (0, 0), screen.get_rect())
            self.widgets.draw(screen)
            self.widgets.update(screen, *args, **kwargs)
        pygame.display.flip()
        if self.RegistryName != ("", ""):
            self._register_update()

    def add(self, widget: pygame.sprite.Sprite):
        self.widgets.add(widget)


