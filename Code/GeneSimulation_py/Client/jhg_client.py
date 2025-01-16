import tkinter as tk


class RowFrame(tk.Frame):
    def __init__(self, master, index):
        super().__init__(master)

        # Row index
        self.index_entry = tk.Entry(self, width=3)
        self.index_entry.insert(0, str(index))
        self.index_entry.config(state='readonly')  # Make it read-only
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
        self.decrement_button = tk.Button(self, text='-', command=lambda: self.decrement_value())
        self.decrement_button.grid(row=0, column=4)

        # Label that holds an integer (allocations)
        self.hold_label = tk.Label(self, text="0", width=5)
        self.hold_label.grid(row=0, column=5)

        # Button to increment a value
        self.increment_button = tk.Button(self, text='+', command=lambda: self.increment_value())
        self.increment_button.grid(row=0, column=6)

    def decrement_value(self):
        try:
            current_value = int(self.hold_label['text'])
            self.hold_label['text'] = str(current_value - 1)  # Allow negative values
        except ValueError:
            self.hold_label['text'] = '-1'  # Default to -1 on invalid input

    def increment_value(self):
        try:
            current_value = int(self.hold_label['text'])
            self.hold_label['text'] = str(current_value + 1)
        except ValueError:
            self.hold_label['text'] = '0'  # Default to 0 on invalid input


class App(tk.Tk):
    def __init__(self):
        super().__init__()

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
        for i in range(11):
            row_frame = RowFrame(self, i)
            row_frame.pack(pady=5)

        # Bottom frame for Submit button and integer entry
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(pady=10)

        self.submit_button = tk.Button(self.bottom_frame, text="Submit", command=self.submit)
        self.submit_button.pack(side=tk.LEFT)

        self.int_entry = tk.Entry(self.bottom_frame, width=5)
        self.int_entry.pack(side=tk.LEFT)

    def submit(self):
        # Placeholder function for submit action
        try:
            submitted_value = int(self.int_entry.get())
            print(f"Submitted value: {submitted_value}")
        except ValueError:
            print("Invalid input! Please enter an integer.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
