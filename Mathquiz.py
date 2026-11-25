import random
import tkinter as tk

# colours and layout stuff
BG = "#10111F"
PANEL = "#1B1D32"
PANEL2 = "#252842"
PURPLE = "#9B5CFF"
CYAN = "#00E5FF"
WHITE = "#FFFFFF"
GREY = "#A5A8C5"
GREEN = "#42E6A4"
RED = "#FF5573"
ORANGE = "#FFB454"
FONT = "Segoe UI"

TOTAL_QUESTIONS = 10
PROGRESS_WIDTH = 430

# number ranges for each diffculty level
DIFFICULTY_RANGES = {
    "Easy": (1, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999),
}

# grade cutoffs from highest to lowest score
GRADE_TIERS = [
    (90, "S", GREEN, "LEGENDARY PERFORMANCE!"),
    (80, "A", GREEN, "EXCELLENT WORK!"),
    (70, "B", CYAN, "GREAT JOB!"),
    (60, "C", CYAN, "GOOD EFFORT!"),
    (50, "D", ORANGE, "KEEP PRACTISING!"),
    (0, "F", RED, "YOU CAN DO BETTER!"),
]

# global variables to track how the quiz is going
score = 0
question_number = 0
attempts = 0
correct_answer = 0
difficulty = ""
answered = False
after_id = None  # stores timer id so we can cancel it if user leaves early
current_screen = "menu"
is_fullscreen = True

root = tk.Tk()
root.title("Math Challenge")
root.configure(bg=BG)
root.attributes("-fullscreen", is_fullscreen)


def rounded_rectangle(canvas, x1, y1, x2, y2, radius, colour, tag=None):
    # skip if box is too small or backwards
    if x2 <= x1 or y2 <= y1:
        return

    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
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

    return canvas.create_polygon(
        points,
        smooth=True,
        splinesteps=24,
        fill=colour,
        outline=colour,
        tags=tag,
    )


# frame with a rounded canvas behind it because tkinter frames dont have round corners
class RoundedPanel(tk.Frame):
    def __init__(self, parent, width, height, colour=PANEL):
        super().__init__(parent, width=width, height=height, bg=BG)
        self.pack_propagate(False)  # stop inner widgets from resizing the panel

        self.canvas = tk.Canvas(
            self, width=width, height=height, bg=BG, highlightthickness=0
        )
        self.canvas.place(x=0, y=0)
        rounded_rectangle(self.canvas, 2, 2, width - 2, height - 2, 25, colour)

        self.content = tk.Frame(self, bg=colour)
        self.content.place(x=12, y=12, width=width - 24, height=height - 24)


# custom rounded button with hover effect
class RoundedButton(tk.Frame):
    def __init__(
        self,
        parent,
        text,
        command,
        width=300,
        height=50,
        colour=PURPLE,
        hover_colour="#7540C4",
        text_colour=WHITE,
        font=(FONT, 13, "bold"),
    ):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"))
        self.pack_propagate(False)

        self.command = command
        self.normal_colour = colour
        self.hover_colour = hover_colour
        self.text_colour = text_colour
        self.text = text
        self.font = font
        self.enabled = True

        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(fill="both", expand=True)
        self.draw_button(colour)

        # mouse bindings for hover and click
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_button(self, colour):
        self.canvas.delete("all")
        width = int(self.canvas["width"])
        height = int(self.canvas["height"])

        rounded_rectangle(self.canvas, 1, 1, width - 1, height - 1, 17, colour)
        self.canvas.create_text(
            width // 2,
            height // 2,
            text=self.text,
            fill=self.text_colour,
            font=self.font,
        )

    def on_enter(self, event):
        if self.enabled:
            self.draw_button(self.hover_colour)

    def on_leave(self, event):
        if self.enabled:
            self.draw_button(self.normal_colour)

    def on_click(self, event):
        if self.enabled:
            self.command()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.canvas.config(cursor="hand2" if enabled else "")
        self.draw_button(self.normal_colour if enabled else "#45455A")


# entry box inside a rounded border
class RoundedEntry(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, width=300, height=55, bg=PANEL)
        self.pack_propagate(False)

        self.canvas = tk.Canvas(
            self, width=300, height=55, bg=PANEL, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        rounded_rectangle(self.canvas, 1, 1, 299, 54, 15, PURPLE)
        rounded_rectangle(self.canvas, 3, 3, 297, 52, 13, PANEL2)

        self.entry = tk.Entry(
            self.canvas,
            font=(FONT, 20, "bold"),
            justify="center",
            bg=PANEL2,
            fg=CYAN,
            insertbackground=CYAN,
            relief="flat",
            bd=0,
        )
        self.canvas.create_window(150, 27, width=270, height=35, window=self.entry)
        self.entry.bind("<Button-1>", lambda event: self.entry.focus_force())


def set_fullscreen(state):
    global is_fullscreen
    is_fullscreen = state
    root.attributes("-fullscreen", is_fullscreen)


def toggle_fullscreen(event=None):
    set_fullscreen(not is_fullscreen)


def exit_fullscreen(event=None):
    if is_fullscreen:
        set_fullscreen(False)


def update_progress():
    # redraw progress fill based on current question number
    progress_bar.delete("fill")
    fill_width = PROGRESS_WIDTH * question_number / TOTAL_QUESTIONS
    if fill_width > 0:
        rounded_rectangle(progress_bar, 0, 0, fill_width, 14, 7, CYAN, tag="fill")


def cancel_pending():
    # stops old .after() callbacks from firing after switching screens
    global after_id
    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None


def clear_screens():
    menu_frame.pack_forget()
    quiz_frame.pack_forget()
    results_frame.pack_forget()


def displayMenu():
    global current_screen
    cancel_pending()
    current_screen = "menu"
    clear_screens()
    menu_frame.pack(pady=15)


def select_difficulty(level):
    global difficulty, current_screen
    difficulty = level
    current_screen = "quiz"
    clear_screens()
    quiz_frame.pack(pady=5)
    start_quiz()


def go_back():
    displayMenu()


def start_quiz():
    global score, question_number, answered
    cancel_pending()
    score = 0
    question_number = 0
    answered = False
    update_score()
    displayProblem()


def randomInt(minimum, maximum):
    return random.randint(minimum, maximum)


def decideOperation():
    # only plus or minus for now
    return random.choice(["+", "-"])


def displayProblem():
    global question_number, attempts, correct_answer, answered, after_id

    after_id = None
    if current_screen != "quiz":
        return

    if question_number >= TOTAL_QUESTIONS:
        displayResults()
        return

    question_number += 1
    attempts = 0
    answered = False

    minimum, maximum = DIFFICULTY_RANGES.get(difficulty, (1, 9))
    num1 = randomInt(minimum, maximum)
    num2 = randomInt(minimum, maximum)
    operation = decideOperation()

    # swap numbers on easy subtraction so kids dont get negative answers
    if difficulty == "Easy" and operation == "-" and num1 < num2:
        num1, num2 = num2, num1

    correct_answer = num1 + num2 if operation == "+" else num1 - num2

    question_label.config(text=f"{num1}  {operation}  {num2}")
    question_count_label.config(
        text=f"QUESTION {question_number:02d} / {TOTAL_QUESTIONS}"
    )
    update_progress()

    answer_entry.entry.config(state="normal")
    answer_entry.entry.delete(0, tk.END)
    submit_button.set_enabled(True)
    feedback_label.config(text="ENTER YOUR ANSWER BELOW", fg=GREY)

    # small delay so focus works nicer after screen changes
    root.after(100, answer_entry.entry.focus_force)


def finish_question(message, colour, delay_ms):
    # lock input briefly so user can see feedback before next question loads
    global answered, after_id
    answered = True
    feedback_label.config(text=message, fg=colour)
    answer_entry.entry.config(state="disabled")
    submit_button.set_enabled(False)
    after_id = root.after(delay_ms, displayProblem)


def isCorrect():
    global attempts, score

    if current_screen != "quiz" or answered:
        return

    user_input = answer_entry.entry.get().strip()
    if not user_input:
        feedback_label.config(text="PLEASE ENTER AN ANSWER", fg=RED)
        answer_entry.entry.focus_force()
        return

    try:
        user_answer = int(user_input)
    except ValueError:
        # user typed letters or symbols instead of a whole number
        feedback_label.config(text="PLEASE ENTER A VALID NUMBER", fg=RED)
        answer_entry.entry.delete(0, tk.END)
        answer_entry.entry.focus_force()
        return

    attempts += 1

    if user_answer == correct_answer:
        points = 10 if attempts == 1 else 5  # full points on first try, half on second
        score += points
        update_score()
        finish_question(f"CORRECT! +{points} POINTS", GREEN, 1100)
    elif attempts == 1:
        # give one more chance before showing the answer
        feedback_label.config(text="WRONG! TRY AGAIN", fg=ORANGE)
        answer_entry.entry.delete(0, tk.END)
        answer_entry.entry.config(state="normal")
        answer_entry.entry.focus_force()
    else:
        finish_question(f"CORRECT ANSWER: {correct_answer}", RED, 1600)


def update_score():
    score_label.config(text=f"{score:03d}")


def get_grade_summary(final_score):
    for min_score, grade, colour, message in GRADE_TIERS:
        if final_score >= min_score:
            return grade, colour, message
    return "F", RED, "YOU CAN DO BETTER!"


def displayResults():
    global current_screen
    cancel_pending()
    current_screen = "results"
    clear_screens()
    results_frame.pack(pady=25)

    grade, grade_colour, message = get_grade_summary(score)
    result_grade.config(text=grade, fg=grade_colour)
    result_score.config(text=f"{score} / {TOTAL_QUESTIONS * 10}")
    result_message.config(text=message)


def replay_quiz():
    displayMenu()


def exit_quiz():
    cancel_pending()
    root.destroy()


# keeps everything centred no matter how big the window is
stage = tk.Frame(root, bg=BG)
stage.place(relx=0.5, rely=0.5, anchor="center")

# app title banner
header = tk.Frame(stage, bg=BG)
header.pack(pady=(0, 8))

tk.Label(header, text="NEON", font=(FONT, 16, "bold"), fg=CYAN, bg=BG).pack()
tk.Label(
    header, text="MATH CHALLENGE", font=(FONT, 27, "bold"), fg=WHITE, bg=BG
).pack()
tk.Label(
    header,
    text="THINK FAST. SOLVE SMART. SCORE BIG.  •  F11 FULLSCREEN  •  ESC WINDOWED",
    font=(FONT, 9, "bold"),
    fg=GREY,
    bg=BG,
).pack(pady=3)

# start menu screen
menu_frame = RoundedPanel(stage, 500, 430, PANEL)
menu_content = menu_frame.content

tk.Label(
    menu_content,
    text="SELECT YOUR LEVEL",
    font=(FONT, 22, "bold"),
    bg=PANEL,
    fg=WHITE,
).pack(pady=(35, 8))
tk.Label(
    menu_content,
    text="Choose a difficulty to begin",
    font=(FONT, 12),
    bg=PANEL,
    fg=GREY,
).pack(pady=(0, 25))


def create_difficulty_button(text, level, colour):
    button = RoundedButton(
        menu_content,
        text=text,
        command=lambda lvl=level: select_difficulty(lvl),
        width=320,
        height=55,
        colour=colour,
        hover_colour="#454966",
    )
    button.pack(pady=10)


create_difficulty_button("01   EASY", "Easy", "#168C83")
create_difficulty_button("02   MODERATE", "Moderate", "#5365D9")
create_difficulty_button("03   ADVANCED", "Advanced", "#8846D9")

# main quiz screen
quiz_frame = RoundedPanel(stage, 550, 650, PANEL)
quiz_content = quiz_frame.content

back_button = RoundedButton(
    quiz_content,
    text="←  BACK TO MENU",
    command=go_back,
    width=180,
    height=38,
    colour=RED,
    hover_colour="#D93659",
    font=(FONT, 11, "bold"),
)
back_button.pack(anchor="w", pady=(3, 5))

question_count_label = tk.Label(
    quiz_content,
    text="QUESTION 01 / 10",
    font=(FONT, 11, "bold"),
    bg=PANEL,
    fg=CYAN,
)
question_count_label.pack(pady=5)

# progress bar canvas
progress_bar = tk.Canvas(
    quiz_content,
    width=PROGRESS_WIDTH,
    height=14,
    bg=PANEL2,
    highlightthickness=0,
)
progress_bar.pack(pady=8)
rounded_rectangle(progress_bar, 0, 0, PROGRESS_WIDTH, 14, 7, PANEL2)

score_panel = RoundedPanel(quiz_content, 200, 85, PANEL2)
score_panel.pack(pady=10)

tk.Label(
    score_panel.content,
    text="CURRENT SCORE",
    font=(FONT, 9, "bold"),
    bg=PANEL2,
    fg=GREY,
).pack(pady=(7, 0))

score_label = tk.Label(
    score_panel.content,
    text="000",
    font=(FONT, 26, "bold"),
    bg=PANEL2,
    fg=CYAN,
)
score_label.pack()

tk.Label(
    quiz_content,
    text="SOLVE THIS",
    font=(FONT, 11, "bold"),
    bg=PANEL,
    fg=PURPLE,
).pack(pady=5)

question_label = tk.Label(
    quiz_content,
    text="5 + 5",
    font=(FONT, 36, "bold"),
    bg=PANEL,
    fg=WHITE,
)
question_label.pack(pady=8)

tk.Label(
    quiz_content,
    text="YOUR ANSWER",
    font=(FONT, 10, "bold"),
    bg=PANEL,
    fg=GREY,
).pack(pady=4)

answer_entry = RoundedEntry(quiz_content)
answer_entry.pack(pady=7)

submit_button = RoundedButton(
    quiz_content,
    text="SUBMIT ANSWER  →",
    command=isCorrect,
    width=300,
    height=52,
    colour=PURPLE,
    hover_colour="#7540C4",
    font=(FONT, 14, "bold"),
)
submit_button.pack(pady=8)

feedback_label = tk.Label(
    quiz_content,
    text="ENTER YOUR ANSWER BELOW",
    font=(FONT, 10, "bold"),
    bg=PANEL,
    fg=GREY,
)
feedback_label.pack(pady=5)

# end of quiz results screen
results_frame = RoundedPanel(stage, 500, 500, PANEL)
results_content = results_frame.content

tk.Label(
    results_content,
    text="CHALLENGE COMPLETE",
    font=(FONT, 21, "bold"),
    bg=PANEL,
    fg=WHITE,
).pack(pady=(35, 15))

result_grade = tk.Label(
    results_content,
    text="A",
    font=(FONT, 70, "bold"),
    bg=PANEL,
    fg=CYAN,
)
result_grade.pack(pady=5)

result_score = tk.Label(
    results_content,
    text="80 / 100",
    font=(FONT, 22, "bold"),
    bg=PANEL,
    fg=WHITE,
)
result_score.pack(pady=8)

result_message = tk.Label(
    results_content,
    text="EXCELLENT WORK!",
    font=(FONT, 12, "bold"),
    bg=PANEL,
    fg=PURPLE,
)
result_message.pack(pady=8)

replay_button = RoundedButton(
    results_content,
    text="PLAY AGAIN",
    command=replay_quiz,
    width=280,
    height=50,
    colour=PURPLE,
    hover_colour="#7540C4",
)
replay_button.pack(pady=12)

exit_button = RoundedButton(
    results_content,
    text="EXIT GAME",
    command=exit_quiz,
    width=280,
    height=45,
    colour=PANEL2,
    hover_colour="#363A5B",
    text_colour=CYAN,
)
exit_button.pack(pady=5)

# keyboard shortcuts
root.bind("<Return>", lambda event: isCorrect())
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_fullscreen)

displayMenu()
root.mainloop()