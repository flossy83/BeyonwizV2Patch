# -------------------------------------------------------------------------------
# Beyonwiz patch by S.Z, 22/09/2020
# -------------------------------------------------------------------------------
#
# 	Fixes:
#	- Video enhancements: auto flesh not disabled when set to 0 *
#	- Aspect ratio: wrong aspect for non-16:9 content *
#	- Autores/multi: frame rate incorrectly detected as 30fps *
#	- Autores: redundant display mode initialisations *
#	- AV Settings: incorrect colour after playing HDR content *
#	- AV Settings: colour space reverting to RGB after applying 2160p modes *
#	- DVB tuner: persistent frame rate stutter after signal interference on HD channels *
#	- Autores/multi: unhandled progressive/interlaced value of -1
#	- Autores/multi: falling back to invalid display mode strings
#	- AV Settings: wrong port/mode/rate shown after disconfirming display mode
#
# 	Improvements:
#	- Autores: detect up to 2160p + vertical videos with improved accuracy
#	- Autores: increase detection of video content change
# 	- Autores: support 1080i and 1080p independently
#	- Autores: remove redundant modes: 25hz, 30hz
#	- Autores: add i60/p60 suffix to 60hz modes
#	- Autores: new mode ordering and defaults
#	- Autores: remove duplicate delay setting
#	- Aspect ratio: always show in AV settings, remove redundant setting, new nomenclature *
#	- Colour space: default to YCbCr444, remove redundant settings, new nomenclature *
#	- Video enhancements: remove redundant settings, new nomenclature
#	- AV Settings: consistently apply video mode and aspect on OK
#	- Movie player: remove redundant service restart on exit
#	- AutoTimer: append event title to custom record path when importing from EPG 
#
#	Unresolved issues:
#	- 23.976fps content cannot be output at 23.976hz
#	- System may become unresponsive when video output mode is 60hz
#	- Incorrect colourimetry when video output mode is 576i
#	- Sharpness setting becomes nonfunctional after playing HDR content
#	- Sharpness setting behaves inconsistently if adjusted after reboot
#	- Events occasionally missing from EPG cache
#	- Inconsistent detection of interlace/progressive on certain media files
#
#	* only for boxes with chipset 3798MV200
#
#	Files modified:
#	/usr/lib/enigma2/python/Components/AVSwitch.pyo
#	/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/VideoEnhancement.pyo
#	/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.pyo
#	/usr/lib/enigma2/python/Screens/MovieSelection.pyo
#	/usr/lib/enigma2/python/Screens/VideoMode.pyo
#	/usr/lib/enigma2/python/Plugins/Extensions/AutoTimer/AutoTimerEditor.pyoo
#
# -------------------------------------------------------------------------------

import os
from datetime import datetime
from boxbranding import getBoxType, getMachineBuild
from Components.About import about

# -------------------------------------------------------------------------------
# Define models which receive the patch.
# -------------------------------------------------------------------------------

patchModels = ("beyonwizv2","beyonwizt2","beyonwizt3","beyonwizt4","beyonwizu4")
# These models will receive the general fixes/improvements which should be
# compatible with boxes running firmware 19.3.
# Set pachModels=() to revert to original code.

patchHisiModels = ("beyonwizv2")
# These models will receive the fixes specific to chipset 3798MV200 (Hisilicon).
# These fixes have only been tested on a Beyonwiz V2.
# Set patchHisiModels=() or patchModels=() to not apply them.
# Models without chipset 3798MV200 will be ignored. 
 
patchGeneral = False; patchHisi = False
if (getBoxType() in patchModels) or (getMachineBuild() in patchModels):
	patchGeneral = True 	
	if (getBoxType() in patchHisiModels) or (getMachineBuild() in patchHisiModels):
		if (about.getChipSetString() in ("3798mv200", "hi3798mv200")):
			patchHisi = True
	

# -------------------------------------------------------------------------------
# Log file
# -------------------------------------------------------------------------------

# To enable logging, place a file called BeyonwizV2Patch.log (case sensitive) in
# /usr/lib/enigma2/python/Components and restart.  To disable logging, delete the file.

logFile = os.path.dirname(os.path.abspath(__file__)) + "/BeyonwizV2Patch.log"
enableLogging = True if os.path.exists(logFile) else False
logNewSession = True

def log(line):	
	global enableLogging, logNewSession
	if enableLogging:	
		if not os.path.exists(logFile): return
		try:
			f = open(logFile, "a")
			if (logNewSession):
				f.write("************" + "\n")
				logNewSession = False
			f.write(datetime.now().strftime("%H:%M:%S") + "  " + line + "\n")
			f.close()
		except:		
			f.close()

# -------------------------------------------------------------------------------