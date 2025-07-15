import tkinter as tk
from tkinter import messagebox
import serial
import folium
import webbrowser
import os
from threading import Thread

# ---------- Parse GNGGA Sentence ----------
def parse_gga(sentence):
    parts = sentence.split(',')
    if len(parts) > 5 and parts[0] == "$GNGGA" and parts[2] and parts[4]:
        try:
            lat = float(parts[2])
            lon = float(parts[4])

            lat_deg = int(lat / 100)
            lat_min = lat - lat_deg * 100
            lat_dec = lat_deg + (lat_min / 60)

            lon_deg = int(lon / 100)
            lon_min = lon - lon_deg * 100
            lon_dec = lon_deg + (lon_min / 60)

            if parts[3] == 'S':
                lat_dec = -lat_dec
            if parts[5] == 'W':
                lon_dec = -lon_dec

            return lat_dec, lon_dec
        except ValueError:
            return None
    return None

# ---------- Update Folium Map ----------
def update_map():
    if initial_coord:
        map_ = folium.Map(location=initial_coord, zoom_start=16)
        folium.Marker(initial_coord, tooltip="Start", icon=folium.Icon(color="blue")).add_to(map_)
    else:
        map_ = folium.Map(location=[0, 0], zoom_start=2)

    if goal_coord:
        folium.Marker(goal_coord, tooltip="Goal", icon=folium.Icon(color="orange")).add_to(map_)
        # Draw line between start and goal
        folium.PolyLine([initial_coord, goal_coord], color="green", weight=2.5, opacity=1).add_to(map_)

    map_.save("map.html")
    webbrowser.open("file://" + os.path.realpath("map.html"))

# ---------- Serial Listening Thread ----------
def listen_serial():
    try:
        ser = serial.Serial('COM5', 9600, timeout=1)
        while True:
            line = ser.readline().decode('ascii', errors='replace').strip()
            if "$GNGGA" in line:
                coords = parse_gga(line)
                if coords:
                    lat_var.set(f"{coords[0]:.6f}")
                    lon_var.set(f"{coords[1]:.6f}")
    except serial.SerialException as e:
        messagebox.showerror("Serial Error", f"Could not open COM5.\n{e}")

# ---------- Set Initial Coord ----------
def set_initial():
    global initial_coord
    try:
        lat = float(lat_var.get())
        lon = float(lon_var.get())
        initial_coord = (lat, lon)
        update_map()
    except ValueError:
        messagebox.showerror("Invalid Input", "Invalid initial coordinates")

# ---------- Set Goal Coord ----------
def set_goal():
    global goal_coord
    try:
        lat = float(goal_lat_var.get())
        lon = float(goal_lon_var.get())
        goal_coord = (lat, lon)
        update_map()
    except ValueError:
        messagebox.showerror("Invalid Input", "Invalid goal coordinates")

# ---------- GUI Setup ----------
app = tk.Tk()
app.title("NEO-M9N GPS Tracker")
app.geometry("350x300")

initial_coord = None
goal_coord = None

lat_var = tk.StringVar()
lon_var = tk.StringVar()
goal_lat_var = tk.StringVar()
goal_lon_var = tk.StringVar()

# Current Location Section
tk.Label(app, text="Current Latitude:").pack()
tk.Entry(app, textvariable=lat_var).pack()
tk.Label(app, text="Current Longitude:").pack()
tk.Entry(app, textvariable=lon_var).pack()
tk.Button(app, text="Set Initial Location", command=set_initial).pack(pady=5)

# Goal Location Section
tk.Label(app, text="Goal Latitude:").pack()
tk.Entry(app, textvariable=goal_lat_var).pack()
tk.Label(app, text="Goal Longitude:").pack()
tk.Entry(app, textvariable=goal_lon_var).pack()
tk.Button(app, text="Set Goal Location", command=set_goal).pack(pady=5)

# Start serial thread
thread = Thread(target=listen_serial, daemon=True)
thread.start()

# Run GUI
app.mainloop()
