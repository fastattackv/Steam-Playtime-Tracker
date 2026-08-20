"""
This file contains the command line interface to interact with the time tracker

CLI arguments:
- help: prints all available commands
- SaveCurrentPlayTimes / save: saves the playtimes as they are now
- DailyPlayTimeSave / daily: saves the current playtimes only if no save was already made today
- GenerateTimeProgressionCSV / progressioncsv: Generates a file that contains the playtime data of all saves
- PrintAllInfo / info: prints everything that the program are capable of retrieving about steam
- PrintGamesAppid / game-appid: prints every appid<->game correpondence saved on this computer

Fastattack, 2026
"""

from parameters import *
from read_steam_functions import *
from games_data_codec import *

import time
import sys
import os



def save_current_playtimes(folder: str) -> str:
    """ Saves the current playtimes in a new file in the given folder. Returns a path to the created file """
    steam_path = read_steam_path()
    users = read_users(steam_path)
    data = read_steam_games_data(steam_path, users[0]["ContactID"])

    filename = f"PlayTimeSave_{users[0]["ContactID"]}_{time.strftime("%d-%m-%Y_%H-%M-%S")}.json"
    filepath = os.path.join(folder, filename)

    encode_games_data(filepath, data, ["LastPlayed", "Playtime", "Playtime2wks", "PlaytimeDisconnected"])

    return filepath



if __name__ == "__main__":

    if len(sys.argv) == 1:  # no arguments given
        exit()
    elif len(sys.argv) == 2:  # 1 arg given
        arg = sys.argv[1]
    else:
        print("Too many arguments given")
        exit()


    if arg == "help":
        print("Available commands:\n"
              "- SaveCurrentPlayTimes / save: saves the playtimes as they are now\n"
              "- DailyPlayTimeSave / daily: saves the current playtimes only if no save was already made today\n"
              "- GenerateTimeProgressionCSV / progressioncsv: Generates a .csv file that contains the playtime data from all saves\n"
              "- PrintAllInfo / info: prints everything that the program are capable of retrieving about steam\n"
              "- PrintGamesAppid: prints every appid<->game correpondence saved on this computer")

    elif arg == "SaveCurrentPlayTimes" or arg == "save":
        file = save_current_playtimes(SAVE_FOLDER)
        print(f"Created save file at: \"{file}\"")

    elif arg == "DailyPlayTimeSave" or arg == "daily":
        files = os.listdir(SAVE_FOLDER)
        if not files:  # no previous save
            file = save_current_playtimes(SAVE_FOLDER)
            print(f"Created save file at: \"{file}\"")
        else:
            last_save_day = files[-1].split("_")[2]
            if last_save_day != time.strftime("%d-%m-%Y"):  # different day than today
                file = save_current_playtimes(SAVE_FOLDER)
                print(f"Created save file at: \"{file}\"")
            else:
                print("A save was already made today")

    elif arg == "GenerateTimeProgressionCSV" or arg == "progressioncsv":
        generate_playtime_progression_csv(SAVE_FOLDER, PROGRESSION_FILEPATH)
        print(f"Generated progression file at: {PROGRESSION_FILEPATH}")

    elif arg == "PrintAllInfo" or arg == "info":
        print_all_available_data()

    elif arg == "PrintGamesAppid" or arg == "game-appid":
        print_appid_game_correspondence()

    else:
        print("Unknown argument:", arg)
