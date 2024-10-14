import tkinter as tk
from tkinter import ttk
import configparser
import modbus_config as mc
import serial.tools.list_ports
from tkinter import messagebox
import time
import tabmenu

def open_config():
    selected_port = combo_box.get()  # 取得選中的 Serial Port
    if selected_port:
        root.destroy()  # 關閉主窗口
        oseeing.client.port = selected_port
        tabmenu.oseeing_tool_start(oseeing) # 打開 config 窗口

root = tk.Tk()
root.title("Oseeing Tools")

oseeing = mc.ModbusConfig()
label = tk.Label(root, text="請選擇串行端口:")
label.pack(pady=10)

ports = serial.tools.list_ports.comports()
port_list = [port.device for port in ports]

combo_box = ttk.Combobox(root, values=port_list)
combo_box.pack(pady=10)
combo_box.set(port_list[0] if port_list else "無可用端口")

# 確認按鈕
confirm_button = tk.Button(root, text="打開 Config", command=open_config)
confirm_button.pack(pady=20)

# 啟動主循環
root.mainloop()