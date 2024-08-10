import tkinter as tk
from tkinter import messagebox, PhotoImage, Canvas
import psycopg2
from werkzeug.security import check_password_hash
import random
import threading
import time
from config import get_db_connection

def connect_db():
    conn = get_db_connection()
    return conn

class HealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Monitor")

        self.is_generating = False

        # Login Frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=80, pady=80)

        # Set background image for login frame
        self.login_bg_image = PhotoImage(file="sw.png")
        self.login_canvas = Canvas(self.login_frame, width=self.login_bg_image.width(), height=self.login_bg_image.height())
        self.login_canvas.pack(fill="both", expand=True)
        self.login_canvas.create_image(10, 10, anchor="nw", image=self.login_bg_image)

        # Place widgets on the canvas instead of directly on the frame
        account_label = tk.Label(self.login_frame, text="Account:", font=("Helvetica", 16))
        self.login_canvas.create_window(270, 250, window=account_label)

        self.account_entry = tk.Entry(self.login_frame, width=40)
        self.login_canvas.create_window(350, 300, window=self.account_entry)

        password_label = tk.Label(self.login_frame, text="Password:", font=("Helvetica", 16))
        self.login_canvas.create_window(280, 350, window=password_label)

        self.password_entry = tk.Entry(self.login_frame, show='*', width=40)
        self.login_canvas.create_window(350, 400, window=self.password_entry)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login, width=10, height=2)
        self.login_canvas.create_window(450, 470, window=self.login_button)

        # Monitor Frame setup remains the same

        # Monitor Frame
        self.monitor_frame = tk.Frame(self.root)
        
        # Set background image
        self.bg_image = PhotoImage(file="sw.png")
        self.canvas = Canvas(self.monitor_frame, width=self.bg_image.width(), height=self.bg_image.height())
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        self.start_button = tk.Button(self.monitor_frame, text="Start", command=self.toggle_generation, font=("Helvetica", 16), padx=10, pady=5)
        self.start_button_window = self.canvas.create_window(310, 330, anchor="nw", window=self.start_button)

    def login(self):
        account = self.account_entry.get()
        password = self.password_entry.get()

        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM users WHERE account = %s', (account,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            self.user_id = user[0]
            self.show_monitor()
        else:
            messagebox.showerror("Login Failed", "Invalid account or password.")

    def show_monitor(self):
        self.login_frame.pack_forget()
        self.monitor_frame.pack(padx=10, pady=10)

    def toggle_generation(self):
        if self.is_generating:
            self.is_generating = False
            self.start_button.config(text="Start")
        else:
            self.is_generating = True
            self.start_button.config(text="Stop")
            self.start_data_generation()

    def start_data_generation(self):
        def generate_data():
            while self.is_generating:
                heart_rate = random.randint(60, 100)
                blood_pressure = random.randint(80, 120)
                body_temp = round(random.uniform(36.0, 37.5), 1)
                blood_oxygen_level = random.randint(95, 100)
                respiratory_rate = random.randint(12, 20)
                blood_sugar_level = random.randint(70, 140)
                sleep_quality = round(random.uniform(0, 1), 1)

                conn = connect_db()
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO health (user_id, heart_rate, blood_pressure, body_temp, blood_oxygen_level, respiratory_rate, blood_sugar_level, sleep_quality, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ''', (self.user_id, heart_rate, blood_pressure, body_temp, blood_oxygen_level, respiratory_rate, blood_sugar_level, sleep_quality))
                conn.commit()
                cur.close()
                conn.close()

                time.sleep(3)  # Wait for 10 seconds before generating new data

        threading.Thread(target=generate_data).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthMonitorApp(root)
    root.mainloop()
