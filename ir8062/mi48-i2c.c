#include <stdio.h>
#include <linux/types.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <errno.h>

#define I2C_RDWR 0x0707
#define DO_WRITE 0
#define DO_READ  1
#define MI48_ADDR 0x40
#define I2C_DEV "/dev/i2c-1"
struct i2c_msg
{
	unsigned short addr;
	unsigned short flags;
#define I2C_M_TEN 0x0010
#define I2C_M_RD 0x0001
	unsigned short len;
	unsigned char *buf;//[2];
};
struct i2c_rdwr_ioctl_data
{
	struct i2c_msg *msgs;
	int nmsgs; 
};
int i2c_fd=-1;
int mi48_i2c_read(unsigned char reg, unsigned char *val) {
    struct i2c_rdwr_ioctl_data mi48_data;
    if (i2c_fd < 0) 
        return -1;
	/******read data from mi48******/
	mi48_data.nmsgs=2;
   	mi48_data.msgs=(struct i2c_msg*)malloc(mi48_data.nmsgs*sizeof(struct i2c_msg));
    mi48_data.msgs[0].buf = (unsigned char*)malloc(1);    
    mi48_data.msgs[1].buf = (unsigned char*)malloc(1);    
	(mi48_data.msgs[0]).len=1; // write length
	(mi48_data.msgs[0]).addr=MI48_ADDR; // mi48 slave address
	(mi48_data.msgs[0]).flags=0; // 0:write 
	(mi48_data.msgs[0]).buf[0]=reg; //register
	
	(mi48_data.msgs[1]).len=1;//read length
	(mi48_data.msgs[1]).addr=MI48_ADDR;// mi48 slave address
	(mi48_data.msgs[1]).flags=I2C_M_RD; //read
	(mi48_data.msgs[1]).buf[0]=0; // buf clear

	if(ioctl(i2c_fd,I2C_RDWR,(unsigned long)&mi48_data) <0)
	{
		perror("error to read data from mi48");
        free(mi48_data.msgs[0].buf);
        free(mi48_data.msgs[1].buf);
        free(mi48_data.msgs);
        return -1;
	}
    *val = mi48_data.msgs[1].buf[0];
	printf("I2C read reg(0x%x)=0x%x\n",reg, (mi48_data.msgs[1]).buf[0]);
    free(mi48_data.msgs[0].buf);
    free(mi48_data.msgs[1].buf);
    free(mi48_data.msgs);
    return 0;
}

int mi48_i2c_write(unsigned char reg, unsigned char val) {
    struct i2c_rdwr_ioctl_data mi48_data;
    if (i2c_fd < 0) 
        return -1;
	mi48_data.nmsgs=1;
	mi48_data.msgs=(struct i2c_msg*)malloc(mi48_data.nmsgs*sizeof(struct i2c_msg));
	if(!mi48_data.msgs)
	{
		perror("malloc error");
		return -1;
	}
    mi48_data.msgs[0].buf = (unsigned char*)malloc(2);
	mi48_data.nmsgs=1;	      			 
	(mi48_data.msgs[0]).len=2; 			// write length, reg+buf
	(mi48_data.msgs[0]).addr=MI48_ADDR;		// MI48 slave address
	(mi48_data.msgs[0]).flags=0; 		//write:0 read:I2C_M_RD
	(mi48_data.msgs[0]).buf[0]=reg;		// register
	(mi48_data.msgs[0]).buf[1]=val;		// value
	
	if(ioctl(i2c_fd, I2C_RDWR, (unsigned long)&mi48_data)<0)
	{
		perror("ioctl error1");
        free(mi48_data.msgs[0].buf);
        free(mi48_data.msgs);
        return -1;
	}
    printf("I2C write (0x%x) = 0x%x\n",(mi48_data.msgs[0]).buf[0],(mi48_data.msgs[0]).buf[1]);
    free(mi48_data.msgs[0].buf);
    free(mi48_data.msgs);
    return 0;
}
int mi48_i2c_init() {
    int ret;
    i2c_fd = open(I2C_DEV, O_RDWR);
	if(i2c_fd<0)
	{
		perror("open I2C device error");
        return -1;
	}
    return i2c_fd;
}
int mi48_i2c_remove() {
    if (i2c_fd >= 0) {
        close(i2c_fd);
        return 0;
    }
    else
        return -1;
}
