import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msg
from clicker.timer import Timer
import threading
import pika

players = dict()
NEW_PLAYER = "new_player"
UPDATE_SCORE = "update_score"
PLAYER_LOST = "player_lost"


class Publisher:

    CREDENTIALS = pika.ConnectionParameters(host='localhost', port=5672)

    def __init__(self):
        self.connection = pika.BlockingConnection(self.CREDENTIALS)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='logs', exchange_type='fanout')

    def publish(self, message):
        self.channel.basic_publish(exchange='logs', routing_key='', body=message)
        print(" [x] Sent %r" % message)

    def close(self):
        self.connection.close()


class Consumer(threading.Thread):

    def on_message(self):
        pass

    def callback(self, ch, method, properties, body: bytes):
        operation, username, score = body.decode("utf-8").split(":")
        if operation == NEW_PLAYER:
            players[username] = {
                "score": score
            }
        elif operation == UPDATE_SCORE:
            players[username]["score"] = score
        elif operation == PLAYER_LOST:
            players.pop(username)
        window.player_list.update_players(players)
        print(f"received: {body.decode('utf-8')}")

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.clients = []
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='logs', exchange_type='fanout')

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange='logs', queue=self.queue_name)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=False)

    def run(self):
        self.channel.start_consuming()


class PlayerList(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

    def update_players(self, players: dict):
        for item in self.items:
            item.destroy()
        self.items.clear()

        payload = list(players.items())
        payload.sort(key=lambda x: int(x[1]["score"]), reverse=True)

        for player, data in payload:
            text = f"Username: {player}\nScore:{data['score']}\n"
            button = tk.Button(
                master=self.master,
                text=text,
            )
            button.pack(fill=tk.BOTH)
            self.items.append(button)


class MainWindow(tk.Tk):
    TIME = 3

    def __init__(self):
        super(MainWindow, self).__init__()
        self.resizable(True, True)
        self.withdraw()
        self.login_layout()
        self.score = 0
        self.username = "None"
        self.protocol("WM_DELETE_WINDOW", self.on_leave)
        self.consumer = Consumer()
        self.publisher = Publisher()
        self.timer = Timer(self.TIME)

    def waiting_layout(self):
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
        self.consumer.start()
        self.deiconify()

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
            if username in players.keys():
                msg.showerror(
                    title="Invalid Username!",
                    message="This username is already taken, choose another!"
                )
                return
            return username

        else:
            raise RuntimeError("Login is no longer available")

    def on_log_in(self):
        self.username = self.validate_username()
        if self.username is not None:
            players[self.username] = {
                "score": self.score
            }
            self.register_player()
            self.login.destroy()
            self.waiting_layout()

    def register_player(self):
        self.publisher.publish(f"{NEW_PLAYER}:{self.username}:{self.score}")

    def update_score(self):
        self.score += 1
        self.publisher.publish(f"{UPDATE_SCORE}:{self.username}:{self.score}")

    def remove_player(self):
        self.publisher.publish(f"{PLAYER_LOST}:{self.username}:{self.score}")
        players.pop(self.username)

    def on_leave(self):
        self.destroy()

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

        self.player_list = PlayerList(
            master=self.player_list_area,
        )
        self.player_list.pack(fill=tk.BOTH)

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
            if self.timer.OUT_OF_TIME.isSet():
                msg.showerror("You Lost")
                self.remove_player()
                import os
                os._exit(0)
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
            command=self.on_click
        )
        self.click.pack(fill=tk.BOTH)

    def on_click(self):
        self.timer.reset()
        self.update_score()


window = MainWindow()
window.mainloop()
