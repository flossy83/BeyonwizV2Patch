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



#### Emergency recovery:

In case the uninstallation steps did not work and the PVR becomes unresponsive, you may need to re-flash the original firmware, which can be obtained here: https://www.beyonwiz.com.au/forum/viewforum.php?f=45

For the Beyonwiz V2, you will need to hold down the front power button while the unit is booting up.

For other models the procedure can be found here: http://www.beyonwiz.com.au/media/downloads/HowToUpgradeBeyonwizTSeriesV163.pdf