import getopt
import sys

from multiprocessing import Queue

from sledilnik.TrackerGame import TrackerGame
from sledilnik.TrackerSetup import TrackerSetup


def main(argv):
    tracker_config_path = './tracker_config.yaml'
    game_config_path = None
    setup = False

    try:
        opts, args = getopt.getopt(argv, "ht:g:s", ["help", "tracker-config=", "game-config=", "setup"])
    except getopt.GetoptError:
        help_text()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help_text()
            sys.exit()
        elif opt in ("-t", "--tracker-config"):
            tracker_config_path = arg
        elif opt in ("-g", "--game-config"):
            game_config_path = arg
        elif opt in ("-s", "--setup"):
            setup = True

    if setup:
        TrackerSetup(tracker_config_path, game_config_path).start()
    else:
        TrackerGame(tracker_config_path, game_config_path).start(Queue())


def help_text():
    print("Usage:")
    print("\t--help (-h)                                     shows this help")
    print("\t--tracker-config (-t) <path to tracker config>  sets path to tracker config")
    print("\t--game-config (-g) <path to game config>        sets path to game config")
    print("\t--setup (-s)                                    runs tracker setup")


if __name__ == '__main__':
    main(sys.argv[1:])
