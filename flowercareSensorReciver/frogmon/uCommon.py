# -*- coding: utf-8 -*-
# uCommon.py

import os

from datetime    import datetime, timedelta

class COM:
	gSetupFile = 'setup.ini'
	
	gProcessNM = os.path.abspath( __file__ )

	gYYYY = '0000'
	gMM   = '00'
	gDD   = '00'
	gHH   = '00'
	gNN   = '00'
	gSS   = '00'
	
	gNOW  = datetime.now()
	gYESTERDAY = gNOW - timedelta(days=1)
	
	gstrYMD = datetime.now().strftime('%Y%m%d')
	gstrYMDHMS = datetime.now().strftime('%Y%m%d%H%M%S')
	gstrDATE = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	gstrTODAY = datetime.now().strftime('%Y-%m-%d')
	gstrYESTERDAY = gYESTERDAY.strftime('%Y%m%d')
