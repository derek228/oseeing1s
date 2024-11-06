#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <signal.h>
#include <getopt.h>
#include <linux/types.h>
#include <time.h>
#include <arpa/inet.h>
#include "spidev.h"
#include "ini-parse.h"
#include "mi48.h"
#include "rs485.h"
#include "socket_stream.h"
#include "mi48-i2c.h"
#define NEW_THERMAL_SCAN 1


#define FILE_RS485_CUSTOM_ID	"/mnt/mtdblock1/oseeing1s-config/id" 
// socket server ip
#define FILE_SERVER_IP	"/ip" 
// set 1, start connect to socket server
#define FILE_SERVER_CONNECTION	"/connect" 
// bit 7 = 0 , full frame mode, =1 9 square mode,
// bit 6:0 , full frame alarm temperature
#define FILE_DEVICE_MODE	"/mnt/mtdblock1/oseeing1s-config/mode" 
// bit 7 = 1, enable alarm, bit 6:0 , alarm temperature
#define FILE_SQUARE1_ALARM	"/mnt/mtdblock1/oseeing1s-config/square1"
#define FILE_SQUARE2_ALARM	"/mnt/mtdblock1/oseeing1s-config/square2"
#define FILE_SQUARE3_ALARM	"/mnt/mtdblock1/oseeing1s-config/square3"
#define FILE_SQUARE4_ALARM	"/mnt/mtdblock1/oseeing1s-config/square4"
#define FILE_SQUARE5_ALARM	"/mnt/mtdblock1/oseeing1s-config/square5"
#define FILE_SQUARE6_ALARM	"/mnt/mtdblock1/oseeing1s-config/square6"
#define FILE_SQUARE7_ALARM	"/mnt/mtdblock1/oseeing1s-config/square7"
#define FILE_SQUARE8_ALARM	"/mnt/mtdblock1/oseeing1s-config/square8"
#define FILE_SQUARE9_ALARM	"/mnt/mtdblock1/oseeing1s-config/square9"

//int sockfd=-1;



// Thermal sensor hardware signal setting
#define CAP_SIG_ID          0x0a 
#define CMD_SIG_TASK_REG    _IOW(CAP_SIG_ID, 0, int32_t*)
#define CAP_MAX_LINE                32
#define CAP_INFO_LEN_UNIT_BYTE      12
#define CAP_MAX_LEN                 (CAP_MAX_LINE * CAP_INFO_LEN_UNIT_BYTE)
#define GPIO_INFO_SIZE_INT          3
#define CAP_MAX_LEN_INT             (CAP_MAX_LEN/4)
//gpio
int state_change = 0;
// SPI interface config
static const char *device = "/dev/spidev1.0";
//static const char *device = "/dev/spidev0.1";
//static const char *device = "/dev/spidev1.1";
static uint32_t mode=0;
static uint8_t bits = 8;
static uint32_t speed = 4000000; //500000    4000000
static uint16_t delay=0;
static int fd_spi;
static int fd_capture;
static uint8_t *tx;
static uint8_t *rx;
static int size;
static uint8_t mi48_data[9920]={0};
static unsigned short temp_kelvin[62][80]={0};
//static uint8_t data[9920]={0};

temperature_t temperature[10] = {0};
uint16_t temperature_alarm=0;
coordinate_t area[9]= { { 1, 1,26,20},
						{27, 1,52,20},
						{53, 1,78,20},
						{ 1,21,26,40},
						{27,21,52,40},
						{53,21,78,40},
						{ 1,41,26,60},
						{27,41,52,60},
						{53,41,78,60}
};

//static char mi48_header_raw[160]={0};
static mi48_header_t mi48_header;
static int mi48_debug=0;
static void mi48_log_print() {
	const char *filename = "/mnt/mtdblock1/mi48";
	if (access(filename, F_OK) != -1) {
		mi48_debug=1;
	} else {
		mi48_debug=0;
    }
}

void sig_event_handler(int sig_id, siginfo_t *sig_info, void *unused)
{
	if ( sig_id == CAP_SIG_ID ) {
		state_change = 1;
	}
}


#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
static void pabort(const char *s)
{
	perror(s);
	abort();
}

static void transfer(int fd, uint8_t const *tx, uint8_t const *rx, size_t len)
{
	int i;
	int ret;
	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)rx,
		.len = len,
		.delay_usecs = delay,
		.speed_hz = speed,
		.bits_per_word = bits,
	};
	if (mode & SPI_TX_QUAD)
		tr.tx_nbits = 4;
	else if (mode & SPI_TX_DUAL)
		tr.tx_nbits = 2;
	if (mode & SPI_RX_QUAD)
		tr.rx_nbits = 4;
	else if (mode & SPI_RX_DUAL)
		tr.rx_nbits = 2;
	if (!(mode & SPI_LOOP)) {
		if (mode & (SPI_TX_QUAD | SPI_TX_DUAL))
			tr.rx_buf = 0;
		else if (mode & (SPI_RX_QUAD | SPI_RX_DUAL))
			tr.tx_buf = 0;
	}

	ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
}

static int memory_print() {
    unsigned long long free_memory;
    FILE *fp = fopen("/proc/meminfo", "r");
    if(fp == NULL) {
        printf("Error: Failed to open /proc/meminfo\n");
        return 1;
    }
    char line[128];
    while(fgets(line, sizeof(line), fp)) {
        if(sscanf(line, "MemFree: %llu kB", &free_memory) == 1) {
            free_memory *= 1024;
            break;
        }
    }
    fclose(fp);
    logd(mi48_debug,"Free memory: %llu bytes\n", free_memory);
    return 0;
}

static int ir8062_hwinit()
{
	//SPI
	int ret = 0;
	// GPIO
	struct sigaction act;
	int i;

	sigemptyset(&act.sa_mask);
	act.sa_flags = (SA_SIGINFO | SA_RESTART);
	act.sa_sigaction = sig_event_handler;
	sigaction(CAP_SIG_ID, &act, NULL);

	printf("signal handler= %d, spi device=%s\n", CAP_SIG_ID,device);

	fd_capture = open("/dev/gpio_cap", O_RDWR);
	if(fd_capture < 0) {
		printf("Open device fail\n");
		return -1;
	}

	fd_spi = open(device, O_RDWR);
	if (fd_spi < 0)
		pabort("can't open device");
	/*
	 * spi mode
	 */
	ret = ioctl(fd_spi, SPI_IOC_WR_MODE, &mode);
	if (ret == -1)
		pabort("can't set spi mode");
	ret = ioctl(fd_spi, SPI_IOC_RD_MODE, &mode);
	if (ret == -1)
		pabort("can't get spi mode");
	/*
	 * bits per word
	 */
	ret = ioctl(fd_spi, SPI_IOC_WR_BITS_PER_WORD, &bits);
	if (ret == -1)
		pabort("can't set bits per word");
	ret = ioctl(fd_spi, SPI_IOC_RD_BITS_PER_WORD, &bits);
	if (ret == -1)
		pabort("can't get bits per word");
	/*
	 * max speed hz
	 */
	ret = ioctl(fd_spi, SPI_IOC_WR_MAX_SPEED_HZ, &speed);
	if (ret == -1)
		pabort("can't set max speed hz");
	ret = ioctl(fd_spi, SPI_IOC_RD_MAX_SPEED_HZ, &speed);
	if (ret == -1)
		pabort("can't get max speed hz");
	
	printf("spi mode: 0x%x\n", mode);
	printf("bits per word: %d\n", bits);
	printf("max speed: %d Hz (%d KHz)\n", speed, speed/1000);

	size = 160;
	tx = malloc(size);
	rx = malloc(size);
	for (i=0; i<size; i++)
	{
		tx[i] = 0;//i;
		//printf("%x ", tx[i] );
	}
	#if 1
	if (mi48_i2c_init()<0)
		printf("ERROR: Can't open i2c-1 device\n");

	mi48_i2c_write(0, 1);
	usleep(100000);
	mi48_i2c_write(0xb4, 0x03);
	mi48_i2c_write(0xd0, 0x02);
	mi48_i2c_write(0xd0, 0x03);
	mi48_i2c_write(0xb1, 0x03);
	unsigned char val=0;
	mi48_i2c_read(0xb2, &val);
	printf("reg(0x%x)=0x%x\n", 0xb2, val);
	mi48_i2c_read(0xb3, &val);
	printf("reg(0x%x)=0x%x\n", 0xb3, val);
	mi48_i2c_read(0xe0, &val);
	printf("reg(0x%x)=0x%x\n", 0xe0, val);
	mi48_i2c_read(0xe1, &val);
	printf("reg(0x%x)=0x%x\n", 0xe1, val);
	mi48_i2c_read(0xe2, &val);
	printf("reg(0x%x)=0x%x\n", 0xe2, val);
	mi48_i2c_read(0xe3, &val);
	printf("reg(0x%x)=0x%x\n", 0xe3, val);
	mi48_i2c_read(0xe4, &val);
	printf("reg(0x%x)=0x%x\n", 0xe4, val);
	mi48_i2c_read(0xe5, &val);
	printf("reg(0x%x)=0x%x\n", 0xe5, val);
	#else
	printf("Reset MI48 \n");
	system("./i2cset -f -y 1 0x40 0 1");
	printf("MI48 reset done\n");
	system("./i2cset -f -y 1 0x40 0xB4 0x03");
	system("./i2cset -f -y 1 0x40 0xD0 0x02");
	system("./i2cset -f -y 1 0x40 0xD0 0x03");

	system("./i2cset -f -y 1 0x40 0xB1 0x03");
	system("./i2cget -f -y 1 0x40 0xB2");
	system("./i2cget -f -y 1 0x40 0xB3");
	system("./i2cget -f -y 1 0x40 0xE0");
	system("./i2cget -f -y 1 0x40 0xE1");
	system("./i2cget -f -y 1 0x40 0xE2");
	system("./i2cget -f -y 1 0x40 0xE3");
	system("./i2cget -f -y 1 0x40 0xE4");
	system("./i2cget -f -y 1 0x40 0xE5");
	#endif
	return ret;
}

static void mi48_header_parse(uint8_t *mi48_header_raw) 
{
	mi48_header.frame_cnt = (mi48_header_raw[0]<<8) | mi48_header_raw[1];
	mi48_header.max = (mi48_header_raw[10]<<8) | mi48_header_raw[11];
	mi48_header.min = (mi48_header_raw[12]<<8) | mi48_header_raw[13];
	logd(mi48_debug,"frame count = %d, max=%d, min=%d\n",mi48_header.frame_cnt,mi48_header.max,mi48_header.min);
/*
	switch (index) {
		case 0: // Frame count
		case 1:
			logd(sensor_debug,"Frame counter : %02X",buf[index]);
			logd(sensor_debug,"%02X\n",buf[index]);
			break;
		case 2:
		case 3:
			logd(sensor_debug,"SenXor VDD : %02X",buf[index]);
			logd(sensor_debug,"%02X\n",buf[index]);
			break;
		case 4:
		case 5:
			logd(sensor_debug,"Die Temperature : %02X",buf[index]);
			logd(sensor_debug,"%02X\n",buf[index]);
			break;
		default :
			break;
	}
*/
}
/*
int oseeing_config_update() {
	unsigned char data, alarm, temp,i;
	for (i=0;i<10;i++) {
		data = get_square_alarm(i);
		if (data < 0) {
			printf("Can't get square(%x) data=%x\n", i,data);
			data = 0;
		}
		oseeing_config[i].alarm = ( data & 0x80 ) >> 7;
		oseeing_config[i].temperature = data & 0x7f ;
		printf("id(%d) : alarm = %d, temp = %d\n", i, oseeing_config[i].alarm,oseeing_config[i].temperature);
	}
	return 0;
}
*/

void mi48_raw_to_kelvin() {
	int i,j;
    for (i = 0; i < 62; i++) {
        for (j = 0; j < 80; j++) {
            temp_kelvin[i][j] = (mi48_data[(i * 80 + j) * 2] << 8) | mi48_data[(i * 80 + j) * 2 + 1];
        }
    }
	//printf("temperature[30][30]= %d\n",temp_kelvin[30][30]);
}

temperature_t *temperature_analysis() {
	int i,j,k;
	unsigned short int max, min;
	//oseeing_config_init();
	mi48_raw_to_kelvin();
	temperature[0].max = mi48_header.max; // (mi48_header.max-2735) / 10;
	temperature[0].min = mi48_header.min; // (mi48_header.min-2735) / 10;
	printf("Frame max temperature = %d, min temperature = %d\n", temperature[0].max,temperature[0].min);
	temperature_alarm = 0;
	if (temperature[0].max >= get_alarm_temperature(0)) {
		temperature_alarm |= 1; //  | temperature_alarm;
	}
	for (i=1; i<10; i++) {
		min=0xFFFF;
		max=0;
		for (j=area[i-1].y1; j<area[i-1].y2; j++) {
			for (k=area[i-1].x1; k<area[i-1].x2; k++) {
				if (temp_kelvin[j][k] > max)
					max = (temp_kelvin[j][k]);
					//max = (temp_kelvin[j][k]-2735)/10;
				if (temp_kelvin[j][k] < min)
					min = (temp_kelvin[j][k]);
					//min = (temp_kelvin[j][k]-2735)/10;
			}
			temperature[i].max = max; // (max-2735); //10;
			temperature[i].min = min; // (min-2735); // /10;
		}
		if (temperature[i].max >= get_alarm_temperature(i)) {
			temperature_alarm = (1<<i) | temperature_alarm;
		}
		printf("Alarm(%d) :area[%d] x1(%d),y1(%d),x2(%d),y2(%d) : max=%d, min=%d\n",get_alarm_temperature(i), i, area[i-1].x1,area[i-1].y1,area[i-1].x2,area[i-1].y2,temperature[i].max,temperature[i].min);
	}
	printf("Alarm = 0x%x\n", temperature_alarm);
	return temperature;
}

uint16_t get_temperature_alarm() {
	return temperature_alarm;
}

temperature_t *get_mi48_temperature() {
	return &temperature[0];
}

int mi48_scan() {
	int spi_count = 0;
	unsigned char cmd;
	mi48_log_print();
	size = 160;
	if (state_change == 1) 
	{
		//led_send_msg(MSG_HEART_BIT);
		state_change = 0;
		transfer(fd_spi,tx,rx,size);
		mi48_header_parse(rx);
		for (spi_count = 0; spi_count<62;spi_count++) {
			transfer(fd_spi,tx,rx,size);
			memcpy(&mi48_data[spi_count*160],rx,size);
		}
// Try to send mi48_data to socket
		socket_transfer(mi48_data);
		// socket end

// Check modbus server request 
/*
		cmd = get_server_command();
		if (cmd)
			temperature_analysis(cmd);
			*/
	}

	return 0; // fail, spi not ready
}
unsigned int mi48_get_max_temperature() {
	return mi48_header.max;
}

unsigned int mi48_get_min_temperature() {
	return mi48_header.min;
}

uint8_t *mi48_get_data() {
	return mi48_data;
}
int mi48_close()
{
	free(rx);
	free(tx);
	close(fd_spi);
	close(fd_capture);
	return 0;	
}
int socket_close() {

}

int mi48_init()
{
	int ret=0;
	ret=ir8062_hwinit();
	oseeing_config_init();
	if (ret < 0) 
		printf("ERROR : MI48 initial failure\n");
	return ret;
}
