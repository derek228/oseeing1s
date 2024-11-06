import tkinter as tk
from tkinter import ttk
import configparser
import modbus_config as mc
import serial.tools.list_ports
from tkinter import messagebox
import time
import tabmenu
import preview
REG_AREA_ALARM_ALL      =   0x001B
REG_TEMPERATURE_UNIT    =   0x0002
def get_device_config():
    
    reg = oseeing.read_reg(REG_TEMPERATURE_UNIT, 1)
    if reg == None:
        messagebox.showerror("Error", "Connection failure...(Unit)")
        return
    else :
        oseeing.unit = reg[0]
    #print(f"Temperature unit = {oseeing.unit}")
    reg = oseeing.read_reg(REG_AREA_ALARM_ALL, 10)
    if reg == None:
        messagebox.showerror("Error", "Connection failure...(Alarm)")
        #root.destroy()  # 關閉主窗口
        return False
    else :
        for i in range(10) :
            oseeing.alarm[i] = reg[i]
            #print(f"Alarm{i} : {oseeing.alarm[i]}")
    return True

def open_config():
    selected_port = combo_box.get()  # 取得選中的 Serial Port
    if selected_port:
        hex_value = id_entry.get().strip()
        oseeing.id = int(hex_value,16)
        print(oseeing.id)
        oseeing.client.port = selected_port
        if get_device_config()== True :
            root.destroy()  # 關閉主窗口
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


id_frame = tk.Frame(root)
id_frame.pack(pady=15)

rs485_id_label = tk.Label(id_frame, text="Device ID:")
rs485_id_label.pack(side=tk.LEFT,padx=5)
#rs485_id_label.grid(row=1,column=0,padx=5, pady=5, sticky='w')
id_entry = tk.Entry(id_frame, width=5)
id_entry.insert(0,hex(oseeing.id).upper()) 
id_entry.pack(side=tk.LEFT, padx=5)
#id_entry.grid(row=1, column=1, padx=5)
#button_id = tk.Button(root, text="連線", command=btn_set_id)
#button_id.grid(row=1, column=2, padx=5)


# 確認按鈕
confirm_button = tk.Button(root, text="Connect", command=open_config)
confirm_button.pack(pady=20)

#print(f"Main : {root.winfo_x()} - {root.winfo_y()}")

# 啟動主循環
root.mainloop()