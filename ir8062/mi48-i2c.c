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
	/* nmsgs這個數量决定了有多少開始信號，對於“單開始時序”，取1*/
};
int i2c_fd=-1;
int mi48_i2c_read(unsigned char reg, unsigned char *val) {
    struct i2c_rdwr_ioctl_data mi48_data;
    if (i2c_fd < 0) 
        return -1;
		/******read data from e2prom******/
	mi48_data.nmsgs=2;
   	mi48_data.msgs=(struct i2c_msg*)malloc(mi48_data.nmsgs*sizeof(struct i2c_msg));
    mi48_data.msgs[0].buf = (unsigned char*)malloc(1);    
    mi48_data.msgs[1].buf = (unsigned char*)malloc(1);    
	(mi48_data.msgs[0]).len=1; //mi48 寫入1個目標的地址
	(mi48_data.msgs[0]).addr=MI48_ADDR; // mi48 設備地址
	(mi48_data.msgs[0]).flags=0;//write
	(mi48_data.msgs[0]).buf[0]=reg; //mi48 reg
	
	(mi48_data.msgs[1]).len=1;//讀出1個數據
	(mi48_data.msgs[1]).addr=MI48_ADDR;// mi48 設備地址
	(mi48_data.msgs[1]).flags=I2C_M_RD;//read
	(mi48_data.msgs[1]).buf[0]=0;//初始化讀緩沖
	//		(mi48_data.msgs[1]).buf[1]=0;//初始化讀緩沖
	//		(mi48_data.msgs[1]).buf[2]=0;//初始化讀緩沖

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
	/*
	 *因为操作時序中，最多是用到2個開始信號（字節讀操作中），所以此將
	 *mi48_data.nmsgs配置为2
	 */
	mi48_data.msgs=(struct i2c_msg*)malloc(mi48_data.nmsgs*sizeof(struct i2c_msg));
	if(!mi48_data.msgs)
	{
		perror("malloc error");
		return -1;
	}
    mi48_data.msgs[0].buf = (unsigned char*)malloc(2);
    // check malloc error
	//                ioctl(fd,I2C_TIMEOUT,1);/*超時時間*/
	//               ioctl(fd,I2C_RETRIES,2);/*重复次數*/
	//
	mi48_data.nmsgs=1;	      			// 從Start到Stop，中間沒有repeat start的話，算一組的I2C data
	(mi48_data.msgs[0]).len=2; 			// i2c寫入兩筆數據
	(mi48_data.msgs[0]).addr=MI48_ADDR;		//設備地址
	(mi48_data.msgs[0]).flags=0; 		//write:0 read:I2C_M_RD
	(mi48_data.msgs[0]).buf[0]=reg;		// 寫入thermal設備地址的Register ex: B4 register
	(mi48_data.msgs[0]).buf[1]=val;		// 寫入這個Register的數值        ex:0xB4 register 填入 0xB3
	
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
