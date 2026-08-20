"""
This file contains functions to read/write the play times read from steam to json files

Fastattack, 2026
Under MIT License
"""

import json
import csv
import os


def encode_games_data(filepath: str, data: dict, values_to_save: list[str]):
    """Writes the given games data to the given file

    :param filepath: file to write to (an existent file will be overwritten)
    :param data: data to save (as read by read_steam_games_data())
    :param values_to_save: parameters to save (LastPlayed, cloud, autocloud, BadgeData, Playtime, Playtime2wks, PlaytimeDisconnected). If none is given, all data will be saved
    """
    data_to_save = data.copy()

    if values_to_save:
        for appid in list(data_to_save.keys()):
            for value in list(data_to_save[appid].keys()):
                if value not in values_to_save:
                    del data_to_save[appid][value]
            if not data_to_save[appid]:  # no values left for this game
                del data_to_save[appid]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)


def decode_games_data(filepath: str) -> dict:
    """Reads the games data from the given file

    :param filepath: file to read from
    :return: data read (of the form as read_steam_games_data() return value)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def generate_playtime_progression_csv(input_folder: str, output_filepath: str) -> dict:
    """Generates a .csv file that contains the playtime data from all saves in the given folder.

    :param input_folder: folder that contains the files "PlayTimeSave_[userid]_[date]_[time].json"
    :param output_filepath: file generate (an existent file will be overwritten). If set to a path that does not exist, will only return the dict without writing to a file
    :return: dict of the form {appid: [playtimes]} with a header containing the dates
    """
    files = os.listdir(input_folder)
    data = {"header": ["appid"]}

    # read files
    for i in range(len(files)):
        data["header"].append(files[i].split("_")[2])

        content = decode_games_data(os.path.join(input_folder, files[i]))
        for appid in content:
            if "Playtime" in content[appid]:
                if appid not in data:
                    data[appid] = [appid]
                    data[appid].extend([0] * i)
                data[appid].append(content[appid]["Playtime"])

    if os.path.isfile(output_filepath):

        # transform data into lists
        data_list = []
        for appid in data:
            data_list.append(data[appid])

        # write output
        with open(output_filepath, "w") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(data_list)

    return data
