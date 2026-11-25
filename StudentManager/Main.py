import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# dark theme colours
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

MAX_COURSEWORK = 60  # 3 coursework marks out of 20 each
MAX_EXAM = 100
MAX_TOTAL = MAX_COURSEWORK + MAX_EXAM
FILE_PATH = Path(__file__).parent / "studentMarks.txt"


class Student:
    # holds one student and calculates their total, precentage and grade
    def __init__(self, code, name, marks, exam):
        self.code = code
        self.name = name
        self.marks = list(marks)  # copy list so it doesnt get messed up later
        self.exam = exam

    def coursework_total(self):
        return sum(self.marks)

    def total_score(self):
        return self.coursework_total() + self.exam

    def percentage(self):
        return (self.total_score() / MAX_TOTAL) * 100

    def grade(self):
        pct = self.percentage()
        if pct >= 70:
            return "A"
        elif pct >= 60:
            return "B"
        elif pct >= 50:
            return "C"
        elif pct >= 40:
            return "D"
        else:
            return "F"

    def to_csv_row(self):
        # save back in the same format as the text file
        return [self.code, self.name, self.marks[0], self.marks[1], self.marks[2], self.exam]

    def details_text(self):
        return (
            f"Name: {self.name}\n"
            f"Code: {self.code}\n"
            f"Coursework: {self.coursework_total()}/{MAX_COURSEWORK} "
            f"({self.marks[0]}, {self.marks[1]}, {self.marks[2]})\n"
            f"Exam: {self.exam}/{MAX_EXAM}\n"
            f"Total: {self.total_score()}/{MAX_TOTAL}\n"
            f"Percentage: {self.percentage():.1f}%\n"
            f"Grade: {self.grade()}"
        )


def check_student_data(code, name, marks, exam):
    # student code has to be 4 digits between 1000 and 9999
    if not (code.isdigit() and len(code) == 4 and 1000 <= int(code) <= 9999):
        raise ValueError("Student code must be a number between 1000 and 9999.")
    if name == "":
        raise ValueError("Please enter a student name.")
    for m in marks:
        if m < 0 or m > 20:
            raise ValueError("Each coursework mark must be between 0 and 20.")
    if exam < 0 or exam > 100:
        raise ValueError("Exam mark must be between 0 and 100.")


# rounded card using canvas because normal tkinter frames dont have rounded corners
class RoundedCard(tk.Canvas):
    def __init__(self, parent, color=PANEL, radius=18, height=115):
        super().__init__(parent, bg=BG, highlightthickness=0, bd=0, height=height)
        self.color = color
        self.radius = radius
        self.bind("<Configure>", self.redraw)

    def redraw(self, event=None):
        self.delete("bg")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return

        # stop radius from breaking on small sizes
        r = min(self.radius, w / 2, h / 2)
        pts = [
            r, 0, w - r, 0, w, 0, w, r,
            w, h - r, w, h, w - r, h, r, h,
            0, h, 0, h - r, 0, r, 0, 0,
        ]
        self.create_polygon(pts, smooth=True, splinesteps=16, fill=self.color, outline="", tags="bg")
        self.tag_lower("bg")


class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager | Dashboard")
        self.root.geometry("1250x780")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)

        # starts fullscreen, F11 toggles it and Esc goes back to window
        self.fullscreen = True
        self.root.attributes("-fullscreen", self.fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.students = []
        self.stat_labels = {}

        self.make_ui()
        self.load_from_file()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)

    def set_status(self, msg):
        self.status_text.set(msg)

    def make_ui(self):
        # sidebar menu on the left
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)  # keeps sidebar width fixed

        tk.Label(sidebar, text="STUDENT", font=(FONT, 22, "bold"), fg=WHITE, bg=SIDEBAR).pack(
            anchor="w", padx=25, pady=(26, 0)
        )
        tk.Label(sidebar, text="MANAGER.", font=(FONT, 22, "bold"), fg=BLUE, bg=SIDEBAR).pack(
            anchor="w", padx=25
        )
        tk.Label(sidebar, text="ACADEMIC MANAGEMENT", font=(FONT, 9, "bold"), fg=GREY, bg=SIDEBAR).pack(
            anchor="w", padx=25, pady=(5, 20)
        )

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(sidebar, text="MAIN MENU", font=(FONT, 9, "bold"), bg=SIDEBAR, fg=GREY).pack(
            anchor="w", padx=25, pady=(0, 8)
        )

        menu_buttons = [
            ("☰  All Records", self.show_all, WHITE, CARD, BLUE_DARK),
            ("◉  View / Find Student", self.view_one_student, WHITE, CARD, BLUE_DARK),
            ("▲  Highest Score", self.show_highest, WHITE, CARD, BLUE_DARK),
            ("▼  Lowest Score", self.show_lowest, WHITE, CARD, BLUE_DARK),
            ("⇅  Sort Records", self.sort_students, WHITE, CARD, BLUE_DARK),
            ("+  Add Student", self.add_student_window, WHITE, BLUE_DARK, BLUE),
            ("✎  Edit Selected", self.edit_selected_student, WHITE, CARD, BLUE_DARK),
            ("✕  Delete Selected", self.delete_selected_student, RED, CARD, BLUE_DARK),
            ("↻  Reload File", self.load_from_file, WHITE, CARD, BLUE_DARK),
            ("💾  Save to File", self.save_to_file, WHITE, CARD, BLUE_DARK),
        ]

        for label, action, fg, bg, active_bg in menu_buttons:
            tk.Button(
                sidebar,
                text=label,
                command=action,
                bg=bg,
                fg=fg,
                activebackground=active_bg,
                activeforeground=WHITE,
                font=(FONT, 10, "bold"),
                relief="flat",
                anchor="w",
                padx=14,
                cursor="hand2",
                bd=0,
            ).pack(fill="x", padx=18, pady=4, ipady=7)

        # main area on the right
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", padx=30, pady=(22, 10))
        tk.Label(header, text="Dashboard", font=(FONT, 27, "bold"), bg=BG, fg=WHITE).pack(anchor="w")
        tk.Label(
            header,
            text="Manage student records and academic performance  •  F11 Fullscreen  •  ESC Windowed",
            font=(FONT, 10),
            bg=BG,
            fg=GREY,
        ).pack(anchor="w", pady=(4, 0))

        # top stat cards
        cards_row = tk.Frame(main, bg=BG)
        cards_row.pack(fill="x", padx=25, pady=(10, 16))
        cards_row.columnconfigure((0, 1, 2), weight=1)

        self.make_stat_card(cards_row, 0, "Total Students", BLUE)
        self.make_stat_card(cards_row, 1, "Class Average", GREEN)
        self.make_stat_card(cards_row, 2, "Highest Score", YELLOW)

        # heading and live search box
        top_bar = tk.Frame(main, bg=BG)
        top_bar.pack(fill="x", padx=30, pady=(0, 10))

        self.heading_var = tk.StringVar(value="Student Records")
        tk.Label(top_bar, textvariable=self.heading_var, font=(FONT, 17, "bold"), bg=BG, fg=WHITE).pack(
            side="left"
        )

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)  # updates search as u type

        tk.Entry(
            top_bar,
            textvariable=self.search_var,
            bg=INPUT,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=(FONT, 11),
            width=25,
            bd=0,
        ).pack(side="right", ipady=8, padx=(10, 0))

        tk.Label(top_bar, text="SEARCH", bg=BG, fg=GREY, font=(FONT, 9, "bold")).pack(side="right")

        # treeview table
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "StudentTable.Treeview",
            background=PANEL,
            foreground=WHITE,
            fieldbackground=PANEL,
            rowheight=38,
            font=(FONT, 10),
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "StudentTable.Treeview.Heading",
            background=CARD,
            foreground=WHITE,
            font=(FONT, 10, "bold"),
            padding=11,
            relief="flat",
        )
        style.map("StudentTable.Treeview", background=[("selected", BLUE_DARK)], foreground=[("selected", WHITE)])
        style.map("StudentTable.Treeview.Heading", background=[("active", BLUE_DARK)])

        table_box = tk.Frame(main, bg=PANEL, padx=12, pady=12)
        table_box.pack(fill="both", expand=True, padx=30, pady=(0, 12))

        cols = ("Code", "Name", "Coursework", "Exam", "Total", "Percentage", "Grade")
        col_widths = [90, 190, 115, 90, 90, 115, 75]

        self.table = ttk.Treeview(
            table_box, columns=cols, show="headings", style="StudentTable.Treeview", selectmode="browse"
        )
        for col, w in zip(cols, col_widths):
            self.table.heading(col, text=col)
            self.table.column(col, width=w, minwidth=65, anchor="w" if col == "Name" else "center", stretch=True)

        scroll = ttk.Scrollbar(table_box, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)

        # alternate row colours so lines are easier to follow
        self.table.tag_configure("even", background=PANEL)
        self.table.tag_configure("odd", background="#26364C")

        # status bar at bottom
        self.status_text = tk.StringVar(value="Ready")
        status_bar = tk.Frame(main, bg=SIDEBAR, height=34)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        tk.Label(status_bar, textvariable=self.status_text, bg=SIDEBAR, fg=GREY, font=(FONT, 9)).pack(
            side="left", padx=25
        )

    def make_stat_card(self, parent, col, title, colour):
        card = RoundedCard(parent, color=PANEL, height=115)
        card.grid(row=0, column=col, sticky="ew", padx=6)
        card.create_text(22, 26, text=title, fill=GREY, font=(FONT, 11), anchor="w")
        val_id = card.create_text(22, 70, text="0", fill=colour, font=(FONT, 26, "bold"), anchor="w")
        self.stat_labels[title] = (card, val_id)

    def update_cards(self):
        total_students = len(self.students)
        if total_students > 0:
            avg_pct = sum(s.percentage() for s in self.students) / total_students
            best_score = max(s.total_score() for s in self.students)
        else:
            avg_pct = 0.0
            best_score = 0

        card_data = {
            "Total Students": str(total_students),
            "Class Average": f"{avg_pct:.1f}%",
            "Highest Score": f"{best_score}/{MAX_TOTAL}",
        }
        for title, text in card_data.items():
            card, item_id = self.stat_labels[title]
            card.itemconfig(item_id, text=text)

    def fill_table(self, rows=None, title="Student Records"):
        self.heading_var.set(title)
        # clear table before adding rows
        for row_id in self.table.get_children():
            self.table.delete(row_id)

        data = self.students if rows is None else rows
        for i, s in enumerate(data):
            tag = "even" if i % 2 == 0 else "odd"
            self.table.insert(
                "",
                "end",
                iid=s.code,
                values=(
                    s.code,
                    s.name,
                    f"{s.coursework_total()}/{MAX_COURSEWORK}",
                    f"{s.exam}/{MAX_EXAM}",
                    f"{s.total_score()}/{MAX_TOTAL}",
                    f"{s.percentage():.1f}%",
                    s.grade(),
                ),
                tags=(tag,),
            )

        self.update_cards()

    def load_from_file(self):
        loaded = []
        try:
            with open(FILE_PATH, "r", encoding="utf-8", newline="") as f:
                lines = list(csv.reader(f))

            if len(lines) == 0:
                raise ValueError("The file is empty.")

            # first line gives how many students are in the file
            expected_count = int(lines[0][0].strip())

            for row in lines[1:]:
                if not row or all(cell.strip() == "" for cell in row):
                    continue  # ignore empty lines
                if len(row) != 6:
                    raise ValueError("Each student line needs 6 values separated by commas.")

                code = row[0].strip()
                name = row[1].strip()
                marks = [int(row[2].strip()), int(row[3].strip()), int(row[4].strip())]
                exam = int(row[5].strip())

                check_student_data(code, name, marks, exam)

                for existing in loaded:
                    if existing.code == code:
                        raise ValueError(f"Duplicate student code: {code}")

                loaded.append(Student(code, name, marks, exam))

            self.students = loaded
            if len(self.students) != expected_count:
                messagebox.showwarning(
                    "Count Mismatch",
                    f"First line says {expected_count} students, but {len(self.students)} were loaded.",
                )
            self.set_status("Loaded studentMarks.txt")

        except FileNotFoundError:
            self.students = []
            self.set_status("studentMarks.txt not found yet.")
            messagebox.showwarning(
                "File Not Found",
                f"Couldn't find:\n{FILE_PATH}\n\nAdd a student to create the file.",
            )
        except (ValueError, IndexError, csv.Error, OSError) as err:
            messagebox.showerror("Error Loading File", str(err))
            self.set_status("Failed to load student marks.")

        self.fill_table()

    def save_to_file(self, show_popup=True):
        try:
            FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(FILE_PATH, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow([len(self.students)])
                for s in self.students:
                    writer.writerow(s.to_csv_row())

            self.set_status("Saved changes to studentMarks.txt")
            if show_popup:
                messagebox.showinfo("Saved", "Student records saved to file.")
            return True
        except OSError as err:
            messagebox.showerror("Save Error", str(err))
            return False

    def get_selected(self, warn=True):
        chosen = self.table.selection()
        if not chosen:
            if warn:
                messagebox.showwarning("No Selection", "Click a student in the table first.")
            return None
        for s in self.students:
            if s.code == chosen[0]:
                return s
        return None

    def show_all(self):
        self.search_var.set("")
        self.fill_table(self.students, "All Student Records")
        if self.students:
            avg = sum(s.percentage() for s in self.students) / len(self.students)
            self.set_status(f"{len(self.students)} students  •  Class average: {avg:.1f}%")
        else:
            self.set_status("0 students in class.")

    def on_search(self, *args):
        term = self.search_var.get().strip().lower()
        if term == "":
            self.fill_table(self.students, "Student Records")
            return
        found = [s for s in self.students if term in s.code.lower() or term in s.name.lower()]
        self.fill_table(found, f"Search Results ({len(found)})")
        self.set_status(f"Found {len(found)} matching student(s).")

    def view_one_student(self):
        # check selected row first, otherwise ask for code or name
        student = self.get_selected(warn=False)
        if student is None:
            query = simpledialog.askstring("Find Student", "Enter student code or name:", parent=self.root)
            if not query:
                return
            q = query.strip().lower()
            for s in self.students:
                if s.code.lower() == q or q in s.name.lower():
                    student = s
                    break
            if student is None:
                messagebox.showinfo("Not Found", f"No student found for '{query.strip()}'.")
                return

        self.fill_table([student], f"Student Record — {student.name} ({student.code})")
        messagebox.showinfo("Student Details", student.details_text())

    def show_highest(self):
        if not self.students:
            messagebox.showinfo("No Data", "No students to check.")
            return
        top = max(self.students, key=lambda s: s.total_score())
        self.fill_table([top], f"Highest Score — {top.name}")
        self.set_status(f"Highest score: {top.name} ({top.total_score()}/{MAX_TOTAL})")
        messagebox.showinfo("Highest Score", top.details_text())

    def show_lowest(self):
        if not self.students:
            messagebox.showinfo("No Data", "No students to check.")
            return
        low = min(self.students, key=lambda s: s.total_score())
        self.fill_table([low], f"Lowest Score — {low.name}")
        self.set_status(f"Lowest score: {low.name} ({low.total_score()}/{MAX_TOTAL})")
        messagebox.showinfo("Lowest Score", low.details_text())

    def sort_students(self):
        if not self.students:
            messagebox.showinfo("No Data", "No students to sort.")
            return

        is_desc = messagebox.askyesno(
            "Sort Records",
            "Sort in DESCENDING order (highest score first)?\n\nChoose 'No' for ASCENDING (lowest first).",
        )
        sorted_list = sorted(self.students, key=lambda s: s.total_score(), reverse=is_desc)
        order_name = "Descending" if is_desc else "Ascending"
        self.fill_table(sorted_list, f"Sorted Records ({order_name})")
        self.set_status(f"Sorted in {order_name.lower()} order.")

    def edit_selected_student(self):
        student = self.get_selected()
        if student:
            self.student_popup(existing=student)

    def delete_selected_student(self):
        student = self.get_selected()
        if not student:
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete {student.name} ({student.code})?")
        if not confirm:
            return

        self.students = [s for s in self.students if s.code != student.code]
        self.save_to_file(show_popup=False)
        self.on_search()
        self.set_status(f"Deleted {student.name}.")

    def add_student_window(self):
        self.student_popup(existing=None)

    def student_popup(self, existing=None):
        win = tk.Toplevel(self.root)
        win.title("Edit Student" if existing else "Add Student")
        win.geometry("480x650")
        win.minsize(450, 610)
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()  # locks main window until popup closes

        # centre popup over main window
        win.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - win.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(0, x)}+{max(0, y)}")

        tk.Label(
            win,
            text="Edit Student" if existing else "Add Student",
            bg=BG,
            fg=WHITE,
            font=(FONT, 23, "bold"),
        ).pack(anchor="w", padx=35, pady=(25, 5))
        tk.Label(win, text="Fill in the student details below.", bg=BG, fg=GREY, font=(FONT, 10)).pack(
            anchor="w", padx=35, pady=(0, 18)
        )

        box = tk.Frame(win, bg=PANEL, padx=25, pady=18)
        box.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        labels_and_vals = [
            ("Student Code (1000-9999)", existing.code if existing else ""),
            ("Student Name", existing.name if existing else ""),
            ("Coursework 1 (0-20)", existing.marks[0] if existing else ""),
            ("Coursework 2 (0-20)", existing.marks[1] if existing else ""),
            ("Coursework 3 (0-20)", existing.marks[2] if existing else ""),
            ("Exam Mark (0-100)", existing.exam if existing else ""),
        ]

        inputs = []
        for lbl, val in labels_and_vals:
            tk.Label(box, text=lbl, bg=PANEL, fg=GREY, font=(FONT, 10, "bold")).pack(anchor="w", pady=(6, 4))
            ent = tk.Entry(
                box,
                bg=INPUT,
                fg=WHITE,
                insertbackground=WHITE,
                disabledbackground=CARD,
                disabledforeground=GREY,
                relief="flat",
                font=(FONT, 11),
                bd=0,
            )
            ent.pack(fill="x", ipady=8)
            ent.insert(0, str(val))
            inputs.append(ent)

        if existing:
            inputs[0].config(state="disabled")  # cant change student code when editing

        def on_save():
            code = existing.code if existing else inputs[0].get().strip()
            name = inputs[1].get().strip()
            try:
                marks = [int(inputs[2].get()), int(inputs[3].get()), int(inputs[4].get())]
                exam = int(inputs[5].get())
                check_student_data(code, name, marks, exam)

                if not existing:
                    for s in self.students:
                        if s.code == code:
                            raise ValueError("A student with this code already exists.")

                new_student = Student(code, name, marks, exam)
                if existing:
                    idx = self.students.index(existing)
                    self.students[idx] = new_student
                else:
                    self.students.append(new_student)

                ok = self.save_to_file(show_popup=False)
                win.destroy()
                self.on_search()
                if ok:
                    self.set_status(f"Saved student {code}.")
                else:
                    self.set_status(f"Updated {code} in app, but saving to file failed.")

            except ValueError as err:
                messagebox.showerror("Invalid Input", str(err), parent=win)

        tk.Button(
            box,
            text="SAVE STUDENT",
            command=on_save,
            bg=BLUE_DARK,
            fg=WHITE,
            activebackground=BLUE,
            activeforeground=BG,
            font=(FONT, 11, "bold"),
            relief="flat",
            cursor="hand2",
            bd=0,
        ).pack(fill="x", ipady=11, pady=(20, 0))

        inputs[1 if existing else 0].focus_set()
        win.bind("<Return>", lambda event: on_save())


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()