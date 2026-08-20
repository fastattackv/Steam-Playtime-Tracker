# Steam Playtime Tracker

Fastattack, 2026


## What is this repo

This repository contains python code that can read steam internal files to locally extract data that you would otherwise need to get from the steam API.

The file `read_steam_functions.py` contains all the functions to read data from the steam files.
It contains functions that can be directly used but is mainly created for an example of how to get the data from steam.

The file `games_data_codec.py` contains functions to write the extracted data to json or csv files.

The file `playtime_saver.py` contains a small program that uses the previous files to save your playtimes.

I am currently working on a way to easily visualize this data from the program. In the meantime, you can use the `GenerateTimeProgressionCSV` argument to generate a csv file that can be used in a program like Excel to visualize the playtimes progression.


## Installation

If you want to use the `playtime_saver.py` file automatically to save your playtimes, you can:

1. Download the `Source` folder from this repo to your machine.
2. Install python and then the `vdf` module from pip
3. Run the `playtime_saver.py` file from a cmd using the different CLI arguments (list them using the `help` argument).

If you want to run this script automatically every day to save your playtimes, you can:

1. Create a .bat file in the `Source` folder you downloaded
2. In this file write the command you would use to save yout playtimes i.e. 
```shell
python "[path where you downloaded the Source folder]/playtime_saver.py" daily
```

By putting `daily` in the command, the playtimes will be saved at most once a day. If you want to save the playtimes each time you run this command, put `save` instead.

Then, to run this command automatically at windows startup, you can create a shortcut to this file and put it in: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
