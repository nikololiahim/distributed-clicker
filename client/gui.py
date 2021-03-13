import tkinter as tk
import tkinter.messagebox as msg
import threading
from client import Client


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


class View(tk.Tk):
    def __init__(self, client):
        self.client = client
        super().__init__()
        self.resizable(True, True)
        self.withdraw()
        self.login_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_leave)
        self.mainloop()

    def login_layout(self):
        self.login = tk.Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)

        self.prompt = tk.Label(
            self.login,
            text="Please, login to continue",
            justify=tk.CENTER,
            font="Helvetica 14 bold"
        )

        self.prompt.place(
            relheight=0.15,
            relx=0.2,
            rely=0.07
        )

        self.username_prompt = tk.Label(
            self.login,
            text="Name: ",
            font="Helvetica 12"
        )

        self.username_prompt.place(
            relheight=0.2,
            relx=0.1,
            rely=0.2
        )

        self.username_field = tk.Entry(
            self.login,
            font="Helvetica 14"
        )

        self.username_field.place(
            relwidth=0.4,
            relheight=0.12,
            relx=0.35,
            rely=0.2
        )
        self.username_field.focus()

        self.login_button = tk.Button(
            master=self.login,
            text="CONTINUE",
            font="Helvetica 14 bold",
            command=self.on_log_in
        )
        self.login_button.place(relx=0.4,
                                rely=0.55)

    def validate_username(self):
        if hasattr(self, "username_field"):
            username = self.username_field.get()
            self.username_field.delete(0, tk.END)
            if not username.isalnum():
                msg.showerror(
                    title="Invalid Username!",
                    message="Username should contain only numbers and/or Latin letters!\n"
                )
                return
            if not 4 <= len(username) <= 12:
                msg.showerror(
                    title="Invalid Username!",
                    message="Username should be between 4 and 12 characters long!\n"
                )
                return
            return username
        else:
            raise RuntimeError("Login is no longer available")

    def on_log_in(self):
        username = self.validate_username()
        if username is not None:
            listening_thread = threading.Thread(target=lambda: self.client.start(username))
            listening_thread.start()
            self.login.destroy()
            self.waiting_layout()

    def on_leave(self):
        self.client.disconnect()
        self.destroy()

    def waiting_layout(self):

        self.players = tk.Frame(
            master=self,
            background="bisque",
            borderwidth=2
        )
        self.players.grid(row=0, column=0, sticky=tk.NSEW)
        self.players_list = PlayerList(
            master=self.players,
            background="pink",
            borderwidth=2
        )
        self.players_list.pack_propagate(0)
        self.players_list.pack()

        self.leave = tk.Button(
            master=self.players,
            text="Leave",
            command=self.on_leave
        )
        self.leave.pack(
            side=tk.BOTTOM
        )

        self.rooms = tk.Frame(
            master=self,
            background="lightblue",
            borderwidth=2
        )
        self.rooms.grid(row=0, column=1, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(0, weight=1)

        threading.Thread(target=self.update_players_list, daemon=True).start()

        # self.state("zoomed")
        self.deiconify()

    def update_players_list(self):
        while True:
            message = self.client.message_queue.get()
            print(message)
            self.players_list.update_players(message)


if __name__ == "__main__":
    client = Client()
    app = View(client)
    app.mainloop()
