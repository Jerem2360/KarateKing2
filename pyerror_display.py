import traceback
import pygame
import logger


class PyError:
    def __init__(self, etype, evalue, tb, origin_filename: str):
        logger.RenderThreadError.log(f"A mod caused a fatal error:")
        lines = []
        for line in traceback.TracebackException(etype, evalue, tb).format():
            inlines = line.split('\n')
            for inline in inlines:
                if (inline != "") and (inline != ''):
                    lines.append(inline)

        for line_ in lines:
            logger.RenderThreadError.log(line_)

        logger.crash(f"Error in \"{origin_filename}\" 's code")

