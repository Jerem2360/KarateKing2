from os import PathLike
import pygame
import pytmx
import pyscroll
from tools import Registry
import logger
import entity


class MapTMX:
    def __init__(self, tmx: str or PathLike, function_unload, game, center: tuple[int, int], zoom):
        self.on_unload = function_unload
        self.game = game
        self._center_entity = None
        self._active = False
        self._tmx_data = pytmx.util_pygame.load_pygame(tmx)
        data = pyscroll.data.TiledMapData(self._tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(data, game.screen.get_size())
        self.map_layer.center(center)
        self.map_layer.zoom = zoom
        self.layers = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=5)
        self.center = self.map_layer.center
        self.RegistryName = ""

        self.collide_hitboxes = []
        for obj in self.list_objects():
            if obj.type == 'collision':
                self.collide_hitboxes.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    def get_object_by_name(self, name: str):
        return self._tmx_data.get_object_by_name(name)

    def list_objects(self):
        return self._tmx_data.objects

    def link_sprite(self, sprite: pygame.sprite.Sprite, center=False):
        self.layers.add(sprite)
        if center:
            self._center_entity = sprite

    def update(self, screen, *args, **kwargs):
        if self._active:
            self.layers.draw(screen)
            self.layers.update(screen)
            self.handle_collisions()

            self.handle_center_on_sprite()

    def handle_collisions(self):
        for sprite in self.layers.sprites():
            if isinstance(sprite, entity.MovingEntity):
                if sprite.feet.collidelist(self.collide_hitboxes) > -1:
                    sprite.__cancel_move__()

    def handle_center_on_sprite(self):
        if self._center_entity is not None:
            self.layers.center(self._center_entity.rect.center)
        pygame.display.flip()

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value: bool):
        if not value:
            self.on_unload(self, self.game.win, self.game)
        self._active = value

    @property
    def zoom(self):
        return self.map_layer.zoom

    @zoom.setter
    def zoom(self, value: int):
        self.map_layer.zoom = value

    def register(self, name: str, module):
        self.RegistryName = module, name
        map_registry.register(f"{module}:{name}", self)
        logger.RenderThreadInfo.log(f"Registered name '{module}:{name}'.")


map_registry = Registry(MapTMX)

