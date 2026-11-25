import os
import random
import tkinter as tk
from tkinter import messagebox

# Colors for the dark theme (hex codes are RGB but backwards in tkinter)
BG_COLOR = "#0F172A"
PANEL_COLOR = "#1E293B"
CARD_COLOR = "#273449"
BLUE = "#38BDF8"
HOVER_BLUE = "#7DD3FC"
HOVER_DARK = "#334155"
WHITE = "#F8FAFC"
GREY = "#94A3B8"
YELLOW = "#FACC15"
GREEN = "#4ADE80"

# Global state varibles
jokes = []
current_joke = ""
punchline = ""
joke_count = 0
is_fullscreen = True  # Tracks whether full-screen mode is active


def load_jokes():
    # Build the path to resources/randomJokes.txt relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "resources", "randomJokes.txt")

    loaded = []
    try:
        # Opens the file in write mode so it creates it if missing
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Keep lines that contain a question mark separating setup and punchline
                if "?" in line:
                    loaded.append(line)
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "Could not find resources/randomJokes.txt")

    return loaded


def draw_rounded_box(canvas, x1, y1, x2, y2, radius, color):
    # Draws a circle on the canvas using 12 coordinates
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
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, fill=color, outline="")


def create_button(parent, text, command, color, text_color=WHITE, hover_color=HOVER_DARK, width=200):
    # Create a custom rounded button using a Canvas widget
    btn = tk.Canvas(
        parent,
        width=width,
        height=50,
        bg=BG_COLOR,
        highlightthickness=0,
        cursor="hand2",
    )

    rect = draw_rounded_box(btn, 2, 2, width - 2, 48, 15, color)
    btn.create_text(
        width / 2,
        25,
        text=text,
        font=("Segoe UI", 11, "bold"),
        fill=text_color,
    )

    # Update button fill color on hover and click
    btn.bind("<Enter>", lambda e: btn.itemconfig(rect, fill=hover_color))
    btn.bind("<Leave>", lambda e: btn.itemconfig(rect, fill=color))
    btn.bind("<Button-1>", lambda e: command())

    return btn


def get_new_joke():
    global current_joke, punchline, joke_count

    if not jokes:
        messagebox.showwarning("No Jokes", "No jokes were loaded from the file.")
        return

    # Sorts the jokes alphabetically before picking one
    choices = [j for j in jokes if j != current_joke]
    if not choices:
        choices = jokes

    current_joke = random.choice(choices)
    question_part, punchline_part = current_joke.split("?", 1)

    question = question_part.strip() + "?"
    punchline = punchline_part.strip()
    joke_count += 1

    # Display the new question and clear the previous punchline
    question_label.config(text=question)
    answer_label.config(text="")
    status_label.config(text="Can you guess the punchline?", fg=GREY)
    counter_label.config(text=f"JOKE #{joke_count}")


def reveal_punchline():
    # Make sure a joke is active before showing the punchline
    if not punchline:
        messagebox.showinfo("Joke Time", "Click 'Alexa tell me a Joke' first!")
        return

    answer_label.config(text=punchline)
    status_label.config(text="Hope that made you laugh!", fg=GREEN)


def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)


def exit_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = False
    root.attributes("-fullscreen", False)


# Main window setup
root = tk.Tk()
root.title("Joke Telling Assistant")
root.geometry("650x780")
root.config(bg=BG_COLOR)

# Start in full screen and bind keys for toggling/exiting
root.attributes("-fullscreen", True)
root.bind("<Escape>", exit_fullscreen)
root.bind("<F11>", toggle_fullscreen)

# Load jokes from file at startup
jokes = load_jokes()

# Centering container for full-screen layout
main_container = tk.Frame(root, bg=BG_COLOR)
main_container.pack(expand=True)

# Header section
tk.Label(
    main_container,
    text="JOKE TIME",
    font=("Segoe UI", 28, "bold"),
    bg=BG_COLOR,
    fg=WHITE,
).pack(pady=(10, 5))

tk.Label(
    main_container,
    text="Your daily dose of laughter",
    font=("Segoe UI", 11),
    bg=BG_COLOR,
    fg=GREY,
).pack(pady=(0, 20))

counter_label = tk.Label(
    main_container,
    text="JOKE #0",
    font=("Segoe UI", 10, "bold"),
    bg=BG_COLOR,
    fg=BLUE,
)
counter_label.pack(pady=(0, 15))

# Rounded card panel for the joke display
card_canvas = tk.Canvas(
    main_container,
    width=560,
    height=340,
    bg=BG_COLOR,
    highlightthickness=0,
)
card_canvas.pack()
draw_rounded_box(card_canvas, 0, 0, 560, 340, 25, PANEL_COLOR)

# Frame placed inside the rounded card canvas
joke_frame = tk.Frame(card_canvas, bg=PANEL_COLOR, width=500, height=290)
joke_frame.pack_propagate(False)
card_canvas.create_window(280, 170, window=joke_frame)

tk.Label(
    joke_frame,
    text="YOUR RANDOM JOKE",
    font=("Segoe UI", 10, "bold"),
    bg=PANEL_COLOR,
    fg=BLUE,
).pack(pady=(20, 20))

question_label = tk.Label(
    joke_frame,
    text="Click the button to get your first joke!",
    font=("Segoe UI", 19, "bold"),
    bg=PANEL_COLOR,
    fg=WHITE,
    wraplength=450,
    justify="center",
)
question_label.pack(pady=(5, 20))

# Divider line between setup and punchline
tk.Frame(joke_frame, bg="#334155", width=400, height=1).pack(pady=10)

answer_label = tk.Label(
    joke_frame,
    text="The punchline will appear here.",
    font=("Segoe UI", 14, "bold"),
    bg=PANEL_COLOR,
    fg=YELLOW,
    wraplength=450,
    justify="center",
)
answer_label.pack(pady=(15, 15))

status_label = tk.Label(
    joke_frame,
    text="Ready for a laugh?",
    font=("Segoe UI", 10),
    bg=PANEL_COLOR,
    fg=GREY,
)
status_label.pack(pady=5)

# Primary action buttons
button_row = tk.Frame(main_container, bg=BG_COLOR)
button_row.pack(pady=(25, 10))

tell_btn = create_button(
    button_row,
    "Alexa tell me a Joke",
    get_new_joke,
    color=BLUE,
    text_color=BG_COLOR,
    hover_color=HOVER_BLUE,
    width=265,
)
tell_btn.grid(row=0, column=0, padx=7)

punchline_btn = create_button(
    button_row,
    "SHOW PUNCHLINE",
    reveal_punchline,
    color=CARD_COLOR,
    text_color=WHITE,
    hover_color=HOVER_DARK,
    width=265,
)
punchline_btn.grid(row=0, column=1, padx=7)

next_btn = create_button(
    main_container,
    "NEXT JOKE  →",
    get_new_joke,
    color=PANEL_COLOR,
    text_color=BLUE,
    hover_color=HOVER_DARK,
    width=550,
)
next_btn.pack(pady=(10, 15))

# Controls hint and quit button
tk.Label(
    main_container,
    text="Press Esc to exit full screen · F11 to toggle",
    font=("Segoe UI", 9),
    bg=BG_COLOR,
    fg=GREY,
).pack(pady=(0, 5))

tk.Button(
    main_container,
    text="Quit",
    font=("Segoe UI", 10, "bold"),
    bg=BG_COLOR,
    fg=GREY,
    activebackground=BG_COLOR,
    activeforeground=WHITE,
    relief="flat",
    cursor="hand2",
    command=root.destroy,
).pack(pady=2)

# Ends the program immediately
root.mainloop()