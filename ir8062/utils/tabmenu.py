import tkinter as tk
from tkinter import ttk
import configparser
import modbus_config as mc
import serial.tools.list_ports
from tkinter import messagebox
import time
import alarm
import preview
import config
entry1 = None
entry2 = None
entry3 = None
def parse_default_ini (oseeing) :
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

# 創建主窗口
def oseeing_tool_start(oseeing) :
    root = tk.Tk()
    root.title("Oseeing Tools")
    root.geometry('800x600')
    parse_default_ini(oseeing)
    print(oseeing.client.port)
    # 創建 Notebook（標籤頁容器）
    notebook = ttk.Notebook(root)

    # 創建每個標籤頁的 Frame
    setting = tk.Frame(notebook)
    view = tk.Frame(notebook)
    alarm_root = tk.Frame(notebook)

    # 將標籤頁添加到 Notebook
    notebook.add(setting, text="Device Configuration")
    notebook.add(alarm_root, text="Alarm Monitor")
    notebook.add(view, text="Preview")
    notebook.pack(expand=True, fill="both")

    # 標籤頁 1 - 輸入框和按鈕
    config.oseeing_setting_start(oseeing, setting)

    # 標籤頁 2 - 輸入框和按鈕
    preview.oseeing_preview_start(oseeing, view)
    # 標籤頁 3 - 輸入框和按鈕
    alarm.oseeing_alarm_start(oseeing, alarm_root)
    notebook.bind("<<NotebookTabChanged>>", alarm.on_tab_selected)
# 啟動主循環
    root.mainloop()
