
import tkinter as tk
from tkinter import messagebox
import random
import os

# Colours
BG = "#0F172A"
PANEL = "#1E293B"
CARD = "#273449"
BLUE = "#38BDF8"
WHITE = "#F8FAFC"
GREY = "#94A3B8"
YELLOW = "#FACC15"
GREEN = "#4ADE80"

# Variables
current_joke = ""
punchline = ""
joke_count = 0


# Load jokes from the text file
def load_jokes():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "resources",
        "randomJokes.txt"
    )

    try:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        jokes = []

        for line in lines:
            if "?" in line:
                jokes.append(line.strip())

        return jokes

    except FileNotFoundError:
        messagebox.showerror(
            "Error",
            "Could not find randomJokes.txt"
        )
        return []


# Make rounded rectangles for the design
def round_box(canvas, x1, y1, x2, y2, radius, colour):

    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]

    return canvas.create_polygon(
        points,
        smooth=True,
        fill=colour,
        outline=""
    )


# Create a button with rounded corners
def make_button(parent, text, command, colour,
                text_colour=WHITE, width=200):

    button = tk.Canvas(
        parent,
        width=width,
        height=50,
        bg=BG,
        highlightthickness=0,
        cursor="hand2"
    )

    shape = round_box(
        button, 2, 2, width - 2, 48,
        15, colour
    )

    button.create_text(
        width / 2,
        25,
        text=text,
        font=("Segoe UI", 11, "bold"),
        fill=text_colour
    )

    # Change colour when mouse is over button
    def hover(event):
        button.itemconfig(shape, fill="#334155")

    def normal(event):
        button.itemconfig(shape, fill=colour)

    button.bind("<Enter>", hover)
    button.bind("<Leave>", normal)
    button.bind("<Button-1>", lambda event: command())

    return button


# Choose and display a random joke
def tell_joke():
    global current_joke, punchline, joke_count

    if len(jokes) == 0:
        messagebox.showwarning(
            "No Jokes",
            "There are no jokes available."
        )
        return

    # Try not to repeat the same joke
    available = []

    for joke in jokes:
        if joke != current_joke:
            available.append(joke)

    if len(available) == 0:
        available = jokes

    current_joke = random.choice(available)

    parts = current_joke.split("?", 1)

    question = parts[0] + "?"
    punchline = parts[1].strip()

    joke_count += 1

    question_label.config(text=question)
    answer_label.config(text="")

    status_label.config(
        text="Can you guess the punchline?",
        fg=GREY
    )

    counter_label.config(
        text="JOKE #" + str(joke_count)
    )


# Show the answer to the joke
def show_punchline():

    if punchline == "":
        messagebox.showinfo(
            "Joke Time",
            "Please get a joke first!"
        )
    else:
        answer_label.config(text=punchline)

        status_label.config(
            text="Hope that made you laugh!",
            fg=GREEN
        )


# Create main window
window = tk.Tk()
window.title("Joke Telling Assistant")
window.geometry("650x700")
window.resizable(False, False)
window.config(bg=BG)

# Load jokes
jokes = load_jokes()


# Main heading
title_label = tk.Label(
    window,
    text="JOKE TIME",
    font=("Segoe UI", 25, "bold"),
    bg=BG,
    fg=WHITE
)
title_label.pack(pady=(30, 5))


subtitle_label = tk.Label(
    window,
    text="Your daily dose of laughter",
    font=("Segoe UI", 11),
    bg=BG,
    fg=GREY
)
subtitle_label.pack(pady=(0, 25))


# Joke counter
counter_label = tk.Label(
    window,
    text="JOKE #0",
    font=("Segoe UI", 10, "bold"),
    bg=BG,
    fg=BLUE
)
counter_label.pack(pady=(0, 15))


# Main rounded panel
panel_canvas = tk.Canvas(
    window,
    width=560,
    height=340,
    bg=BG,
    highlightthickness=0
)
panel_canvas.pack()

round_box(
    panel_canvas,
    0, 0, 560, 340,
    25, PANEL
)


# Frame inside the rounded panel
joke_frame = tk.Frame(
    panel_canvas,
    bg=PANEL,
    width=500,
    height=290
)

joke_frame.pack_propagate(False)

panel_canvas.create_window(
    280, 170,
    window=joke_frame
)


# Small heading
heading_label = tk.Label(
    joke_frame,
    text="YOUR RANDOM JOKE",
    font=("Segoe UI", 10, "bold"),
    bg=PANEL,
    fg=BLUE
)
heading_label.pack(pady=(20, 20))


# Joke question
question_label = tk.Label(
    joke_frame,
    text="Click the button to get your first joke!",
    font=("Segoe UI", 19, "bold"),
    bg=PANEL,
    fg=WHITE,
    wraplength=450,
    justify="center"
)
question_label.pack(pady=(5, 20))


# Line between question and answer
line = tk.Frame(
    joke_frame,
    bg="#334155",
    width=400,
    height=1
)
line.pack(pady=10)


# Joke punchline
answer_label = tk.Label(
    joke_frame,
    text="The punchline will appear here.",
    font=("Segoe UI", 14, "bold"),
    bg=PANEL,
    fg=YELLOW,
    wraplength=450,
    justify="center"
)
answer_label.pack(pady=(15, 15))


# Small status message
status_label = tk.Label(
    joke_frame,
    text="Ready for a laugh?",
    font=("Segoe UI", 10),
    bg=PANEL,
    fg=GREY
)
status_label.pack(pady=5)


# Frame for buttons
button_frame = tk.Frame(
    window,
    bg=BG
)
button_frame.pack(pady=(25, 10))


# Tell joke button
tell_button = make_button(
    button_frame,
    "TELL ME A JOKE",
    tell_joke,
    BLUE,
    BG,
    265
)
tell_button.grid(row=0, column=0, padx=7)


# Show punchline button
answer_button = make_button(
    button_frame,
    "SHOW PUNCHLINE",
    show_punchline,
    CARD,
    WHITE,
    265
)
answer_button.grid(row=0, column=1, padx=7)


# Next joke button
next_button = make_button(
    window,
    "NEXT JOKE  →",
    tell_joke,
    PANEL,
    BLUE,
    550
)
next_button.pack(pady=(10, 20))


# Exit button
exit_button = tk.Button(
    window,
    text="EXIT",
    font=("Segoe UI", 10, "bold"),
    bg=BG,
    fg=GREY,
    activebackground=BG,
    activeforeground=WHITE,
    relief="flat",
    cursor="hand2",
    command=window.destroy
)
exit_button.pack(pady=5)


# Start the program
window.mainloop()
