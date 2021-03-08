import tkinter as tk
import tkinter.ttk as ttk
from clicker.timer import Timer
import threading


class PlayerList(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

    def update_players(self, players: dict):
        for item in self.items:
            item.destroy()
        self.items.clear()
        for player in players.values():
            text = f"{player['name']}\n{player['address']}:{player['port']}\n"
            button = tk.Button(
                master=self.master,
                text=text,
            )
            button.pack(fill=tk.BOTH)
            self.items.append(button)


class MainWindow(tk.Tk):
    TIME = 5

    def __init__(self):
        super(MainWindow, self).__init__()
        self.timer = Timer(self.TIME)
        self.place_player_list()
        self.place_game_area()
        self.place_click()
        self.place_timer()
        self.place_whose_turn()

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.timer.start()

    def place_game_area(self):
        self.game_area = tk.Frame(
            master=self,
            background="bisque",
            borderwidth=4,
        )
        self.game_area.grid(row=1, column=1, sticky=tk.NSEW)

    def place_player_list(self):
        self.player_list_area = tk.Canvas(
            master=self,
            background="bisque",
            borderwidth=4,
        )
        self.player_list_area.grid(row=1, column=0, sticky=tk.NSEW)
        self.player_list_title = tk.Label(
            master=self,
            background="lightblue",
            text="Players"
        )
        self.player_list_title.grid(row=0, column=0, sticky=tk.NSEW)

    def place_whose_turn(self):
        self.whose_turn = tk.Label(
            master=self,
            background="lightblue",
            text="Player's turn now!"
        )
        self.whose_turn.grid(row=0, column=1, sticky=tk.NSEW)

    def update_progress_bar(self):
        import time
        while True:
            self.progress_bar['value'] = int(self.timer.current_time)
            time.sleep(1)


    def place_timer(self):
        self.progress_bar = ttk.Progressbar(
            master=self.game_area,
            maximum=self.TIME,
            orient="horizontal",
            mode="determinate",
        )

        self.update_progress_bar_thread = threading.Thread(
            target=self.update_progress_bar,
            daemon=True,
        )
        self.update_progress_bar_thread.start()

        self.progress_bar.pack(fill=tk.BOTH)

    def place_click(self):
        self.click = tk.Button(
            master=self.game_area,
            height=10,
            width=10,
            text="CLICK!",
            command=self.timer.reset
        )
        self.click.pack(fill=tk.BOTH)


if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
