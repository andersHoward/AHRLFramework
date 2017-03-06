"""Main program entry class."""


import logging
import Constants as CONST
import Init as init


logging.basicConfig(format=CONST.LOGGING_FORMAT, filename="debug.log",
                    level=logging.DEBUG, filemode="w")
init.Init()
# TODO Set the initial state to new game.
# TODO Open junction, which will check the state to see if we have a game.
