import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
import json
import os
from datetime import datetime

# ------------------ Setup ------------------ #
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Productive Day - To-Do List")
app.geometry("600x700")
app.resizable(False, False)

TASKS_FILE = "tasks.json"
SCORES_FILE = "scores.json"
tasks = []

# ------------------ Utils ------------------ #
def today_str():
    return datetime.today().strftime("%Y-%m-%d")

def save_score():
    completed = sum(t.completed.get() == "on" for t in tasks)
    total = len(tasks)
    percent = int((completed / total) * 100) if total > 0 else 0

    try:
        with open(SCORES_FILE, "r") as f:
            history = json.load(f)
    except:
        history = {}

    history[today_str()] = percent

    with open(SCORES_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return {}

# ------------------ Task Widget ------------------ #
class TaskWidget:
    def __init__(self, master, text, completed=False, priority="None"):
        self.text = text
        self.completed = ctk.StringVar(value="on" if completed else "off")
        self.priority = priority

        self.frame = ctk.CTkFrame(master, corner_radius=10)
        self.frame.pack(fill="x", pady=6, padx=10)

        display_text = self.get_display_text()

        self.checkbox = ctk.CTkCheckBox(
            self.frame,
            text=display_text,
            variable=self.completed,
            onvalue="on",
            offvalue="off",
            command=update_score
        )
        self.checkbox.pack(side="left", padx=10, pady=5)

        self.edit_button = ctk.CTkButton(self.frame, text="✏️", width=30, command=self.edit_task)
        self.edit_button.pack(side="right", padx=5)

        self.delete_button = ctk.CTkButton(self.frame, text="🗑️", width=30, command=self.delete)
        self.delete_button.pack(side="right", padx=5)

    def get_display_text(self):
        tag = f"[{self.priority}]" if self.priority != "None" else ""
        return f"{tag} {self.text}".strip()

    def edit_task(self):
        def save_changes():
            new_text = name_entry.get().strip()
            new_priority = priority_menu.get()
            if new_text():
                self.text = new_text
                self.priority = new_priority
                self.checkbox.configure(text=self.get_display_text())
                edit_win.destroy()
                save_tasks()
                update_score()

        edit_win = ctk.CTkToplevel(app)
        edit_win.geometry("300x200")
        edit_win.title("Edit Task")

        name_entry = ctk.CTkEntry(edit_win, placeholder_text="Rename Task")
        name_entry.insert(0, self.text)
        name_entry.pack(pady=15)

        priority_menu = ctk.CTkOptionMenu(edit_win, values=["None", "Low", "Medium", "High"])
        priority_menu.set(self.priority)
        priority_menu.pack(pady=10)

        save_btn = ctk.CTkButton(edit_win, text="Save Changes", command=save_changes)
        save_btn.pack(pady=10)

    def delete(self):
        self.frame.destroy()
        tasks.remove(self)
        save_tasks()
        update_score()

    def to_dict(self):
        return {
            "text": self.text,
            "completed": self.completed.get() == "on",
            "priority": self.priority
        }
# ------------------ Task Functions ------------------ #

def add_task():
    text = task_entry.get().strip()
    if text:
        priority = priority_menu.get()
        new_task = TaskWidget(task_frame, text, priority=priority)
        tasks.append(new_task)
        task_entry.delete(0, 'end')
        priority_menu.set("None")
        save_tasks()
        update_score()

def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)
    save_score()

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return
    with open(TASKS_FILE, "r") as f:
        task_list = json.load(f)
    for task_data in task_list:
        if "text" in task_data:
            t = TaskWidget(
                task_frame,
                task_data["text"],
                completed=task_data.get("completed", False),
                priority=task_data.get("priority", "None")
            )
            tasks.append(t)


def update_score():
    total = len(tasks)
    if total == 0:
        score_label.configure(text="Daily Score: 0/100")
        return
    done = sum(t.completed.get() == "on" for t in tasks)
    percent = int((done / total) * 100)
    score_label.configure(text=f"Daily Score: {percent}/100")
    save_score()

def toggle_theme():
    current = ctk.get_appearance_mode()
    ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")

# ------------------ UI Layout ------------------ #

# Header
title_label = ctk.CTkLabel(app, text="✨ Productive Day", font=("Arial", 26, "bold"))
title_label.pack(pady=20)

# Task entry
task_entry = ctk.CTkEntry(app, placeholder_text="Enter a new task...")
task_entry.pack(padx=20, pady=5, fill="x")

# Priority dropdown
priority_menu = ctk.CTkOptionMenu(app, values=["None", "Low", "Medium", "High"])
priority_menu.set("None")
priority_menu.pack(pady=5)

# Add button
add_button = ctk.CTkButton(app, text="➕ Add Task", command=add_task)
add_button.pack(pady=5)

# Task display frame
task_frame = ctk.CTkScrollableFrame(app, height=350, corner_radius=10)
task_frame.pack(padx=20, pady=10, fill="both", expand=True)

# Score
score_label = ctk.CTkLabel(app, text="Daily Score: 0/100", font=("Arial", 18))
score_label.pack(pady=10)

# Bottom buttons
bottom_frame = ctk.CTkFrame(app, fg_color="transparent")
bottom_frame.pack(pady=10)

theme_button = ctk.CTkButton(bottom_frame, text="🌓 Toggle Theme", command=toggle_theme)
theme_button.pack(side="left", padx=10)

history_button = ctk.CTkButton(bottom_frame, text="📅 View Score History", command=lambda: show_history())
history_button.pack(side="left", padx=10)

# Load tasks and update score
load_tasks()
update_score()
def show_history():
    scores = load_scores()

    history_win = ctk.CTkToplevel(app)
    history_win.title("📅 Daily Score History")
    history_win.geometry("400x400")

    calendar = Calendar(history_win, selectmode='day', date_pattern='yyyy-mm-dd')
    calendar.pack(pady=20)

    result_label = ctk.CTkLabel(history_win, text="Select a date to view score", font=("Arial", 14))
    result_label.pack(pady=10)

    def show_score_for_selected_date(event=None):
        selected_date = calendar.get_date()
        score = scores.get(selected_date, "No data")
        result_label.configure(text=f"{selected_date} Score: {score}/100")

    calendar.bind("<<CalendarSelected>>", show_score_for_selected_date)

    # Automatically select today's date
    calendar.selection_set(today_str())
    show_score_for_selected_date()

app.mainloop()
