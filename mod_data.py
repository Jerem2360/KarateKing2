import os
from importlib import util
import importer


def check_mods():
    realpath = os.path.realpath(os.curdir)

    os.chdir("mods/")
    mods = []

    for file in os.listdir():
        if file.endswith('.py'):
            mod_name = file.split('.py')[0]
            mods.append(mod_name)

    os.chdir(realpath)

    return mods


def import_mods(mods_info: list[str]):
    modlist = {}
    for modname in mods_info:

        modlist[modname] = importer.import_module(modname, f"mods\\{modname}.py")

    return modlist

