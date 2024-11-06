import serial
import time
import socket
import struct
import numpy as np
#import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
from tkinter import messagebox
import threading
import modbus_config
from ctypes import c_int16
#from tkinter import Tk, Label, Button, messagebox
from PIL import Image, ImageTk
import matplotlib.cm as cm
HOST = '0.0.0.0'  # 接收端的IP地址
PORT = 8080

RS485_SET_SERVER_IP	=	b"\xf1\xf1\x03\x03" #0x50
RS485_SET_SOCKET_START=	b"\xf1\xf1\x02\x02" #0x51
RS485_RESET_DEVICE_ID = b"\xf1\xf1\x01\x01"
global SERIAL_PORT
SERIAL_PORT = "COM5"
BAUDRATE = 9600 # 115200
DeviceID = b"\xF1\xF1" #0xAA

REG_SENSOR_GAIN         =   0x0021	#reg[0xB9] 0,4: 0 (Max), 1:Auto, 2:0.25, 3:0.5
REG_SENSOR_EMISSIVITY   =   0x0022	# reg[0xCA] 1~100
REG_SENSOR_SENSITIVITY	=   0x0023	# reg[0xC2] 0~255
REG_SENSOR_OFFSET	    =	0x0024	# reg[0xCB] +/- 12.7K
REG_SENSOR_FILTER	    =	0x0025	# reg[0xD0~0xD3] TBD

Result = False

oseeing = None
connect_button = None
reset_botton = None

def receive_data():
    global disp
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on {HOST}:{PORT}...")
        
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")
            img_handle = None
            while True:
                total_bytes = 62 * 80 * 2  # Each RGB565 data point is 2 bytes
                data = b''
                # Receive data until we get the expected amount
                while len(data) < total_bytes:
                    packet = conn.recv(total_bytes - len(data))
                    if not packet:
                        print("Connection closed or data missing")
                        return
                    data += packet

                # Convert data to numpy array and process
                disp = struct.unpack('>4960H', data)
                disp = np.array(disp, dtype=np.uint16).reshape((62, 80))
                #print("Disp Array Shape:", disp.shape)
                #print("Disp Array Data Type:", disp.dtype)
                #print("Disp Array Content:", disp)
                # Normalize data to [0, 255] for image
                norm_disp = (disp - disp.min()) / (disp.max() - disp.min())
                # Convert to RGB image using a colormap
                colored_img = (cm.jet(norm_disp)[:, :, :3] * 255).astype(np.uint8)
                # Convert to PIL image
                try:
                    img = Image.fromarray(colored_img,'RGB')
                except Exception as e:
                    print(f"Image conversion error: {e}")
                    print(f"Colored image shape: {colored_img.shape}, dtype: {colored_img.dtype}")
                img = img.resize((320, 248))  # Resize for better display

                # Update Tkinter image
                tk_img = ImageTk.PhotoImage(image=img)
                image_label.config(image=tk_img)
                image_label.image = tk_img  # Keep reference to avoid garbage collection

                root.update_idletasks()
                root.update()

                data = b''  # Reset data for next frame

def set_socket_enable(en) :
    data_packet = RS485_SET_SOCKET_START + en.to_bytes(1,byteorder="big")
    return  send_and_receive_data(data_packet)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def send_ip_addr(command_id):
    ip_address = get_local_ip()
    ip_address_bytes = ip_address.encode('utf-8')
    ip_length = len(ip_address_bytes)
    data_packet = RS485_SET_SERVER_IP + ip_length.to_bytes(1,byteorder="big") + ip_address_bytes
    return send_and_receive_data(data_packet) 

def send_and_receive_data(data_packet):
    retry=3
    print(oseeing.client.port)
    with serial.Serial(oseeing.client.port, BAUDRATE, timeout=1) as ser:
        ser.flushInput()  # Clear receive buffer
        ser.flushOutput()  # Clear send buffer
        
        ser.write(data_packet)
        print("Data sent:", data_packet)
        
        while retry:
            received_data = ser.read(len(data_packet))
        
            if received_data == data_packet:
                print("Received data matches sent data:", received_data)
                return True
            else:
                print("Received data does not match sent data or no data received.")
                print(received_data)
                retry -= 1
            if retry == 0 :
                print(f"Set command({data_packet}) fail....")
                return False
        time.sleep(1)

def reset_rs485_id():
    data_packet = RS485_RESET_DEVICE_ID
    return send_and_receive_data(data_packet) 
    print("Reset RS485 ID")

def btn_gain():
    value = gain_entry.get().strip()
    data = int(value)
    if (data > 4) | (data < 0):
        messagebox.showerror("錯誤", "range is 0~4")
        return
    if oseeing.write_reg(REG_SENSOR_GAIN, data) == None:
        messagebox.showerror("錯誤", "連接異常")
def btn_emissivity():
    value = emissivity_entry.get().strip()
    data = int(value)
    if (data > 255) | (data < 0):
        messagebox.showerror("錯誤", "range is 0~255")
        return
    if oseeing.write_reg(REG_SENSOR_EMISSIVITY, data) == None:
        messagebox.showerror("錯誤", "連接異常")
def btn_sensitivity():
    value = sensitivity_entry.get().strip()
    data = int(value)
    if (data > 100) | (data < 0):
        messagebox.showerror("錯誤", "range is 0~100")
        return
    if oseeing.write_reg(REG_SENSOR_SENSITIVITY, data) == None:
        messagebox.showerror("錯誤", "連接異常")
def btn_offset():
    value = offset_entry.get().strip()
    #data = c_int16(int(value)).value
    #print(f"{type(data)} : {data}")
    val = int(value)
    if (val > 127) | (val < -127):
        messagebox.showerror("錯誤", "range is -127~127")
        return
    data = int(value) & 0xFFFF
    print(f"{type(data)} : {data}")
    if oseeing.write_reg(REG_SENSOR_OFFSET, data) == None:
        messagebox.showerror("錯誤", "連接異常")
def btn_filter():
    value = filter_entry.get().strip()
    data = int(value)
    if (data > 3) | (data < 0):
        messagebox.showerror("錯誤", "range is 0~3")
        return
    if oseeing.write_reg(REG_SENSOR_FILTER, data) == None:
        messagebox.showerror("錯誤", "連接異常")

import threading

def connect_device():
    global receive_thread
    global oseeing
    if connect_button['text'] == "Preview":
        if send_ip_addr( RS485_SET_SERVER_IP):
            if set_socket_enable(1):
                connect_button.config(text="Stop")
                receive_thread = threading.Thread(target=receive_data)
                receive_thread.start()
    else:
        if set_socket_enable(0):
            connect_button.config(text="Preview")
            if receive_thread.is_alive():
                print("Stopping data reception...")


def save_settings():
    print("save")

def on_motion(event):
    """Handle mouse hover to show temperature."""
    x, y = event.x, event.y
    # Scale mouse position to data array index
    data_x = int(x / 4)  # Rescaled for the 80x data width
    data_y = int(y / 4)  # Rescaled for the 62x data height

    if 0 <= data_x < 80 and 0 <= data_y < 62:  # Ensure the indices are in bounds
        temp_value = disp[data_y, data_x]
        tooltip.config(text=f"Temperature: {(temp_value-2735)/10}°C")
        #tooltip.place(x=event.x_root - root.winfo_x() + 10, y=event.y_root - root.winfo_y() + 10)
        tooltip.place(x=10, y=500)
        #print(f"x-root={event.x_root}, x-win={root.winfo_x()}, y-root={event.y_root}, y-win={root.winfo_y()} ")
        tooltip.lift()  # Raise tooltip to be visible
    else:
        tooltip.place_forget()

gain_entry = None
emissivity_entry = None
sensitivity_entry = None
offset_entry = None 
filter_entry = None
image_label = None
tooltip = None
root = None
#def oseeing_preview_start(oc, root) :
def oseeing_preview_start(oc, r) :
    global oseeing
    global connect_button
    global reset_botton
    global gain_entry
    global emissivity_entry
    global sensitivity_entry
    global offset_entry 
    global filter_entry
    global image_label
    global tooltip
    global root
    oseeing = oc
    root = r
    print(f"preview com port {oseeing.client.port}")
    #print(f"Preview : {root.winfo_x()} - {root.winfo_y()}")
# GAIN
    gain_label = tk.Label(root, text="Gain(0 (Max), 1:Auto, 2:0.25, 3:0.5):", anchor="w")
    gain_label.grid(row=1,column=0,padx=5, pady=5,stick='w')
    gain_entry = tk.Entry(root, width=5)
    gain_entry.grid(row=1, column=1, padx=5)
    button_gain = tk.Button(root, text="確認", command=btn_gain)
    button_gain.grid(row=1, column=2, padx=5)
#EMISSIVITY
    emissivity_label = tk.Label(root, text="Emissivity (0~100):", anchor="w")
    emissivity_label.grid(row=2,column=0,padx=5, pady=5,stick='w')
    emissivity_entry = tk.Entry(root, width=5)
    emissivity_entry.grid(row=2, column=1, padx=5)
    button_emissivity = tk.Button(root, text="確認", command=btn_emissivity)
    button_emissivity.grid(row=2, column=2, padx=5)

#SENSITIVITY
    sensitivity_label = tk.Label(root, text="sensitivity (0~255):", anchor="w")
    sensitivity_label.grid(row=3,column=0,padx=5, pady=5,stick='w')
    sensitivity_entry = tk.Entry(root, width=5)
    sensitivity_entry.grid(row=3, column=1, padx=5)
    button_sensitivity = tk.Button(root, text="確認", command=btn_sensitivity)
    button_sensitivity.grid(row=3, column=2, padx=5)
#OFFSET
    offset_label = tk.Label(root, text="offset (+/-127):", anchor="w")
    offset_label.grid(row=4,column=0,padx=5, pady=5,stick='w')
    offset_entry = tk.Entry(root, width=5)
    offset_entry.grid(row=4, column=1, padx=5)
    button_offset = tk.Button(root, text="確認", command=btn_offset)
    button_offset.grid(row=4, column=2, padx=5)
#FILTER
    filter_label = tk.Label(root, text="filter:", anchor="w")
    filter_label.grid(row=5,column=0,padx=5, pady=5,stick='w')
    filter_entry = tk.Entry(root, width=5)
    filter_entry.grid(row=5, column=1, padx=5)
    button_filter = tk.Button(root, text="確認", command=btn_filter)
    button_filter.grid(row=5, column=2, padx=5)

    reset_button = tk.Button(root, text="Reset ID", command=reset_rs485_id)
    reset_button.grid(row=15,column=0)

    connect_button = tk.Button(root, text="Preview", command=connect_device)
    connect_button.grid(row=16,column=0)
    # Label to display the image
    image_label = tk.Label(root)
    #image_label.pack()
    image_label.grid(row=17, column=0, padx=5)
    image_label.bind("<Motion>", on_motion)
    tooltip = tk.Label(root, text="", bg="yellow")
    tooltip.grid(row=0, column=1)  # Place it next to the image_label
    tooltip.grid_remove()  # Initially hide the tooltip

#save_button = tk.Button(root, text="Save Settings", command=save_settings)
#save_button.grid(row=20,column=0)

