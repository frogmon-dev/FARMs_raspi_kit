# uFlowerCare.py
import os
import json

from collections import OrderedDict
from time import time, sleep, localtime, strftime
from unidecode       import unidecode

#프로그램 시작
from frogmon.uGlobal   import GLOB
from frogmon.uCommon   import COM

def get_current_path():
    # 현재 스크립트 파일의 위치를 기준으로 bin 디렉토리 경로를 설정
    return os.path.dirname(os.path.abspath(__file__))  + '/'

configFileNM = get_current_path() + '../bin/setup.ini'
JsonDir = get_current_path() + '../bin/json/'

from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE
from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend, BluetoothBackendException

mParameters = OrderedDict([
        (MI_LIGHT,        dict(name="LightIntensity"  , name_pretty='Sunlight Intensity'         , typeformat='%d'  , unit='lux'    , device_class="illuminance")),
        (MI_TEMPERATURE,  dict(name="AirTemperature"  , name_pretty='Air Temperature'            , typeformat='%.1f', unit='°C'     , device_class="temperature")),
        (MI_MOISTURE,     dict(name="SoilMoisture"    , name_pretty='Soil Moisture'              , typeformat='%d'  , unit='%'      , device_class="humidity")),
        (MI_CONDUCTIVITY, dict(name="SoilConductivity", name_pretty='Soil Conductivity/Fertility', typeformat='%d'  , unit='µS/cm')),
        (MI_BATTERY,      dict(name="Battery"         , name_pretty='Sensor Battery Level'       , typeformat='%d'  , unit='%'      , device_class="battery"))
    ])

class pwinfo :
    e_pty = 0
    e_sky = 0
    e_wsd = 0.0
    e_t1h = 0
    e_reh = 0
    
class FLOWERCARE:
    def __init__(self):
        self.flores = OrderedDict([])
        self.confUpdate()
        
    # Identifier cleanup
    def clean_identifier(name):
        clean = name.strip()
        for this, that in [[' ', '-'], ['ä', 'ae'], ['Ä', 'Ae'], ['ö', 'oe'], ['Ö', 'Oe'], ['ü', 'ue'], ['Ü', 'Ue'], ['ß', 'ss']]:
            clean = clean.replace(this, that)
        clean = unidecode(clean)
        return clean
	
        
    def confUpdate(self):
        self.used_adapter          = GLOB.get_ini_value(configFileNM, 'FLOWERCARE', 'adapter', 'hci0')
        self.reporting_mode        = 'json'
        self.daemon_enabled        = True
        self.default_base_topic    = 'miflora'
        self.sleep_period          = 300
        self.miflora_cache_timeout = self.sleep_period - 1
        
        
    def chkSensor(self):
        for [name, mac] in GLOB.get_key_value_list(configFileNM, 'DEVICE'):
            if '@' in name:
                name_pretty, location_pretty = name.split('@')
            else:
                name_pretty, location_pretty = name, ''
                
            name_clean = self.clean_identifier(name_pretty)
            location_clean = self.clean_identifier(location_pretty)

            flora = dict()
            print('Adding sensor to device list and testing connection ...')
            print('Name:		  "{}"'.format(name_pretty))
            
            flora_poller = MiFloraPoller(mac=mac, backend=GatttoolBackend, cache_timeout=self.miflora_cache_timeout, adapter=self.used_adapter)
            flora['poller'] = flora_poller
            flora['name_pretty'] = name_pretty
            flora['mac'] = flora_poller._mac
            flora['refresh'] = self.sleep_period
            flora['location_clean'] = location_clean
            flora['location_pretty'] = location_pretty
            flora['stats'] = {"count": 0, "success": 0, "failure": 0}
            
            try:
                flora_poller.fill_cache()
                flora_poller.parameter_value(MI_LIGHT)
                flora['firmware'] = flora_poller.firmware_version()
            except (IOError, BluetoothBackendException):
                print('Initial connection to Mi Flora sensor "{}" ({}) failed.')
            else:
                print('Internal name: "{}"'.format(name_clean))
                print('Device name:   "{}"'.format(flora_poller.name()))
                print('MAC address:   {}'.format(flora_poller._mac))
                print('Firmware:	  {}'.format(flora_poller.firmware_version()))
            print()
            self.flores[name_clean] = flora
        return self.flores

    def atOnce(self):
        self.chkSensor()
        GLOB.setUpdateTime()
        self.confUpdate()
        for [flora_name, flora] in self.flores.items():
            data = dict()
            attempts = 2
            flora['poller']._cache = None
            flora['poller']._last_read = None
            flora['stats']['count'] = flora['stats']['count'] + 1
            #print_line('Retrieving data from sensor "{}" ...'.format(flora['name_pretty']))
            while attempts != 0 and not flora['poller']._cache:
                try:
                    flora['poller'].fill_cache()
                    flora['poller'].parameter_value(MI_LIGHT)
                except (IOError, BluetoothBackendException):
                    attempts = attempts - 1
                    if attempts > 0:
                        print('Retrying ...')
                    flora['poller']._cache = None
                    flora['poller']._last_read = None

            if not flora['poller']._cache:
                flora['stats']['failure'] = flora['stats']['failure'] + 1
                print('Failed to retrieve data from Mi Flora sensor "{}" ({}), success rate: {:.0%}'.format(
                    flora['name_pretty'], flora['mac'], flora['stats']['success']/flora['stats']['count']
                    ))
                print()
                continue
            else:
                flora['stats']['success'] = flora['stats']['success'] + 1

            for param,_ in mParameters.items():
                data[param] = flora['poller'].parameter_value(param)
            
            rc = -1
            try:
                data['timestamp']   = COM.gstrDATE
                data['name']        = flora_name
                data['name_pretty'] = flora['name_pretty']
                data['mac']         = flora['mac']
                data['firmware']    = flora['firmware']
                
                print('Data for "{}": {}'.format(flora_name, json.dumps(data)))
                with open(JsonDir+flora_name+'.json', 'w', encoding="utf-8") as make_file:
                    json.dump(data, make_file, ensure_ascii=False, indent="\t")
                
                rc = 1
            except Exception as e :
                print("[ERROR][FLOWERCARE] : %s" % e)
    
FC = FLOWERCARE()
FC.atOnce()