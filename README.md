### Beyonwiz V2 patch (unofficial)
---

#### About

This release is an unofficial patch for the Beyonwiz V2 PVR. It provides the following fixes and improvements:

Fixes:

* Autores/multi: non-30fps video detected as 30fps *
* Autores: redundant display mode initialisations *
* Autores/multi: video_progressive = -1 not handled
* Autores/multi: falling back to invalid modes
* Aspect ratio: wrong aspect for non-16:9 content *
* AV Settings: colour space reverting to RGB after applying 2160p modes *
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
* AV Settings: add GUI option to increase detection of video mode and aspect
* AV Settings: consistently apply video mode and aspect on userOK

\* only for chipset 3798MV200


#### System Requirements

This patch was written and tested on a Beyonwiz V2 running firmware 19.3.20200328.

It also appears to be compatible with other Beyonwiz boxes running firmware 19.3.20200328, however you will need to manually edit one of the source code files to specify which other models the patch should also apply to (by default it only applies to Beyonwiz V2).


#### Installation

Installation consists of copying 4 uncompiled source code files to the PVR.  This can be done by connecting a computer to the same local network as the PVR, such as by wifi or ethernet cable, and using an FTP application to copy the files across.  The PVR should then automatically compile and run the updated files at the next restart.

Step by step instructions for Windows PCs:

1. Enable the PVR's network adapter in its system settings.

2. Connect a Windows PC to the same local network as the PVR, such as by enabling the PC's wifi adapter, or by connecting the PC directly to the rear of the PVR via ethernet cable. 
   
3. Determine the PVR's IP address on your local network, which should be listed in the PVR's network settings.
   
4. Determine the PVR's network username and password, which should be listed in the PVR's network settings (for Beyonwiz PVR's, the default username is "root").

5. Obtain an FTP application for Windows, eg. WinSCP.

6. Use the FTP application to connect to the PVR using the IP address, username and password from steps 3 and 4.
   
7. Use the FTP application to copy the following files from the PVR to your PC:

	* /usr/lib/enigma2/python/Components/AVSwitch.pyo
	* /usr/lib/enigma2/python/Screens/VideoMode.pyo
	* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/VideoEnhancement.pyo
	* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.pyo
	
	Keep these files in case you want to remove the patch, in which case we will copy them back to the PVR.
   
8. Download the following files from the Downloads section of this Bitbucket repository:

	* AVSwitch.py
	* VideoMode.py
	* VideoEnhancement.py
	* plugin.py
	
9. Use the FTP application to copy the above files to the following locations on the PVR:

	* /usr/lib/enigma2/python/Components/AVSwitch.py
	* /usr/lib/enigma2/python/Screens/VideoMode.py
	* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/VideoEnhancement.py
	* /usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.py

10. Restart the PVR.

11. Optional step: delete the files specified in step 9, but leave their respective .pyo files.


#### Uninstallation:

1. Delete the files specified in step 9.

2. Copy the original files obtained in step 7 back to the PVR.

3. Restart the PVR.


#### Emergency recovery:

In case the uninstallation steps did not work and the PVR becomes unresponsive, you may need to re-flash the original firmware, which can be obtained here: https://www.beyonwiz.com.au/forum/viewforum.php?f=45

For the Beyonwiz V2, you will need to hold down the front power button while the unit is booting up.

For other models the procedure can be found here: http://www.beyonwiz.com.au/media/downloads/HowToUpgradeBeyonwizTSeriesV163.pdf