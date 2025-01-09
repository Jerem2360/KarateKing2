import pygame
from os import PathLike
from tools import Registry, Coordinates, RGBColor, Action, Direction
import logger
from typing import Literal


class SpriteSheet:
    def __init__(self, image: str or PathLike, x_frames: int, y_frames: int, frame_size: tuple[int, int]):
        """
        Sort the 'image' sprite sheet as a grid of (x_frames * y_frames) dimensions, considering
        that a frame's size is 'frame_size'.

        Will iterate through frames on the image from left to right, and from top to bottom.
        """
        self.frames = []
        self.frame_rect = pygame.rect.Rect(0, 0, *frame_size)
        lign = 0
        column = 0
        sheet = pygame.image.load(image)

        for i in range(y_frames):
            current_y = lign * frame_size[1]
            for j in range(x_frames):
                result = pygame.Surface(frame_size)
                current_x = column * frame_size[0]

                min_x = current_x
                max_x = min_x + frame_size[0]

                min_y = current_y
                max_y = min_y + frame_size[1]

                result.blit(sheet, (0, 0), pygame.rect.Rect(min_x, min_y, max_x - min_x, max_y - min_y))
                self.frames.append(result)
                column += 1
            lign += 1
            column = 0


class MovingFrames:
    def __init__(self, left_frames: list[int], right_frames: list[int], up_frames: list[int], down_frames: list[int], sprite_sheet: SpriteSheet):
        """
        Sort frames of a sprite sheet by direction in all
        4 cardinal points (left, right, up and down) and by animation order.
        """
        self.dict = {}
        self.frame_limit = {
            "left": len(left_frames),
            "right": len(right_frames),
            "up": len(up_frames),
            "down": len(down_frames)
        }
        self.sprite_sheet = sprite_sheet
        left_frame_counter = 1
        for frame in left_frames:
            try:
                self.dict[f"left{left_frame_counter}"] = sprite_sheet.frames[frame]
            except KeyError:
                raise KeyError(f"Sprite sheet has no frame {frame}.")
            left_frame_counter += 1
        right_frame_counter = 1
        for frame in right_frames:
            try:
                self.dict[f"right{right_frame_counter}"] = sprite_sheet.frames[frame]
            except KeyError:
                raise KeyError(f"Sprite sheet has no frame {frame}.")
            right_frame_counter += 1
        up_frame_counter = 1
        for frame in up_frames:
            try:
                self.dict[f"up{up_frame_counter}"] = sprite_sheet.frames[frame]
            except KeyError:
                raise KeyError(f"Sprite sheet has no frame {frame}.")
            up_frame_counter += 1
        down_frame_counter = 1
        for frame in down_frames:
            try:
                self.dict[f"down{down_frame_counter}"] = sprite_sheet.frames[frame]
            except KeyError:
                raise KeyError(f"Sprite sheet has no frame {frame}.")
            down_frame_counter += 1


Texture = str or PathLike or SpriteSheet


class Entity(pygame.sprite.Sprite):
    def __init__(self, xy: Coordinates, texture: Texture, unique_group=False):
        """
        Simple entity class.
        Something that has a texture, and that can be at some coordinates on a map.
        Entities cannot show on screen without a map in background.
        """
        self.RegistryName = ""
        if unique_group:
            self._group = pygame.sprite.Group()
            super().__init__(self._group)
        else:
            super().__init__()
        self._u_g = unique_group

        self._sheet = None
        if isinstance(texture, SpriteSheet):
            self._sheet = texture

            self.image = self._get_frame(0)
            image_size = texture.frame_rect.w, texture.frame_rect.h

        else:
            self.image = pygame.image.load(texture)
            image_size = self.image.get_rect().w, self.image.get_rect().h

        self.rect = pygame.rect.Rect(*xy, *image_size)

    def _get_frame(self, num: int) -> pygame.Surface or None:
        """
        Internal method that returns a sprite sheet's 'num' -th frame.
        """
        if self._sheet is not None:
            return self._sheet.frames[num]

    def update(self, screen: pygame.Surface, *args, **kwargs):
        """
        Update self.
        What happens to the entity at every round of the game's main loop.
        """
        self.rect.topleft = (self.rect.x, self.rect.y)
        pygame.display.flip()

    def register(self, name: str, module):
        """
        Register self to the game's entity registry.
        """
        self.RegistryName = module, name
        entity_registry.register(f"{module}:{name}", self)
        logger.RenderThreadInfo.log(f"Registered name '{module}:{name}'.")


entity_registry = Registry(Entity)
"""Register an entity so that it can be updated by the game's main loop."""


class MovingEntity(Entity):
    def __init__(self, xy: Coordinates, feet_rect: pygame.rect.Rect, texture: Texture, image_bg_color: RGBColor = (0, 0, 0), speed=4):
        """
        An entity, but its coordinates can be changed. In other words, it can move.
        """
        self.bgcolor = image_bg_color
        self.speed = speed
        self.moved = False

        super().__init__(xy, texture)

        self.old_position = self.rect.x, self.rect.y
        self.feet = feet_rect

    def __cancel_move__(self):
        self.rect.x, self.rect.y = self.old_position
        self.rect.topleft = self.rect.x, self.rect.y

    def __move__(self, side: str):
        """
        What happens when a MovingEntity moves, regardless to the direction.
        """
        self.old_position = self.rect.x, self.rect.y

    def __go_left__(self):
        """
        Update self's coordinates.
        """
        self.rect.x -= self.speed
        self.moved = True

    def __go_right__(self):
        """
        Update self's coordinates.
        """
        self.rect.x += self.speed
        self.moved = True

    def __go_up__(self):
        """
        Update self's coordinates.
        """
        self.rect.y -= self.speed
        self.moved = True

    def __go_down__(self):
        """
        Update self's coordinates.
        """
        self.rect.y += self.speed
        self.moved = True

    def move_left(self):
        """
        Move self to the left, depending on its speed.
        """
        self.__move__("left")
        self.__go_left__()

    def move_right(self):
        """
        Move self to the right, depending on its speed.
        """
        self.__move__("right")
        self.__go_right__()

    def move_up(self):
        """
        Move self upwards, depending on its speed.
        """
        self.__move__("up")
        self.__go_up__()

    def move_down(self):
        """
        Move self downwards, depending on its speed.
        """
        self.__move__("down")
        self.__go_down__()

    def update(self, screen: pygame.Surface, *args, **kwargs):
        """
        Implement self.update(), knowing that self's coordinates can change.
        """
        self.rect.topleft = (self.rect.x, self.rect.y)
        self.feet.midbottom = self.rect.midbottom
        pygame.display.flip()
        super().update(screen, *args, **kwargs)


class AnimatedMovingEntity(MovingEntity):
    def __init__(self, xy: Coordinates, feet_rect: pygame.rect.Rect, sorted_frames: MovingFrames, image_bg_color: RGBColor = (0, 0, 0), speed=3):
        """
        An entity that can move and has an animated texture, represented by 'sorted_frames'.
        """
        super().__init__(xy, feet_rect, sorted_frames.sprite_sheet, image_bg_color=image_bg_color, speed=speed)
        self.do_rotate = True
        self._rotation = "down"
        self.moving_animation_switch_rate = speed * 3
        self.frames = sorted_frames.dict
        self.moving_counter = 0
        self.frameno = 1

        if not (sorted_frames.frame_limit["left"] == sorted_frames.frame_limit["right"] ==
                sorted_frames.frame_limit["up"] == sorted_frames.frame_limit["down"]):
            raise ValueError("All directions must have the same amount of frames.")

        super().__init__(xy, feet_rect, sorted_frames.sprite_sheet, speed=speed)
        self.last_frame = sorted_frames.frame_limit["left"]

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value: Direction):
        self._rotation = value

    def _choose_image(self):
        """
        Update self.image. Set it to the correct animation frame, depending on
        self.frameno and self.rotation .
        """
        self.image = self.frames[self.rotation + str(self.frameno)]
        self.image.set_colorkey(self.bgcolor)

    def update(self, screen: pygame.Surface, *args, **kwargs):
        """
        Implement self.update(), knowing that self's texture changes regularly.
        """
        if self.moving_counter > self.moving_animation_switch_rate:
            if self.frameno < self.last_frame:
                self.frameno += 1
            else:
                self.frameno = 1
            self.moving_counter = 0

        self._choose_image()
        super().update(screen, *args, **kwargs)

    def __move__(self, side: str):
        """
        Implement self.__move__(), knowing that self's rotation
        can change. It's animation frame can also change depending
        on how many it moved in total.
        """
        super().__move__(side)
        if self.do_rotate:
            self.rotation = side
        self.moving_counter += 1


class LivingEntity(AnimatedMovingEntity):
    def __init__(self, xy: Coordinates, sprite_sheet: str or PathLike, feet_rect=pygame.rect.Rect(0, 0, 16, 12)):
        sheet = SpriteSheet(sprite_sheet, 3, 4, (32, 32))

        self._say = None

        left = [3, 4, 5, 4]
        right = [6, 7, 8, 7]
        up = [9, 10, 11, 10]
        down = [0, 1, 2, 1]
        sorted_frames = MovingFrames(left, right, up, down, sheet)
        super().__init__(xy, feet_rect, sorted_frames)

        self.do_rotate = True
        self._moving_algorithm = []
        self.current_step = 0
        self.current_tick = 0
        self.moving_steps_delay = 100

    @property
    def moving_script(self):
        return self._moving_algorithm

    @moving_script.setter
    def moving_script(self, value: list[tuple[Direction, int]]):
        self._moving_algorithm = value

    def choose_move(self, move: Action):
        if move == "-left":
            self.move_left()
        elif move == "-right":
            self.move_right()
        elif move == "-up":
            self.move_up()
        elif move == "-down":
            self.move_down()
        elif move.startswith("-say: "):
            self.say(move.split("say: ")[-1])

    def say(self, text: str):
        self._say = text

    def update(self, screen: pygame.Surface, *args, **kwargs):
        if len(self._moving_algorithm) > 0:
            if len(self._moving_algorithm) > self.current_step:
                move, repeat = self._moving_algorithm[self.current_step]
                for i in range(repeat):
                    self.choose_move(move)

                self.current_step = 0
                self.current_tick = 0

            else:
                if self.current_tick >= self.moving_steps_delay:
                    self.current_tick = 0
                    self.current_step += 1
                else:
                    self.current_tick += 1
        super().update(screen, *args, **kwargs)

    def rotate_left(self):
        self.rotation = "left"

    def rotate_right(self):
        self.rotation = "right"

    def rotate_up(self):
        self.rotation = "up"

    def rotate_down(self):
        self.rotation = "down"



