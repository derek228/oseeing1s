#ifndef __MI48_H__
#define __MI48_H__

typedef struct {
	unsigned int frame_cnt;
	unsigned int max;
	unsigned int min;
}mi48_header_t;

typedef struct {
	unsigned char alarm;
	unsigned char temperature;
}oseeing_config_t;

typedef struct {
	unsigned short int max;
	unsigned short int min;
}temperature_t;

typedef struct {
	unsigned char x1;
	unsigned char y1;
	unsigned char x2;
	unsigned char y2;
}coordinate_t;

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

//int mi48_scan(char *data);
int mi48_scan();
uint8_t *mi48_get_data();
int mi48_init();
int mi48_close();
unsigned int mi48_get_max_temperature();
unsigned int mi48_get_min_temperature();
#endif
