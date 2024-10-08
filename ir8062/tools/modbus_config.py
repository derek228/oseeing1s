from pymodbus.client.sync import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

# 创建 Modbus RTU 客户端
client = ModbusSerialClient(
    method='rtu',
    port='/dev/ttyUSB1',  # 设置为你的串口设备
    baudrate=9600,        # 波特率
    timeout=1             # 超时时间
)

# 连接客户端
client.connect()

# ------------------ 03 读保持寄存器 -------------------
def read_holding_registers(start_address, count, unit):
    # 读取保持寄存器 (功能码 03)
    result = client.read_holding_registers(start_address, count, unit=unit)
    if not result.isError():
        print(f"寄存器值: {result.registers}")
        return result.registers
    else:
        print(f"读取寄存器失败: {result}")
        return None

# ------------------ 06 写单个保持寄存器 -------------------
def write_single_register(address, value, unit):
    # 写单个保持寄存器 (功能码 06)
    result = client.write_register(address, value, unit=unit)
    if not result.isError():
        print(f"写入成功: 地址={address}, 值={value}")
    else:
        print(f"写入失败: {result}")

# 使用示例
slave_id = 0xac  # 从站ID

# 读保持寄存器（功能码03），从地址 0 开始读 2 个寄存器
#read_holding_registers(start_address=0x001a, count=10, unit=slave_id)
ret = read_holding_registers(start_address=0x0001, count=1, unit=slave_id)
print(f"Alarm : 0x{ret[0]:04X}")
#for reg in ret :
    #print(f"Alarm status = {reg:04X}")


# 写单个保持寄存器（功能码06），向地址 0 写入值 1234
#write_single_register(address=0x0010, value=0xb00, unit=slave_id)
#write_single_register(address=0x0012, value=0xb10, unit=slave_id)
#write_single_register(address=0x0014, value=0xb20, unit=slave_id)
#write_single_register(address=0x0016, value=0xb30, unit=slave_id)
#write_single_register(address=0x0018, value=0xb40, unit=slave_id)
#write_single_register(address=0x0019, value=0xb50, unit=slave_id)
#write_single_register(address=0x0020, value=0x00ac, unit=slave_id)

# 断开客户端
client.close()
