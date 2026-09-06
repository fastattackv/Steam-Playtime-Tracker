"""
This file contains the functions to process and show playtime progression

Fastattack, 2026
"""

import matplotlib.pyplot as plt
import numpy as np


def visualize_appid(data: dict, appid: str, date1: str | None = None, date2: str | None = None):
    """Traces a graph of playtime in function of time

    :param data: data obtained from generate_playtime_progression_csv()
    :param appid: appid of the app to graph
    :param date1: date to start the graph at (if set to None, all dates will be shown)
    :param date2: date to end the graph at (if set to None, all dates will be shown)
    """
    if date1 is not None and date2 is not None:
        start = 1
        end = len(data["header"]) - 1
        while data["header"][start] < date1 and start < len(data["header"]):
            start += 1
        while data["header"][end] > date2 and end > 0:
            end -= 1

        dates = data["header"][start:end]
        playtimes = data[appid][start:end]
    else:
        dates = data["header"][1:]
        playtimes = data[appid][1:]

    np_dates = np.array(dates)
    np_data = np.array(playtimes, dtype="float")
    np_data = np_data / 60

    plt.plot(np_dates, np_data)
    plt.ylabel("Playtime (in hours)")
    plt.title(f"Playtime progression for game {appid}")
    plt.show()


def visualize_all_appids(data: dict, date1: str | None = None, date2: str | None = None, exclude: list | None = None):
    """Traces a graph of playtime in function of time (shows only the games whose playtimes changed in the given period)

    :param data: data obtained from generate_playtime_progression_csv()
    :param date1: date to start the graph at (if set to None, all dates will be shown)
    :param date2: date to end the graph at (if set to None, all dates will be shown)
    :param exclude: excludes the given games from being shown
    """
    # set excluded data
    if exclude is None:
        exclude = ["header"]
    else:
        exclude.append("header")
    exclude = set(exclude)

    # determine what data should be shown
    if date1 is not None and date2 is not None:
        start = 1
        end = len(data["header"]) - 1
        while data["header"][start] < date1 and start < len(data["header"]):
            start += 1
        while data["header"][end] > date2 and end > 0:
            end -= 1
    else:
        start = 1
        end = len(data["header"])

    dates = data["header"][start:end]

    fig, ax = plt.subplots()

    # prepare data
    lines = []
    for appid in data:
        if appid in exclude:
            continue

        playtimes = data[appid][start:end]

        if playtimes[0] != playtimes[-1]:
            np_dates = np.array(dates)
            np_data = np.array(playtimes, dtype="float")
            np_data = np_data / 60
            line, = ax.plot(np_dates, np_data, label=appid)
            lines.append((line, np_data[-1], appid))

    # show games appids on the right
    for line, y_end, appid in lines:
        ax.annotate(
            appid,
            xy=(1, y_end),
            xycoords=("axes fraction", "data"),
            xytext=(5, 0),
            textcoords="offset points",
            color=line.get_color(),
            va="center",
            fontsize=9,
        )
    fig.subplots_adjust(right=0.8)

    # label graph
    ax.set_ylabel("Playtime (in hours)")
    ax.set_title("Playtime progression for all games")

    plt.show()
