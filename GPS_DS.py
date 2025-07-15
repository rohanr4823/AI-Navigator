import serial
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
import re

class GPSVisualizer:
    def __init__(self, root, port='COM5', baudrate=9600):
        self.root = root
        self.root.title("Neo-M9N GPS Visualizer")
        
        # GPS data variables
        self.current_lat = 0.0
        self.current_lon = 0.0
        self.fixed_points = []  # Stores other coordinates to display
        self.running = True
        
        # Setup GUI
        self.setup_gui()
        
        # Setup serial connection
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        
        # Start serial reading thread
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
        # Start GUI update loop
        self.update_gui()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Info display
        self.info_label = ttk.Label(main_frame, text="Waiting for GPS data...")
        self.info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.set_title("GPS Coordinates")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.grid(True)
        
        # Initial scatter plot (empty)
        self.current_point = self.ax.scatter([], [], c='red', label='Current Position')
        self.other_points = self.ax.scatter([], [], c='blue', label='Other Points')
        self.ax.legend()
        
        # Canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, pady=10)
        
        # Add point button
        ttk.Button(controls_frame, text="Add Current Point", 
                  command=self.add_current_point).grid(row=0, column=0, padx=5)
        
        # Clear points button
        ttk.Button(controls_frame, text="Clear Points", 
                  command=self.clear_points).grid(row=0, column=1, padx=5)
        
        # Quit button
        ttk.Button(controls_frame, text="Quit", 
                  command=self.quit_app).grid(row=0, column=2, padx=5)
    
    def parse_nmea(self, sentence):
        """Parse NMEA sentences to extract coordinates"""
        try:
            if sentence.startswith('$GNRMC') or sentence.startswith('$GPRMC'):
                parts = sentence.split(',')
                if parts[2] == 'A':  # Data is valid
                    lat = self.nmea_to_decimal(parts[3], parts[4])
                    lon = self.nmea_to_decimal(parts[5], parts[6])
                    return lat, lon
                
            elif sentence.startswith('$GNGGA') or sentence.startswith('$GPGGA'):
                parts = sentence.split(',')
                if parts[6] != '0':  # Fix quality is not 0
                    lat = self.nmea_to_decimal(parts[2], parts[3])
                    lon = self.nmea_to_decimal(parts[4], parts[5])
                    return lat, lon
                    
        except (ValueError, IndexError):
            pass
        
        return None, None
    
    def nmea_to_decimal(self, value, direction):
        """Convert NMEA coordinates to decimal degrees"""
        try:
            degrees = float(value[:2]) if direction in ['N', 'S'] else float(value[:3])
            minutes = float(value[2:])
            decimal = degrees + minutes / 60.0
            if direction in ['S', 'W']:
                decimal *= -1
            return decimal
        except:
            return 0.0
    
    def read_serial(self):
        """Read data from serial port and parse GPS sentences"""
        buffer = ""
        while self.running:
            try:
                data = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                if data:
                    buffer += data
                    
                    # Check for complete sentences
                    while '$' in buffer and '*' in buffer:
                        start = buffer.index('$')
                        end = buffer.index('*', start)
                        if end + 2 <= len(buffer):  # Check if checksum is present
                            sentence = buffer[start:end+3]
                            buffer = buffer[end+3:]
                            
                            # Parse the sentence
                            lat, lon = self.parse_nmea(sentence)
                            if lat is not None and lon is not None:
                                self.current_lat = lat
                                self.current_lon = lon
                        else:
                            break
            except:
                pass
    
    def add_current_point(self):
        """Add current position to the fixed points list"""
        if self.current_lat != 0.0 and self.current_lon != 0.0:
            self.fixed_points.append((self.current_lon, self.current_lat))
            self.update_plot()
    
    def clear_points(self):
        """Clear all fixed points"""
        self.fixed_points = []
        self.update_plot()
    
    def update_plot(self):
        """Update the matplotlib plot with current data"""
        self.ax.clear()
        
        # Plot fixed points if any
        if self.fixed_points:
            lons, lats = zip(*self.fixed_points)
            self.ax.scatter(lons, lats, c='blue', label='Other Points')
        
        # Plot current position
        if self.current_lat != 0.0 and self.current_lon != 0.0:
            self.ax.scatter([self.current_lon], [self.current_lat], c='red', label='Current Position')
        
        # Set plot properties
        self.ax.set_title("GPS Coordinates")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.grid(True)
        self.ax.legend()
        
        # Auto-scale the view
        self.ax.relim()
        self.ax.autoscale_view()
        
        self.canvas.draw()
    
    def update_gui(self):
        """Update the GUI with current GPS data"""
        # Update info label
        if self.current_lat != 0.0 and self.current_lon != 0.0:
            info_text = f"Current Position: {self.current_lat:.6f}°N, {self.current_lon:.6f}°E"
            info_text += f"\nFixed Points: {len(self.fixed_points)}"
        else:
            info_text = "Waiting for valid GPS fix..."
        
        self.info_label.config(text=info_text)
        
        # Update plot
        self.update_plot()
        
        # Schedule next update
        if self.running:
            self.root.after(1000, self.update_gui)
    
    def quit_app(self):
        """Clean up and quit the application"""
        self.running = False
        self.serial_port.close()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSVisualizer(root)
    root.mainloop()