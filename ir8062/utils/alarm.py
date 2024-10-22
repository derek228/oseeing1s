import tkinter as tk
import serial
import serial.tools.list_ports
import struct
import threading
import modbus_config
import time
REG_AREA_TEMPERATURE_ALL    =   0x001A
REG_AREA_ALARM_ALL          =   0x001B
REG_ALARM_STATUS_ALL        =   0x0001
oseeing = None


def update_temperature(square_id, temperature):
    """
    更新對應正方形的溫度顯示
    :param square_id: 小正方形的 ID
    :param temperature: 接收到的溫度數據
    """
    if square_id == 0:
        # 更新大正方形的溫度顯示
        large_label.config(text=f"ID: 0\nTemp: {temperature}°C")
        large_frame.config(bg="yellow")  # 大正方形背景設為黃色
    elif square_id in squares:
        # 更新小正方形的溫度顯示
        color = "red"  # 這裡設定了溫度背景顏色為紅色
        squares[square_id].config(text=f"ID: {square_id}\nTemp: {temperature}°C", bg=color)

def alarm_update(id, alm, temp) :
    print(f"ID={id}, alarm={alm}, temperature={temp}")
    if id == 0 :
        if alm > 0 :
            color = "red"
        else :
            color = "yellow"
        large_label.config(text=f"ID: 0\nTemp: {temp}°C")
        large_frame.config(bg=color)  # 大正方形背景設為黃色
    else :
        if alm > 0 :
            color = "red"  # 這裡設定了溫度背景顏色為紅色
        else :
            color = "white"
        squares[id].config(text=f"ID: {id}\nTemp: {temp}°C", bg=color)

def read_modbus():
    global alarm_status
    global max_temperature
    while running :
        alarm_status = oseeing.read_reg(REG_ALARM_STATUS_ALL,1)
        max_temperature = oseeing.read_reg(REG_AREA_TEMPERATURE_ALL,10)
        print(f"Alarm statux = {alarm_status}")
        print(max_temperature)
        alarm_update(0, alarm_status[0]&0x0001, max_temperature[0])
        for i in range(1,10) :
            alarm_update(i, alarm_status[0]&(1<<(i)), max_temperature[i])
            #alarm_update(i+1, 0, max_temperature[i+1])
        time.sleep(1)


def on_tab_selected(event):
    global running
    selected_tab = event.widget.index(event.widget.select())
    if selected_tab == 1:  # 假設第二個 tab 需要啟動執行緒
        print("啟動 UART 執行緒")
        running = True
        thread = threading.Thread(target=read_modbus, daemon=True)
        thread.start()
    else:
        # 當離開第二個 tab 時，停止 UART 執行緒
        if running:
            print("停止 UART 執行緒")
            running = False

large_frame = None
large_label = None
squares = {}
alarm_root = None
running = False
alarm_status = [0]
max_temperature= [0,0,0,0,0,0,0,0,0,0]
def oseeing_alarm_start(oc, root) :
    global large_frame
    global large_label
    global squares
    global alarm_root 
    global oseeing
    alarm_root = root
    oseeing = oc
# 創建大正方形的 Frame，ID 為 0
    large_frame = tk.Frame(root, width=500, height=500, bg="yellow", borderwidth=2, relief="solid")
    large_frame.grid(row=0, column=0, padx=10, pady=10)

# 大正方形顯示 ID 0 和溫度
    large_label = tk.Label(large_frame, text="ID: 0\nTemp: N/A", font=("Arial", 16), bg="yellow")
    large_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

# 儲存所有小正方形 Label
    #squares = {}

# 創建九個小正方形，排列在大正方形內
    for row in range(3):
        for col in range(3):
            small_frame = tk.Frame(large_frame, width=100, height=100, bg="white", borderwidth=1, relief="solid")
            small_frame.grid(row=row + 1, column=col, padx=5, pady=5)
        
            square_id = row * 3 + col + 1  # 小正方形 ID 從 1 開始
            label = tk.Label(small_frame, text=f"ID: {square_id}\nTemp: N/A", font=("Arial", 12), bg="white")
            label.pack(expand=True)
        
            squares[square_id] = label
# 開啟獨立執行緒來讀取 UART 數據
    thread = threading.Thread(target=read_modbus, daemon=True)
    thread.start()

# 每隔一秒發送一次命令
    #root.after(1000, send_command)

# 開始 Tkinter 主循環
