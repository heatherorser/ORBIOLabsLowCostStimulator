import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from spidriver import SPIDriver
import struct
import time

# Initialize SPI driver
s = SPIDriver("COM6")
print(s.mode)

# Define a global variable a
a = 0

# Define command codes and span code
WRITE_SPAN_DAC = 0x60
SPAN_CODE = 0x03

def set_span():
    write(0x8F0003) # write 2x to initiate voltage range. 3 for +/- 10 V, 4 for +/- 2.5 V, and 2 for +/- 5 V
    write(0x8F0003)

def plot_wave():
    global a
    amplitude1_str = amplitude1_entry.get()
    amplitude2_str = amplitude2_entry.get()
    amplitude3_str = amplitude3_entry.get()
    amplitude4_str = amplitude4_entry.get()
    t1_str = t1_entry.get()
    t2_str = t2_entry.get()
    t3_str = t3_entry.get()
    t4_str = t4_entry.get() or "1"
    t5_str = t5_entry.get() or "1"
    t6_str = t6_entry.get() or "1"
    t7_str = t7_entry.get() or "1"

    # Check if mandatory fields are filled
    if not all([amplitude1_str, amplitude2_str, t1_str, t2_str, t3_str]):
        messagebox.showerror("Error", "Please fill in all required fields for y1, y2, t1, t2, and t3.")
        return

    if (piecewise_y3_var.get() != "zero" and not all([t4_str, t5_str])) or (piecewise_y4_var.get() != "zero" and not all([t6_str, t7_str])):
        messagebox.showerror("Error", "Please fill in all required fields for the selected waveforms.")
        return

    # Convert values to floats
    try:
        amplitude1 = float(amplitude1_str)
        amplitude2 = float(amplitude2_str)
        amplitude3 = float(amplitude3_str) if amplitude3_str else 0
        amplitude4 = float(amplitude4_str) if amplitude4_str else 0
        t1 = float(t1_str)
        t2 = float(t2_str)
        t3 = float(t3_str)
        t4 = float(t4_str) if t4_str else 1
        t5 = float(t5_str) if t5_str else 1
        t6 = float(t6_str) if t6_str else 1
        t7 = float(t7_str) if t7_str else 1
    except ValueError:
        # Notify the user if conversion fails
        messagebox.showerror("Error", "Invalid input. Please enter valid numerical values.")
        return

    # Check if amplitude is within the allowed range
    max_amplitude = 10  # Set the max amplitude to ±10V
    if any(amp > max_amplitude or amp < -max_amplitude for amp in [amplitude1, amplitude2, amplitude3, amplitude4]):
        messagebox.showerror(f"Error", f"Amplitude must be between -{max_amplitude} and {max_amplitude}.")
        return

    # Validate time values
    if not (0 < t1 <= t2 < t3 <= t4 <= t5 <= t6 <= t7 <= 1):
        messagebox.showerror("Error", "Time values must satisfy 0 < t1 <= t2 < t3 <= t4 <= t5 <= t6 <= t7 <= 1.")
        return

    # Generate x values for one full cycle
    num_points = 500
    x_values = np.linspace(0, 2 * np.pi, num_points)
    x_axis_values = np.linspace(0, 1, num_points)

    # Generate y values based on piecewise wave type
    piecewise_y1 = piecewise_y1_var.get()
    piecewise_y2 = piecewise_y2_var.get()
    piecewise_y3 = piecewise_y3_var.get() if amplitude3_str and piecewise_y3_var.get() != "zero" else 'zero'
    piecewise_y4 = piecewise_y4_var.get() if amplitude4_str and piecewise_y4_var.get() != "zero" else 'zero'

    def generate_wave(wave_type, x_values, amplitude):
        if wave_type == "sin":
            return np.sin(x_values) * amplitude
        elif wave_type == "triangle":
            return (2 / np.pi) * np.arcsin(np.sin(x_values)) * amplitude
        elif wave_type == "square":
            return np.sign(np.sin(x_values)) * amplitude
        elif wave_type == "sawtooth":
            return (2 / np.pi) * np.arctan(np.tan(x_values / 2)) * amplitude
        elif wave_type == "inverse_sawtooth":
            return amplitude - (2 / np.pi) * np.arctan(np.tan(x_values / 2)) * amplitude
        elif wave_type == "zero":
            return np.zeros_like(x_values)

    # Determine the indices for the piecewise sections
    t1_idx = int(t1 * num_points)
    t2_idx = int(t2 * num_points)
    t3_idx = int(t3 * num_points)
    t4_idx = int(t4 * num_points)
    t5_idx = int(t5 * num_points)
    t6_idx = int(t6 * num_points)
    t7_idx = int(t7 * num_points)

    # Generate the wave segments
    y_values = np.zeros(num_points)
    y_values[:t1_idx] = generate_wave(piecewise_y1, np.linspace(0, np.pi, t1_idx), amplitude1)
    y_values[t2_idx:t3_idx] = generate_wave(piecewise_y2, np.linspace(0, np.pi, t3_idx - t2_idx), amplitude2)
    y_values[t4_idx:t5_idx] = generate_wave(piecewise_y3, np.linspace(0, np.pi, t5_idx - t4_idx), amplitude3)
    y_values[t6_idx:t7_idx] = generate_wave(piecewise_y4, np.linspace(0, np.pi, t7_idx - t6_idx), amplitude4)

    # Clear previous plot if exists
    ax.clear()

    # Plot the graph
    ax.plot(x_axis_values, y_values)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Voltage', fontsize=12)
    ax.set_title('Waveform', fontsize=14)
    ax.grid(True)

    # Update the plot
    canvas.draw()

    # Update the table
    for row in tree.get_children():
        tree.delete(row)

    for y in y_values:
        ## This is where values are converted to range of interest. y-value needs to account for offset and is set using output measurements.
        ## The value of the divisor has valid values for the three voltage ranges of 20, 10, and 5 respectively
        output = int(((y - 8.751) * ((2 ** 16)-10) / 20)-4095) 
        output_hex = f"{output & 0xFFFF:04X}"  # Ensure 4 hex digits
        code = "009F" + output_hex # 9F address writes to both DACs. Output voltage on B is inverse of A.
        tree.insert("", "end", values=(y, output_hex, code))

def write(code):
    # Extract the three bytes to send
    byte1 = (code >> 16) & 0xFF
    byte2 = (code >> 8) & 0xFF
    byte3 = code & 0xFF
    s.sel()
    s.write(struct.pack("BBB", byte1, byte2, byte3))
    s.unsel()

def run_wave():
    global a
    a = 1
    print(f"Run button clicked, a = {a}")

    # Set the span before starting the waveform
    set_span()

    # Extract data from the table and send to DAC
    while a == 1:
        for row in tree.get_children():
            _, _, code_str = tree.item(row, 'values')
            code = int(code_str, 16)
            write(code)
            #print(f"Writing to DAC")
            #popup.update()
            #time.sleep(0.001)  # Adjust the sleep time as needed

def stop_wave():
    global a
    a = 0
    print(f"Stop button clicked, a = {a}")

popup = tk.Tk()
popup.title("Wave Information")
popup.geometry("860x900")  # Adjust the size of the popup window

# Add note at the top
additional_note = tk.Label(popup, text="Fill in for at least 2 samples. Each sample draws a half wave and selecting zero for y2 and y3 will be considered as a blank.", font=("Arial", 12), fg="red")
additional_note.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

# Create a matplotlib figure and canvas
fig, ax = plt.subplots(figsize=(7, 4))  # Adjust figsize as needed
canvas = FigureCanvasTkAgg(fig, master=popup)
canvas_widget = canvas.get_tk_widget()

# Create user information section
piecewise_y1_label = ttk.Label(popup, text="y1:", font=("Arial", 12))
piecewise_y1_options = ["sin", "triangle", "square", "sawtooth", "inverse_sawtooth", "zero"]
piecewise_y1_var = tk.StringVar()
piecewise_y1_dropdown = ttk.Combobox(popup, textvariable=piecewise_y1_var, values=piecewise_y1_options, state="readonly", font=("Arial", 12), width=16)
amplitude1_label = ttk.Label(popup, text="Amplitude 1:", font=("Arial", 12)) #(max=6,min=-6) initially
amplitude1_entry = ttk.Entry(popup, font=("Arial", 12))
piecewise_t1_label = ttk.Label(popup, text="0 < t1 <", font=("Arial", 12))
t1_entry = ttk.Entry(popup, font=("Arial", 12), width=5)
piecewise_t2_label = ttk.Label(popup, text="", font=("Arial", 12))
t2_entry = ttk.Entry(popup, font=("Arial", 12), width=5)

piecewise_y2_label = ttk.Label(popup, text="y2:", font=("Arial", 12))
piecewise_y2_options = ["sin", "triangle", "square", "sawtooth", "inverse_sawtooth", "zero"]
piecewise_y2_var = tk.StringVar()
piecewise_y2_dropdown = ttk.Combobox(popup, textvariable=piecewise_y2_var, values=piecewise_y2_options, state="readonly", font=("Arial", 12), width=16)
amplitude2_label = ttk.Label(popup, text="Amplitude 2:", font=("Arial", 12)) # (max=6,min=-6) initially
amplitude2_entry = ttk.Entry(popup, font=("Arial", 12))
piecewise_t3_label = ttk.Label(popup, text="< t <", font=("Arial", 12))
t3_entry = ttk.Entry(popup, font=("Arial", 12), width=5)
piecewise_t4_label = ttk.Label(popup, text="", font=("Arial", 12))
t4_entry = ttk.Entry(popup, font=("Arial", 12), width=5)

piecewise_y3_label = ttk.Label(popup, text="y3:", font=("Arial", 12))
piecewise_y3_options = ["sin", "triangle", "square", "sawtooth", "inverse_sawtooth", "zero"]
piecewise_y3_var = tk.StringVar()
piecewise_y3_dropdown = ttk.Combobox(popup, textvariable=piecewise_y3_var, values=piecewise_y3_options, state="readonly", font=("Arial", 12), width=16)
amplitude3_label = ttk.Label(popup, text="Amplitude 3:", font=("Arial", 12)) # (max=6,min=-6) initially
amplitude3_entry = ttk.Entry(popup, font=("Arial", 12))
piecewise_t5_label = ttk.Label(popup, text="< t <", font=("Arial", 12))
t5_entry = ttk.Entry(popup, font=("Arial", 12), width=5)
piecewise_t6_label = ttk.Label(popup, text="", font=("Arial", 12))
t6_entry = ttk.Entry(popup, font=("Arial", 12), width=5)

piecewise_y4_label = ttk.Label(popup, text="y4:", font=("Arial", 12))
piecewise_y4_options = ["sin", "triangle", "square", "sawtooth", "inverse_sawtooth", "zero"]
piecewise_y4_var = tk.StringVar()
piecewise_y4_dropdown = ttk.Combobox(popup, textvariable=piecewise_y4_var, values=piecewise_y4_options, state="readonly", font=("Arial", 12), width=16)
amplitude4_label = ttk.Label(popup, text="Amplitude 4:", font=("Arial", 12)) # (max=6,min=-6) initially
amplitude4_entry = ttk.Entry(popup, font=("Arial", 12))
piecewise_t7_label = ttk.Label(popup, text="< t <", font=("Arial", 12))
t7_entry = ttk.Entry(popup, font=("Arial", 12), width=5)

note_label = ttk.Label(popup, text="Note: t is a percentage of a period that runs from 0-1", font=("Arial", 10))

# Create a ttk Style
style = ttk.Style()
style.configure('TButton', font=('Arial', 12))

# Arrange the controls in the grid layout
piecewise_y1_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
piecewise_y1_dropdown.grid(row=1, column=1, padx=10, pady=5)
amplitude1_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
amplitude1_entry.grid(row=2, column=1, padx=10, pady=5)
piecewise_t1_label.grid(row=1, column=2, padx=10, pady=5, sticky="e")
t1_entry.grid(row=1, column=3, padx=10, pady=5)
piecewise_t2_label.grid(row=1, column=4, padx=10, pady=5, sticky="e")
t2_entry.grid(row=1, column=5, padx=10, pady=5)

piecewise_y2_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
piecewise_y2_dropdown.grid(row=3, column=1, padx=10, pady=5)
amplitude2_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
amplitude2_entry.grid(row=4, column=1, padx=10, pady=5)
t2_entry.grid(row=3, column=2, padx=10, pady=5)
piecewise_t3_label.grid(row=3, column=3, padx=10, pady=5, sticky="e")
t3_entry.grid(row=3, column=4, padx=10, pady=5)
piecewise_t4_label.grid(row=3, column=5, padx=10, pady=5, sticky="e")
t4_entry.grid(row=3, column=6, padx=10, pady=5)

piecewise_y3_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
piecewise_y3_dropdown.grid(row=5, column=1, padx=10, pady=5)
amplitude3_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
amplitude3_entry.grid(row=6, column=1, padx=10, pady=5)
t4_entry.grid(row=5, column=2, padx=10, pady=5)
piecewise_t5_label.grid(row=5, column=3, padx=10, pady=5, sticky="e")
t5_entry.grid(row=5, column=4, padx=10, pady=5)
piecewise_t6_label.grid(row=5, column=5, padx=10, pady=5, sticky="e")
t6_entry.grid(row=5, column=6, padx=10, pady=5)

piecewise_y4_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
piecewise_y4_dropdown.grid(row=7, column=1, padx=10, pady=5)
amplitude4_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
amplitude4_entry.grid(row=8, column=1, padx=10, pady=5)
t6_entry.grid(row=7, column=2, padx=10, pady=5)
piecewise_t7_label.grid(row=7, column=3, padx=10, pady=5, sticky="e")
t7_entry.grid(row=7, column=4, padx=10, pady=5)

note_label.grid(row=8, column=2, columnspan=6, padx=10, pady=10, sticky="w")

# Place the canvas for the graph
canvas_widget.grid(row=10, column=0, columnspan=6, padx=10, pady=10)

# Create and place buttons below the graph
plot_button = ttk.Button(popup, text="Plot", command=plot_wave)
plot_button.grid(row=11, column=0, padx=10, pady=10)

run_button = ttk.Button(popup, text="Run", command=run_wave)
run_button.grid(row=11, column=1, padx=10, pady=10)

stop_button = ttk.Button(popup, text="Stop", command=stop_wave)
stop_button.grid(row=11, column=2, padx=10, pady=10)

# Create a Treeview widget for the data table
columns = ("y", "output", "code")
tree = ttk.Treeview(popup, columns=columns, show="headings", height=30)
tree.heading("y", text="Y Value")
tree.heading("output", text="Output (Hex)")
tree.heading("code", text="Code")
tree.grid(row=0, column=8, columnspan=6, padx=10, pady=10, rowspan=11, sticky="we")

# Add a scrollbar to the Treeview
scrollbar = ttk.Scrollbar(popup, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=14, rowspan=11, sticky='ns')

popup.mainloop()
