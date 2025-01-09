import imp
from os import PathLike


def import_module(name: str, path: str or PathLike):

    details = ("." + path.split('.')[len(path.split('.')) - 1], 'r', 1)

    f_data = (open(path, 'r'), path, details)

    return imp.load_module(name, *f_data)
