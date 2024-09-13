# oseeing1s
Oseeing 1S modbus project
Support RS485 modbus 
Support socket thermal image preview

# Configuartion tools
	Path : uart-init
	file :
		oseeing1s-config.py : configuartion oseeing device alarm setting by RS485
		oseeing1s-connect.py : preview oseeing device thermal image, need rj45 ethernet support
		oseeing.ini : oseeing default setting
		get_temperature.py : test program, continue get oseeing device temperature and alarm status
		alarm_monitor.py : Test program, GUI interface to monitor oseeing device alarm status. Only support default device ID of 0xAA	
