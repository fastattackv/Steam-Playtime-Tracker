"""
This file contains the functions to process and show playtime progression from the GUI

Fastattack, 2026
Under MIT License
"""


import ctypes
import customtkinter as ctk
import MoreCustomTkinterWidgets as mctk

from playtime_visualization_CLI import visualize_appid, visualize_all_appids



class VisualizationSelectionWindow(ctk.CTk):
    def __init__(self, data: dict, correspondence: dict, title: str=None, geometry: str=None, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)


        # prepare data
        self.games_data = {"header": data["header"]}
        self.correspondence_data = correspondence

        for appid in data:
            if appid != "header":
                if int(appid) in self.correspondence_data:
                    self.games_data[f"{self.correspondence_data[int(appid)]} ({appid})"] = data[appid]
                else:
                    self.games_data[appid] = data[appid]

        self.min_date = mctk.Date(*map(int, reversed(self.games_data["header"][1].split("-"))))
        self.max_date = mctk.Date(*map(int, reversed(self.games_data["header"][-1].split("-"))))


        # set window properties
        if title is None:
            title = "Steam playtime tracker: progression visualization"
        self.title(title)

        if geometry is None:
            geometry = "450x600"
        self.geometry(geometry)

        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)


        # define fonts and vars
        self.font_title = ctk.CTkFont(size=40, weight="bold")
        self.font_big = ctk.CTkFont(size=25)
        self.font_normal = ctk.CTkFont(size=18)

        self.game_exclude_var = ctk.BooleanVar(self, value=False)  # show=0 / exclude=1
        self.game_exclude_var.trace_add("write", self.on_game_include_change)


        # create widgets
        self.title_label = ctk.CTkLabel(self, font=self.font_title)
        self.title_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.content_frame1 = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame1.grid_columnconfigure(0, weight=1)
        self.content_frame1.grid_rowconfigure(0, weight=1)
        self.frame1_button_start = ctk.CTkButton(self.content_frame1, width=300, height=60, text="Start visualization", font=self.font_big, command=self.switch_to_frame2)
        self.frame1_button_start.grid(row=0, column=0, padx=10, pady=10)

        self.content_frame2 = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame2.grid_columnconfigure([0, 1], weight=1)
        self.content_frame2.grid_rowconfigure([0, 1], weight=1)
        self.content_frame2.grid_rowconfigure(2, weight=3)
        self.content_frame2.grid_rowconfigure(3, weight=0)
        self.frame2_label = ctk.CTkLabel(self.content_frame2, text="Select games to show", font=self.font_big)
        self.frame2_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="sw")
        self.frame2_show_box = ctk.CTkRadioButton(self.content_frame2, text="Show", font=self.font_normal, variable=self.game_exclude_var, value=0)
        self.frame2_show_box.grid(row=1, column=0)
        self.frame2_show_box.set(True)
        self.frame2_exclude_box = ctk.CTkRadioButton(self.content_frame2, text="Exclude", font=self.font_normal, variable=self.game_exclude_var, value=1)
        self.frame2_exclude_box.grid(row=1, column=1)
        games_list = list(self.games_data.keys())
        games_list.remove("header")
        self.frame2_selector = mctk.Selector(self.content_frame2, names_list=games_list, multiple_choices=True)
        self.frame2_selector.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.frame2_back = ctk.CTkButton(self.content_frame2, text="Back", command=self.switch_to_frame1)
        self.frame2_back.grid(row=3, column=0, padx=5, pady=5)
        self.frame2_validate = ctk.CTkButton(self.content_frame2, text="Validate", command=self.validate_frame2)
        self.frame2_validate.grid(row=3, column=1, padx=5, pady=5)

        self.content_frame3 = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame3.grid_columnconfigure([0, 1], weight=1)
        self.content_frame3.grid_rowconfigure(0, weight=2)
        self.content_frame3.grid_rowconfigure(1, weight=3)
        self.content_frame3.grid_rowconfigure(2, weight=0)
        self.frame3_start_label = ctk.CTkLabel(self.content_frame3, text="Start date", font=self.font_big)
        self.frame3_start_label.grid(row=0, column=0)
        self.frame3_end_label = ctk.CTkLabel(self.content_frame3, text="End date", font=self.font_big)
        self.frame3_end_label.grid(row=0, column=1)
        self.frame3_date_selector_start = mctk.DateSelector(self.content_frame3, default_date=self.min_date, min_date=self.min_date, max_date=self.max_date, date_format="%y-%m-%d")
        self.frame3_date_selector_start.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.frame3_date_selector_end = mctk.DateSelector(self.content_frame3, default_date=self.max_date, min_date=self.min_date, max_date=self.max_date, date_format="%y-%m-%d")
        self.frame3_date_selector_end.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.frame3_back = ctk.CTkButton(self.content_frame3, text="Back", command=self.switch_to_frame2)
        self.frame3_back.grid(row=3, column=0, padx=5, pady=5)
        self.frame3_validate = ctk.CTkButton(self.content_frame3, text="Validate", command=self.validate_frame3)
        self.frame3_validate.grid(row=3, column=1, padx=5, pady=5)

        self.content_frame4 = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame4.grid_columnconfigure(0, weight=1)
        self.content_frame4.grid_rowconfigure([0, 1], weight=1)
        #self.frame4_label = ctk.CTkLabel(self.content_frame4, text="To modify your selection,\nplease quit the current graph window\nand then click back", font=self.font_normal)
        #self.frame4_label.grid(row=0, column=0, padx=10, pady=10)
        self.frame4_button = ctk.CTkButton(self.content_frame4, width=300, height=60, text="Back", font=self.font_normal, command=self.switch_to_frame3)
        self.frame4_button.grid(row=1, column=0, padx=10, pady=10)


        # start app
        self.switch_to_frame1()


    def hide_all_frames(self):
        self.content_frame1.grid_forget()
        self.content_frame2.grid_forget()
        self.content_frame3.grid_forget()
        self.content_frame4.grid_forget()

    def switch_to_frame1(self):
        self.hide_all_frames()
        self.title_label.configure(text="Welcome")
        self.content_frame1.grid(row=1, column=0, sticky="nsew")

    def switch_to_frame2(self):
        self.hide_all_frames()
        self.title_label.configure(text="Games selection")
        self.content_frame2.grid(row=1, column=0, sticky="nsew")

    def switch_to_frame3(self):
        self.hide_all_frames()
        self.title_label.configure(text="Date interval")
        self.content_frame3.grid(row=1, column=0, sticky="nsew")

    def switch_to_frame4(self):
        self.hide_all_frames()
        self.title_label.configure(text="Visualization")
        self.content_frame4.grid(row=1, column=0, sticky="nsew")


    def on_game_include_change(self, *args):
        if self.game_exclude_var.get():
            self.frame2_label.configure(text="Select games to exclude")
        else:
            self.frame2_label.configure(text="Select games to show")

    def validate_frame2(self):
        if self.frame2_selector.get_selections() or self.game_exclude_var.get():
            self.switch_to_frame3()
        else:
            mctk.showwarning("Steam playtime tracker: progression visualization", "Please select at least one game to show")


    def validate_frame3(self):
        self.switch_to_frame4()

        selection = self.frame2_selector.get_selections()

        if self.game_exclude_var.get():
            visualize_all_appids(self.games_data, str(self.frame3_date_selector_start.get()), str(self.frame3_date_selector_end.get()), selection, exclude_no_change=False)
        else:
            if len(selection) == 1:
                visualize_appid(self.games_data, selection[0], str(self.frame3_date_selector_start.get()), str(self.frame3_date_selector_end.get()))
            else:
                apps_to_show = {app: data for app, data in self.games_data.items() if app in selection or app =="header"}
                visualize_all_appids(apps_to_show, str(self.frame3_date_selector_start.get()), str(self.frame3_date_selector_end.get()), exclude_no_change=False)



def show_selection_GUI(data: dict, correspondence: dict):
    """ Shows the GUI to modify the graphs to be shown """
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    win = VisualizationSelectionWindow(data, correspondence)

    win.mainloop()
