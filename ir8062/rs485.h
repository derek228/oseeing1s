#ifndef __RS485__
#define __RS485__

#define TX_BUFFER	128
#define RX_BUFFER	128
#define RS485_DEV "/dev/ttyS8" // rs485 port
//#define RS485_DEV "/dev/ttyS4" // uart port
#define RS485_DEFAULT_BAUDRATE 9600
#define BUFFER_SIZE	32
#define RS485_DEFAULT_ID	0xAA
#define DEFAULT_TEMPERATURE_UNIT	0 // 0: K, 1:F, 2:C
typedef struct {
	int dev;
	unsigned int baudrate;
	char tx_buf[TX_BUFFER];
	char rx_buf[RX_BUFFER];
} rs485_t;

// Configuration Files
#define FILE_ALARM_TEMPERATURE  "/mnt/mtdblock1/oseeing1s-config/alarm_temperature"
#define FILE_RS485_CUSTOM_ID    "/mnt/mtdblock1/oseeing1s-config/id" 
#define FILE_SERVER_IP          "/ip" 
#define FILE_SERVER_CONNECTION  "/connect" 
#define FILE_TEMPERATURE_UNIT	"/mnt/mtdblock1/oseeing1s-config/unit"

// Modbus R/W Register List , 0x03, 0x06
// Write : Set Alarm Temperature
// Read : Get Max temperature
#define REG_FRAME_TEMPERATURE	0x0010
#define REG_AREA_TEMPERATURE_1	0x0011
#define REG_AREA_TEMPERATURE_2	0x0012
#define REG_AREA_TEMPERATURE_3	0x0013
#define REG_AREA_TEMPERATURE_4	0x0014
#define REG_AREA_TEMPERATURE_5	0x0015
#define REG_AREA_TEMPERATURE_6	0x0016
#define REG_AREA_TEMPERATURE_7	0x0017
#define REG_AREA_TEMPERATURE_8	0x0018
#define REG_AREA_TEMPERATURE_9	0x0019
#define REG_MODBUS_ID			0x0020
#define REG_TEMPERATURE_UNIT	0x0002


// Modbus Read only Register List , 0x03
#define REG_AREA_TEMPERATURE_ALL	0x001A
#define REG_AREA_ALARM_ALL          0x001B
#define REG_ALARM_STATUS_ALL		0x0001

// Vendor command list , {id}{CMD_}{Data Length}{Data}
#define CMD_SET_SERVER_IP		0x02 // 0x50 // set server ip
#define CMD_SET_STREAM_TRANSFER_STATUS	0x03 // 0x51 // 0 : stop transfer, 1: Start transfer


typedef struct {
    unsigned char id;
	unsigned char unit;
	char ipaddr[17];
    uint16_t alarm_temperature[10];
}oseeing_config_t;

void update_oseeing_config();
//int get_alarm_temperature();
uint16_t get_alarm_temperature(int idx);

//void get_oseeing_config();

#endif // RS485_H