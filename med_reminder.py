import json
import os
from tkinter import *
from tkinter import messagebox
from apscheduler.schedulers.background import BackgroundScheduler
from plyer import notification

file_name = "data.json"

scheduler = BackgroundScheduler()
scheduler.start()

current_user = None


def data_loader():
    if not os.path.exists(file_name):
        return {}
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
        return data
    except:
        return {}


def data_saver(data):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)


def send_notification(medicine, dosage):
    notification.notify(
        title="Medicine Reminder",
        message=f"Take {medicine} ({dosage})",
        timeout=10
    )


def schedule_medicine(medicine, dosage, time_str):
    hour, minute = map(int, time_str.split(":"))
    scheduler.add_job(
        send_notification,
        "cron",
        hour=hour,
        minute=minute,
        args=[medicine, dosage]
    )


data = data_loader()


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def login_screen():
    clear_screen()

    Label(root, text="Medicine Reminder", font=("Arial", 16)).pack(pady=10)

    Button(root, text="Login", width=20, command=login).pack(pady=5)
    Button(root, text="Sign Up", width=20, command=signup).pack(pady=5)
    Button(root, text="Exit", width=20, command=root.quit).pack(pady=5)


def login():
    username = simple_input("Login", "Enter username")
    if username not in data:
        messagebox.showerror("Error", "User does not exist")
        return

    password = simple_input("Login", "Enter password")

    if data[username]["password"] != password:
        messagebox.showerror("Error", "Incorrect password")
        return

    global current_user
    current_user = username

    dashboard()


def signup():
    username = simple_input("Sign Up", "Choose username")

    if username in data:
        messagebox.showerror("Error", "Username already exists")
        return

    password = simple_input("Sign Up", "Choose password")

    data[username] = {
        "password": password,
        "medicines": []
    }

    data_saver(data)

    global current_user
    current_user = username

    dashboard()


def dashboard():
    clear_screen()

    Label(root, text=f"Welcome {current_user}", font=("Arial", 14)).pack(pady=10)

    Button(root, text="Add Medicine", width=25, command=add_medicine).pack(pady=5)
    Button(root, text="Remove Medicine", width=25, command=remove_medicine).pack(pady=5)
    Button(root, text="View Schedule", width=25, command=view_schedule).pack(pady=5)
    Button(root, text="Logout", width=25, command=login_screen).pack(pady=5)


def add_medicine():
    name = simple_input("Medicine", "Medicine name")
    dosage = simple_input("Dosage", "Dosage")
    time = simple_input("Time", "Time (HH:MM 24hr)")

    for med in data[current_user]["medicines"]:
        if med["medicine"] == name and med["dosage"] == dosage and med["time"] == time:
            messagebox.showinfo("Info", "Already entered in schedule")
            return

    data[current_user]["medicines"].append({
        "medicine": name,
        "dosage": dosage,
        "time": time
    })

    data_saver(data)

    schedule_medicine(name, dosage, time)

    messagebox.showinfo("Success", "Medicine added")


def remove_medicine():
    meds = data[current_user]["medicines"]

    if not meds:
        messagebox.showinfo("Info", "No medicines in schedule")
        return

    text = ""
    for i, med in enumerate(meds):
        text += f"{i+1}. {med['medicine']} | {med['time']}\n"

    index = simple_input("Remove Medicine", f"Enter number\n{text}")

    try:
        index = int(index) - 1
        removed = meds.pop(index)
        data_saver(data)

        messagebox.showinfo(
            "Removed",
            f"{removed['medicine']} removed from schedule"
        )
    except:
        messagebox.showerror("Error", "Invalid selection")


def view_schedule():
    meds = data[current_user]["medicines"]

    if not meds:
        messagebox.showinfo("Schedule", "No medicines in schedule")
        return

    text = ""

    for med in meds:
        text += f"{med['medicine']} | {med['dosage']} | {med['time']}\n"

    messagebox.showinfo("Your Schedule", text)


def simple_input(title, message):
    popup = Toplevel(root)

    popup.title(title)

    Label(popup, text=message).pack(pady=5)

    entry = Entry(popup)
    entry.pack(pady=5)

    result = {"value": None}

    def submit():
        result["value"] = entry.get()
        popup.destroy()

    Button(popup, text="Submit", command=submit).pack(pady=5)

    root.wait_window(popup)

    return result["value"]


root = Tk()
root.geometry("300x300")

login_screen()

root.mainloop()
