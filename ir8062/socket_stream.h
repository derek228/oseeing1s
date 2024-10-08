#ifndef __SOCKET_STREAM_H__
#define __SOCKET_STREAM_H__

#define SERVER_IP "192.168.100.70"  // Server IP address (fix ip )
#define SERVER_PORT 8080

//int is_socket_connection();
int socket_transfer(uint8_t *data);
#endif // __SOCKET_STREAM_H__