### Beyonwiz V2 patch (unofficial)
---

#### About

This release is an unofficial patch for the Beyonwiz V2 PVR.  It includes the following fixes and improvements:

Fixes:

* Video enhancements: auto flesh not disabled when set to 0
* Aspect ratio: wrong aspect for non-16:9 content
* Autores/multi: frame rate incorrectly detected as 30fps
* Autores: redundant display mode initialisations
* AV Settings: incorrect colour after playing HDR content
* AV Settings: colour space reverting to RGB after applying 2160p modes
* DVB tuner: persistent frame rate stutter after signal interference on HD channels
* Autores/multi: unhandled progressive/interlaced value of -1
* Autores/multi: falling back to invalid display mode strings
* AV Settings: wrong port/mode/rate shown after disconfirming display mode

Improvements:

* Autores: detect up to 2160p + vertical videos with improved accuracy
* Autores: increase detection of video content change
* Autores: support 1080i and 1080p independently
* Autores: remove redundant modes: 25hz, 30hz
* Autores: add i60/p60 suffix to 60hz modes
* Autores: new mode ordering and defaults
* Autores: remove duplicate delay setting
* Aspect ratio: always show in AV settings, remove redundant setting, new nomenclature
* Colour space: default to YCbCr444, remove redundant settings, new nomenclature
* Video enhancements: remove redundant settings, new nomenclature
* AV Settings: consistently apply video mode and aspect on OK
* Movie player: remove redundant service restart on exit
* AutoTimer: append event title to custom record path when importing from EPG 

Unresolved issues:

* 23.976fps content cannot be output at 23.976hz
* System may become unresponsive when video output mode is 60hz
* Incorrect colourimetry when video output mode is 576i
* Sharpness setting becomes nonfunctional after playing HDR content
* Sharpness setting behaves inconsistently if adjusted after reboot (fix: [tiny.cc/AutoSharpness](https://tiny.cc/AutoSharpness))
* Events occasionally missing from EPG cache
* Inconsistent detection of interlace/progressive on certain media files

Files modified:

* /usr/lib/enigma2/python/Components/AVSwitch.pyo
* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/VideoEnhancement.pyo
* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.pyo
* /usr/lib/enigma2/python/Screens/MovieSelection.pyo
* /usr/lib/enigma2/python/Screens/VideoMode.pyo
* /usr/lib/enigma2/python/Plugins/Extensions/AutoTimer/AutoTimerEditor.pyo


#### System Requirements

This patch was written and tested on a Beyonwiz V2 running firmware 19.3.20200328 and 19.3.20200901.

It should also be compatible with future versions of 19.3, however this cannot be guaranteed in case future Beyonwiz firmware modifies any of its dependencies.


#### Installation

Before installation it's recommended to backup your system configuration settings in case something goes wrong and you have to reflash the original firmware.  This can be accessed by main menu > setup > software manager > create backup.

1. Download the .ipk file from the downloads section and copy it to a USB drive.

2. Insert the drive into the PVR and follow the on-screen instructions.  Otherwise, use the PVR's file explorer to manually run the .ipk file.

3. Launch 'Beyonwiz V2 Patch' from the system plugins menu.

4. Select 'Install' (green key).

5. After installation is complete, restart the PVR.


#### Removal

1. Launch 'Beyonwiz V2 Patch' from the system plugins menu.

2. Select 'Uninstall' (yellow key).

3. After uninstallation is complete, restart the PVR.

You can also optionally remove the plugin by navigating to the system plugins menu and selecting 'remove plugins' (red key) and selecting the 'Beyonwiz V2 Patch' plugin.  Once complete, restart the PVR.


#### Emergency recovery

In case the installation or removal steps did not work and the PVR becomes unresponsive, you may need to re-flash the original firmware, which can be obtained here: https://www.beyonwiz.com.au/forum/viewforum.php?f=45

For the Beyonwiz V2 you will need to hold down the front power button while the unit is booting up.

After re-flashing the original firmware, you can restore your original configuration settings from the backup you made previously via main menu > setup > software manager > restore backup.


#### Screenshot

![Alt text](https://bitbucket.org/CalibrationTools/images/downloads/screenshot3.png)