import tkinter as tk
from tkinter import ttk
import configparser
import modbus_config
import serial.tools.list_ports
from tkinter import messagebox
import time

# Read/Write register
REG_FRAME_TEMPERATURE   =   0x0010
REG_AREA_TEMPERATURE_1	=   0x0011
REG_AREA_TEMPERATURE_2	=   0x0012
REG_AREA_TEMPERATURE_3	=   0x0013
REG_AREA_TEMPERATURE_4	=   0x0014
REG_AREA_TEMPERATURE_5	=   0x0015
REG_AREA_TEMPERATURE_6	=   0x0016
REG_AREA_TEMPERATURE_7	=   0x0017
REG_AREA_TEMPERATURE_8	=   0x0018
REG_AREA_TEMPERATURE_9	=   0x0019
REG_TEMPERATURE_UNIT    =   0x0002
# Write Only register
REG_MODBUS_ID   =   0x0020

# Read only register
REG_AREA_TEMPERATURE_ALL    =   0x001A
REG_AREA_ALARM_ALL          =   0x001B
REG_ALARM_STATUS_ALL        =   0x0001

def connect_device():
    print("connect_device")

def update_config() :
    hex_value = frame_alarm_entry.get().strip()
    oseeing.alarm[0] = int(hex_value)
    #oseeing.alarm[0]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
# Square 1
    hex_value = square1_alarm_entry.get().strip()
    oseeing.alarm[1] = int(hex_value)
    #oseeing.alarm[1]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square1 alarm temperature={oseeing.alarm[1]}")

# Square 2
    hex_value = square2_alarm_entry.get().strip()
    oseeing.alarm[2] = int(hex_value)
    #oseeing.alarm[2]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square2 alarm temperature={oseeing.alarm[2]}")

# Square 3
    hex_value = square3_alarm_entry.get().strip()
    oseeing.alarm[3] = int(hex_value)
    #oseeing.alarm[3]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square3 alarm temperature={oseeing.alarm[3]}")

# Square 4
    hex_value = square4_alarm_entry.get().strip()
    oseeing.alarm[4] = int(hex_value)
    #oseeing.alarm[4]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square4 alarm temperature={oseeing.alarm[4]}")

# Square 5
    hex_value = square5_alarm_entry.get().strip()
    oseeing.alarm[5] = int(hex_value)
    #oseeing.alarm[5]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square5 alarm temperature={oseeing.alarm[5]}")

# Square 6
    hex_value = square6_alarm_entry.get().strip()
    oseeing.alarm[6] = int(hex_value)
    #oseeing.alarm[6]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square6 alarm temperature={oseeing.alarm[6]}")

# Square 7
    hex_value = square7_alarm_entry.get().strip()
    oseeing.alarm[7] = int(hex_value)
    #oseeing.alarm[7]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square7 alarm temperature={oseeing.alarm[7]}")

# Square 8
    hex_value = square8_alarm_entry.get().strip()
    oseeing.alarm[8] = int(hex_value)
    #oseeing.alarm[8]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square8 alarm temperature={oseeing.alarm[8]}")

# Square 9
    hex_value = square9_alarm_entry.get().strip()
    oseeing.alarm[9] = int(hex_value)
    #oseeing.alarm[9]=oseeing.transfer_temperature_unit_to_kelvin(int(hex_value))
    print(f"Square9 alarm temperature={oseeing.alarm[9]}")
    '''
    for i in range(10) :
        temp = oseeing.get_temperature_unit_str(i)
        print(f"index = {i} type = {type(temp)} {temp}")
    '''
def parse_default_ini () :
    ini_config = configparser.ConfigParser()
    try :
        ini_config.read('oseeing1s.ini')
    except Exception as e:
        print(f"ERROR : {e}")
    sections = ini_config.sections()
    print('Sections:', sections)
    for section in sections:
        print('Section:', section)
        options = ini_config.options(section)
        if section == "CONFIGURATION" :
            for option in options:
                value = ini_config.get(section, option)
                if option == 'id' :
                    oseeing.id = int(value,16)
                    #oseeing.set_id(id)
                    #oseeing.set_id(id)
                elif option == 'temperature_unit' :
                    oseeing.unit = int(value)
                elif option == 'frame_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,0)
                elif option == 'square1_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,1)
                elif option == 'square2_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,2)
                elif option == 'square3_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,3)
                elif option == 'square4_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,4)
                elif option == 'square5_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,5)
                elif option == 'square6_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,6)
                elif option == 'square7_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,7)
                elif option == 'square8_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,8)
                elif option == 'square9_alarm_temperature' :
                    oseeing.set_alarm_temperature(value,9)
                print(f'{option} = {value}')    

def download_settings() :
    if oseeing.client.port == None :
        messagebox.showerror("錯誤", "未指定COM Port")
        return
 
    #write frame
    update_config()
    oseeing.write_reg(REG_TEMPERATURE_UNIT,oseeing.unit)
    idx = 0
    for val in oseeing.alarm :
        reg=REG_FRAME_TEMPERATURE+idx
        print(f"{idx} Write {reg:04X} = {val}")
        ret = oseeing.write_reg(reg, val)
        if ret == None :
            messagebox.showerror("Error", "Write Modbus device failure")
        else :
            print(f"Write {reg:04X} = {val}")
        idx += 1
        time.sleep(0.01)

def save_settings():
    print("save settings")
    update_config()
    #update_temperature_unit()
    config = configparser.RawConfigParser()
    with open('oseeing1s.ini', 'w') as file:
        file.write("\n")
    config['CONFIGURATION'] = {
    	'id':hex(oseeing.id),
        'temperature_unit':oseeing.unit,
        'frame_alarm_temperature':oseeing.alarm[0],
        'square1_alarm_temperature':oseeing.alarm[1],
        'square2_alarm_temperature':oseeing.alarm[2],
        'square3_alarm_temperature':oseeing.alarm[3],
        'square4_alarm_temperature':oseeing.alarm[4],
        'square5_alarm_temperature':oseeing.alarm[5],
        'square6_alarm_temperature':oseeing.alarm[6],
        'square7_alarm_temperature':oseeing.alarm[7],
        'square8_alarm_temperature':oseeing.alarm[8],
        'square9_alarm_temperature':oseeing.alarm[9]
    	}
    with open('oseeing1s.ini', 'a') as configfile:
        config.write(configfile)
    print("Settings saved to oseeing1s.ini")    

def btn_write_id():
    hex_value = write_id_entry.get().strip()
    id = int(hex_value, 16)
    if not (0x01 <= int(hex_value, 16) <= 0xF0):
        messagebox.showerror("錯誤", "請輸入有效的 1-byte 十六進制數（01 - F0）")
        return
    if oseeing.client.port == None :
        messagebox.showerror("錯誤", "未指定COM Port")
        return
    #if oseeing.set_device_id(id) :
    
    if oseeing.write_reg(REG_MODBUS_ID, id) != None:
        messagebox.showerror("確認", f"ID({hex(id)})修改完成")
        oseeing.id = id
        #oseeing.set_id(hex_value)
        #id_entry.delete(0, tk.END)  
        #id_entry.insert(0,hex(int(oseeing.id,16))) 
    else :
        messagebox.showerror("錯誤", "連接異常")
'''
def btn_set_id():
    print(f"id_entry = {type(id_entry)}")
    hex_value = id_entry.get().strip()
    id = int(hex_value, 16)
    #if len(hex_value) != 2 or not (0x00 <= int(hex_value, 16) <= 0xFF):
    if not (0x01 <= int(hex_value, 16) <= 0xF0):
        messagebox.showerror("錯誤", "請輸入有效的 1-byte 十六進制數（01 - F0）")
        return
    if oseeing.client.port == None :
        messagebox.showerror("錯誤", "未指定COM Port")
        return
    oseeing.id = id 
    if oseeing.write_reg(REG_MODBUS_ID, oseeing.id) != None:
        messagebox.showerror("確認", f"Oseeing 裝置已連接, ID({hex(id)})")
    else :
        messagebox.showerror("錯誤", "連接異常")
'''
# Square 1
def btn_set_square1_alarm_temperature():
    hex_value = square1_alarm_entry.get().strip()
    oseeing.alarm[1]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_1, oseeing.alarm[1])
    print(f"Square1 alarm temperature={oseeing.alarm[1]}")

# Square 2
def btn_set_square2_alarm_temperature():
    hex_value = square2_alarm_entry.get().strip()
    oseeing.alarm[2]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_2, oseeing.alarm[2])
    print(f"Square2 alarm temperature={oseeing.alarm[2]}")

# Square 3
def btn_set_square3_alarm_temperature():
    hex_value = square3_alarm_entry.get().strip()
    oseeing.alarm[3]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_3, oseeing.alarm[3])
    print(f"Square3 alarm temperature={oseeing.alarm[3]}")

# Square 4
def btn_set_square4_alarm_temperature():
    hex_value = square4_alarm_entry.get().strip()
    oseeing.alarm[4]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_4, oseeing.alarm[4])
    print(f"Square4 alarm temperature={oseeing.alarm[4]}")

# Square 5
def btn_set_square5_alarm_temperature():
    hex_value = square5_alarm_entry.get().strip()
    oseeing.alarm[5]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_5, oseeing.alarm[5])
    print(f"Square5 alarm temperature={oseeing.alarm[5]}")

# Square 6
def btn_set_square6_alarm_temperature():
    hex_value = square6_alarm_entry.get().strip()
    oseeing.alarm[6]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_6, oseeing.alarm[6])
    print(f"Square6 alarm temperature={oseeing.alarm[6]}")

# Square 7
def btn_set_square7_alarm_temperature():
    hex_value = square7_alarm_entry.get().strip()
    oseeing.alarm[7]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_7, oseeing.alarm[7])
    print(f"Square7 alarm temperature={oseeing.alarm[7]}")

# Square 8
def btn_set_square8_alarm_temperature():
    hex_value = square8_alarm_entry.get().strip()
    oseeing.alarm[8]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_8, oseeing.alarm[8])
    print(f"Square8 alarm temperature={oseeing.alarm[8]}")

# Square 9
def btn_set_square9_alarm_temperature():
    hex_value = square9_alarm_entry.get().strip()
    oseeing.alarm[9]=int(hex_value)
    oseeing.write_reg(REG_AREA_TEMPERATURE_9, oseeing.alarm[9])
    print(f"Square9 alarm temperature={oseeing.alarm[9]}")

def btn_set_frame_alarm_temperature():
    hex_value = frame_alarm_entry.get().strip()
    print(type(hex_value))
    oseeing.alarm[0]=int(hex_value)
    print(type(oseeing.alarm[0]))
    print(oseeing.alarm[0])
    oseeing.write_reg(REG_FRAME_TEMPERATURE, oseeing.alarm[0])
    print(f"Set frame alarm temperature={oseeing.alarm[0]}")

# 定義一個函數來更新顯示選中的值
def update_label(*args):
    curr_unit = oseeing.unit
    selected_value = selected_option.get()
    oseeing.unit = options.index(selected_value)  # 獲取選中的值在列表中的索引
    temperature_unit_label.config(text=f"溫度單位：{selected_value}")
    temp0_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp1_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp2_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp3_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp4_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp5_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp6_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp7_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp8_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    temp9_unit_label.config(text=f"0.1 {options[oseeing.unit]}")
    print(f"Unit = {selected_value}, Index = {oseeing.unit}")
    update_temperature_unit(curr_unit)

def update_temperature_unit(curr) :
    frame_alarm_entry.delete(0,tk.END)
    square1_alarm_entry.delete(0,tk.END)
    square2_alarm_entry.delete(0,tk.END)
    square3_alarm_entry.delete(0,tk.END)
    square4_alarm_entry.delete(0,tk.END)
    square5_alarm_entry.delete(0,tk.END)
    square6_alarm_entry.delete(0,tk.END)
    square7_alarm_entry.delete(0,tk.END)
    square8_alarm_entry.delete(0,tk.END)
    square9_alarm_entry.delete(0,tk.END)
    frame_alarm_entry.insert(0,oseeing.get_temperature_unit(0, curr))
    square1_alarm_entry.insert(0,oseeing.get_temperature_unit(1, curr))
    square2_alarm_entry.insert(0,oseeing.get_temperature_unit(2, curr))
    square3_alarm_entry.insert(0,oseeing.get_temperature_unit(3, curr))
    square4_alarm_entry.insert(0,oseeing.get_temperature_unit(4, curr))
    square5_alarm_entry.insert(0,oseeing.get_temperature_unit(5, curr))
    square6_alarm_entry.insert(0,oseeing.get_temperature_unit(6, curr))
    square7_alarm_entry.insert(0,oseeing.get_temperature_unit(7, curr))
    square8_alarm_entry.insert(0,oseeing.get_temperature_unit(8, curr))
    square9_alarm_entry.insert(0,oseeing.get_temperature_unit(9, curr))

# variable initial
oseeing = None
options = ["°K", "°F", "°C"]
frame_alarm_entry = None
square1_alarm_entry = None
square2_alarm_entry = None
square3_alarm_entry = None
square4_alarm_entry = None
square5_alarm_entry = None
square6_alarm_entry = None
square7_alarm_entry = None
square8_alarm_entry = None
square9_alarm_entry = None
id_entry = None
selected_option = None
temperature_unit_label = None
temp0_unit_label = None
temp1_unit_label = None
temp2_unit_label = None
temp3_unit_label = None
temp4_unit_label = None
temp5_unit_label = None
temp6_unit_label = None
temp7_unit_label = None
temp8_unit_label = None
temp9_unit_label = None
write_id_entry = None
def oseeing_setting_start(oc, root) :
# variable initial
    global mac_result
    global oseeing 
    global frame_alarm_entry 
    global square1_alarm_entry 
    global square2_alarm_entry 
    global square3_alarm_entry 
    global square4_alarm_entry 
    global square5_alarm_entry 
    global square6_alarm_entry 
    global square7_alarm_entry 
    global square8_alarm_entry 
    global square9_alarm_entry 
    global id_entry 
    global selected_option 
    global temperature_unit_label 
    global temp0_unit_label 
    global temp1_unit_label 
    global temp2_unit_label 
    global temp3_unit_label 
    global temp4_unit_label 
    global temp5_unit_label 
    global temp6_unit_label 
    global temp7_unit_label 
    global temp8_unit_label 
    global temp9_unit_label 
    global write_id_entry

    oseeing=oc
    ip_result= "None"
    mac_result = "None"


#print_ini_setting()
# 建立主視窗
    #root.title("Oseeing Tool")
    #root.geometry('800x600')
    #root.resizable(True,True)

#options = ["凱式溫度", "華氏溫度", "攝氏溫度"]

    # 建立 COM Port 標籤和文字輸入欄

    '''# Set Modbus ID
    rs485_id_label = tk.Label(root, text="Modbus Device ID:", anchor="w")
    rs485_id_label.grid(row=1,column=0,padx=5, pady=5, sticky='w')
    id_entry = tk.Entry(root, width=5)
    id_entry.insert(0,hex(oseeing.id).upper()) 
    print(f"id_entry = {type(id_entry)}")
    #id_entry.insert(0,hex(int(oseeing.id,16))) 
    #id_entry.insert(0,oseeing.id) 

    id_entry.grid(row=1, column=1, padx=5)
    button_id = tk.Button(root, text="連線", command=btn_set_id)
    button_id.grid(row=1, column=2, padx=5)
'''
    # Set Frame Alarm params
    frame_alarm_temperature = tk.Label(root, text="Frame Alarm Temperature:", anchor="w")
    frame_alarm_temperature.grid(row=2,column=0,padx=5, pady=5, sticky='w')
    frame_alarm_entry = tk.Entry(root, width=5)
    frame_alarm_entry.insert(0,oseeing.alarm[0])
    print(f"{type(oseeing.alarm[0])} : {oseeing.alarm[0]}")
    #frame_alarm_entry.insert(0,oseeing.get_temperature_unit(0))
    frame_alarm_entry.grid(row=2, column=1, padx=5)
    #temp_frame = tk.Label(root, text="°C")
    temp0_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp0_unit_label.grid(row=2, column=3, padx=0, sticky='w')
    button_frame_alarm = tk.Button(root, text="確認", command=btn_set_frame_alarm_temperature)
    button_frame_alarm.grid(row=2, column=2, padx=5)

    # Set Square1 Alarm params
    square1_alarm_temperature = tk.Label(root, text="Area1 Alarm Temperature:", anchor="w")
    square1_alarm_temperature.grid(row=3,column=0,padx=5, pady=5, sticky='w')
    square1_alarm_entry = tk.Entry(root, width=5)
    square1_alarm_entry.insert(0,oseeing.alarm[1])
    print(f"{type(oseeing.alarm[1])} : {oseeing.alarm[1]}")
    #square1_alarm_entry.insert(0,oseeing.get_temperature_unit(1))
    square1_alarm_entry.grid(row=3, column=1, padx=5, sticky='w')
    temp1_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp1_unit_label.grid(row=3, column=3, padx=0)
    button_square1 = tk.Button(root, text="確認", command=btn_set_square1_alarm_temperature)
    button_square1.grid(row=3, column=2, padx=5)

    # Set Square2 Alarm params
    square2_alarm_temperature = tk.Label(root, text="Area2 Alarm Temperature:", anchor="w")
    square2_alarm_temperature.grid(row=4,column=0,padx=5, pady=5, sticky='w')
    square2_alarm_entry = tk.Entry(root, width=5)
    square2_alarm_entry.insert(0,oseeing.alarm[2])
    print(f"{type(oseeing.alarm[2])} : {oseeing.alarm[2]}")
    #square2_alarm_entry.insert(0,oseeing.get_temperature_unit(2))
    square2_alarm_entry.grid(row=4, column=1, padx=5, sticky='w')
    temp2_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp2_unit_label.grid(row=4, column=3, padx=0)
    button_square2 = tk.Button(root, text="確認", command=btn_set_square2_alarm_temperature)
    button_square2.grid(row=4, column=2, padx=5)

    # Set Square3 Alarm params
    square3_alarm_temperature = tk.Label(root, text="Area3 Alarm Temperature:", anchor="w")
    square3_alarm_temperature.grid(row=5,column=0,padx=5, pady=5, sticky='w')
    square3_alarm_entry = tk.Entry(root, width=5)
    square3_alarm_entry.insert(0,oseeing.alarm[3])
    print(f"{type(oseeing.alarm[3])} : {oseeing.alarm[3]}")
    #square3_alarm_entry.insert(0,oseeing.get_temperature_unit(3))
    square3_alarm_entry.grid(row=5, column=1, padx=5, sticky='w')
    temp3_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp3_unit_label.grid(row=5, column=3, padx=0)
    button_square3 = tk.Button(root, text="確認", command=btn_set_square3_alarm_temperature)
    button_square3.grid(row=5, column=2, padx=5)

    # Set Square4 Alarm params
    square4_alarm_temperature = tk.Label(root, text="Area4 Alarm Temperature:", anchor="w")
    square4_alarm_temperature.grid(row=6,column=0,padx=5, pady=5, sticky='w')
    square4_alarm_entry = tk.Entry(root, width=5)
    square4_alarm_entry.insert(0,oseeing.alarm[4])
    print(f"{type(oseeing.alarm[4])} : {oseeing.alarm[4]}")
    #square4_alarm_entry.insert(0,oseeing.get_temperature_unit(4))
    square4_alarm_entry.grid(row=6, column=1, padx=5, sticky='w')
    temp4_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp4_unit_label.grid(row=6, column=3, padx=0)
    button_square4 = tk.Button(root, text="確認", command=btn_set_square4_alarm_temperature)
    button_square4.grid(row=6, column=2, padx=5)

    # Set Square5 Alarm params
    square5_alarm_temperature = tk.Label(root, text="Area5 Alarm Temperature:", anchor="w")
    square5_alarm_temperature.grid(row=7,column=0,padx=5, pady=5, sticky='w')
    square5_alarm_entry = tk.Entry(root, width=5)
    square5_alarm_entry.insert(0,oseeing.alarm[5])
    print(f"{type(oseeing.alarm[5])} : {oseeing.alarm[5]}")
    #square5_alarm_entry.insert(0,oseeing.get_temperature_unit(5))
    square5_alarm_entry.grid(row=7, column=1, padx=5, sticky='w')
    temp5_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp5_unit_label.grid(row=7, column=3, padx=0)
    button_square5 = tk.Button(root, text="確認", command=btn_set_square5_alarm_temperature)
    button_square5.grid(row=7, column=2, padx=5)

    # Set Square6 Alarm params
    square6_alarm_temperature = tk.Label(root, text="Area6 Alarm Temperature:", anchor="w")
    square6_alarm_temperature.grid(row=8,column=0,padx=5, pady=5, sticky='w')
    square6_alarm_entry = tk.Entry(root, width=5)
    square6_alarm_entry.insert(0,oseeing.alarm[6])
    print(f"{type(oseeing.alarm[6])} : {oseeing.alarm[6]}")
    #square6_alarm_entry.insert(0,oseeing.get_temperature_unit(6))
    square6_alarm_entry.grid(row=8, column=1, padx=5, sticky='w')
    temp6_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp6_unit_label.grid(row=8, column=3, padx=0)
    button_square6 = tk.Button(root, text="確認", command=btn_set_square6_alarm_temperature)
    button_square6.grid(row=8, column=2, padx=5)

    # Set Square7 Alarm params
    square7_alarm_temperature = tk.Label(root, text="Area7 Alarm Temperature:", anchor="w")
    square7_alarm_temperature.grid(row=9,column=0,padx=5, pady=5, sticky='w')
    square7_alarm_entry = tk.Entry(root, width=5)
    square7_alarm_entry.insert(0,oseeing.alarm[7])
    print(f"{type(oseeing.alarm[7])} : {oseeing.alarm[7]}")
    #square7_alarm_entry.insert(0,oseeing.get_temperature_unit(7))
    square7_alarm_entry.grid(row=9, column=1, padx=5, sticky='w')
    temp7_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp7_unit_label.grid(row=9, column=3, padx=0)
    button_square7 = tk.Button(root, text="確認", command=btn_set_square7_alarm_temperature)
    button_square7.grid(row=9, column=2, padx=5)

    # Set Square8 Alarm params
    square8_alarm_temperature = tk.Label(root, text="Area8 Alarm Temperature:", anchor="w")
    square8_alarm_temperature.grid(row=10,column=0,padx=5, pady=5, sticky='w')
    square8_alarm_entry = tk.Entry(root, width=5)
    square8_alarm_entry.insert(0,oseeing.alarm[8])
    print(f"{type(oseeing.alarm[8])} : {oseeing.alarm[8]}")
    #square8_alarm_entry.insert(0,oseeing.get_temperature_unit(8))
    square8_alarm_entry.grid(row=10, column=1, padx=5, sticky='w')
    temp8_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp8_unit_label.grid(row=10, column=3, padx=0)
    button_square8 = tk.Button(root, text="確認", command=btn_set_square8_alarm_temperature)
    button_square8.grid(row=10, column=2, padx=5)

    # Set Square9 Alarm params
    square9_alarm_temperature = tk.Label(root, text="Area9 Alarm Temperature:", anchor="w")
    square9_alarm_temperature.grid(row=11,column=0,padx=5, pady=5, sticky='w')
    square9_alarm_entry = tk.Entry(root, width=5)
    square9_alarm_entry.insert(0,oseeing.alarm[9])
    print(f"{type(oseeing.alarm[9])} : {oseeing.alarm[9]}")
    #square9_alarm_entry.insert(0,oseeing.get_temperature_unit(9))
    square9_alarm_entry.grid(row=11, column=1, padx=5, sticky='w')
    temp9_unit_label = tk.Label(root, text=f"0.1 {options[oseeing.unit]}", anchor="w")
    temp9_unit_label.grid(row=11, column=3, padx=0)
    button_square9 = tk.Button(root, text="確認", command=btn_set_square9_alarm_temperature, anchor="w")
    button_square9.grid(row=11, column=2, padx=5)

    save_button = tk.Button(root, text="儲存設定", command=save_settings, anchor="w")
    save_button.grid(row=13,column=0,padx=5, pady=5, sticky='w')

    write_button = tk.Button(root, text="寫入裝置", command=download_settings, anchor="w")
    write_button.grid(row=13,column=1)


    write_id_label = tk.Label(root, text="New Device ID:", anchor="w")
    write_id_label.grid(row=12,column=0,padx=5, pady=5,stick='w')
    write_id_entry = tk.Entry(root, width=5)
    #id_entry.insert(0,(oseeing.id))
    write_id_entry.grid(row=12, column=1, padx=5)
    button_write_id = tk.Button(root, text="確認", command=btn_write_id)
    button_write_id.grid(row=12, column=2, padx=5)
    #button_reset_id = tk.Button(root, text="重置ID", command=btn_reset_id)
    #button_reset_id.grid(row=12, column=3, padx=5)

    # Temperature unit select
    # 設定一個變量來存儲當前選中的值
    selected_option = tk.StringVar()
    selected_option.set(options[oseeing.unit])  # 設置默認值為 "凱式溫度"
    # 創建下拉選單
    dropdown = tk.OptionMenu(root, selected_option, *options)
    dropdown.grid(row=14,column=1,padx=5, sticky='w')
    # 創建一個標籤顯示選中的值
    temperature_unit_label = tk.Label(root, text=f"溫度單位：{options[oseeing.unit]}", anchor="w")
    temperature_unit_label.grid(row=14,column=0,padx=5, pady=5, sticky='w')
    # 綁定變量的變化事件
    selected_option.trace_add("write", update_label)

    # 啟動主迴圈
    #root.mainloop()
