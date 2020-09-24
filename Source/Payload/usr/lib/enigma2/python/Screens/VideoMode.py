from os import path
from enigma import iPlayableService, iServiceInformation, eTimer, eServiceCenter, eServiceReference, eDVBDB
from Screens.Screen import Screen
from Screens.ChannelSelection import FLAG_IS_DEDICATED_3D
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.AVSwitch import iAVSwitch
from boxbranding import getBoxType, getMachineBuild
from Components.Sources.FrontendStatus import FrontendStatus
from Components.Sources.FrontendInfo import FrontendInfo
import time
from Components.BeyonwizV2Patch import patchGeneral, patchHisi, log


resolutionlabel = None


class VideoSetup(Screen, ConfigListScreen):
	
	def __init__(self, session, menu_path=""):
		Screen.__init__(self, session)
		screentitle = _("Settings")
		if config.usage.show_menupath.value == 'large':
			menu_path += screentitle
			title = menu_path
			self["menu_path_compressed"] = StaticText("")
		elif config.usage.show_menupath.value == 'small':
			title = screentitle
			self["menu_path_compressed"] = StaticText(menu_path + " >" if not menu_path.endswith(' / ') else menu_path[:-3] + " >" or "")
		else:
			title = screentitle
			self["menu_path_compressed"] = StaticText("")
		self.skinName = ["Setup"]
		self.setup_title = title
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)
		self['footnote'] = Label()

		self.hw = iAVSwitch
		self.onChangedEntry = []

		# handle hotplug by re-creating setup
		self.onShow.append(self.startHotplug)
		self.onHide.append(self.stopHotplug)

		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)

		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions", "MenuActions"], {
			"cancel": self.keyCancel,
			"save": self.apply,
			"menu": self.closeRecursive,
		}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["description"] = Label("")

		self.createSetup()
		self.grabLastGoodMode()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def startHotplug(self):
		self.hw.on_hotplug.append(self.createSetup)

	def stopHotplug(self):
		self.hw.on_hotplug.remove(self.createSetup)

	def createSetup(self):
		level = config.usage.setup_level.index

		self.list = [
			getConfigListEntry(
				_("Video output"), config.av.videoport,
				_("Configures which video output connector will be used."))
		]
		if config.av.videoport.value in ('HDMI', 'YPbPr', 'Scart-YPbPr') and not path.exists(resolveFilename(SCOPE_PLUGINS) + 'SystemPlugins/AutoResolution'):
			
			if (patchGeneral):			
				self.list.append(getConfigListEntry(
				_("Automatic resolution"), config.av.autores,
				_("If enabled, the resolution of the video content will determine the output resolution.  Note: 2160p output modes will only be applied if you have confirmed your display supports 2160p by also setting the non-automatic mode to 2160p.")))			
			else:
				self.list.append(getConfigListEntry(
				_("Automatic resolution"), config.av.autores,
				_("If enabled, the output resolution will try to match the resolution of the video content.")))
			
			if config.av.autores.value:			
				if (patchGeneral):			
					self.list.append(getConfigListEntry(
					_("Delay time"), config.av.autores_delay,
					_("Sets the time delay before detecting the resolution, refresh rate and aspect ratio of the video content when it changes.")))		
				else:
					self.list.append(getConfigListEntry(
					_("Delay time"), config.av.autores_delay,
					_("Sets the time before checking the video source for resolution/refresh rate infomation.")))
					
				
				if (patchGeneral):
					self.list.append(getConfigListEntry(
					_("Automatic resolution label"), config.av.autores_label_timeout,
					_("Controls the display and duration of a notification label which pops up when the output resolution is automatically changed.")))
				else:
					self.list.append(getConfigListEntry(
					_("Automatic resolution label"), config.av.autores_label_timeout,
					_("Allows you to adjust the amount of time the resolution information display stays on screen.")))
						
				if (patchGeneral):
				
					self.list.append(getConfigListEntry(
						_("Output 2160p60 / 2160p30 as"), config.av.autores_uhd60,
						_("Choose the output mode when viewing 2160p60 / 2160p30 content.")))
					self.list.append(getConfigListEntry(
						_("Output 2160p50 / 2160p25 as"), config.av.autores_uhd50,
						_("Choose the output mode when viewing 2160p50 / 2160p25 content.")))
					self.list.append(getConfigListEntry(
						_("Output 2160p24 as"), config.av.autores_uhd24,
						_("Choose the output mode when viewing 2160p24 content.")))
									
					self.list.append(getConfigListEntry(
						_("Output 1080p60 / 1080p30 as"), config.av.autores_hd60p,
						_("Choose the output mode when viewing 1080p60 / 1080p30 content.")))
					self.list.append(getConfigListEntry(
						_("Output 1080p50 / 1080p25 as"), config.av.autores_hd50p,
						_("Choose the output mode when viewing 1080p50 / 1080p25 content.")))
						
					self.list.append(getConfigListEntry(
						_("Output 1080p24 as"), config.av.autores_hd24,
						_("Choose the output mode when viewing 1080p24 content.")))				
						
					self.list.append(getConfigListEntry(
						_("Output 1080i60 as"), config.av.autores_hd60i,
						_("Choose the output mode when viewing 1080i60 content.")))
					self.list.append(getConfigListEntry(
						_("Output 1080i50 as"), config.av.autores_hd50i,
						_("Choose the output mode when viewing 1080i50 content.")))
													
					self.list.append(getConfigListEntry(
						_("Output 720p60 / 720p30 as"), config.av.autores_ed60,
						_("Choose the output mode when viewing 720p60 / 720p30 content.")))								
					self.list.append(getConfigListEntry(
						_("Output 720p50 / 720p25 as"), config.av.autores_ed50,
						_("Choose the output mode when viewing 720p50 / 720p25 content.")))			
					self.list.append(getConfigListEntry(
						_("Output 720p24 as"), config.av.autores_ed24,
						_("Choose the output mode when viewing 720p24 content.")))				
					
					self.list.append(getConfigListEntry(
						_("Output 576p50 / 576p25 as"), config.av.autores_sd50p,
						_("Choose the output mode when viewing 576p50 / 576p25 content.")))
					self.list.append(getConfigListEntry(
						_("Output 576i50 as"), config.av.autores_sd50i,
						_("Choose the output mode when viewing 576i50 content.")))		

					self.list.append(getConfigListEntry(
						_("Output 480p60 / 480p30 as"), config.av.autores_sd60p,
						_("Choose the output mode when viewing 480p60 / 480p30 content.")))			
					self.list.append(getConfigListEntry(
						_("Output 480p24 as"), config.av.autores_sd24,
						_("Choose the output mode when viewing 480p24 content.")))				
					self.list.append(getConfigListEntry(
						_("Output 480i60 as"), config.av.autores_sd60i,
						_("Choose the output mode when viewing 480i60 content.")))
						
				elif (not patchGeneral):

					self.list.append(getConfigListEntry(
						_("Show 480 24Hz as"), config.av.autores_sd24,
						_("This option allows you to choose how to display 480 24Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 576 25Hz as"), config.av.autores_sd25,
						_("This option allows you to choose how to display 576 25Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 480 30Hz as"), config.av.autores_sd30,
						_("This option allows you to choose how to display 480 30Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 576i 50Hz as"), config.av.autores_sd50i,
						_("This option allows you to choose how to display 576i 50Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 576p 50Hz as"), config.av.autores_sd50p,
						_("This option allows you to choose how to display 576p 50Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 480i 60Hz as"), config.av.autores_sd60i,
						_("This option allows you to choose how to display 480i 60Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 480p 60Hz as"), config.av.autores_sd60p,
						_("This option allows you to choose how to display 480p 60Hz content.")))

					self.list.append(getConfigListEntry(
						_("Show 720 24Hz as"), config.av.autores_ed24,
						_("This option allows you to choose how to display 720 24Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 720 25Hz as"), config.av.autores_ed25,
						_("This option allows you to choose how to display 720 25Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 720 30Hz as"), config.av.autores_ed30,
						_("This option allows you to choose how to display 720 30Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 720 50Hz as"), config.av.autores_ed50,
						_("This option allows you to choose how to display 720 50Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 720 60Hz as"), config.av.autores_ed60,
						_("This option allows you to choose how to display 720 60Hz content.")))

					self.list.append(getConfigListEntry(
						_("Show 1080 24Hz as"), config.av.autores_hd24,
						_("This option allows you to choose how to display 1080 24Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 1080 25Hz as"), config.av.autores_hd25,
						_("This option allows you to choose how to display 1080 25Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 1080 30Hz as"), config.av.autores_hd30,
						_("This option allows you to choose how to display 1080 30Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 1080 50Hz as"), config.av.autores_hd50,
						_("This option allows you to choose how to display 1080 50Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 1080 60Hz as"), config.av.autores_hd60,
						_("This option allows you to choose how to display 1080 60Hz content.")))

					self.list.append(getConfigListEntry(
						_("Show 2160 24Hz as"), config.av.autores_uhd24,
						_("This option allows you to choose how to display 2160 24Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 2160 25Hz as"), config.av.autores_uhd25,
						_("This option allows you to choose how to display 2160 25Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 2160 30Hz as"), config.av.autores_uhd30,
						_("This option allows you to choose how to display 2160 30Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 2160 50Hz as"), config.av.autores_uhd50,
						_("This option allows you to choose how to display 2160 50Hz content.")))
					self.list.append(getConfigListEntry(
						_("Show 2160 60Hz as"), config.av.autores_uhd60,
						_("This option allows you to choose how to display 2160 60Hz content.")))

		# if we have modes for this port:
		if (config.av.videoport.value in config.av.videomode and not config.av.autores.value) or config.av.videoport.value == 'Scart':
			# add mode- and rate-selection:
			if (patchGeneral):
				self.list.append(getConfigListEntry(pgettext("Video output mode", "Mode"), config.av.videomode[config.av.videoport.value], _("Configures the video output resolution mode.")))
			else:
				self.list.append(getConfigListEntry(pgettext("Video output mode", "Mode"), config.av.videomode[config.av.videoport.value], _("This option configures the video output mode (or resolution).")))

			if config.av.videomode[config.av.videoport.value].value == 'PC':
				self.list.append(getConfigListEntry(_("Resolution"), config.av.videorate[config.av.videomode[config.av.videoport.value].value], _("This option configures the screen resolution in PC output mode.")))
			
			elif config.av.videoport.value != 'Scart':
				if (patchGeneral):
					self.list.append(getConfigListEntry(_("Refresh rate"), config.av.videorate[config.av.videomode[config.av.videoport.value].value], _("Configures the refresh rate of the screen.  If set to multi, the video content will determine the refresh rate (24hz/50hz/60hz).")))
				else:
					self.list.append(getConfigListEntry(_("Refresh rate"), config.av.videorate[config.av.videomode[config.av.videoport.value].value], _("Configure the refresh rate of the screen. Multi means refresh rate depends on the source 24/50/60Hz")))

		
		
		if (patchGeneral): 
			if (not config.av.autores.value): #avoid duplicate 
				self.list.append(getConfigListEntry(_("Delay time"), config.av.autores_delay,_("Sets the time delay before detecting the resolution, refresh rate and aspect ratio of the video content when it changes.")))
		else:
			if config.av.autores.value in ('all', 'hd') or config.av.videorate[config.av.videomode[config.av.videoport.value].value].value == 'multi':
				self.list.append(getConfigListEntry(_("Delay time"), config.av.autores_delay,_("Sets the time before checking the video source for resolution/refresh rate infomation.")))

		port = config.av.videoport.value
		if port not in config.av.videomode:
			mode = None
		else:
			mode = config.av.videomode[port].value

		
		force_wide = self.hw.isWidescreenMode(port, mode)

		if (patchGeneral):
			self.list.append(getConfigListEntry(_("Aspect ratio"), config.av.aspect, _("Set this value to the aspect ratio of your display screen.")))
			# Otherwise user could select 480/576, change the aspect, then select 720/1080/2160 
			# and still be in the 480/576 aspect without knowing it
		else:	
			if not force_wide:
				self.list.append(getConfigListEntry(_("Aspect ratio"), config.av.aspect, _("Set this value to the aspect ratio of your display screen.")))
			

		if (patchGeneral):
			if (patchHisi):
				if config.av.aspect.value == "16:9":
					self.list.append(getConfigListEntry(_("Display non-16:9 content as"), config.av.policy_43, _("When the content is not 16:9, choose how the picture should be displayed.")))
				elif config.av.aspect.value == "16:10":
					self.list.append(getConfigListEntry(_("Display non-16:10 content as"), config.av.policy_43, _("When the content is not 16:10, choose how the picture should be displayed.")))
				elif config.av.aspect.value == "4:3": 
					self.list.append(getConfigListEntry(_("Display non-4:3 content as"), config.av.policy_43, _("When the content is not 4:3, choose how the picture should be displayed.")))				
			else:
				if config.av.aspect.value in ("16:9", "16:10", "auto"):
					self.list.extend((
						getConfigListEntry(_("Display 4:3 content as"), config.av.policy_43, _("When the content has an aspect ratio of 4:3, choose how the picture should be displayed.")),
						getConfigListEntry(_("Display >16:9 content as"), config.av.policy_169, _("When the content has an aspect ratio wider than 16:9, choose how the picture should be displayed."))
					))
				elif config.av.aspect.value == "4:3":
					self.list.append(getConfigListEntry(_("Display 16:9 content as"), config.av.policy_169, _("When the content has an aspect ratio of 16:9, choose how the picture should be displayed.")))
				
				
		
		
		else:
			if force_wide or config.av.aspect.value in ("16:9", "16:10"):
				
				self.list.extend((
					getConfigListEntry(_("Display 4:3 content as"), config.av.policy_43, _("When the content has an aspect ratio of 4:3, choose whether to scale/stretch the picture.")),
					getConfigListEntry(_("Display >16:9 content as"), config.av.policy_169, _("When the content has an aspect ratio of 16:9, choose whether to scale/stretch the picture."))
				))
			
			elif config.av.aspect.value == "4:3":			
				self.list.append(getConfigListEntry(_("Display 16:9 content as"), config.av.policy_169, _("When the content has an aspect ratio of 16:9, choose whether to scale/stretch the picture.")))

		if config.av.videoport.value == "Scart":
			self.list.append(getConfigListEntry(_("Color format"), config.av.colorformat, _("Configure which color format should be used on the SCART output.")))
			if level >= 1:
				self.list.append(getConfigListEntry(_("WSS on 4:3"), config.av.wss, _("When enabled, content with an aspect ratio of 4:3 will be stretched to fit the screen.")))
				if SystemInfo["ScartSwitch"]:
					self.list.append(getConfigListEntry(_("Auto scart switching"), config.av.vcrswitch, _("When enabled, your receiver will detect activity on the VCR SCART input.")))

	
		if SystemInfo["havecolorspace"]:
			self.list.append(getConfigListEntry(_("HDMI colour space"), config.av.hdmicolorspace,_("Sets the encoding scheme used to define colour subcomponents.")))

		if SystemInfo["havecolorimetry"]:
			self.list.append(getConfigListEntry(_("HDMI colourimetry"), config.av.hdmicolorimetry,_("Sets the encoding scheme used to define the wavelength and luminance of colour subcomponents.")))

		if SystemInfo["havehdmicolordepth"]:
			self.list.append(getConfigListEntry(_("HDMI colour depth"), config.av.hdmicolordepth,_("Sets the encoding scheme used to define the number of steps of colour gradation.")))

		if SystemInfo["havehdmihdrtype"]:
			self.list.append(getConfigListEntry(_("HDMI HDR type"), config.av.hdmihdrtype,_("Sets the encoding scheme used to define luminance in high dynamic range content.")))

		if level >= 1:
			if SystemInfo["CanDownmixAC3"]:
				self.list.append(getConfigListEntry(_("AC3 downmix"), config.av.downmix_ac3, _("Choose whether multi channel AC3 (Dolby Digital) sound tracks should be downmixed to stereo.")))
			if SystemInfo["CanDownmixDTS"]:
				self.list.append(getConfigListEntry(_("DTS downmix"), config.av.downmix_dts, _("Choose whether multi channel DTS sound tracks should be downmixed to stereo.")))
			if SystemInfo["CanDownmixAAC"]:
				self.list.append(getConfigListEntry(_("AAC downmix"), config.av.downmix_aac, _("Choose whether multi channel AAC sound tracks should be downmixed to stereo.")))
			if SystemInfo["CanAACTranscode"]:
				self.list.append(getConfigListEntry(_("AAC transcoding"), config.av.transcodeaac, _("Choose whether AAC sound tracks should be transcoded.")))
			if SystemInfo["CanPcmMultichannel"]:
				self.list.append(getConfigListEntry(_("PCM Multichannel"), config.av.pcm_multichannel, _("Choose whether multi-channel sound tracks should be output as PCM.")))
			
			self.list.extend((
				getConfigListEntry(_("General AC3 delay"), config.av.generalAC3delay, _("Configures the general audio delay of Dolby Digital (AC3) sound tracks.")),
				getConfigListEntry(_("General PCM delay"), config.av.generalPCMdelay, _("Configures the general audio delay of stereo sound tracks."))
			))

			if SystemInfo["Can3DSurround"]:
				self.list.append(getConfigListEntry(_("3D Surround"), config.av.surround_3d,_("Configures the 3D surround sound feature.")))

			if SystemInfo["Can3DSpeaker"] and config.av.surround_3d.value != "none":
				self.list.append(getConfigListEntry(_("3D Surround Speaker Position"), config.av.surround_3d_speaker,_("Configures the speaker position for 3D surround sound.")))

			if SystemInfo["CanAutoVolume"]:
				self.list.append(getConfigListEntry(_("Auto Volume Level"), config.av.autovolume,_("Configures the auto volume level feature.")))

			if SystemInfo["Canedidchecking"]:
				self.list.append(getConfigListEntry(_("Bypass HDMI EDID Check"), config.av.bypass_edid_checking, _("If enabled, your display will not be checked for compatibility before setting a display mode.")))
				# appears broken on V2; AVSwitch.py appears to write invalid values (0/1) to
				# proc/stb/hdmi/bypass_edid_checking (default = "strict"; other values unknown).

		if SystemInfo["haveboxmode"]:
			self.list.append(getConfigListEntry(_("Video Chip Mode*"), config.av.boxmode,_("Choose between High Dynamic Range (HDR) or Picture in Picture (PIP). Both are not possible at the same time. A FULL REBOOT is required for it to take effect")))
			
		
		if (patchGeneral) and (not patchHisi):	
			self.list.append(getConfigListEntry(
				_("Video detection level"), config.av.autores_detectionlevel,
				_("If set to high, more system events will be monitored when trying to detect changes to the resolution, frame rate and aspect ratio of the video content.  If certain media files are not displaying as intended, try setting this value to high, otherwise the recommended value is normal.")))
	

		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if config.usage.sort_settings.value:
			self["config"].list.sort()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def confirm(self, confirmed):
		
		if (patchGeneral):
			
			if not confirmed:
				config.av.videoport.setValue(self.last_good[0])
				config.av.videomode[self.last_good[0]].setValue(self.last_good[1])
				config.av.videorate[self.last_good[1]].setValue(self.last_good[2])
				self.hw.setMode(*self.last_good)
				self.createSetup() # otherwise GUI doesn't get updated
			else:
				self.keySave()	
			
			if (patchHisi):
				# Prevent driver applying proc/stb/video/videomode_Nhz on zap causing redundant mode changes
				port = config.av.videoport.value
				mode = config.av.videomode[port].value
				rate = config.av.videorate[mode].value
				log("VideoSetup.confirm() autores:%s, rate:%s" % (config.av.autores.value, rate))
				if (config.av.autores.value) or (rate == "multi"):
					current_mode = getOutputMode("", "VideoSetup.confirm() ")
					if (current_mode != "unsupported"):
						setOutputMode(current_mode, "_50hz", "VideoSetup.confirm() ")
						setOutputMode(current_mode, "_60hz", "VideoSetup.confirm() ")
						setOutputMode(current_mode, "_24hz", "VideoSetup.confirm() ")
						
				if (AutoVideoMode.LastInstance != None):
					AutoVideoMode.LastInstance.previous_tuner_type = None
					# AutoVideoMode.LastInstance.previous_dynamic_range = None
					AutoVideoMode.LastInstance.VideoChangeDetect("VideoSetup.confirm() ")
				
		else:			
			if not confirmed:
				config.av.videoport.setValue(self.last_good[0])
				config.av.videomode[self.last_good[0]].setValue(self.last_good[1])
				config.av.videorate[self.last_good[1]].setValue(self.last_good[2])
				self.hw.setMode(*self.last_good)
			else:
				self.keySave()

	def grabLastGoodMode(self):
		port = config.av.videoport.value
		mode = config.av.videomode[port].value
		rate = config.av.videorate[mode].value
		self.last_good = (port, mode, rate)

	def saveAll(self):
		if config.av.videoport.value == 'Scart':
			config.av.autores.setValue(False)
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	def apply(self):
	
		if (patchGeneral):
			
			port = config.av.videoport.value
			mode = config.av.videomode[port].value
			rate = config.av.videorate[mode].value
						
			if not (config.av.autores.value):
				self.hw.setMode(port, mode, rate)
			
			if (not config.av.autores.value) and ((port, mode, rate) != self.last_good):
				from Screens.MessageBox import MessageBox
				self.session.openWithCallback(self.confirm, MessageBox, _("Is this video mode OK?"), MessageBox.TYPE_YESNO, timeout=20, default=False)
			else:
				self.keySave()				
				
				if (patchHisi):
					# Prevent driver applying proc/stb/video/videomode_Nhz on zap causing redundant mode changes
					log("VideoSetup.apply() autores:%s, rate:%s" % (config.av.autores.value, rate))
					if (config.av.autores.value) or (rate == "multi"):
						current_mode = getOutputMode("", "VideoSetup.apply() ")
						if (current_mode != "unsupported"):
							setOutputMode(current_mode, "_50hz", "VideoSetup.apply() ")
							setOutputMode(current_mode, "_60hz", "VideoSetup.apply() ")
							setOutputMode(current_mode, "_24hz", "VideoSetup.apply() ")
					
					if (AutoVideoMode.LastInstance != None):
						AutoVideoMode.LastInstance.previous_tuner_type = None
						# AutoVideoMode.LastInstance.previous_dynamic_range = None
						AutoVideoMode.LastInstance.VideoChangeDetect("VideoSetup.apply() ")
	
		else:
			port = config.av.videoport.value
			mode = config.av.videomode[port].value
			rate = config.av.videorate[mode].value
			if (port, mode, rate) != self.last_good:
				self.hw.setMode(port, mode, rate)
				from Screens.MessageBox import MessageBox
				self.session.openWithCallback(self.confirm, MessageBox, _("Is this video mode OK?"), MessageBox.TYPE_YESNO, timeout=20, default=False)
			else:
				self.keySave()
	
	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

		
class AutoVideoModeLabel(Screen):

	def __init__(self, session):

		Screen.__init__(self, session)
		
		self["content"] = Label()
		self["restxt"] = Label()

		self.hideTimer = eTimer()
		self.hideTimer.callback.append(self.hide)

		self.onShow.append(self.hide_me)

	def hide_me(self):
		idx = config.av.autores_label_timeout.index
		if idx:
			idx += 4
			self.hideTimer.start(idx * 1000, True)
	
	
previous = None
isDedicated3D = False


def applySettings(mode=config.osd.threeDmode.value, znorm=int(config.osd.threeDznorm.value)):
	global previous, isDedicated3D
	mode = isDedicated3D and mode == "auto" and "sidebyside" or mode
	mode == "3dmode" in SystemInfo["3DMode"] and mode or mode == 'sidebyside' and 'sbs' or mode == 'topandbottom' and 'tab' or 'off'
	if previous != (mode, znorm):
		try:
			open(SystemInfo["3DMode"], "w").write(mode)
			open(SystemInfo["3DZNorm"], "w").write('%d' % znorm)
			previous = (mode, znorm)
		except:
			return

			
class AutoVideoMode(Screen):
	
	LastInstance = None

	def __init__(self, session):
		
		AutoVideoMode.LastInstance = self		
		Screen.__init__(self, session)
		self.current3dmode = config.osd.threeDmode.value

		
		self.retry = True
		self.bufferfull = True
		self.detecttimer = eTimer()
		self.detecttimer.callback.append(self.VideoChangeDetect)
		
		if (patchHisi):
			self.ptsInfoLastFPS = None
			self.ptsInfoCount = 0
			self.ptsInfoCountMax = 1
			self.ptsInfoFrequency = 3000
			self.ptsInfoTimer = eTimer()
			self.ptsInfoTimer.callback.append(self.monitorPtsInfo)
			self.previous_tuner_type = None		
			self.hdrTimer = eTimer()
			self.hdrTimer.callback.append(self.cycleHdrType)
			self.previous_dynamic_range = "SDR"				
			self.monitor_EMI = False
			self.previous_video_framerate = None
			self.cycleFPStimer = eTimer()
			self.restoreFPStimer = eTimer()	
			self.cycleFPStimer.callback.append(self.cycleFPS)			
			self.restoreFPStimer.callback.append(self.restoreFPS)
			
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
		{
			iPlayableService.evStart: self.__evStart,
			iPlayableService.evTunedIn: self.__evTunedIn,		
			iPlayableService.evVideoSizeChanged: self.__evVideoSizeChanged,
			iPlayableService.evVideoProgressiveChanged: self.__evVideoProgressiveChanged,
			iPlayableService.evVideoFramerateChanged: self.__evVideoFramerateChanged,
			iPlayableService.evBuffering: self.__evBuffering,
			iPlayableService.evEnd: self.__evEnd,		
			# iPlayableService.evTuneFailed: self.__evTuneFailed,	
			# iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
			# iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
			# iPlayableService.evNewProgramInfo: self.__evNewProgramInfo,
			# iPlayableService.evSOF: self.__evSOF,
			# iPlayableService.evEOF: self.__evEOF,
			# iPlayableService.evSeekableStatusChanged: self.__evSeekableStatusChanged,
			# iPlayableService.evCuesheetChanged: self.__evCuesheetChanged,		
			# iPlayableService.evStopped: self.__evStopped,
			# iPlayableService.evHBBTVInfo: self.__evHBBTVInfo,
			# iPlayableService.evUser: self.__evUser,	
		})
	
	def checkIfDedicated3D(self):
			service = self.session.nav.getCurrentlyPlayingServiceReference()
			servicepath = service and service.getPath()
			if servicepath and servicepath.startswith("/"):
					if service.toString().startswith("1:"):
						info = eServiceCenter.getInstance().info(service)
						service = info and info.getInfoString(service, iServiceInformation.sServiceref)
						return service and eDVBDB.getInstance().getFlag(eServiceReference(service)) & FLAG_IS_DEDICATED_3D == FLAG_IS_DEDICATED_3D and "sidebyside"
					else:
						return ".3d." in servicepath.lower() and "sidebyside" or ".tab." in servicepath.lower() and "topandbottom"
			service = self.session.nav.getCurrentService()
			info = service and service.info()
			return info and info.getInfo(iServiceInformation.sIsDedicated3D) == 1 and "sidebyside"

	def __evStart(self):

		if (patchGeneral):
			log("__evStart()")
			self.retry = True
			if (config.av.autores_detectionlevel.value == "High"):			
				self.VideoChanged("__evStart() ")
			
		if config.osd.threeDmode.value == "auto":
			global isDedicated3D
			isDedicated3D = self.checkIfDedicated3D()
			if isDedicated3D:
				applySettings(isDedicated3D)
			else:
				applySettings()
			
	def __evTunedIn(self):
		
		if (patchHisi) and (self.monitor_EMI == True):
			log("__evTunedIn() EMI detected; cycling decoder FPS in 5 seconds")
			self.cycleFPStimer.stop()
			self.restoreFPStimer.stop()
			self.cycleFPStimer.start(5000, True)
	
	def __evEnd(self):
	
		if (patchGeneral): 
			
			logStr = "__evEnd() "
			self.detecttimer.stop()
			
			if (patchHisi):	
				
				self.monitor_EMI = False
				self.cycleFPStimer.stop()
				self.restoreFPStimer.stop()
				self.hdrTimer.stop()
				self.ptsInfoTimer.stop()
				self.ptsInfoCount = 0
				self.ptsInfoLastFPS = None
			
				# If user zaps again while detecttimer is still active, 
				# previous_tuner_type and previous_dynamic_range won't be updated		
				try:
					info = self.session.nav.getCurrentService().info()
					tData = info.getInfoObject(iServiceInformation.sTransponderData)
					tuner_type = tData.get("tuner_type", "None")
					if (tuner_type != self.previous_tuner_type):
						logStr += "tuner_type changed; resetting previous_tuner_type"
						self.previous_tuner_type = None
				except: tuner_type = "None"
				

				dynamic_range = getDynamicRange()
				if (dynamic_range != self.previous_dynamic_range):
					if not ("DVB" in tuner_type and dynamic_range == None):
						logStr += "dynamic_range changed; resetting previous_dynamic_range"
						self.previous_dynamic_range = None
					
			log(logStr)
									
	def __evVideoSizeChanged(self):
		log("__evVideoSizeChanged()")
		self.VideoChanged("__evVideoSizeChanged() ")
	
	def __evVideoProgressiveChanged(self):
		log("__evVideoProgressiveChanged()")
		self.VideoChanged("__evVideoProgressiveChanged() ")
		
	def __evVideoFramerateChanged(self):
		log("__evVideoFramerateChanged()")
		self.VideoChanged("__evVideoFramerateChanged() ")
	
	def __evBuffering(self):
		log("__evBuffering()")
		bufferInfo = self.session.nav.getCurrentService().streamed().getBufferCharge()
		if bufferInfo[0] > 98:
			self.bufferfull = True
			self.VideoChanged("__evBuffering() ")
		else:
			self.bufferfull = False
	
	def VideoChanged(self, caller=""):
		
		# if (patchGeneral): log("%sVideoChanged() " % caller)
		
		delay = config.av.autores_delay.value
		service = self.session.nav.getCurrentlyPlayingServiceReference()
		
		if (service) and (service.toString().startswith('4097:')):	
			if not patchGeneral: delay = delay * 2
			elif not patchHisi: delay = delay + 2000
		if (patchGeneral) and (caller == "__evStart() "): delay += 2000
				
		self.detecttimer.stop()
		self.detecttimer.start(delay, True)
					
	def VideoChangeDetect(self, caller=""):		
			
		global resolutionlabel
		
		if (patchGeneral):			
			
			log("%sVideoChangeDetect() start" % caller)
	
			# Get "global" video output mode from config
			config_port = config.av.videoport.value
			config_mode = str(config.av.videomode[config_port].value).strip() #576i,576p,720p,1080p,2160p (no rate)
			config_res = str(config.av.videomode[config_port].value).strip()[:-1] #576,720,1080,2160 (no suffix)
			config_rate_hz = str(config.av.videorate[config_mode].value).strip() #50Hz,60Hz,multi (GUI value)
			config_rate = config_rate_hz.replace('Hz', '') #50,60,multi
			config_mode = "576i" if (config_mode.upper() == "PAL") else config_mode	
			config_mode = "480i" if (config_mode.upper() == "NTSC") else config_mode
					
			
			# Get service info
			info = None
			try: info = self.session.nav.getCurrentService().info()
			except: pass		
			if not info:			
				logStr = "%sVideoChangeDetect() failed to get service info" % caller						
				if (self.retry): logStr += "; retrying once more"
				else: logStr += "; returning"
				log(logStr)
				if (self.retry): self.retry = False; self.VideoChanged("%sVideoChangeDetect() " % caller)
				return
			tData = info.getInfoObject(iServiceInformation.sTransponderData)			
			tuner_type = tData.get("tuner_type", "None")
			
				
			# Determine switching_mode (multi and autores can both be enabled; autores takes priority)
			switching_mode = "autores" if (config.av.autores.value) else "multi" if (config_rate == "multi") else False
			

			# Get current output mode (eg. 576i, 576p, 720p, 720p50, 1080p, 1080p50 etc.)		
			current_mode = getOutputMode("", "%sVideoChangeDetect() " % caller)
			current_mode_50hz = getOutputMode("_50hz", "%sVideoChangeDetect() " % caller)
			current_mode_60hz = getOutputMode("_60hz", "%sVideoChangeDetect()" % caller)
			current_mode_24hz = getOutputMode("_24hz", "%sVideoChangeDetect()" % caller)
			log("%sVideoChangeDetect() got current_mode=%s, 50hz=%s, 60hz=%s, 24hz=%s" \
				% (caller, current_mode, current_mode_50hz, current_mode_60hz, current_mode_24hz))


			# Get video stream info	
			video_height = int(info.getInfo(iServiceInformation.sVideoHeight))
			video_width = int(info.getInfo(iServiceInformation.sVideoWidth))
			video_framerate = int(info.getInfo(iServiceInformation.sFrameRate))
			video_progressive = int(info.getInfo(iServiceInformation.sProgressive))
										# 2160x3840 vertical videos	  
			if not ((0 < video_height <= 3840) and (0 < video_width <= 4096)):
				def _fromProc(pathname, base=10):
					res = None
					if path.exists(pathname):
						f = open(pathname, "r")
						try:
							val = int(f.read(), base)
							if val >= 0: res = val
						except: pass
						f.close()
					return res
				video_width = _fromProc("/proc/stb/vmpeg/0/xres", 16)
				video_height = _fromProc("/proc/stb/vmpeg/0/yres", 16)		
				video_framerate = _fromProc("/proc/stb/vmpeg/0/framerate")
				video_progressive = _fromProc("/proc/stb/vmpeg/0/progressive")		
			video_progressive = 1 if (video_progressive != 0) else video_progressive
						
			pts_info_success = False		
			if (patchHisi):
				# try to get video_framerate from /proc/vfmw/pts_info instead (more reliable)
				pts_info_fps = getPtsInfoFPS()
				if isinstance(pts_info_fps, int):
					pts_info_success = True
					video_framerate = pts_info_fps

			if 	not (isinstance(video_width, int) and isinstance(video_height, int) and
				isinstance(video_framerate, int) and isinstance(video_progressive, int) and
				(0 < video_width <= 4096) and (0 < video_height <= 3840) and
				(5000 <= video_framerate <= 120000)):
				logStr = "%sVideoChangeDetect() failed to get video stream info from service or proc" % caller
				if (self.retry): logStr += "; retrying once more"
				else: logStr += "; returning"
				log(logStr)
				if (self.retry): self.retry = False; self.VideoChanged("%sVideoChangeDetect() " % caller)
				return		
			
			log("%sVideoChangeDetect() got stream info: w=%s, h=%s, fps=%s, p=%s, pts_info=%s" \
				% (caller, video_width, video_height, video_framerate, video_progressive, pts_info_success))
			
			

			# Determine new output res and framerate 
			# Note: this algorithm chooses the nearest res which won't result in
			# resolution loss.  eg. 854x480 will resolve to 720 rather than 480
			# since 480 is 720x480 which is less than 854x480.
			# Test script: https://pastebin.com/j3n8SDCE 
			if (video_width >= video_height):
				vertical_video = False
				if	(video_width > 1920) or (video_height > 1088): new_res = "2160"
				elif (video_width > 1280) or (video_height > 720): new_res = "1080"						
				elif (video_width > 720): new_res = "720"
				elif (video_height > 480): new_res = "576"		
				elif (video_height <= 480): new_res = "480"
				else: new_res = config_res
			else:
				vertical_video = True # vertical phone video
				if (video_height > 1088): new_res = "2160"
				elif (video_height > 720): new_res = "1080"
				elif (video_height > 576): new_res = "720"
				elif (video_height > 480): new_res = "576"
				elif (video_height <= 480): new_res = "480"
				else: new_res = config_res
	
			new_rate = None		
			if (patchHisi) and (getBoxType() == "beyonwizv2" or getMachineBuild() == "beyonwizv2"):		
				# Beyonwiz V2-specific bodge: Since DVB is zap-intensive, the probability of incorrect
				# frame rate detection is much higher, so we'll force 50hz for DVB only.  
				# Non-DVB sources will be checked again <ptsInfoFrequency> seconds after zap.
				if ("DVB" in tuner_type) and (video_framerate not in (25000, 50000)):				
					new_rate = "50"			
					log("%sVideoChangeDetect() tuner_type=%s; video_framerate=%s; forcing new_rate=%s" \
						% (caller, tuner_type, video_framerate, new_rate))			
				else:				
					log("%sVideoChangeDetect() tuner_type=%s; using detected video_framerate=%s" \
						% (caller, tuner_type, video_framerate))
			
			if not new_rate:
				if video_framerate in (25000, 50000): new_rate = "50"
				elif video_framerate in (29970, 30000, 59940, 60000): new_rate = "60"
				elif video_framerate in (23976, 24000) and SystemInfo["have24hz"]: new_rate = "24"
				else:
					if (switching_mode == "multi"): new_rate = "50"
					else: new_rate = config_rate
						
						
			# edge cases: 480p50, 576p60
			if (new_res == "480" and new_rate == "50"): new_res = "576"
			elif (new_res == "576" and new_rate == "60"): new_res = "720"
						
			log("%sVideoChangeDetect() inferred new_res=%s, new_rate=%s, vertical_video=%s" % (caller, new_res, new_rate, vertical_video))
			
		
		
			# fix HDR colour bug
			if (patchHisi):
				dynamic_range = getDynamicRange(); play_state = getPlayState()				
				if (dynamic_range != None) and (play_state != None):			
					if (dynamic_range != self.previous_dynamic_range):				
						if (play_state == "PLAY"):
							self.cycleHdrType(True, "%sVideoChangeDetect() " % caller)
						else:
							log("%sVideoChangeDetect() couldn't cycle HDR type; video paused; " \
								"trying again in 5 seconds" % caller)
							self.hdrTimer.stop()
							self.hdrTimer.start(5000, True)					
					self.previous_dynamic_range = dynamic_range # also on evEnd
					
			
			
			# enable frame rate stutter fix on DVB signal interference
			if (patchHisi) and ("DVB" in tuner_type) and (int(new_res) >= 720):
				self.previous_video_framerate = video_framerate
				self.monitor_EMI = True
					
				

			# return if autores and multi are disabled
			if not switching_mode:
				log("%sVideoChangeDetect() autores and multi are disabled; setting aspect and returning" % caller)
				self.setAspect(tuner_type, "%sVideoChangeDetect() " % caller)
				return
			
			
			
			# determine new output mode string
			new_mode = None				
			if (switching_mode == "multi"):		
				try:
					new_mode = iAVSwitch.rates[config_mode]["multi"][int(new_rate)]
					log("%sVideoChangeDetect() multi: got new_mode=%s from AVSwitch.rates[config_mode][\"multi\"]" \
						% (caller, new_mode))
				except:
					log("%sVideoChangeDetect() multi: failed to get new_mode from AVSwitch.rates[config_mode][\"multi\"]" \
						% caller)		
			
			if (switching_mode == "autores"):	
				if new_res == "480" and new_rate == "24":
					new_mode = config.av.autores_sd24.value
				elif new_res == "576" and new_rate == "50" and video_progressive == 0:
					new_mode = config.av.autores_sd50i.value
				elif new_res == "576" and new_rate == "50" and video_progressive == 1: 
					new_mode = config.av.autores_sd50p.value
				elif new_res == "480" and new_rate == "60" and video_progressive == 0:
					new_mode = config.av.autores_sd60i.value
				elif new_res == "480" and new_rate == "60" and video_progressive == 1: 
					new_mode = config.av.autores_sd60p.value
				elif new_res == "720" and new_rate == "24":
					new_mode = config.av.autores_ed24.value
				elif new_res == "720" and new_rate == "50":
					new_mode = config.av.autores_ed50.value
				elif new_res == "720" and new_rate == "60":
					new_mode = config.av.autores_ed60.value
				elif new_res == "1080" and new_rate == "24":
					new_mode = config.av.autores_hd24.value
				elif new_res == "1080" and new_rate == "50" and video_progressive == 0:
					new_mode = config.av.autores_hd50i.value				
				elif new_res == "1080" and new_rate == "50" and video_progressive == 1:
					new_mode = config.av.autores_hd50p.value	
				elif new_res == "1080" and new_rate == "60" and video_progressive == 0:
					new_mode = config.av.autores_hd60i.value
				elif new_res == "1080" and new_rate == "60" and video_progressive == 1:
					new_mode = config.av.autores_hd60p.value
				elif new_res == "2160" and new_rate == "24":
					new_mode = config.av.autores_uhd24.value
				elif new_res == "2160" and new_rate == "50":
					new_mode = config.av.autores_uhd50.value
				elif new_res == "2160" and new_rate == "60":
					new_mode = config.av.autores_uhd60.value
					
				if (new_mode):
					
					log("%sVideoChangeDetect() autores: found matching mode in config.av.autores: %s" \
						% (caller, new_mode))			
					if (new_mode.endswith("60")) or (new_mode.startswith("576")):
						new_mode = new_mode[:-2]
	
				if (not new_mode) or (("2160" in new_mode) and (config_mode != "2160p")):
					
					if (not new_mode):
						log("%sVideoChangeDetect() autores: failed to find a matching mode in config.av.autores" % caller)
					
					elif ("2160" in new_mode) and (config_mode != "2160p"):  # Avoid black screen on non-4k displays
						log("%sVideoChangeDetect() autores: new_mode=2160 and config_mode!=2160p" % caller)					
					
					log("%sVideoChangeDetect() autores: falling back to AVSwitch.rates[config_mode]" % caller)			
					try:
						new_mode = iAVSwitch.rates[config_mode]["multi"][int(new_rate)]
						log("%sVideoChangeDetect() autores: found matching mode in " \
							"AVSwitch.rates[config_mode][\"multi\"]: %s" % (caller, new_mode))
					except:
						try: 
							new_mode = iAVSwitch.rates[config_mode][config_rate_hz][int(new_rate)]
							log("%sVideoChangeDetect() autores: found matching mode in " \
								"AVSwitch.rates[config_mode]: %s" % (caller, new_mode))					
						except:
							log("%sVideoChangeDetect() autores: failed fallback to AVSwitch.rates[config_mode]" % caller)

				if (new_mode):
					if new_mode.startswith("576"): # 576i,576p
						new_mode_label = new_mode + "50" 
					elif new_mode.endswith("i") or new_mode.endswith("p"): # 480i,480p,720p,1080i,1080p,2160p
						new_mode_label = new_mode + "60"
					else: # 720p24,720p50,1080i50,1080p24,1080p50,2160p24,2160p50
						new_mode_label = new_mode
	
		
			
			# Set new output mode			
			if (new_mode != None):
			
				if (current_mode != "unsupported") and (new_mode != current_mode):			
					
					setOutputMode(new_mode, "", "%sVideoChangeDetect() " % caller)			
					# Show autores label
					if (switching_mode == "autores"):
						
						p_string = "i" if (video_progressive == 0) else "p"			
						label_rate = (2 * video_framerate) if (video_progressive == 0) else video_framerate
						label_rate = (label_rate + 500) / 1000					
						resolutionlabel["content"].setText("%s %s%s%s" % (_("        Video content:"), new_res, p_string, label_rate))
						resolutionlabel["restxt"].setText(_("        Video mode: %s") % new_mode_label)
						# unable to override skin in class AutoVideoModeLabel
						resolutionlabel.hide()
						if int(config.av.autores_label_timeout.value) > 0:
							resolutionlabel.show()
				else:
					log("%sVideoChangeDetect() skipped writing new_mode (current_mode=new_mode or unsupported)" % caller)	
				
				
				if (patchHisi):
				# Prevent driver applying proc/stb/video/videomode_Nhz on every zap causing redundant mode changes
					if (current_mode_50hz != "unsupported") and (new_mode != current_mode_50hz):
						setOutputMode(new_mode, "_50hz", "%sVideoChangeDetect() " % caller)
					else:
						log("%sVideoChangeDetect() skipped writing 50hz new_mode " \
							"(current_mode_50hz=new_mode or unsupported)" % caller)				
					if (current_mode_60hz != "unsupported") and (new_mode != current_mode_60hz):
						setOutputMode(new_mode, "_60hz", "%sVideoChangeDetect() " % caller)
					else:
						log("%sVideoChangeDetect() skipped writing 60hz new_mode " \
							"(current_mode_60hz=new_mode or unsupported)" % caller)			
					if (current_mode_24hz != "unsupported") and (new_mode != current_mode_24hz):
						setOutputMode(new_mode, "_24hz", "%sVideoChangeDetect() " % caller)
					else:
						log("%sVideoChangeDetect() skipped writing 24hz new_mode " \
							"(current_mode_24hz=new_mode or unsupported)" % caller)
				
					
					# fix colour space reverting to RGB after setting 2160
					if (current_mode != "unsupported") and (new_mode != current_mode):	
						
						cycler = {"444":"rgb","422":"rgb","rgb":"444","auto":"444"}
						previous_colorspace = config.av.hdmicolorspace.value					
						log("%sVideoChangeDetect() cycling colour space from %s to %s to %s" \
							% (caller, previous_colorspace, cycler[config.av.hdmicolorspace.value], previous_colorspace))
						
						config.av.hdmicolorspace.value = cycler[config.av.hdmicolorspace.value]
						# time.sleep(0.05)
						config.av.hdmicolorspace.value = previous_colorspace
						
						# untested but may be preferable to relying on config notifiers
						# current_colorspace = config.av.hdmicolorspace.value
						# cycled_colorspace = cycler[config.av.hdmicolorspace.value]
						# log("%sVideoChangeDetect() cycling colour space from %s to %s to %s" \
							# % (caller, current_colorspace, cycled_colorspace, current_colorspace))
						# try:
							# f=open("/proc/stb/video/hdmi_colorspace","w");f.write(cycled_colorspace);f.close() 
							# f=open("/proc/stb/video/hdmi_colorspace","w");f.write(current_colorspace);f.close()
						# except: log("%sVideoChangeDetect() failed to cycle colour space" % caller)
					
					
					# monitor proc/vfmw/pts_info for framerate change
					if (caller == "monitorPtsInfo() "):
						self.ptsInfoTimer.stop()
						self.ptsInfoCount = 0
						self.ptsInfoLastFPS = None				
					else:
						if (video_framerate == 30000) and ("DVB" not in tuner_type):
							self.ptsInfoTimer.stop()
							self.ptsInfoCount = 0
							self.ptsInfoLastFPS = video_framerate
							self.ptsInfoTimer.start(self.ptsInfoFrequency, True)
							log("%sVideoChangeDetect() checking framerate from pts_info " \
								"in %s seconds" % (caller, self.ptsInfoFrequency/1000))
					

			else:
				log("%sVideoChangeDetect() skipped writing new_mode (new_mode=None)" % caller)

			self.setAspect(tuner_type, "%sVideoChangeDetect() " % caller)
			
			log("%sVideoChangeDetect() finish" % caller)
	
		elif (not patchGeneral):
		
			config_port = config.av.videoport.value
			config_mode = str(config.av.videomode[config_port].value).strip()
			config_res = str(config.av.videomode[config_port].value).strip()[:-1]
			config_rate = str(config.av.videorate[config_mode].value).strip().replace('Hz', '')

			if not (config_rate == "multi" or config.av.autores.value):
				return

			if config_mode.upper() == 'PAL':
				config_mode = "576i"
			if config_mode.upper() == 'NTSC':
				config_mode = "480i"

			f = open("/proc/stb/video/videomode")
			current_mode = f.read().strip()
			f.close()
			if current_mode.upper() == 'PAL':
				current_mode = "576i"
			if current_mode.upper() == 'NTSC':
				current_mode = "480i"

			service = self.session.nav.getCurrentService()
			if not service:
				return

			info = service.info()
			if not info:
				return

			video_height = int(info.getInfo(iServiceInformation.sVideoHeight))
			video_width = int(info.getInfo(iServiceInformation.sVideoWidth))
			video_framerate = int(info.getInfo(iServiceInformation.sFrameRate))
			video_progressive = int(info.getInfo(iServiceInformation.sProgressive))

			if not ((0 < video_height <= 2160) and (0 < video_width <= 4096)):

				def _fromProc(pathname, base=10):
					res = None
					if path.exists(pathname):
						f = open(pathname, "r")
						try:
							val = int(f.read(), base)
							if val >= 0:
								res = val
						except:
							pass
						f.close()
					return res

				video_height = _fromProc("/proc/stb/vmpeg/0/yres", 16)
				video_width = _fromProc("/proc/stb/vmpeg/0/xres", 16)
				video_framerate = _fromProc("/proc/stb/vmpeg/0/framerate")
				video_progressive = _fromProc("/proc/stb/vmpeg/0/progressive")

			if not ((0 < video_height <= 2160) and (0 < video_width <= 4096)):
				print "[VideoMode] Can not determine video characteristics from service or /proc - do nothing"
				return

			if video_progressive == 0:
				video_fieldrate = 2 * video_framerate
			else:
				video_fieldrate = video_framerate


			p_string = ""
			if video_progressive == 0:
				p_string = "i"
			elif video_progressive == 1:
				p_string = "p"

			resolutionlabel["content"].setText("%s %ix%i%s %iHz" % (_("Video content:"), video_width, video_height, p_string, (video_fieldrate + 500) / 1000))

			if (700 < video_width <= 720) and video_height <= 480 and video_framerate in (23976, 24000, 29970, 30000, 59940, 60000):
				new_res = "480"
			elif (700 < video_width <= 720) and video_height <= 576 and video_framerate in (25000, 50000):
				new_res = "576"
			elif (video_width == 1280) and video_height <=720:
				new_res = "720"
			else:
				new_res = config_res

			new_rate = config_rate

			if config.av.autores.value and video_framerate > 0:
				new_rate = str((video_fieldrate + 500) / 1000)

			if new_rate == "multi":
				if video_framerate in (25000, 50000):
					new_rate = "50"
				elif SystemInfo["have24hz"] and video_framerate in (23976, 24000):
					new_rate = "24"
				else:
					new_rate = "60"

			new_mode = None
			if config.av.autores.value:
				if new_res == "480" and new_rate == "24":
					new_mode = config.av.autores_sd24.value
				elif new_res == "576" and new_rate == "25":
					new_mode = config.av.autores_sd25.value
				elif new_res == "480" and new_rate == "30":
					new_mode = config.av.autores_sd30.value
				elif new_res == "576" and new_rate == "50" and video_progressive == 0:
					new_mode = config.av.autores_sd50i.value
				elif new_res == "576" and new_rate == "50" and video_progressive == 1:
					new_mode = config.av.autores_sd50p.value
				elif new_res == "480" and new_rate == "60" and video_progressive == 0:
					new_mode = config.av.autores_sd60i.value
				elif new_res == "480" and new_rate == "60" and video_progressive == 1:
					new_mode = config.av.autores_sd60p.value
				elif new_res == "720" and new_rate == "24":
					new_mode = config.av.autores_ed24.value
				elif new_res == "720" and new_rate == "25":
					new_mode = config.av.autores_ed25.value
				elif new_res == "720" and new_rate == "30":
					new_mode = config.av.autores_ed30.value
				elif new_res == "720" and new_rate == "50":
					new_mode = config.av.autores_ed50.value
				elif new_res == "720" and new_rate == "60":
					new_mode = config.av.autores_ed60.value
				elif new_res == "1080" and new_rate == "24":
					new_mode = config.av.autores_hd24.value
				elif new_res == "1080" and new_rate == "25":
					new_mode = config.av.autores_hd25.value
				elif new_res == "1080" and new_rate == "30":
					new_mode = config.av.autores_hd30.value
				elif new_res == "1080" and new_rate == "50":
					new_mode = config.av.autores_hd50.value
				elif new_res == "1080" and new_rate == "60":
					new_mode = config.av.autores_hd60.value
				elif new_res == "2160" and new_rate == "24":
					new_mode = config.av.autores_uhd24.value
				elif new_res == "2160" and new_rate == "25":
					new_mode = config.av.autores_uhd25.value
				elif new_res == "2160" and new_rate == "30":
					new_mode = config.av.autores_uhd30.value
				elif new_res == "2160" and new_rate == "50":
					new_mode = config.av.autores_uhd50.value
				elif new_res == "2160" and new_rate == "60":
					new_mode = config.av.autores_uhd60.value
				else:
					print "[VideoMode] autores could not find a mode for res=%s, rate=%s" % (new_res, new_rate)
			elif config_rate == 'multi' and path.exists('/proc/stb/video/videomode_%shz' % new_rate):
				try:
					f = open("/proc/stb/video/videomode_%shz" % new_rate, "r")
					multi_videomode = f.read().strip()
					f.close()
					if multi_videomode:
						new_mode = multi_videomode
				except:
					print "[VideoMode] exception when trying to find multi mode for", new_rate

			if not new_mode:
				print "[VideoMode] still don't have a new_mode making one from config_mode=%s, newrate=%s" % (config_mode, new_rate)
				new_mode = config_mode + new_rate

			if new_mode != current_mode:
				try:
					f = open("/proc/stb/video/videomode", "w")
					f.write(new_mode)
					f.close()

					resolutionlabel["restxt"].setText(_("Video mode: %s") % new_mode)
					resolutionlabel.hide()  # Need to hide then show to restart the timer
					if config.av.autores.value and int(config.av.autores_label_timeout.value) > 0:
						resolutionlabel.show()
				except:
					print "[VideoMode] FAILED to setMode - port: %s, mode: %s" % (config_port, new_mode)

			iAVSwitch.setAspect(config.av.aspect)
			iAVSwitch.setWss(config.av.wss)
			iAVSwitch.setPolicy43(config.av.policy_43)
			iAVSwitch.setPolicy169(config.av.policy_169)
		
	def setAspect(self, tuner_type, caller=""):
		iAVSwitch.setAspect(config.av.aspect, caller)
		iAVSwitch.setWss(config.av.wss)	

		if (patchHisi):
			if ("DVB" not in tuner_type) or (tuner_type != self.previous_tuner_type):
				iAVSwitch.setPolicy43(config.av.policy_43, cycle=True, caller=caller)
			else:
				iAVSwitch.setPolicy43(config.av.policy_43, cycle=False, caller=caller)
			self.previous_tuner_type = tuner_type	
		else:
			iAVSwitch.setPolicy43(config.av.policy_43, cycle=False, caller=caller)
			iAVSwitch.setPolicy169(config.av.policy_169, cycle=False, caller=caller)
		
	def monitorPtsInfo(self):	
		
		self.ptsInfoCount += 1				
		currentFPS = getPtsInfoFPS()
		
		if (currentFPS) and (self.ptsInfoLastFPS) and (currentFPS != self.ptsInfoLastFPS):		
			log("monitorPtsInfo() framerate changed; calling VideoChangeDetect() " \
				"(currentFPS=%s, ptsInfoLastFPS=%s)" % (currentFPS, self.ptsInfoLastFPS))			
			self.VideoChangeDetect("monitorPtsInfo() ")
		
		else:
			log("monitorPtsInfo() framerate unchanged, or is False/None " \
				"(currentFPS=%s, ptsInfoLastFPS=%s)" % (currentFPS, self.ptsInfoLastFPS))
				
		#log("monitorPtsInfo() (currentFPS=%s, self.ptsInfoLastFPS=%s)" % (currentFPS, self.ptsInfoLastFPS))
						
		if (self.ptsInfoCount >= self.ptsInfoCountMax) or (not currentFPS) or (not self.ptsInfoLastFPS):
			self.ptsInfoTimer.stop()
			self.ptsInfoCount = 0
			self.ptsInfoLastFPS = None
		else:
			self.ptsInfoTimer.stop()
			self.ptsInfoTimer.start(self.ptsInfoFrequency, True)
	
	def cycleHdrType(self, force=False, caller=""):

		if force or getPlayState() == "PLAY":
			
			self.hdrTimer.stop()	
			cycler = {"none":"hlg","hlg":"hdr10","hdr10":"hlg","dolby":"hlg","auto":"hlg"}		
			previous_hdrtype = config.av.hdmihdrtype.value									
			
			log("%scycleHdrType() cycling HDR type from %s to %s to %s" \
				% (caller, previous_hdrtype, cycler[config.av.hdmihdrtype.value], previous_hdrtype))		
			
			config.av.hdmihdrtype.value = cycler[config.av.hdmihdrtype.value]	
			time.sleep(0.05) # necessary	
			config.av.hdmihdrtype.value = previous_hdrtype
			
			# untested but may be preferable to relying on config notifiers
			# current_hdrtype = config.av.hdmihdrtype.value
			# cycled_hdrtype = cycler[config.av.hdmihdrtype.value]
			# log("%scycleHdrType() cycling HDR type from %s to %s to %s" \
				# % (caller, current_hdrtype, cycled_hdrtype, current_hdrtype))
			# try:
				# f=open("/proc/stb/video/hdmi_hdrtype","w");f.write(cycled_hdrtype);f.close()
				# time.sleep(0.05) # necessary
				# f=open("/proc/stb/video/hdmi_hdrtype","w");f.write(current_hdrtype);f.close()
			# except: log("%scycleHdrType() failed to cycle HDR type" % caller)
				
		else:
			log("%scycleHdrType() video is paused; trying again in 3 seconds" % caller)
			self.hdrTimer.stop()
			self.hdrTimer.start(3000, True)
		
	def cycleFPS(self):

		self.cycleFPStimer.stop()	
		fps = self.previous_video_framerate
		lut = {23976:"5",24000:"5",25000:"5",29970:"5",30000:"5",50000:"5",59970:"5",60000:"5"}
		if (fps not in lut) or (self.monitor_EMI == False): return	
		try:
			f = open("/proc/hisi/msp/vdec_ctrl", "w"); f.write("setfps handle %s" % lut[fps]); f.close()
			self.restoreFPStimer.start(100, False)
			log("cycleFPS() wrote %s to /proc/hisi/msp/vdec_ctrl" % lut[fps])
		except:
			log("cycleFPS() failed writing to /proc/msp/vdec_ctrl")
				
	def restoreFPS(self, caller=""):
		
		self.restoreFPStimer.stop()	
		fps = self.previous_video_framerate
		lut = {23976:"24",24000:"24",25000:"25",29970:"30",30000:"30",50000:"50",59970:"60",60000:"60"}
		if (fps not in lut) or (self.monitor_EMI == False): return		
		try:
			f = open("/proc/hisi/msp/vdec_ctrl", "w"); f.write("setfps handle %s" % lut[fps]); f.close()
			log("%srestoreFPS() wrote %s to /proc/hisi/msp/vdec_ctrl" % (caller, lut[fps]))
			# f = open("/proc/hisi/msp/vdec_ctrl", "w"); f.write("setfps handle -1"); f.close()
			# writing invalid values such as -1 appears to reset the decoder to the source frame rate
		except:
			log("%srestoreFPS() failed writing to /proc/msp/vdec_ctrl" % caller)

			
def getOutputMode(hz="", caller=""):		
	if (path.exists("/proc/stb/video/videomode%s" % hz)):
		try:
			f = open("/proc/stb/video/videomode%s" % hz, "r")
			mode = f.read().strip()
			f.close()
			mode = "576i" if (mode.upper() == "PAL") else mode
			mode = "480i" if (mode.upper() == "NTSC") else mode
			return str(mode)
		except:
			log("%sgetOutputMode() failed to read /proc/stb/video/videomode%s" % (caller, hz))
			return "unsupported"				
	else:
		return "unsupported"

		
def getPtsInfoFPS(caller=""):
	pts_info_fps = False
	if path.exists("/proc/vfmw/pts_info"):	
		try:
			f = open("/proc/vfmw/pts_info", "r")
			pts_info = str(f.read())
			pos = pts_info.find("Output Frame Rate") + 21
			fps = int(pts_info[pos:pos+2])
			fps_ = {23:23976,24:24000,25:25000,29:29970,30:30000,50:50000,59:59940,60:60000}
			pts_info_fps = fps_[fps] # exception if not in dict
		except: pass
		try: f.close()
		except: pass
	return pts_info_fps

	
def getDynamicRange(source="hifb0", caller=""):
					# hifb0 is observed to be more reliable
	
	dynamic_range = None
	
	if (source == "vdec00"):
		if path.exists("/proc/hisi/msp/vdec00"):	
			try:
				f = open("/proc/hisi/msp/vdec00", "r")
				txt = str(f.read())
				pos = txt.find("SrcFrmType") + 38
				string = txt[pos:pos+3].replace(" ","")
				dynamic_range = "SDR" if (string == "SDR") else "HDR" if (string != "") else None
			except: pass
			try: f.close()
			except: pass
	
	elif (source == "hifb0"):
		if path.exists("/proc/hisi/msp/hifb0"):
			try:
				f = open("/proc/hisi/msp/hifb0", "r")
				txt = str(f.read())
				pos = txt.find("HDR") + 33
				string = txt[pos:pos+1]
				dynamic_range = "SDR" if (string == "n") else "HDR" if (string == "y") else None
			except: pass		
			try: f.close()
			except: pass

	return dynamic_range

	
def getPlayState(caller=""):
	state = None
	if path.exists("/proc/hisi/msp/sync00"):
		try:
			f = open("/proc/hisi/msp/sync00", "r")
			txt = str(f.read())
			pos = txt.find("CrtStatus") + 23
			string = txt[pos:pos+4]
			if (string == "PLAY"): state = "PLAY"	
		except: pass
		try: f.close()
		except: pass
	return state
	

def setOutputMode(modeString, hz="", caller=""):			
	if (path.exists("/proc/stb/video/videomode%s" % hz)):
		try:
			f = open("/proc/stb/video/videomode%s" % hz, "w")
			f.write(modeString)
			f.close()
			log("%ssetOutputMode() wrote %s to /proc/stb/video/videomode%s" % (caller, modeString, hz))
		except:
			log("%ssetOutputMode() failed writing %s to /proc/stb/video/videomode%s" % (caller, modeString, hz))
	else:
		log("%ssetOutputMode() failed writing %s to /proc/stb/video/videomode%s" % (caller, modeString, hz))

		
def autostart(session):
	global resolutionlabel
	if not path.exists(resolveFilename(SCOPE_PLUGINS) + 'SystemPlugins/AutoResolution'):
		if resolutionlabel is None:
			resolutionlabel = session.instantiateDialog(AutoVideoModeLabel)
		AutoVideoMode(session)
	else:
		config.av.autores.setValue(False)
		config.av.autores.save()
		configfile.save()

		
