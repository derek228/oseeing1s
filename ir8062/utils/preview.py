import serial
import time
import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
from tkinter import messagebox
import threading
import modbus_config
HOST = '0.0.0.0'  # 接收端的IP地址
PORT = 8080

RS485_SET_SERVER_IP	=	b"\xf1\xf1\x03\x03" #0x50
RS485_SET_SOCKET_START=	b"\xf1\xf1\x02\x02" #0x51
RS485_RESET_DEVICE_ID = b"\xf1\xf1\x01\x01"
global SERIAL_PORT
SERIAL_PORT = "COM5"
BAUDRATE = 9600 # 115200
DeviceID = b"\xF1\xF1" #0xAA

Result = False

oseeing = None
connect_button = None
reset_botton = None

def receive_data():
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots()
    
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

                # Print the actual size of the received data
                #print(f"Received data size: {len(data)} bytes")
                
                disp = struct.unpack('4960H', data)
                disp = np.array(disp, dtype=np.uint16).reshape((62, 80))
                
                # Normalize the temperature data to range [0, 1]
                norm_disp = (disp - disp.min()) / (disp.max() - disp.min())
                
                # Update the plot with the new data
                if img_handle is None:
                    img_handle = ax.imshow(norm_disp, cmap='jet', interpolation='nearest')
                else:
                    img_handle.set_data(norm_disp)
                
                plt.draw()
                plt.pause(0.01)  # Pause to update the plot


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

def oseeing_preview_start(oc, root) :
    global oseeing
    global connect_button
    global reset_botton
    oseeing = oc
    print(f"preview com port {oseeing.client.port}")
    connect_button = tk.Button(root, text="Preview", command=connect_device)
    connect_button.grid(row=15,column=0)

    reset_button = tk.Button(root, text="Reset ID", command=reset_rs485_id)
    reset_button.grid(row=16,column=0)

#save_button = tk.Button(root, text="Save Settings", command=save_settings)
#save_button.grid(row=20,column=0)

