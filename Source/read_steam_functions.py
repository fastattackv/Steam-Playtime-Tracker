"""
This file contains functions to extract data from steam to use for whatever project.
Every function written here works fully locally and no internet request needs to be made.
Because of this, some data retrieved is cached data, thus it is not possible to confirm that the extracted data is always up to date

Fastattack, 2026
Under MIT License
"""


import winreg
import os
import json
import struct
import vdf  # installed with "pip install vdf"


STEAMWORK_COMMON_REDISTRIBUTABLES_APPID = "228980"



# -------------------------------------------------- Read Functions ----------------------------------------------------
# Functions to read data from steam folders


def read_steam_path() -> str:
    r"""Reads the steam installation path from the registry and returns the path where steam is installed at

    :return: path of Steam installation path (usually: "C:\Program Files (x86)\Steam")
    """
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
    val = winreg.QueryValueEx(key, "InstallPath")
    path = val[0]
    if os.path.isdir(path):
        return path
    else:
        return ""


def read_users(steam_path: str) -> list[dict[str, str]]:
    """Reads different files from steam_path to determine what users are logged in

    :param steam_path: steam installation path (as read by steam_read_path())
    :return: list of users (each user is a dict containing LongID, AccountName, PersonaName, LastLogin, ContactID)
    """
    # find the loginusers.vdf file
    loginusers_path = os.path.normpath(steam_path + "/config/loginusers.vdf")
    if not os.path.isfile(loginusers_path):
        return []

    # read the found loginusers.vdf file
    users = []
    with open(loginusers_path,  "r", encoding="utf-8") as f:
        content = vdf.load(f)
    for long_id in content["users"]:
        new_user = {
            "LongID": long_id,
            "AccountName": content["users"][long_id]["AccountName"],
            "PersonaName": content["users"][long_id]["PersonaName"],
            "LastLogin": content["users"][long_id]["Timestamp"],
            "ContactID": None
        }
        users.append(new_user)

    # find the userdata folder
    userdata_path = os.path.normpath(steam_path + "/userdata")
    if os.path.isdir(userdata_path):
        for contact_id in os.listdir(userdata_path):
            localconfig_path = os.path.normpath(userdata_path + f"/{contact_id}/config/localconfig.vdf")
            if not os.path.isfile(localconfig_path):
                continue
            with open(localconfig_path, "r", encoding="utf-8") as f:
                content = vdf.load(f)
            for user in users:
                if user["PersonaName"] == content["UserLocalConfigStore"]["friends"]["PersonaName"]:
                    user["ContactID"] = contact_id
                    break

    return users


def read_steam_libraries(steam_path: str) -> list[str]:
    r"""Returns the paths where the manifests are stored for the steam libraries

    :param steam_path: steam installation path (as read by steam_read_path())
    :return: path of the directories to the manifests (usually: "C:\Program Files (x86)\Steam\steamapps")
    """
    # find a libraryfolders.vdf file
    if os.path.isdir(os.path.join(steam_path, "steamapps")) and os.path.isfile(os.path.join(steam_path, "steamapps", "libraryfolders.vdf")):
        path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    elif os.path.isdir(os.path.join(steam_path, "config")) and os.path.isfile(os.path.join(steam_path, "config", "libraryfolders.vdf")):
        path = os.path.join(steam_path, "config", "libraryfolders.vdf")
    else:
        return []

    # read the file and check if the libraries exist
    libs = []
    with open(path, "r", encoding="utf-8") as f:
        content = vdf.load(f)
    for lib in content["libraryfolders"]:
        path = os.path.normpath(content["libraryfolders"][lib]["path"] + "/steamapps")
        if os.path.isdir(path):
            libs.append(path)
    return libs


def read_steam_games_installed(steamapps_folder: str) -> dict[int, str]:
    r"""Reads what steam games are installed in the given library

    :param steamapps_folder: folder containing the manifests of installation (usually: "C:\Program Files (x86)\Steam\steamapps")
    :return: dictionary containing the installed games: {appid: "game name"}
    """
    installed_games = {}
    for item in os.listdir(steamapps_folder):
        file_path = os.path.normpath(os.path.join(steamapps_folder, item))
        if os.path.isfile(file_path) and file_path.endswith(".acf"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = vdf.load(f)
                if content["AppState"]["appid"] != STEAMWORK_COMMON_REDISTRIBUTABLES_APPID:
                    installed_games[int(content["AppState"]["appid"])] = content["AppState"]["name"]
    return installed_games


def parse_appinfo(path: str) -> dict:
    r"""Reads the given appinfo file and returns a dict containing info stocked in the file. Greatly helped by https://github.com/SteamDatabase/SteamAppInfo

    :param path: path of the file to read (usually: "C:\Program Files (x86)\Steam\appcache\appinfo.vdf")
    :return: dict containing {appid: {infos}}
    """
    int32 = struct.Struct('<I')  # 4 bytes
    int64 = struct.Struct('<Q')  # 8 bytes

    return_dict = {}
    with open(path, "rb") as f:

        # read file header (almost useless in this case)
        magic = f.read(4)
        if magic != b")DV\x07":
            raise SyntaxError("Invalid magic, got %s" % repr(magic))
        universe = int32.unpack(f.read(4))[0]
        string_table_offset = int64.unpack(f.read(8))[0]
        previous_offset = f.tell()
        f.seek(previous_offset + string_table_offset)
        string_count = int32.unpack(f.read(4))[0]
        f.seek(previous_offset)

        # read game infos
        while True:
            appid = int32.unpack(f.read(4))[0]
            if appid == 0:
                break

            size = int32.unpack(f.read(4))[0]
            end = f.tell() + size

            app = {
                'appid': appid,
                'info_state': int32.unpack(f.read(4))[0],
                'last_updated': int32.unpack(f.read(4))[0],
                'picsToken': int64.unpack(f.read(8))[0],
                'sha1Text': f.read(20),
                'change_number': int32.unpack(f.read(4))[0],
                'sha1Binary': f.read(20),
                'name': None,
                'type': None,
                'icon_hash': None,
                'binary_content': f.read(end - f.tell())
            }

            # read the name of the game (is separated by \x01\x04\x00\x00\x00)
            name = b""
            if b"\x01\x04\x00\x00\x00" in app["binary_content"]:
                index = app["binary_content"].index(b"\x01\x04\x00\x00\x00") + 5
                while app["binary_content"][index:index + 1] != b"\x00":
                    name += app["binary_content"][index:index + 1]
                    index += 1
                app["name"] = bytes.decode(name)

            # read the type of item (is separated by \x01\x05\x00\x00\x00)
            obj_type = b""
            if b"\x01\x05\x00\x00\x00" in app["binary_content"]:
                index = app["binary_content"].index(b"\x01\x05\x00\x00\x00") + 5
                while app["binary_content"][index:index + 1] != b"\x00":
                    obj_type += app["binary_content"][index:index + 1]
                    index += 1
                if obj_type in [b"Game", b"DLC", b"Demo", b"Config", b"Beta", b"Tool", b"ownersonly", b"Application"]:
                    app["type"] = bytes.decode(obj_type)

            # read the icon hash (is separated by \x01X\x01\x00\x00 and is 40 bytes long)
            if b"\x01X\x01\x00\x00" in app["binary_content"]:
                index = app["binary_content"].index(b"\x01X\x01\x00\x00") + 5
                app["icon_hash"] = bytes.decode(app["binary_content"][index: index + 40])

            return_dict[appid] = app

    return return_dict


def read_steam_achievements_progress(steam_path: str, userid: str) -> dict[int, dict[str, str]]:
    r"""Reads the achievement_progress.json file (usually at: "C:\Program Files (x86)\Steam\userdata\[userid]\config\librarycache\achievement_progress.json")

    :param steam_path: steam installation path (as read by steam_read_path())
    :param userid: contact id of the user to get the achievements from
    :return:
    """
    # find the achievement_progress.json file
    achievementprogress_path = os.path.normpath(steam_path + f"/userdata/{userid}/config/librarycache/achievement_progress.json")
    if not os.path.isfile(achievementprogress_path):
        return {}

    # read the file found
    progress = {}
    with open(achievementprogress_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    for appid, values in content["mapCache"]:
        progress[appid] = {
            "unlocked": values["unlocked"],
            "total": values["total"],
            "percentage": values["percentage"],
            "all_unlocked": values["all_unlocked"],
        }

    return progress


def read_steam_achievements_game(steam_path: str, userid: str, appid: int) -> list[dict]:
    r"""Reads the data for the achievements of a given game

    :param steam_path: steam installation path (as read by steam_read_path())
    :param userid: contact id of the user to get the achievements from
    :param appid: appid of the game to get the achievements from
    :return: If the appid is a game with achievements it should contain the id, name, description, icon and obtention percentage of the achievement as well as your progress towards it.
    If the appid is not a game with achievements, the returned data could be empty or contain unexpected data
    The data for each achievement will also contain its type (Highlight / Unachieved / AchievedHidden)
    """
    # find the file
    achievement_file_path = os.path.normpath(steam_path + f"/userdata/{userid}/config/librarycache/{appid}.json")
    if not os.path.isfile(achievement_file_path):
        return []

    # extract data
    with open(achievement_file_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    achievements = []
    for item in content[0][1]["data"]["vecHighlight"]:
        item["type"] = "Highlight"
        achievements.append(item)
    for item in content[0][1]["data"]["vecUnachieved"]:
        item["type"] = "Unachieved"
        achievements.append(item)
    for item in content[0][1]["data"]["vecAchievedHidden"]:
        item["type"] = "AchievedHidden"
        achievements.append(item)

    return content[0][1]["data"]


def read_steam_friends(steam_path: str, userid: str) -> dict[dict]:
    r"""Reads the localconfig.vdf file (usually at: "C:\Program Files (x86)\Steam\userdata\[userid]\config\localconfig.vdf") to extract information about your friends

    :param steam_path: steam installation path (as read by steam_read_path())
    :param userid: contact id of the user to get the contacts from
    :return: a dict of dicts usually containing NameHistory, name, avatar
    """
    # find the localconfig.vdf file
    localconfig_path = os.path.normpath(steam_path + f"/userdata/{userid}/config/localconfig.vdf")
    if not os.path.isfile(localconfig_path):
        return {}

    # extract data
    with open(localconfig_path, "r", encoding="utf-8") as f:
        content = vdf.load(f)["UserLocalConfigStore"]["friends"]
    for key in list(content.keys()):
        if not key.isnumeric():
            del content[key]
            continue
        if "NameHistory" in content[key]:
            content[key]["NameHistory"] = list(content[key]["NameHistory"].values())

    return content


def read_steam_games_data(steam_path: str, userid: str) -> dict:
    r"""Reads the localconfig.vdf file (usually at: "C:\Program Files (x86)\Steam\userdata\[userid]\config\localconfig.vdf") to extract information about your games

    :param steam_path: steam installation path (as read by steam_read_path())
    :param userid: contact id of the user to get the games from
    :return: The data retrieved here is not always the same, check it before using it.
    It usually contains LastPlayed, cloud (contains last_sync_state), autocloud (contains lastlaunch, lastexit), BadgeData, Playtime, Playtime2wks and PlaytimeDisconnected
    All data retrieved is of type str
    """
    # find the localconfig.vdf file
    localconfig_path = os.path.normpath(steam_path + f"/userdata/{userid}/config/localconfig.vdf")
    if not os.path.isfile(localconfig_path):
        return {}

    # extract data
    with open(localconfig_path, "r", encoding="utf-8") as f:
        content = vdf.load(f)

    return content["UserLocalConfigStore"]["Software"]["Valve"]["Steam"]["apps"]



# -------------------------------------------------- Print Functions ---------------------------------------------------
# Functions printing data from steam using the above functions


def _print_dict(data: dict, indent=1):
    """ Internal function to factor print_all_available_data() """
    for key, value in data.items():
        if type(value) is list:
            print(f"{'  ' * indent}- {key}:")
            _print_list(value, indent + 1)
        elif type(value) is dict:
            print(f"{'  ' * indent}- {key}:")
            _print_dict(value, indent + 1)
        else:
            print(f"{'  ' * indent}- {key}: {value}")


def _print_list(data: list, indent=1):
    """ Internal function to factor print_all_available_data() """
    for i in range(len(data)):
        value = data[i]
        if type(value) is list:
            print(f"{'  ' * indent}- {i}:")
            _print_list(value, indent+1)
        elif type(value) is dict:
            print(f"{'  ' * indent}- {i}:")
            _print_dict(value, indent+1)
        else:
            print(f"{'  '*indent}- {value}")


def print_all_available_data():
    """ Prints everything that the above function are capable of retrieving (except appinfo parsing) """
    print("\n------------------------- General data -------------------------\n\n")

    steam_path = read_steam_path()
    print(f"Steam installation path: \"{steam_path}\"\n\n")

    users = read_users(steam_path)
    print("Users found:")
    _print_list(users)
    print("\n")

    libraries = read_steam_libraries(steam_path)
    print("Libraries found:")
    _print_list(libraries)
    print("\n")

    input("Press enter to continue...")
    print("\n\n\n\n------------------------- Games data -------------------------\n\n")

    print("Games installed:")
    for lib in libraries:
        print(f"\nLibrary: {lib}:")
        games = read_steam_games_installed(lib)
        _print_dict(games)
    print("\n")

    input("Press enter to continue...")
    print("\n\n\n\n------------------------- Users data -------------------------\n\n")

    for user_dict in users:
        userid = user_dict["ContactID"]
        name = user_dict["PersonaName"]
        print(f"User {name} ({userid}):\n\n")

        friends = read_steam_friends(steam_path, userid)
        print("Friends:")
        _print_dict(friends)

        achievements = read_steam_achievements_progress(steam_path, userid)
        print(f"\n\nAchievements:\n")
        _print_dict(achievements)

        games_data = read_steam_games_data(steam_path, userid)
        print(f"\n\nGames data:\n")
        _print_dict(games_data)

        input("\n\nPress enter to continue...")


def print_appid_game_correspondence(path: str | None = None):
    """ Prints every appid<->game that the appinfo file contains """
    if path is None:
        steam_path = read_steam_path()
        path = os.path.normpath(os.path.join(steam_path, "appcache/appinfo.vdf"))

    if not os.path.isfile(path):
        print("appinfo filepath is incorrect:", path)
        return

    data = parse_appinfo(path)

    for appid in data:
        if data[appid]["type"] in ["Game", "DLC", "Demo", "Beta", "Application"]:
            print(f"{appid} <=> {data[appid]['name']}")



if __name__ == "__main__":
    print_appid_game_correspondence()
    print("\n\n\n\n")
    print_all_available_data()
