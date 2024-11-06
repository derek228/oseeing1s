#ifndef __MI48_I2C_H__
#define __MI48_I2C_H__
int mi48_i2c_read(unsigned char reg, unsigned char *val);
int mi48_i2c_write(unsigned char reg, unsigned char val);
int mi48_i2c_init();
int mi48_i2c_remove();
#endif // __MI48_I2C_H__

