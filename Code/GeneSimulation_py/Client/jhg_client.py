import socket
import tkinter as tk
import json
from multiprocessing import Process, Queue


import data_collection_script

current_total = 0
max_total = 22
client_socket = None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.max_value = 22
        self.current_total = 0

        self.title("Row Example")

        # Labels for the columns
        header_frame = tk.Frame(self)
        header_frame.pack(pady=5)

        tk.Label(header_frame, text="Index").grid(row=0, column=0)
        tk.Label(header_frame, text="Popularity").grid(row=0, column=1)
        tk.Label(header_frame, text="Sent").grid(row=0, column=2)
        tk.Label(header_frame, text="Received").grid(row=0, column=3)
        tk.Label(header_frame, text="").grid(row=0, column=4)  # Placeholder for button column
        tk.Label(header_frame, text="Allocations").grid(row=0, column=5)
        tk.Label(header_frame, text="").grid(row=0, column=6)  # Placeholder for button column

        # Create 11 rows
        self.row_frames = []
        for i in range(11):
            row_frame = RowFrame(self, i)
            row_frame.pack(pady=5)
            self.row_frames.append(row_frame)

        # Bottom frame for Submit button and integer entry
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(pady=10)

        self.submit_button = tk.Button(self.bottom_frame, text="Submit", command=self.submit)
        self.submit_button.pack(side=tk.LEFT)

        self.int_entry = tk.Label(self.bottom_frame, width=5)
        self.int_entry.pack(side=tk.LEFT)
        self.int_entry["text"] = self.current_total

        # replace this with a process from the finished script.


    def start_receiver(self):
        self.queue = Queue()  # Create a queue for communication
        p = Process(target=self.receive_data, args=(self.queue,))
        p.start()
        self.check_queue()  # Start checking the queue for messages

    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()  # Non-blocking get
                print("Received from server:", message)
                # Process the message as needed
        except Exception:
            pass
        self.after(100, self.check_queue)  # Check the queue again after 100 ms



    def update_displayed_total(self):
        self.int_entry['text'] = str(max_total - current_total)

    def submit(self):
        results = []
        for row_frame in self.row_frames:
            allocations = row_frame.hold_label['text']
            results.append(allocations)
        print("here are the results ", results)
        submission = {
            "SUBMISSION": results
        }
        # put this in the data collection portion, call a funciton or whatever. make it an import.

class RowFrame(tk.Frame):
    def __init__(self, master, index):
        super().__init__(master)

        # Row index
        self.index_entry = tk.Entry(self, width=3)
        self.index_entry.insert(0, str(index))
        self.index_entry.config(state='readonly')
        self.index_entry.grid(row=0, column=0)

        # Text box for floats (popularity)
        self.float_entry = tk.Entry(self)
        self.float_entry.grid(row=0, column=1)

        # Text box for integers (sent)
        self.int_entry1 = tk.Entry(self)
        self.int_entry1.grid(row=0, column=2)

        # Another text box for integers (received)
        self.int_entry2 = tk.Entry(self)
        self.int_entry2.grid(row=0, column=3)

        # Button to decrement a value
        self.decrement_button = tk.Button(self, text='-', command=self.decrement_value)
        self.decrement_button.grid(row=0, column=4)

        # Label that holds an integer (allocations)
        self.hold_label = tk.Label(self, text="0", width=5)
        self.hold_label.grid(row=0, column=5)

        # Button to increment a value
        self.increment_button = tk.Button(self, text='+', command=self.increment_value)
        self.increment_button.grid(row=0, column=6)

    def decrement_value(self):
        global current_total, max_total

        current_value = int(self.hold_label['text'])
        if current_value == 0 and current_total < max_total:
            current_total += 1
            current_value -= 1
        elif current_value > 0 and current_total < max_total + 1:
            current_total -= 1
            current_value -= 1

        self.hold_label['text'] = str(current_value)
        self.master.update_displayed_total()

    def increment_value(self):
        global current_total, max_total
        current_value = int(self.hold_label['text'])
        if current_value == 0 and current_total < max_total:
            current_total += 1
            current_value += 1
        elif current_value > 0 and current_total < max_total:
            current_total += 1
            current_value += 1

        self.hold_label['text'] = str(current_value)
        self.master.update_displayed_total()


def start_gui(): # our version of the main funciton. could probably slap this under init.
    app = App()
    app.mainloop()
