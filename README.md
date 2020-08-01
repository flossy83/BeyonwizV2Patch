### Beyonwiz V2 patch (unofficial)
---

#### About

This release is an unofficial patch for the Beyonwiz V2 PVR. It provides the following fixes and improvements:

Fixes:

* Video enhancements: auto flesh not disabled when set to 0 *
* Aspect ratio: wrong aspect for non-16:9 content *
* Autores/multi: non-30fps video detected as 30fps *
* Autores: redundant display mode initialisations *
* AV Settings: incorrect colour after playing 2160p/HDR content *
* AV Settings: colour space reverting to RGB after applying 2160p modes *
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
* Aspect ratio: remove redundant setting, nomenclature *
* Colour space: default to YCbCr444, remove redundant setting, nomenclature *
* Video enhancements: remove redundant colour space setting, nomenclature
* AV Settings: add GUI option to increase detection of video content
* AV Settings: consistently apply video mode and aspect on userOK

\* only for chipset 3798MV200

Files modified:

* /usr/lib/enigma2/python/Components/AVSwitch.py
* /usr/lib/enigma2/python/Screens/VideoMode.py
* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/VideoEnhancement.py
* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.py


#### System Requirements

This patch was written and tested on a Beyonwiz V2 running firmware 19.3.20200328.

It has been written to be compatible with other Beyonwiz boxes running firmware 19.3.20200328, however you will need to manually edit one of the source code files to specify which other models the patch should also apply to (by default it only applies to Beyonwiz V2).


#### Installation

Before installation it is recommended to backup your system configuration settings in case something goes wrong and you have to reflash the original firmware.  This can be accessed by main menu > setup > software manager > create backup.

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