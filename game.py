from const import module, en_us
from tools import Registry
import window
from typing import Literal, Any, Final
import logger
from triggers import Trigger
import gui
import pygame
import sys
import time
import pygame.constants
import map
import entity
import thread
from os import PathLike
import logging
import const


Sprite = pygame.sprite.Sprite
Surface = pygame.Surface


class _Key:
    def __init__(self):
        self.p = pygame

    def __getitem__(self, item: str):
        return self.p.__getattr__(f"K_{item}")


keys = _Key()


def check_key_type(to_check: pygame.event.Event, key: int):
    return to_check.type == key


@Trigger
def OnGameStarts(modlist: dict, win: window.Window, game_) -> tuple[Literal[0, 1], Any] or Literal[0, 1]:
    """
    A trigger that you can override freely and safely to do custom actions on game starts.
    'modlist' is a dict[str, module] of currently active mods,
    in the form of python modules, with their display name.
    See the Trigger class for more details.
    """
    return 0


@Trigger
def OnKeyPressed(key, game, window_):
    """
    Same as OnGameStarts, but activates only when a pygame event is triggered.
    """
    return 0


@Trigger
def OnExit(game, window_):
    """
    Same as OnGameStarts, but activates only when game attempts to exit.
    """
    return 0


@Trigger
def OnMapUnload(map_: map.MapTMX, win: window.Window, game_):
    """
    Same as OnGameStarts, but activates only when a map is unloaded.
    """
    return 0


@Trigger
def OnGUIUnload(gui_: gui.GUI, win: window.Window, game_):
    """
    Same as OnGameStarts, but activates only when a GUI is unloaded.
    """
    return 0


@Trigger
def OnReadyToLoadMap(window_, game_):
    """
    Same as OnGameStarts, but activates only when the game is ready to load it's first map.
    """
    return 0


class Game:
    def __init__(self, mods: dict[str, module]):

        self.disable_pyscroll_log()
        self._map_t = None
        self._ent_t = None
        self.running = False
        self._status = "menu"
        self.clock = pygame.time.Clock()
        modlist: Final = mods
        pygame.init()
        # open window:
        self.win = window.Window(en_us.DEFAULT_TITLE)
        logger.RenderThreadInfo.log("Finishing up...")

        self._active_map = None
        self.screen = self.win.screen
        # run trigger:
        OnGameStarts(modlist, self.win, self)
        logger.RenderThreadInfo.log("Done!")
        self.in_menu = False
        self.mainloop()

    @staticmethod
    def disable_pyscroll_log():
        pyscroll_logger = logging.getLogger('orthographic')
        pyscroll_logger.disabled = True

    def exit(self):
        logger.RenderThreadInfo.log("Exiting game...")
        OnExit(self, self.win)
        pygame.quit()
        sys.exit()

    @staticmethod
    def unload_registry(reg: Registry):
        for k, v in reg:
            v.active = False

    def load_menu(self, menu: gui.Menu):
        self.unload_registry(gui.menu_registry)
        self.unload_registry(map.map_registry)
        self._status = "frozen"

        menu.active = True
        self._status = "menu"

    def load_map(self, map_: map.MapTMX):
        self._status = "frozen"
        self.unload_registry(gui.menu_registry)
        self.unload_registry(map.map_registry)

        map_.active = True
        self._status = "map"

    def update_registry(self, reg: Registry, on_unload: Trigger):
        for k, v in reg:
            v.update(self.screen)
            v.on_unload = on_unload

    def handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.exit()
            OnKeyPressed(event.type, self, self.win)

    def mainloop(self):
        self.running = True

        while self.running:

            self.handle_inputs()

            if self._status == "map":
                self.update_registry(map.map_registry, OnMapUnload)

            if self._status == "menu":
                self.update_registry(gui.menu_registry, OnGUIUnload)

            if self._status == "frozen":
                self.screen.fill((0, 0, 0))

            if self._status == "load_first_map":
                OnReadyToLoadMap(self.win, self)

            self.clock.tick(const.MAX_FPS)

    def new_map(self, tmx: str or PathLike, center: tuple[int, int], zoom: int or float) -> map.MapTMX:
        return map.MapTMX(tmx, OnMapUnload, self, center, zoom)

    def new_menu(self, bg: str or PathLike) -> gui.Menu:
        return gui.Menu(bg, self, OnMapUnload)

    def status(self, status: Literal["frozen", "menu", "map", "load_first_map"]):
        self._status = status

