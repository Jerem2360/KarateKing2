from typing import Literal, Final
import sys
import time
import pygame


class ConsoleColor:
    def __init__(self, code: Literal[30, 31, 32, 33, 34, 35, 36, 37]):
        self.code = code
        self._enabled = False

        self.activate_color = f"\033[{self.code}m"
        self.reset_color = "\033[39m"

    def enable_ansi(self):
        """
        Enable ansi codes for the command prompt (the console).
        **Only works on Windows**
        """
        if sys.platform == "win32":
            self._enabled = True
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32')
            hStdOut = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
            mode.value |= 4
            kernel32.SetConsoleMode(hStdOut, mode)
            del ctypes
        else:
            raise NotImplementedError("This function is only implemented on Windows!")


class Ostream:
    def __init__(self, color: ConsoleColor, OriginName: str):
        self.color = color
        self._name = OriginName

    def _writeline(self, text, file):
        file.write(self.color.activate_color + text + self.color.reset_color)

    def log(self, text, *args, sep="", end="\n", file=sys.stdout, flush=False):
        final = f"[{self._name}] " + str(text)
        for arg in args:
            final += sep
            final += str(arg)
        final += end
        self._writeline(final, file)
        if flush:
            file.flush()


BLACK = ConsoleColor(30)
RED = ConsoleColor(31)
GREEN = ConsoleColor(32)
YELLOW = ConsoleColor(33)
BLUE = ConsoleColor(34)
MAGENTA = ConsoleColor(35)
CYAN = ConsoleColor(36)
WHITE = ConsoleColor(37)


RenderThreadInfo: Final[Ostream] = Ostream(MAGENTA, "Main-Thread/Info")
RenderThreadWarn: Final[Ostream] = Ostream(YELLOW, "Main-Thread/Warn")
RenderThreadError: Final[Ostream] = Ostream(RED, "Main-Thread/Error")


def crash(reason="Fatal Error"):
    time.sleep(2)
    RenderThreadError.log(f"The game was found in crash state: {reason}.\nStopping...")
    time.sleep(5)
    pygame.quit()
    sys.exit()

