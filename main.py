"""Main program entry class."""


import logging
import Constants as CONST
import Init as init

verbose_logger = logging.basicConfig(format=CONST.CRITICAL_LOGGING_FORMAT, filename="critical.log",
                    level=logging.CRITICAL, filemode="w")
debug_logger = logging.basicConfig(format=CONST.DEBUG_LOGGING_FORMAT, filename="debug.log",
                    level=logging.DEBUG, filemode="w")
init.Init()
# TODO Set the initial state to new game.
# TODO Open junction, which will check the state to see if we have a game.
