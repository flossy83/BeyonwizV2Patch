### Beyonwiz V2 patch (unofficial)
---

#### About

This release is an unofficial patch for the Beyonwiz PVR.  It includes the following fixes and improvements:

Fixes:

* Video enhancements: auto flesh not disabled when set to 0
* Aspect ratio: wrong aspect for non-16:9 content
* Autores/multi: non-30fps video detected as 30fps
* Autores: redundant display mode initialisations
* AV Settings: incorrect colour after playing HDR content
* AV Settings: colour space reverting to RGB after applying 2160p modes
* DVB tuner: persistent frame rate stutter after signal interference on HD channels
* Autores/multi: video_progressive = -1 not handled
* Autores/multi: falling back to invalid modes
* AV Settings: wrong port/mode/rate shown after disconfirming display mode

Improvements:

* Autores: detect up to 2160p + vertical videos, improved accuracy
* Autores: support 1080i and 1080p independently
* Autores: remove redundant modes: 25hz, 30hz
* Autores: add i60/p60 suffix to 60hz modes
* Autores: new mode ordering and defaults
* Autores: remove duplicate delay setting
* Aspect ratio: always show in GUI
* Aspect ratio: remove redundant setting, nomenclature
* Colour space: default to YCbCr444, remove redundant settings, nomenclature
* Video enhancements: remove redundant settings, nomenclature
* AV Settings: add GUI option to increase detection of video content
* AV Settings: consistently apply video mode and aspect on userOK

Unresolved issues:

* 23.976fps content cannot be output at 23.976hz
* System becomes unresponsive for approx. 30 seconds after playing 60fps content
* Incorrect colourimetry when video output mode is 576i
* Sharpness setting becomes nonfunctional after playing HDR content
* Sharpness setting behaves inconsistently if adjusted after reboot (fix: tiny.cc/AutoSharpness)
* EPG events missing from graphical EPG view when event start/end times overlap 

Files modified:

* /usr/lib/enigma2/python/Components/AVSwitch.py
* /usr/lib/enigma2/python/Screens/VideoMode.py
* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/VideoEnhancement.py
* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.py


#### System Requirements

This patch was written and tested on a Beyonwiz V2 running firmware 19.3.20200328.

The patch contains all the original unpatched code, and will only run the new patched code if it detects your box is a Beyonwiz V2.

The new code was written to be compatible with other Beyonwiz boxes running firmware 19.3.20200328, and has been tested on a Beyonwiz T2.  Many of the fixes and improvements are specific to Beyonwiz V2 and will not be applied to other models.


#### Installation

Before installation it's recommended to backup your system configuration settings in case something goes wrong and you have to reflash the original firmware.  This can be accessed by main menu > setup > software manager > create backup.

1. Download the .ipk file from the downloads section and copy it to a USB drive.

2. Insert the drive into the PVR and follow the on-screen instructions.  Otherwise, use the PVR's file explorer to manually run the .ipk file.

3. Navigate to the plugins menu and select 'Beyonwiz Patch (unofficial)'.

4. Select 'Install patch' (green key).

5. Restart the PVR.


#### Removal

1. Navigate to the plugins menu and select Beyonwiz Patch (unofficial).

2. Select 'Remove patch' (red key).

3. Restart the PVR.


#### Emergency recovery:

In case the installation or removal steps did not work and the PVR becomes unresponsive, you may need to re-flash the original firmware, which can be obtained here: https://www.beyonwiz.com.au/forum/viewforum.php?f=45

For the Beyonwiz V2 you will need to hold down the front power button while the unit is booting up.

For other models the procedure can be found here: http://www.beyonwiz.com.au/media/downloads/HowToUpgradeBeyonwizTSeriesV163.pdf

After re-flashing the original firmware, you can restore your original configuration settings from the backup you made previously via main menu > setup > software manager > restore backup.