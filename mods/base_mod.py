import game
import logger
import window as win
import gui
from tools import Registry, Coordinates
import entity
import pygame
import map
import game_globals


constants = {
    "city1_map": "mods/base_mod/assets/maps/city1/exterior.tmx",
    "player": "mods/base_mod/assets/entities/player/player.png",
    "main_menu_bg": "mods/base_mod/assets/menus/main_menu/background.jpg",
    "main_menu_play_button": "mods/base_mod/assets/menus/main_menu/play_button.png"
}


def play_button_command(main_menu: gui.Menu, game_: game.Game):
    """
    What will the play button do when clicked by the user.
    """
    main_menu.active = False
    game_.status("load_first_map")


player_data = Registry(object)

main_menu_ = None

@game.OnGameStarts.redef
def OnGameStarts(modlist, window: win.Window, game_: game.Game) -> int:
    """
    Redefine 'OnGameStarts' trigger so that we can register the
    main menu ("base_mod:main_menu") when the game starts.
    """
    logger.RenderThreadInfo.log("Hello from Base Mod!")
    # create the menu object:
    main_menu = game_.new_menu(constants["main_menu_bg"])

    # create the 'play' button:
    play_button_pos = (round(window.screen.get_rect().w / 2) - 120, round(window.screen.get_rect().h / 2) - 101)
    play_button = gui.Button(play_button_pos, (4, 1), constants["main_menu_play_button"], command=play_button_command)
    play_button.command_args = (main_menu, game_)  # the positional arguments that will be passed the the button's command.

    main_menu.add(play_button)  # add the button to the menu

    # activate and register the main menu ("base_mod:main_menu") :
    game_.load_menu(main_menu)
    main_menu.register("main_menu", __name__)

    game_globals.vars_.store("main_menu_id", main_menu.RegistryName)

    return 0  # everything happened correctly.


class PlayerEntity(entity.AnimatedMovingEntity):
    def __init__(self, xy: Coordinates):
        """
        An implementation class for the actual player.
        **internal class only!**
        """
        sheet = entity.SpriteSheet(constants["player"], 3, 4, (32, 32))  # load the player sprite sheet.

        # list the frame id's that corresponds
        left = [3, 4, 5, 4]
        right = [6, 7, 8, 7]
        up = [9, 10, 11, 10]
        down = [0, 1, 2, 1]
        sorted_frames = entity.MovingFrames(left, right, up, down, sheet)
        feet_rect = pygame.rect.Rect(0, 0, 16, 12)
        super().__init__(xy, feet_rect, sorted_frames)

        self.feet = pygame.rect.Rect(0, 0, self.rect.width * 0.5, 12)

        self.do_rotate = True

    def update(self, screen: pygame.Surface, *args, **kwargs):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            self.move_up()
        elif keys[pygame.K_q]:
            self.move_left()
        elif keys[pygame.K_s]:
            self.move_down()
        elif keys[pygame.K_d]:
            self.move_right()

        super().update(screen, *args, **kwargs)


@game.OnReadyToLoadMap.redef
def OnReadyToLoadMap(window: win.Window, game_: game.Game):

    center_x = window.screen.get_size()[0] / 2
    center_y = window.screen.get_size()[1] / 2
    city1_map = game_.new_map(constants["city1_map"], (center_x, center_y), 1)
    city1_map.register("city1/map", __name__)
    game_.load_map(city1_map)

    city1_map_spawn = city1_map.get_object_by_name("player_spawn")
    player = PlayerEntity((city1_map_spawn.x, city1_map_spawn.y))
    player.register("player", __name__)
    city1_map.link_sprite(player, center=True)

    return 0


