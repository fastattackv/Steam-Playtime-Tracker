"""
This file contains the command line interface to interact with the time tracker

CLI arguments:
- help: prints all available commands
- SaveCurrentPlayTimes / save: saves the playtimes as they are now
- DailyPlayTimeSave / daily: saves the current playtimes only if no save was already made today
- GenerateTimeProgressionCSV / progressioncsv: Generates a file that contains the playtime data of all saves
- PrintAllInfo / info: prints everything that the program are capable of retrieving about steam
- PrintGamesAppids / appids: prints every appid<->game correpondence saved on this computer
- Visualization_GUI / graph: starts the graphing interface to visualize the saved data
- Visualization_CLI / graph_CLI: starts the graphing dialog to visualize the saved data

Fastattack, 2026
Under MIT License
"""

from parameters import *
from read_steam_functions import *
from games_data_codec import *
from playtime_visualization_CLI import *
from playtime_visualization_GUI import *

import time
import sys
import os



def is_date(val: str):
    """ Checks whether a given string is a date following the DATE_FORMAT. This function supposes that DATE_FORMAT is valid """
    format_index = 0
    val_index = 0

    while format_index < len(DATE_FORMAT) and val_index < len(val):
        if DATE_FORMAT[format_index] == "%":
            if format_index+1 < len(DATE_FORMAT):
                if DATE_FORMAT[format_index + 1] == "Y":
                    if val_index + 3 < len(val) and val[val_index:val_index + 4].isnumeric():
                        format_index += 2
                        val_index += 4
                    else:
                        return False
                elif DATE_FORMAT[format_index + 1] == "m":
                    if val_index + 1 < len(val) and val[val_index:val_index + 2].isnumeric():
                        format_index += 2
                        val_index += 2
                    else:
                        return False
                elif DATE_FORMAT[format_index + 1] == "d":
                    if val_index + 1 < len(val) and val[val_index:val_index + 2].isnumeric():
                        format_index += 2
                        val_index += 2
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            if DATE_FORMAT[format_index] == val[val_index]:
                format_index += 1
                val_index += 1
            else:
                return False

    if format_index == len(DATE_FORMAT) and val_index == len(val):
        return True
    else:
        return False


def save_current_playtimes(folder: str) -> str:
    """ Saves the current playtimes in a new file in the given folder. Returns a path to the created file """
    steam_path = read_steam_path()
    users = read_users(steam_path)
    data = read_steam_games_data(steam_path, users[0]["ContactID"])

    filename = f"PlayTimeSave_{users[0]["ContactID"]}_{time.strftime(f"{DATE_FORMAT}_{TIME_FORMAT}")}.json"
    filepath = os.path.join(folder, filename)

    encode_games_data(filepath, data, ["LastPlayed", "Playtime", "Playtime2wks", "PlaytimeDisconnected"])

    return filepath


def visualization_dialog():
    """ Starts the visualization dialog """
    running = True
    games_data = generate_playtime_progression_csv(SAVE_FOLDER, "")

    while running:
        val = input("\nDo you want to exit / see the progression for a specific game / progression for all games ? [0 / 1 / 2]: ")

        if val == "0":
            running = False

        elif val == "1":

            appid = input("Enter the appid of the game to visualize: ")
            if appid in games_data:
                val = input("On what interval do you want to see the progression ? [all/define]: ")

                if val == "all":
                    visualize_appid(games_data, appid)

                elif val == "define":
                    print("Enter the dates between which the progression should be shown")
                    date1 = input(f"Enter the first date [{DATE_FORMAT}]: ")
                    if not is_date(date1):
                        print(f"{date1} is not a valid date")
                        exit()
                    date2 = input(f"Enter the second date [{DATE_FORMAT}]: ")
                    if not is_date(date2):
                        print(f"{date2} is not a valid date")
                        exit()
                    if date2 > date1:
                        date1, date2 = date2, date1
                    visualize_appid(games_data, appid, date1, date2)

                else:
                    print("Incorrect input")

            else:
                print("No data found for the given appid")

        elif val == "2":
            val = input("On what interval do you want to see the progression ? [all/define]: ")

            if val == "all":
                visualize_all_appids(games_data)

            elif val == "define":
                print("Enter the dates between which the progression should be shown")
                date1 = input(f"Enter the first date [{DATE_FORMAT}]: ")
                if not is_date(date1):
                    print(f"{date1} is not a valid date")
                    exit()
                date2 = input(f"Enter the second date [{DATE_FORMAT}]: ")
                if not is_date(date2):
                    print(f"{date2} is not a valid date")
                    exit()
                print(date1, date2)
                if date2 < date1:
                    date1, date2 = date2, date1
                print(date1, date2)
                visualize_all_appids(games_data, date1, date2)

            else:
                print("Incorrect input")

        else:
            print("Incorrect input")



if __name__ == "__main__":

    if len(sys.argv) == 1:  # no arguments given
        arg = "help"
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
              "- PrintGamesAppids / appids: prints every appid<->game correpondence saved on this computer\n"
              "- Visualization / graph: starts the graphing dialog to visualize the saved data")

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
            if last_save_day != time.strftime(DATE_FORMAT):  # different day than today
                file = save_current_playtimes(SAVE_FOLDER)
                print(f"Created save file at: \"{file}\"")
            else:
                print("A save was already made today")

    elif arg == "GenerateTimeProgressionCSV" or arg == "progressioncsv":
        generate_playtime_progression_csv(SAVE_FOLDER, PROGRESSION_FILEPATH)
        print(f"Generated progression file at: {PROGRESSION_FILEPATH}")

    elif arg == "PrintAllInfo" or arg == "info":
        print_all_available_data()

    elif arg == "PrintGamesAppid" or arg == "appids":
        print_appid_game_correspondence()

    elif arg == "Visualization_CLI" or arg == "graph_CLI":
        visualization_dialog()

    elif arg == "Visualization_GUI" or arg == "graph":
        games_data = generate_playtime_progression_csv(SAVE_FOLDER, "")
        
        steam_path = read_steam_path()
        path = os.path.normpath(os.path.join(steam_path, "appcache/appinfo.vdf"))
        raw_data = parse_appinfo(path)
        correspondence = {}
        
        for appid in raw_data:
            if raw_data[appid]["type"] in ["Game", "Demo", "Beta"]:
                correspondence[appid] = raw_data[appid]['name']
        
        show_selection_GUI(games_data, correspondence)

    else:
        print("Unknown argument:", arg)
