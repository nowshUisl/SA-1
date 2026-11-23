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

# The student marks file is stored in the resources folder.
# as this Python file.

FILE_PATH = Path(__file__).parent / "resources" / "studentMarks.txt"

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

            if not code.isascii() or not code.isdigit() or len(code) != 4 or not 1000 <= int(code) <= 9999:
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

# STUDENT TABLE

table_container = tk.Frame(
    main,
    bg=PANEL,
    padx=12,
    pady=12
)

table_container.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(0, 15)
)

columns = (
    "Code",
    "Name",
    "Coursework",
    "Exam",
    "Total",
    "Percentage",
    "Grade"
)

tree = ttk.Treeview(
    table_container,
    columns=columns,
    show="headings",
    style="Modern.Treeview",
    selectmode="browse"
)

widths = [90, 190, 115, 90, 90, 115, 75]

for column, width in zip(columns, widths):
    tree.heading(column, text=column)
    tree.column(
        column,
        width=width,
        minwidth=65,
        anchor="center",
        stretch=True
    )

tree.column("Name", anchor="w")

scrollbar = ttk.Scrollbar(
    table_container,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

# Alternate row colours.
tree.tag_configure("even", background=PANEL)
tree.tag_configure("odd", background="#26364C")

# REFRESH AND FILTER TABLE

def refresh_table(data=None):

    for item in tree.get_children():
        tree.delete(item)

    display_data = students if data is None else data

    for index, student in enumerate(display_data):

        tag = "even" if index % 2 == 0 else "odd"

        tree.insert(
            "",
            "end",
            iid=student["code"],
            values=(
                student["code"],
                student["name"],
                f"{get_coursework(student)}/60",
                f"{student['exam']}/100",
                f"{get_total(student)}/160",
                f"{get_percentage(student):.1f}%",
                get_grade(student)
            ),
            tags=(tag,)
        )

    update_stats()


def apply_search(*args):

    query = search_var.get().strip().lower()

    results = [
        s for s in students
        if query in s["code"].lower()
        or query in s["name"].lower()
    ]

    refresh_table(results)

    if query:
        set_status(f"Found {len(results)} matching students.")


search_var.trace_add("write", apply_search)


def display_all():

    search_var.set("")
    refresh_table()
    set_status("Displaying all student records.")

# SELECTED STUDENT

def get_selected_student():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Student",
            "Please select a student from the table first."
        )
        return None

    code = selected[0]

    for student in students:
        if student["code"] == code:
            return student

    return None

# ADD / UPDATE STUDENT FORM
# Display the selected student's results.
# View individual student record
def view_student():
    student = get_selected_student()

    if student:
        messagebox.showinfo(
            "Student Record",
            f"Name: {student['name']}\n"
            f"Code: {student['code']}\n"
            f"Coursework: {get_coursework(student)}/60\n"
            f"Exam: {student['exam']}/100\n"
            f"Total: {get_total(student)}/160\n"
            f"Percentage: {get_percentage(student):.1f}%\n"
            f"Grade: {get_grade(student)}"
        )

def student_form(existing=None):

    form = tk.Toplevel(root)

    form.title(
        "Update Student" if existing else "Add Student"
    )

    form.geometry("480x650")
    form.minsize(450, 610)
    form.configure(bg=BG)
    form.transient(root)
    form.grab_set()

    # Center the form over the main window.
    form.update_idletasks()

    x = root.winfo_rootx() + (
        root.winfo_width() - form.winfo_width()
    ) // 2

    y = root.winfo_rooty() + (
        root.winfo_height() - form.winfo_height()
    ) // 2

    form.geometry(f"+{max(0, x)}+{max(0, y)}")

    title = "Edit Student" if existing else "Add New Student"

    tk.Label(
        form,
        text=title,
        bg=BG,
        fg=WHITE,
        font=(FONT, 23, "bold")
    ).pack(anchor="w", padx=35, pady=(25, 5))

    tk.Label(
        form,
        text="Enter the student information below.",
        bg=BG,
        fg=GREY,
        font=(FONT, 10)
    ).pack(anchor="w", padx=35, pady=(0, 18))

    panel = tk.Frame(
        form,
        bg=PANEL,
        padx=25,
        pady=18
    )

    panel.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=(0, 25)
    )

    labels = [
        "Student Code",
        "Student Name",
        "Coursework Mark 1 (0-20)",
        "Coursework Mark 2 (0-20)",
        "Coursework Mark 3 (0-20)",
        "Exam Mark (0-100)"
    ]

    values = [
        existing["code"] if existing else "",
        existing["name"] if existing else "",
        existing["marks"][0] if existing else "",
        existing["marks"][1] if existing else "",
        existing["marks"][2] if existing else "",
        existing["exam"] if existing else ""
    ]

    entries = []

    for label_text, value in zip(labels, values):

        tk.Label(
            panel,
            text=label_text,
            bg=PANEL,
            fg=GREY,
            font=(FONT, 10, "bold")
        ).pack(anchor="w", pady=(6, 4))

        entry = tk.Entry(
            panel,
            bg=INPUT,
            fg=WHITE,
            insertbackground=WHITE,
            disabledbackground=CARD,
            disabledforeground=GREY,
            relief="flat",
            font=(FONT, 11),
            bd=0
        )

        entry.pack(fill="x", ipady=8)
        entry.insert(0, str(value))
        entries.append(entry)

    if existing:
        entries[0].config(state="disabled")

    # Validate the form and save the record.
    def save_record():

        code = (
            existing["code"]
            if existing else entries[0].get().strip()
        )

        name = entries[1].get().strip()

        try:
            marks = [
                int(entries[2].get()),
                int(entries[3].get()),
                int(entries[4].get())
            ]

            exam = int(entries[5].get())

            if not code.isascii() or not code.isdigit() or len(code) != 4 or not 1000 <= int(code) <= 9999:
             raise ValueError(
            "Student code must be between 1000 and 9999.") 

            if not name:
                raise ValueError("Please enter a student name.")

            if any(m < 0 or m > 20 for m in marks):
                raise ValueError(
                    "Coursework marks must be between 0 and 20."
                )

            if not 0 <= exam <= 100:
                raise ValueError(
                    "Exam mark must be between 0 and 100."
                )

            if not existing and any(
                s["code"] == code for s in students
            ):
                raise ValueError(
                    "This student code already exists."
                )

            record = {
                "code": code,
                "name": name,
                "marks": marks,
                "exam": exam
            }

            if existing:
                index = students.index(existing)
                students[index] = record
            else:
                students.append(record)

            if save_students(show_message=False):
                form.destroy()
                apply_search()
                set_status(
                    f"Student {code} saved successfully."
                )
            else:
                # The record remains in memory even if
                # writing to disk fails.
                form.destroy()
                apply_search()

        except ValueError as error:
            messagebox.showerror(
                "Invalid Details",
                str(error),
                parent=form
            )

    tk.Button(
        panel,
        text="SAVE STUDENT",
        command=save_record,
        bg=BLUE_DARK,
        fg=WHITE,
        activebackground=BLUE,
        activeforeground=BG,
        font=(FONT, 11, "bold"),
        relief="flat",
        cursor="hand2",
        bd=0
    ).pack(fill="x", ipady=11, pady=(20, 0))

    entries[1 if existing else 0].focus_set()

    form.bind("<Return>", lambda event: save_record())
