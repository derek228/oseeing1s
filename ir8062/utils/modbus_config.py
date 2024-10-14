from pymodbus.client.sync import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

class ModbusConfig :
    def __init__(self) :
        self.client = ModbusSerialClient(
            method='rtu',
            port=None,  # 设置为你的串口设备
            baudrate=9600,        # 波特率
            timeout=1             # 超时时间
        )
        self.id = 0xAA
        self.alarm=[0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF]
        self.max_temperature=[0,0,0,0,0,0,0,0,0,0]
        # temperature unit : 
        # 2 : Celsius 
        # 1 : Fahrenheit 
        # 0: Kelvin
        self.unit=0

    def set_serial(self, ser) :
        self.client.port = ser

    def set_id(self, id):
        self.id = id

    def set_alarm_temperature(self,val,idx):
        if 1:
            self.alarm[idx] = int(val)
            print(f"unit{self.unit} Alarm Temperature {idx}={self.alarm[idx]} K")
        else :
            temp = int(val)
            if self.unit == 0 :
                self.alarm[idx]=temp
            elif self.unit == 1:
                self.alarm[idx] = int((50*temp+22985)/9)
            elif self.unit == 2:
                self.alarm[idx] = 10*temp + 2735
            print(f"{type(val)} : unit{self.unit} Alarm Temperature {idx}={val}, {self.alarm[idx]} K")

    def get_temperature_unit_str(self, idx) :
        if self.unit == 0 :
            temp = self.alarm[idx]
        elif self.unit == 1 :
            temp = int(((self.alarm[idx]*9/5) - 4597))
        elif self.unit == 2 :
            temp = int((self.alarm[idx]-2735))
        return str(temp)
    
    def get_temperature_unit(self, idx) :
        if self.unit == 0 :
            temp = self.alarm[idx]
        elif self.unit == 1 :
            temp = (int((self.alarm[idx]*9/5) - 4597))
        elif self.unit == 2 :
            temp = ((self.alarm[idx]-2735))
        print(f"{idx} ==> {type(temp)} : {temp}")
        return (temp)
    
    def transfer_temperature_unit_to_kelvin(self, val) :
            if self.unit == 0 :
                temp=val
            elif self.unit == 1:
                temp = int((5*val+22983)/9)
            elif self.unit == 2:
                temp = val + 2735
            print(f"{type(val)} : unit{self.unit} Save Alarm Temperature ={val}, {temp} K")
            return temp

    def read_reg(self, start_address, count):
        self.client.connect()
        result = self.client.read_holding_registers(start_address, count, unit=self.id)
        self.client.close()
        if not result.isError():
            print(f"register: {result.registers}")
            return result.registers
        else:
            print(f"Read fail: {result}")
            return None

#client.connect()
    def write_reg(self, address, value):
        self.client.connect()
        #print(f"Write: {type(self.id)}ID={self.id}, {type(address)}register={address}, {type(value)}value={value}")
        result = self.client.write_register(address, value, unit=self.id)
        self.client.close()
        if not result.isError():
            print(f"Write: register={address:04X}, value={value}")
            return self.id
        else:
            print(f"Write fail: {result}")
            return None

'''
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

# Write Only register
REG_MODBUS_ID   =   0x0020

# Read only register
REG_AREA_TEMPERATURE_ALL    =   0x001A
REG_ALARM_STATUS_ALL        =   0x0001

# Read register（03）
read_holding_registers(REG_AREA_TEMPERATURE_ALL, 10, slave_id)
ret = read_holding_registers(REG_ALARM_STATUS_ALL, 1, slave_id)
print(f"Alarm : 0x{ret[0]:04X}")
ret = read_holding_registers(REG_FRAME_TEMPERATURE, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_1, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_2, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_3, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_4, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_5, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_6, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_7, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_8, 1, slave_id)
ret = read_holding_registers(REG_AREA_TEMPERATURE_9, 1, slave_id)

# Write single register（06）
#write_single_register(address=0x0010, value=0xb00, unit=slave_id)
#write_single_register(address=0x0012, value=0xb10, unit=slave_id)
#write_single_register(address=0x0014, value=0xb20, unit=slave_id)
#write_single_register(address=0x0016, value=0xb30, unit=slave_id)
#write_single_register(address=0x0018, value=0xb40, unit=slave_id)
#write_single_register(address=0x0019, value=0xb50, unit=slave_id)
#write_single_register(address=0x0020, value=0x00ac, unit=slave_id)

# 断开客户端
client.close()
'''