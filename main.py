import pygame
import mod_data
import game
import logger


def make_list_displayable(list_: dict):
    result = []
    for item in list_:
        result.append(item)
    return result


if __name__ == '__main__':

    logger.RenderThreadInfo.log("Launching the game...")

    logger.RenderThreadInfo.log("Scanning for mods...")
    mods_info = mod_data.check_mods()
    modlist = mod_data.import_mods(mods_info)

    modlist_d = make_list_displayable(modlist)
    len_ = len(modlist_d)

    logger.RenderThreadInfo.log(f"Found {len_} mods: {repr(modlist_d)}.")

    logger.RenderThreadInfo.log("Successfully loaded mods. Launching GUIs...")
    game_ = game.Game(modlist)

