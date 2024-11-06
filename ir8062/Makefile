.SUFFIXES : .x .o .c .s

CC := arm-linux-gcc
#STRIP := arm-linux-strip
TARGET = oseeing1s

#SRCS := ini-parser.c main.c
#OBJS= main.o cJSON.o curl_fun.o sensor.o cJSON.o
#OBJS= main.o cJSON.o sensor.o ini-parse.o cloud-service.o http-igreent.o rs485.o led_control.o jpegenc.o alarm.o
#OBJS= main.o ini-parse.o rs485.o led_control.o jpegenc.o alarm.o ethernet.o mi48.o cloud-service.o cJSON.o curl_thread.o
#OBJS= main.o ini-parse.o rs485.o led_control.o jpegenc.o alarm.o ethernet.o mi48-socket.o cloud-service.o cJSON.o curl_thread.o
OBJS= main.o rs485.o led_control.o ethernet.o mi48-socket.o socket_stream.o utils.o mi48-i2c.o
LIBS = -lcurl -lm -ljpeg #-lssl -lcrypto #-ljson-c -lnsl 

$(TARGET) : $(OBJS)
	$(CC) -o $(TARGET) $(OBJS) $(LDFLAGS) $(CFLAGS) $(LIBS) 
clean:
	rm -r *.o

