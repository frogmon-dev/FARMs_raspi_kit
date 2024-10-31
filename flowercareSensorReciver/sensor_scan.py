# -*- coding: utf-8 -*- 
import os
from tendo import singleton
try:
	me = singleton.SingleInstance()
except :
	print("another process running!")
	exit()

#프로그램 시작
from bluepy.btle import Scanner, DefaultDelegate
from frogmon.uGlobal   import GLOB

def get_current_path():
    # 현재 스크립트 파일의 위치를 기준으로 bin 디렉토리 경로를 설정
    return os.path.dirname(os.path.abspath(__file__))

configFileNM = get_current_path() + '/../bin/setup.ini'


print('')
print('--------------------------------------------------')
print('**  Welcome to FROGMON corp.')
print("**  Let's make it together")
print("**  user id (%s)" % (GLOB.get_ini_value(configFileNM, 'SETUP', 'user_id', 'test')))
print('--------------------------------------------------')
print('')

TARGET_UUID = "0000fe95-0000-1000-8000-00805f9b34fb"
target_dev = None    

#############################################
# Define scan callback
#############################################
class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev:
			print("Discovered device %s" % dev.addr)
		elif isNewData:
			print("Received new data from %s" % dev.addr)

#############################################
# Define notification callback
#############################################
class NotifyDelegate(DefaultDelegate):
	#Constructor (run once on startup)  
	def __init__(self, params):
		DefaultDelegate.__init__(self)

	#func is caled on notifications
	def handleNotification(self, cHandle, data):
		print("Notification : " + data.decode("utf-8"))

#############################################
# Main starts here
#############################################
scanner = Scanner().withDelegate(ScanDelegate())
try:
	devices = scanner.scan(10.0)
except Exception as e:
    print(f"An error occurred: {e}")    

cnt = 0
dev_str=''

GLOB.recreate_section(configFileNM, 'DEVICE')

for dev in devices:
	#print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
	for (adtype, desc, value) in dev.getScanData():
		# Check iBeacon UUID
		# 255 is manufacturer data (1  is Flags, 9 is Name)
		#print("  (AD Type=%d) %s = %s" % (adtype, desc, value))
		if adtype == 2 and TARGET_UUID in value:
			cnt = cnt+1
			target_dev = dev
			print("%d) Device %s (%s), RSSI=%d dB" % (cnt, dev.addr, dev.addrType, dev.rssi))
			dev_str = "sensor%02d" % (cnt)			
			GLOB.set_key_value(configFileNM, 'DEVICE', dev_str, dev.addr)

GLOB.set_key_value(configFileNM, 'FLOWERCARE', 'sensor_cnt', "%d" %cnt)

if cnt > 0 :
	print('식물 정보 감지 센서 %d개를 찾았습니다. ' % cnt)
else :
	print('식물 정보 센서를 감지 하지 못하였습니다.')
	print('제어기와 너무 멀리 떨어지거나 건전지 교체 시기인지 확인하여 주세요')
