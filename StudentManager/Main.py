import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import csv

# STUDENT MANAGER - DARK NAVY DASHBOARD

# COLOURS

BG = "#0F172A"
SIDEBAR = "#111C30"
PANEL = "#1E293B"
CARD = "#243449"
INPUT = "#162238"
BLUE = "#38BDF8"
BLUE_DARK = "#0284C7"
WHITE = "#F8FAFC"
GREY = "#94A3B8"
BORDER = "#334155"
GREEN = "#4ADE80"
RED = "#FB7185"
YELLOW = "#FACC15"

FONT = "Segoe UI"

# The text file must be in the same folder
# as this Python file.

FILE_PATH = Path(__file__).with_name("studentMarks.txt")

students = []
current_filter = "all"

# STUDENT CALCULATIONS

def get_coursework(student):
    # Add the three coursework marks.
    return sum(student["marks"])


def get_total(student):
    # Coursework is out of 60 and exam out of 100.
    return get_coursework(student) + student["exam"]


def get_percentage(student):
    # Maximum possible total is 160.
    return get_total(student) / 160 * 100


def get_grade(student):
    percentage = get_percentage(student)

    if percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    return "F"

# FILE HANDLING

def load_students():
    global students

    loaded = []

    try:
        with open(FILE_PATH, "r", encoding="utf-8",
                  newline="") as file:
            rows = list(csv.reader(file))

        if not rows:
            raise ValueError("The student file is empty.")

        expected = int(rows[0][0])

        for row in rows[1:]:
            if not row or all(not x.strip() for x in row):
                continue

            if len(row) != 6:
                raise ValueError("A record must have 6 fields.")

            code = row[0].strip()
            name = row[1].strip()
            marks = [int(x.strip()) for x in row[2:5]]
            exam = int(row[5].strip())

            if not code.isdigit() or len(code) != 4:
                raise ValueError("Invalid student code.")

            if not name:
                raise ValueError("Student name is missing.")

            if any(m < 0 or m > 20 for m in marks):
                raise ValueError("Invalid coursework mark.")

            if not 0 <= exam <= 100:
                raise ValueError("Invalid examination mark.")

            if any(s["code"] == code for s in loaded):
                raise ValueError("Duplicate student code.")

            loaded.append({
                "code": code,
                "name": name,
                "marks": marks,
                "exam": exam
            })

        students = loaded

        if len(students) != expected:
            messagebox.showwarning(
                "File Warning",
                f"Expected {expected} records, "
                f"but loaded {len(students)}."
            )

        set_status("Student records loaded successfully.")

    except FileNotFoundError:
        students = []
        set_status("No student file found. Add a student to begin.")
        messagebox.showwarning(
            "File Not Found",
            f"Could not find:\n{FILE_PATH}\n\n"
            "You can add students and save a new file."
        )

    except (ValueError, IndexError, csv.Error) as error:
        messagebox.showerror("File Error", str(error))
        set_status("Could not load student records.")

    except OSError as error:
        messagebox.showerror("File Error", str(error))

    refresh_table()


def save_students(show_message=True):
    # Save all records to the text file.
    try:
        with open(FILE_PATH, "w", encoding="utf-8",
                  newline="") as file:

            writer = csv.writer(file)
            writer.writerow([len(students)])

            for student in students:
                writer.writerow([
                    student["code"],
                    student["name"],
                    *student["marks"],
                    student["exam"]
                ])

        set_status("All student records saved successfully.")

        if show_message:
            messagebox.showinfo(
                "Saved",
                "Student records saved successfully."
            )

        return True

    except OSError as error:
        messagebox.showerror("Save Error", str(error))
        return False

# ROUNDED RECTANGLE HELPER

def rounded_rectangle(canvas, x1, y1, x2, y2,
                      radius=18, fill=PANEL):

    # Draw a rounded polygon using standard Tkinter.
    radius = min(radius, (x2-x1)/2, (y2-y1)/2)

    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]

    return canvas.create_polygon(
        points,
        smooth=True,
        splinesteps=16,
        fill=fill,
        outline=""
    )

# REUSABLE ROUNDED CARD

class RoundedCard(tk.Canvas):

    def __init__(self, parent, color=PANEL,
                 radius=18, height=100, **kwargs):

        super().__init__(
            parent,
            bg=BG,
            highlightthickness=0,
            bd=0,
            height=height,
            **kwargs
        )

        self.card_color = color
        self.radius = radius

        self.bind("<Configure>", self.draw_card)

    def draw_card(self, event=None):
        self.delete("background")

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 10 or height < 10:
            return

        # Draw background behind card content.
        points = [
            18, 0,
            width-18, 0,
            width, 0,
            width, 18,
            width, height-18,
            width, height,
            width-18, height,
            18, height,
            0, height,
            0, height-18,
            0, 18,
            0, 0
        ]

        self.create_polygon(
            points,
            smooth=True,
            splinesteps=16,
            fill=self.card_color,
            outline="",
            tags="background"
        )

        self.tag_lower("background")

# MAIN WINDOW

root = tk.Tk()
root.title("Student Manager | Dashboard")
root.geometry("1250x780")
root.minsize(1000, 650)
root.configure(bg=BG)

# APPLICATION LAYOUT

sidebar = tk.Frame(root, bg=SIDEBAR, width=235)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

main = tk.Frame(root, bg=BG)
main.pack(side="left", fill="both", expand=True)

# STATUS MESSAGE

status_var = tk.StringVar(value="Ready")

def set_status(message):
    status_var.set(message)

# SIDEBAR HEADER

tk.Label(
    sidebar,
    text="STUDENT",
    font=(FONT, 22, "bold"),
    fg=WHITE,
    bg=SIDEBAR
).pack(anchor="w", padx=25, pady=(30, 0))

tk.Label(
    sidebar,
    text="MANAGER.",
    font=(FONT, 22, "bold"),
    fg=BLUE,
    bg=SIDEBAR
).pack(anchor="w", padx=25)

tk.Label(
    sidebar,
    text="ACADEMIC MANAGEMENT",
    font=(FONT, 9, "bold"),
    fg=GREY,
    bg=SIDEBAR
).pack(anchor="w", padx=25, pady=(5, 30))

tk.Frame(
    sidebar, bg=BORDER, height=1
).pack(fill="x", padx=20, pady=(0, 20))

tk.Label(
    sidebar,
    text="MAIN MENU",
    font=(FONT, 9, "bold"),
    bg=SIDEBAR,
    fg=GREY
).pack(anchor="w", padx=25, pady=(0, 12))

# MAIN HEADER

header = tk.Frame(main, bg=BG)
header.pack(fill="x", padx=30, pady=(25, 12))

tk.Label(
    header,
    text="Dashboard",
    font=(FONT, 27, "bold"),
    bg=BG,
    fg=WHITE
).pack(anchor="w")

tk.Label(
    header,
    text="Manage student records and academic performance",
    font=(FONT, 10),
    bg=BG,
    fg=GREY
).pack(anchor="w", pady=(4, 0))

# DASHBOARD STATISTICS

stats_frame = tk.Frame(main, bg=BG)
stats_frame.pack(fill="x", padx=25, pady=(12, 18))

stats_frame.columnconfigure(0, weight=1)
stats_frame.columnconfigure(1, weight=1)
stats_frame.columnconfigure(2, weight=1)

stat_values = {}

def create_stat_card(column, title, color):

    canvas = RoundedCard(
        stats_frame,
        color=PANEL,
        height=120
    )

    canvas.grid(
        row=0,
        column=column,
        sticky="ew",
        padx=6
    )

    # Canvas text is drawn on top of the rounded card.
    canvas.create_text(
        22, 27,
        text=title,
        fill=GREY,
        font=(FONT, 11),
        anchor="w",
        tags="content"
    )

    value_id = canvas.create_text(
        22, 73,
        text="0",
        fill=color,
        font=(FONT, 26, "bold"),
        anchor="w",
        tags="content"
    )

    stat_values[title] = (canvas, value_id)

    return canvas


create_stat_card(0, "Total Students", BLUE)
create_stat_card(1, "Class Average", GREEN)
create_stat_card(2, "Highest Score", YELLOW)


def update_stats():

    count = len(students)

    if students:
        average = sum(
            get_percentage(s) for s in students
        ) / count

        highest = max(get_total(s) for s in students)
    else:
        average = 0
        highest = 0

    values = {
        "Total Students": str(count),
        "Class Average": f"{average:.1f}%",
        "Highest Score": f"{highest}/160"
    }

    for title, value in values.items():
        canvas, item = stat_values[title]
        canvas.itemconfig(item, text=value)


# TABLE HEADER AND SEARCH

table_header = tk.Frame(main, bg=BG)
table_header.pack(fill="x", padx=30, pady=(0, 12))

tk.Label(
    table_header,
    text="Student Records",
    font=(FONT, 17, "bold"),
    bg=BG,
    fg=WHITE
).pack(side="left")

search_var = tk.StringVar()

search_entry = tk.Entry(
    table_header,
    textvariable=search_var,
    bg=INPUT,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    font=(FONT, 11),
    width=27,
    bd=0
)

search_entry.pack(
    side="right",
    ipady=10,
    padx=(10, 0)
)

tk.Label(
    table_header,
    text="SEARCH",
    bg=BG,
    fg=GREY,
    font=(FONT, 9, "bold")
).pack(side="right")

# TABLE STYLING

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Modern.Treeview",
    background=PANEL,
    foreground=WHITE,
    fieldbackground=PANEL,
    rowheight=40,
    font=(FONT, 10),
    borderwidth=0,
    relief="flat"
)

style.configure(
    "Modern.Treeview.Heading",
    background=CARD,
    foreground=WHITE,
    font=(FONT, 10, "bold"),
    padding=12,
    relief="flat"
)

style.map(
    "Modern.Treeview",
    background=[("selected", BLUE_DARK)],
    foreground=[("selected", WHITE)]
)

style.map(
    "Modern.Treeview.Heading",
    background=[("active", DARK_BLUE)]
) if False else None

