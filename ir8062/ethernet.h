#ifndef __ETHERNET_H__
#define __ETHERNET_H__
#define ETHERNET_DEVICE_NAME		"eth0"
char *eth_get_mac();
void eth_set_fake_mac(char *no);
int eth_init();
int get_eth_status();
#endif
