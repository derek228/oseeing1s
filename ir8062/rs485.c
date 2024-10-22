/*
 * Copyright (c) 2014 Nuvoton technology corporation
 * All rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 */
 
#include     <stdio.h>
#include     <stdlib.h>
#include	<stdint.h>
#include     <unistd.h> 
#include     <sys/types.h>
#include     <sys/stat.h> 
#include     <fcntl.h> 
#include     <termios.h>  
#include     <errno.h>
#include     <string.h>
#include 	<signal.h>
#include    <pthread.h>
#include <linux/serial.h>
#include "ini-parse.h"
#include "rs485.h"
#include "mi48.h"
#include "utils.h"

/* Driver-specific ioctls: ...\linux-3.10.x\include\uapi\asm-generic\ioctls.h */
#define TIOCGRS485      0x542E
#define TIOCSRS485      0x542F
//#define DEBUG_RS485
oseeing_config_t oseeing_config={0};
unsigned char server_cmd=0;
pthread_t uart_tid;
int serial_port;
static unsigned char rs485_id = 0xAA;
static char buffer[BUFFER_SIZE];
static char rx[BUFFER_SIZE];
const unsigned char RESET_DEVICE_ID[6]={0xAA,0xFF,0x5A,0xA5,0x03,0x24};

struct my_serial_rs485
{
	unsigned long	flags;			/* RS485 feature flags */
#define SER_RS485_ENABLED		(1 << 0)	/* If enabled */
#define SER_RS485_RTS_ON_SEND		(1 << 1)	/* Logical level for
							   RTS pin when
							   sending */
#define SER_RS485_RTS_AFTER_SEND	(1 << 2)	/* Logical level for
							   RTS pin after sent*/
#define SER_RS485_RX_DURING_TX		(1 << 4)
	unsigned long	delay_rts_before_send;	/* Delay before send (milliseconds) */
	unsigned long	delay_rts_after_send;	/* Delay after send (milliseconds) */
	unsigned long	padding[5];		/* Memory is cheap, new structs
					   are a royal PITA .. */
};

static struct termios newtios,oldtios; /*termianal settings */
static int saved_portfd=-1;            /*serial port fd */



static void reset_tty_atexit(void)
{
	if(saved_portfd != -1)
	{
		tcsetattr(saved_portfd,TCSANOW,&oldtios);
	} 
}

/*cheanup signal handler */
static void reset_tty_handler(int signal)
{
	if(saved_portfd != -1)
	{
		tcsetattr(saved_portfd,TCSANOW,&oldtios);
	}
	_exit(EXIT_FAILURE);
	//printf("ERROR (%s): Feiled...\n",__FUNCTION__);
}

static int open_port(const char *portname)
{
	struct sigaction sa;
	int portfd;
#if (__GNUC__ == 4 && __GNUC_MINOR__ == 3)
	struct my_serial_rs485 rs485conf;
	struct my_serial_rs485 rs485conf_bak;
#else
	struct serial_rs485 rs485conf;
	struct serial_rs485 rs485conf_bak;
#endif	
	//printf("opening serial port:%s\n",portname);
	/*open serial port */
	//if ((portfd=open(portname, O_RDWR | O_NOCTTY | O_NONBLOCK)) < 0) // 以读写方式打开串口设备
	if((portfd=open(portname,O_RDWR | O_NOCTTY, 0)) < 0 )
	{
   		printf("open serial port %s fail \n ",portname);
   		return portfd;
	}

	printf("opening serial port:%s\n",portname);

	/*get serial port parnms,save away */
	tcgetattr(portfd,&newtios);
	memcpy(&oldtios,&newtios,sizeof newtios);
	/* configure new values */
	cfmakeraw(&newtios); /*see man page */
	newtios.c_iflag |=IGNPAR; /*ignore parity on input */
	newtios.c_oflag &= ~(OPOST | ONLCR | OLCUC | OCRNL | ONOCR | ONLRET | OFILL); 
	newtios.c_cflag = CS8 | CLOCAL | CREAD;
	//newtios.c_cc[VMIN]=1; /* block until 1 char received */
	newtios.c_cc[VMIN]=0; /* block until 1 char received */
	newtios.c_cc[VTIME]=0; /*no inter-character timer */
	/* 115200 bps */
	cfsetospeed(&newtios,RS485_DEFAULT_BAUDRATE);
	cfsetispeed(&newtios,RS485_DEFAULT_BAUDRATE);
	/* register cleanup stuff */
	atexit(reset_tty_atexit);
	memset(&sa,0,sizeof sa);
	sa.sa_handler = reset_tty_handler;
	sigaction(SIGHUP,&sa,NULL);
	sigaction(SIGINT,&sa,NULL);
	sigaction(SIGPIPE,&sa,NULL);
	sigaction(SIGTERM,&sa,NULL);
	/*apply modified termios */
	saved_portfd=portfd;
	tcflush(portfd,TCIFLUSH);
	tcsetattr(portfd,TCSADRAIN,&newtios);
	
		
	if (ioctl (portfd, TIOCGRS485, &rs485conf) < 0) 
	{
		/* Error handling.*/ 
		printf("ioctl TIOCGRS485 error.\n");
	}
	/* Enable RS485 mode: */
	rs485conf.flags |= SER_RS485_ENABLED;

	/* Set logical level for RTS pin equal to 1 when sending: */
	rs485conf.flags |= SER_RS485_RTS_ON_SEND;
	//rs485conf.flags |= SER_RS485_RTS_AFTER_SEND;

	/* set logical level for RTS pin equal to 0 after sending: */ 
	rs485conf.flags &= ~(SER_RS485_RTS_AFTER_SEND);
	//rs485conf.flags &= ~(SER_RS485_RTS_ON_SEND);

	/* Set rts delay after send, if needed: */
	rs485conf.delay_rts_after_send = 0x80;

	if (ioctl (portfd, TIOCSRS485, &rs485conf) < 0)
	{
		/* Error handling.*/ 
		printf("ioctl TIOCSRS485 error.\n");
	}

	if (ioctl (portfd, TIOCGRS485, &rs485conf_bak) < 0)
	{
		/* Error handling.*/ 
		printf("ioctl TIOCGRS485 error.\n");
	}
	else
	{
		printf("rs485conf_bak.flags 0x%x.\n", rs485conf_bak.flags);
		printf("rs485conf_bak.delay_rts_before_send 0x%x.\n", rs485conf_bak.delay_rts_before_send);
		printf("rs485conf_bak.delay_rts_after_send 0x%x.\n", rs485conf_bak.delay_rts_after_send);
	}

	return portfd;
}

static void sendcmd(char *tx, size_t size) {
	#ifdef DEBUG_RS485
	int i;
	printf("Send data:\n");
	for (i=0;i<size;i++)
		printf("0x%x, ", tx[i]);
	#endif
	write(serial_port, tx, size);
}

static ssize_t readdev(char *rx) {
	ssize_t rx_size=0;
	memset(rx,0,BUFFER_SIZE);
	rx_size = read(serial_port, rx, BUFFER_SIZE);
	return rx_size; // read(serial_port,rx,size); // return read length
}

static void echo_rx_data(char *rx, ssize_t len) {
	memset(buffer, 0 , BUFFER_SIZE);
	memcpy(buffer, rx, len);
	//printf("Echo RX Data len = %d\n",len);
	write(serial_port,buffer,len);
}

int serial_init() {
	serial_port = open_port(RS485_DEV);
	if (serial_port < 0) {
		printf("Can't open RS485 dev of %s\n", RS485_DEV);
	}
	return serial_port;
}
void oseeing_alarm_default() {
	int i;
	for (i=0;i<10;i++) {
		oseeing_config.alarm_temperature[i]=0xFFFF;
	}
}

void oseeing_config_init() {
	int i;
	if (file_exist(FILE_RS485_CUSTOM_ID) < 0) {
		oseeing_config.id = RS485_DEFAULT_ID;
		printf("No custom ID defile, use default id 0xAA\n");
	}
	else {
		if (read_char_from_file(FILE_RS485_CUSTOM_ID,&oseeing_config.id) < 0) {
			printf("ERROR (%s) : Can't read RS485 ID, use default id 0xAA\n");
			oseeing_config.id = RS485_DEFAULT_ID;
		}
		printf("Oseeing RS485 ID = 0x%x\n", oseeing_config.id);
	}
	if (file_exist(FILE_ALARM_TEMPERATURE) < 0) {
		printf("Empty Alarm temperature setting. disable all alarm\n");
		oseeing_alarm_default();
	}
	else {
		if ( (read_shortint_from_file(FILE_ALARM_TEMPERATURE, oseeing_config.alarm_temperature)) < 0) {
			printf("ERROR (%s) : Can't read Alarm temperature config, Disable all\n");
			oseeing_alarm_default();
		}
#ifdef DEBUG_RS485		
		else {
			printf("===== Alarm Setting =====\n");
			for (i=0; i<10; i++) {
				printf("%d , ", oseeing_config.alarm_temperature[i]);
			}
		}
#endif		
	}
	if (file_exist(FILE_TEMPERATURE_UNIT) < 0) {
		oseeing_config.unit = DEFAULT_TEMPERATURE_UNIT;
		printf("No temperature unit file, use default unit(K)\n");
	}
	else {
		if (read_char_from_file(FILE_TEMPERATURE_UNIT,&oseeing_config.unit) < 0) {
			printf("ERROR (%s) : Can't read temperature unit, use default unit(K)\n");
			oseeing_config.unit = DEFAULT_TEMPERATURE_UNIT;
		}
		printf("Oseeing temperature unit = %d\n", oseeing_config.unit);
	}
}

static int set_rs485_id_config(unsigned char *id) {
	oseeing_config.id = *id;
	return write_char_to_file(FILE_RS485_CUSTOM_ID, id,1);
}
static int set_temperature_unit_config(unsigned char *unit) {
	oseeing_config.unit = *unit;
	printf("%s : UNIT = %d\n", __FUNCTION__, oseeing_config.unit);
	return write_char_to_file(FILE_TEMPERATURE_UNIT, unit,1);
}
char unit_str[3]={'K','F','C'};

static int set_alarm_area_config(int idx, short int temp) {
	read_alarm_temperature();
	switch (oseeing_config.unit) {
		case 1 : // F2K
			oseeing_config.alarm_temperature[idx] = F2K(temp);
		break;
		case 2 : // C2K
			oseeing_config.alarm_temperature[idx] = C2K(temp);
		break;
		default: // K
			oseeing_config.alarm_temperature[idx]=temp;
		break;
	}
	printf("Set Alarm[%d] is %d(%c)=%d(K)\n",idx,temp,unit_str[oseeing_config.unit],oseeing_config.alarm_temperature[idx]);
	return write_shortint_to_file(FILE_ALARM_TEMPERATURE, &oseeing_config.alarm_temperature[0], 10);
}

static int oseeing_tool_config_check(char *rx, ssize_t len) {
	if ((rx[0]==0xF1) && (rx[1]==0xF1)) {
		if ((rx[2]==0x01) && (rx[3]==0x01)) { // reset RS485 ID
			if (file_exist(FILE_RS485_CUSTOM_ID)<0) {
				printf("No RS485 custom ID defined\n");
			}
			else if (remove(FILE_RS485_CUSTOM_ID) == 0) {
				printf("Reset RS485 custom ID(0x%x) as 0x%x\n", oseeing_config.id,RS485_DEFAULT_ID);
				oseeing_config.id = RS485_DEFAULT_ID;
			}
		}
		else if ((rx[2]==0x02) && (rx[3]==0x02)) { // Set Stream transfer enable/disable
			printf("Set Socket connect %d\n", rx[4]);
			write_char_to_file(FILE_SERVER_CONNECTION,&rx[4],1);
		}
		else if ((rx[2] == 0x03) && (rx[3]==0x03)) { // Set server ip address
			printf("Set Socket server IP(%d) = %s\n",rx[4], &rx[5]);
			write_char_to_file(FILE_SERVER_IP,&rx[5],rx[4]);
		}
		else 
			printf("Unknow command 0x%x\n", rx[2]);

		echo_rx_data(rx,len);
		return 1;
	}
	return 0;
}
static uint16_t temperature_unit_conversion(uint16_t t) {
	uint16_t ret = t;
	if (t==0xFFFF) {
		printf("Alarm disable");
	}
	else if (oseeing_config.unit == 1) {
		ret = K2F(t) ; 
	}
	else if (oseeing_config.unit == 2) {
		ret = K2C(t);
	}
	printf("Temperature unit conversion(%d) = %d\n", oseeing_config.unit, ret);
	return ret;
}
static int read_modbus_regs(char *rx, ssize_t len) {
	uint16_t reg = (rx[2]<<8) | rx[3];
	uint16_t readlen = (rx[4] << 8) | rx[5];
	uint16_t regdata=0, crc, sendlen;
	char sendbuf[32]={0};
	char *data;
	int i;
#ifdef DEBUG_RS485	
	for (i=0; i<len; i++)
		printf("0x%x, ",rx[i]);
#endif	
	temperature_t *temp=temperature_analysis();
	printf("\nRead Reg(0x%x), len=%d\n", reg, readlen);
	sendbuf[0]=rx[0];
	sendbuf[1]=rx[1];
	sendbuf[2]=readlen*2;
	data = &sendbuf[3];

	switch (reg) {
		case REG_TEMPERATURE_UNIT:
			printf("Get Unit = %d\n", oseeing_config.unit);
			data[0] = (oseeing_config.unit & 0xff00) >> 8;
			data[1] = oseeing_config.unit & 0xff;
			printf("Get temperature unit = 0x%x, 0x%x\n",data[0],data[1]);
		break;
		case REG_AREA_TEMPERATURE_ALL: 
			printf("Get Temperature all(Unit = %d)\n", oseeing_config.unit);
			for (i=0; i<10; i++) {
				#if 1 
				regdata = temperature_unit_conversion(temp[i].max);
				data[i*2] = (regdata & 0xff00) >> 8;
				data[i*2+1] = regdata & 0xff;
				#else
				data[i*2] = (temp[i].max&0xff00) >> 8;
				data[i*2+1] = temp[i].max&0xff;
				printf("send temperature data[%d]=0x%x, 0x%x\n",i, data[i*2],data[i*2+1]);
				#endif
			}
			//printf("Get All area temperature\n");
		break;
		case REG_AREA_ALARM_ALL:
			for (i=0; i<10; i++) {
				#if 1 
				regdata = temperature_unit_conversion(oseeing_config.alarm_temperature[i]);
				data[i*2] = (regdata & 0xff00) >> 8;
				data[i*2+1] = regdata & 0xff;
				printf("send alarm data[%d]=%d\n",i, regdata);
				#else
				data[i*2] = (oseeing_config.alarm_temperature[i] & 0xff00) >> 8;
				data[i*2+1] = oseeing_config.alarm_temperature[i] & 0xff;
				printf("send alarm data[%d]=0x%x, 0x%x\n",i, data[i*2],data[i*2+1]);
				#endif
			}
		case REG_FRAME_TEMPERATURE:
			#if 1 
			regdata = temperature_unit_conversion(temp[0].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[0] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[0] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[0] & 0xff;
			printf("Get temperature[0] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_1:
			#if 1 
			regdata = temperature_unit_conversion(temp[1].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[1] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[1] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[1] & 0xff;
			printf("Get temperature[1] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_2:
			#if 1 
			regdata = temperature_unit_conversion(temp[2].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[2] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[2] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[2] & 0xff;
			printf("Get temperature[2] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_3:
			#if 1 
			regdata = temperature_unit_conversion(temp[3].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[3] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[3] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[3] & 0xff;
			printf("Get temperature[3] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_4:
			#if 1 
			regdata = temperature_unit_conversion(temp[4].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[4] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[4] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[4] & 0xff;
			printf("Get temperature[4] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_5:
			#if 1 
			regdata = temperature_unit_conversion(temp[5].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[5] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[5] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[5] & 0xff;
			printf("Get temperature[5] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_6:
			#if 1 
			regdata = temperature_unit_conversion(temp[6].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[6] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[6] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[6] & 0xff;
			printf("Get temperature[6] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_7:
			#if 1 
			regdata = temperature_unit_conversion(temp[7].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[7] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[7] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[7] & 0xff;
			printf("Get temperature[7] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_8:
			#if 1 
			regdata = temperature_unit_conversion(temp[8].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[8] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[8] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[8] & 0xff;
			printf("Get temperature[8] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;
		case REG_AREA_TEMPERATURE_9:
			#if 1 
			regdata = temperature_unit_conversion(temp[9].max);
			data[0] = (regdata & 0xff00) >> 8;
			data[1] = regdata & 0xff;
			printf("Get temperature[9] max = %d\n",regdata);
			#else
			data[0] = (oseeing_config.alarm_temperature[9] & 0xff00) >> 8;
			data[1] = oseeing_config.alarm_temperature[9] & 0xff;
			printf("Get temperature[9] max = 0x%x, 0x%x\n",data[0],data[1]);
			#endif
		break;	
		case REG_ALARM_STATUS_ALL :
			regdata=get_temperature_alarm();
			data[0] = (regdata&0xff00) >> 8;
			data[1] = regdata&0xff;
			printf("Get All area temperature 0x%x\n", regdata);
		break;
		default:
		// Error code, {ID}{fun|0x80}{Error code}{CRC}
			printf("Read register ERROR : UNKNOW Register value 0x%x\n", reg);
			sendbuf[1] |= 0x80;
			sendbuf[2] = 0x02; // Illegal Address
			// snedbuf[3..4]=CRC
			calculate_modbus_crc(sendbuf, 3 );
			sendcmd(sendbuf, 5);
			return;
		break;
	}
	sendlen = sendbuf[2]+3;
	crc = calculate_modbus_crc(sendbuf, sendbuf[2]+3 );
	sendbuf[sendlen] = crc&0xff;
	sendbuf[sendlen+1] = (crc&0xff00) >> 8;
	sendcmd(sendbuf, sendbuf[2]+3+2); // data + header(2bytes)+CRC(2bytes)
}

// {ID} {function} {reg (2bytes)} {data (2bytes)} {CRC}
// return : {ID} {function} {data} {CRC}
static int write_modbus_regs(char *rx, ssize_t len){
	uint16_t reg = (rx[2]<<8) | rx[3];
	uint16_t writedata = (rx[4] << 8) | rx[5];;
	char sendbuf[16] = {0};
	switch (reg) {
		case REG_FRAME_TEMPERATURE:
			set_alarm_area_config(0, writedata);
			//printf("Set alarm[0] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[0], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_1:
			set_alarm_area_config(1, writedata);
			//printf("Set alarm[1] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[1], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_2:
			set_alarm_area_config(2, writedata);
			//printf("Set alarm[2] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[2], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_3:
			set_alarm_area_config(3, writedata);
			//printf("Set alarm[3] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[3], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_4:
			set_alarm_area_config(4, writedata);
			//printf("Set alarm[4] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[4], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_5:
			set_alarm_area_config(5, writedata);
			//printf("Set alarm[5] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[5], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_6:
			set_alarm_area_config(6, writedata);
			//printf("Set alarm[6] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[6], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_7:
			set_alarm_area_config(7, writedata);
			//printf("Set alarm[7] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[7], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_8:
			set_alarm_area_config(8, writedata);
			//printf("Set alarm[8] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[8], writedata, unit_str[oseeing_config.unit]);
		break;
		case REG_AREA_TEMPERATURE_9:
			set_alarm_area_config(9, writedata);
			//printf("Set alarm[9] = %d(K), %d(%c), \n",oseeing_config.alarm_temperature[9], writedata, unit_str[oseeing_config.unit]);
		break;	
		case REG_MODBUS_ID:
			set_rs485_id_config(&rx[5]);
			printf("Set Modbus ID = 0x%x\n", oseeing_config.id);
		break;
		case REG_TEMPERATURE_UNIT:
			set_temperature_unit_config(&rx[5]);
			printf("Set Temperature Unit = 0x%x\n", oseeing_config.unit);
		break;
		default:
		// Error code, {ID}{fun|0x80}{Error code}{CRC}
			printf("Write register ERROR : UNKNOW Register value 0x%x\n", reg);
			sendbuf[0] = rx[0];
			sendbuf[1] = rx[1] | 0x80;
			sendbuf[2] = 0x02; // Illegal Address
			// snedbuf[3..4]=CRC
			calculate_modbus_crc(sendbuf, 3 );
			sendcmd(sendbuf, 5);
			return -1;
		break;
	}
	//read_alarm_temperature();
	return 1;
}
static int rx_data_parse(char *rx, ssize_t len) {
	int ret = 0;
	/*
	unsigned char *data;
	unsigned char id = rx[0];
	unsigned char fun = rx[1];
	short int reg = (rx[2]<<8) | rx[3];
	unsigned char cmdlen;
	*/
	char *data, id, fun;
	//uint16_t reg;
	if (check_modbus_crc(rx, len)==0) { 
		printf("ERROR : CRC ERROR \n");
		return -1;
	}
	id = rx[0];
	fun = rx[1];
	if (id != oseeing_config.id) {
		printf("ID not match %d:%d\n", id, oseeing_config.id);
		return -1;
	}
	if (fun == 0x03) // read reg
		read_modbus_regs(rx, len);
	else if (fun == 0x06) { // write reg
		if (write_modbus_regs(rx,len) > 0)
			echo_rx_data(rx,len);
	}
	else
		printf("ERROR : Unknow Modbus function code 0x%x\n", fun);
	return ret;
}


// export function
int read_alarm_temperature() {
	int ret = 0, i;
	if (file_exist(FILE_ALARM_TEMPERATURE) < 0)
		return -1;
	ret = read_shortint_from_file(FILE_ALARM_TEMPERATURE, oseeing_config.alarm_temperature);
#ifdef DEBUG_RS485	
	for (i=0; i<10; i++) 
		printf("area[%d] = 0x%x\n",i, oseeing_config.alarm_temperature[i]);
#endif	
	return ret; 
}

uint16_t get_alarm_temperature(int idx) {
	return oseeing_config.alarm_temperature[idx];
}

unsigned char get_server_command() {
	unsigned char ret = server_cmd;
	server_cmd = 0;
	return ret;
}
int send_sensor_info(unsigned char *data, int len, unsigned char cmd) {
	int i;
	if (len <=0 ) {
		printf("Not assisgned return data\n");
		return -1;
	}
	
	memset(buffer, 0 , BUFFER_SIZE);
	buffer[0]=rs485_id;
	buffer[1]=cmd;
	buffer[2]=len;
	if (len != 0) {
		memcpy(&buffer[3], data, len);
	}
	write(serial_port,buffer,len+3);
#ifdef DEBUG_RS485	
	printf("Send info(%d) = ", len+3);
	for (i=0 ; i<len+3; i++) 
		printf("0x%x ", buffer[i]);
	printf("\n");
#endif	
	return 0;
}

// end export function
void *uart_thread(void *arg) {
	ssize_t rx_size = 0;
	int i;
    while (1) {

		rx_size=readdev(rx);
		if (oseeing_tool_config_check(rx, rx_size))
			continue;
		if (rx_size > 6)
			rx_data_parse(rx,rx_size);
    }
    close(serial_port);
	printf("EXIT uart\n");

    return;
}
void uart_thread_destory() {
    pthread_cancel(uart_tid);
    pthread_join(uart_tid, NULL);  
}	
int uart_thread_create() {
    if (pthread_create(&uart_tid, NULL, uart_thread, NULL) != 0) {
        perror("uart pthread_create");
        return -1;
    }
    return 0;
}
int rs485_init() {
	serial_init();
	uart_thread_create();
}
