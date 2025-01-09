import sys
import logger
from pyerror_display import PyError


class Trigger:
    def __init__(self, func: callable):
        """
        Triggers are sort of events that are usually called
        by the game itself. By default they do nothing, but you can
        override them as you want.
        Multiple overrides will cumulate and each of them will be executed
        when the trigger is called.

        This class is usually used as a function decorator. See game.py
        and base_mod.py for some examples.
        """
        self._file = self.__module__
        self.callables = {"__main__": func}

    def __call__(self, *args, **kwargs):
        """
        Implement self(*args, **kwargs).
        Calls the actual trigger with possible return values.
        """
        return_ = []
        for _callable in self.callables:
            result = None
            try:
                result = self.callables[_callable](*args, **kwargs)
            except:
                PyError(*sys.exc_info(), self.callables[_callable].__code__.co_filename)

            # assert result is not None
            if isinstance(result, tuple):
                errorlevel, *return_ = result
            else:
                errorlevel = result

            if errorlevel == 1:
                logger.RenderThreadError.log(f'Error in trigger at line {self.callables[_callable].__code__.co_firstlineno} of file '
                                             f"{self.callables[_callable].__code__.co_filename}, mod '{self._file}' raised an error.")
                logger.crash(reason=f"Error raised by mod '{_callable}'")
            return_.append(result)
        return return_

    def redef(self, func: callable):
        """
        Redefine/override the trigger's action, the things it will do when called.
        Supports multiple redefinitions, that are all stored into a list and are
        all executed when the trigger is called.

        Syntax:

        - return 0: Signify to the game that everything happened correctly.
        - return 1: Signify to the game that an error occurred during the trigger's execution.
        - return 0, x, y: Same as 'return 0' but gives back x and y to the caller.

        In most cases, this method should be used as a function decorator.
        """
        self.callables[func.__module__] = func
