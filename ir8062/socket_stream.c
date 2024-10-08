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
#include "socket_stream.h"
#include "ethernet.h"
#include "rs485.h"

static int sockfd = -1;
static int socket_connected = -1;
static struct sockaddr_in server_addr;

static unsigned char get_server_connect() {
	char conn;
	if (file_exist(FILE_SERVER_CONNECTION) < 0)
		return 0;
	read_char_from_file(FILE_SERVER_CONNECTION,&conn);
	printf("Socket connect status = %d\n", conn);
	return (uint8_t) conn;
}

static int get_server_ip(unsigned char *ip) {
	int ret = 0;
	if (file_exist(FILE_SERVER_IP) < 0)
		return -1;
	memset(ip, 0 , 17);
	ret = read_char_from_file(FILE_SERVER_IP,ip);
	if (ret > 16) {
		printf("Unknow IP address format %s\n",ip);
		ret = -1;
	}
	return ret;
}

static int is_socket_connection() {
	// check config
	static unsigned char ipaddr[17]={0};
	if (get_server_connect()==0) {
		socket_connected = -1;
		if (sockfd >=0 )
			close(sockfd);
		sockfd = -1;
		
		return -1;
	}
	else {
		if (get_server_ip(ipaddr)<0)
			return -1;
	}
    // create socket
	if (sockfd <0) {
		printf("Socket disconnect, try to init...\n");
		server_addr.sin_family = AF_INET;
		server_addr.sin_port = htons(SERVER_PORT);
    // 将 IP 地址转换为二进制格式并存储在 server_addr 结构中
//		if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
		if (inet_pton(AF_INET, ipaddr, &server_addr.sin_addr) <= 0) {
			perror("Invalid address/ Address not supported");
			return -1;
		}

	    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
	        perror("Socket creation failed");
			return -1;
	    }
	}
	if (socket_connected < 0) {
	    // 连接到接收端
		printf("Connect to Socket... \n");
		socket_connected=connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr));
   		if (socket_connected < 0) {
	        perror("Connection Failed");
	        return -1;
	    }
		return 1;
	}
	return 1;
}

// Send mi48_data to socket
int socket_transfer(uint8_t *data) {
	if (get_eth_status() == 0)
		return -1;
	if (is_socket_connection() > 0) {
		ssize_t sent_bytes = send(sockfd, data, 9920, MSG_NOSIGNAL);
		printf("sent_bytes = %d\n", sent_bytes);
		if (sent_bytes < 0) {
			perror("Failed to send mi48_data");
			socket_connected = -1;
			close(sockfd);
			sockfd = -1;
		}
	}
}
