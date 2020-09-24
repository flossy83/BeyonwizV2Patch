# OS
import os, stat, traceback, hashlib
from shutil import copy, copyfile, rmtree
from enigma import eTimer
from Tools import Notifications
from datetime import datetime
from time import time, strftime
from Components.About import about
from boxbranding import getBoxType, getMachineBuild

# GUI screens
from Screens.Screen import Screen
from Screens.TextBox import TextBox
from Screens.MessageBox import MessageBox
from Components.ConfigList import ConfigListScreen

# Data structures
from enigma import ePoint
from collections import deque
from Components.Label import Label
from Components.Sources.Boolean import Boolean
from Components.Sources.StaticText import StaticText
from Components.config import config, configfile, ConfigSubsection, ConfigText 
from Components.ActionMap import ActionMap

# Misc
from Components.config import KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END
from Plugins.Plugin import PluginDescriptor


class Installer(Screen):
	
	instance = None
	pendingRestart = False
	
	def __init__(self, session):
		
		log("__init__() start")
		Installer.instance = self 

		self.skin = """
		<screen name="Installer" position="350,206" size="580,307" title="Beyonwiz V2 Patch" >
		<widget name="boxModel" position="48,36" size="520,25" font="Regular;20"/>
		<widget name="firmware" position="48,76" size="520,25" font="Regular;20"/>
		<widget name="status" position="48,116" size="520,25" font="Regular;20"/>	
		<widget name="checksum1label" position="48,156" size="115,25" font="Regular;20"/>
		<widget name="checksum1" position="166,160" size="402,25" font="Regular;16"/>
		<widget name="checksum2label" position="48,196" size="145,25" font="Regular;20"/>
		<widget name="checksum2" position="195,200" size="374,25" font="Regular;16"/>
		<ePixmap name="red" position="4,e-40" size="140,40" pixmap="skin_default/buttons/red.png"
		alphatest="on" zPosition="1"/>
		<ePixmap name="green" position="148,e-40" size="140,40" pixmap="skin_default/buttons/green.png"
		alphatest="on" zPosition="1"/>
		<ePixmap name="yellow" position="292,e-40" size="140,40" pixmap="skin_default/buttons/yellow.png"
		alphatest="on" zPosition="1"/>
		<ePixmap name="blue" position="436,e-40" size="140,40" pixmap="skin_default/buttons/blue.png"
		alphatest="on" zPosition="1"/>
		<widget name="key_red" position="4,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#9f1313" font="Regular;20" transparent="1" zPosition="2"/>	
		<widget name="key_red" position="4,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#9f1313" font="Regular;20" render="Label"
		transparent="1" zPosition="3"/>
		<widget name="key_green" position="148,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#1f771f" font="Regular;20" transparent="1" zPosition="2"/>	
		<widget name="key_green" position="148,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#1f771f" font="Regular;20" render="Label"
		transparent="1" zPosition="3"/>
		<widget name="key_yellow" position="292,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#a08500" font="Regular;20" transparent="1" zPosition="2"/>
		<widget name="key_yellow" position="292,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#a08500" font="Regular;20" render="Label"
		transparent="1" zPosition="3"/>	
		<widget name="key_blue" position="436,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#18188b" font="Regular;20" transparent="1" zPosition="2"/>
		<widget name="key_blue" position="436,e-40" size="140,40" borderWidth="1" halign="center"
		valign="center" backgroundColor="#18188b" font="Regular;20" render="Label"
		transparent="1" zPosition="3"/>	
		</screen>"""

		Screen.__init__(self, session)
		self.session = session
		
		boxModels = {"beyonwizv2":"Beyonwiz V2", "beyonwizt2":"Beyonwiz T2",
		"beyonwizt3":"Beyonwiz T3", "beyonwizt4":"Beyonwiz T4", "beyonwizu4":"Beyonwiz U4"}
		if getBoxType() in boxModels:			self.boxModel = boxModels[getBoxType()]
		elif getMachineBuild() in boxModels:	self.boxModel = boxModels[getMachineBuild()]
		elif getBoxType(): 						self.boxModel = getBoxType()
		elif getMachineBuild(): 				self.boxModel = getMachineBuild()
		else: 									self.boxModel = "unknown."

		self.firmwareVer = about.getImageVersionString() + "." + about.getBuildString()
		self.patchVer = "1.0"
		self.setTitle("Beyonwiz V2 Patch v" + self.patchVer)
		
		self["boxModel"] = Label(_("Box model: " + self.boxModel))
		self["firmware"] = Label(_("Current firmware: " + self.firmwareVer))	
		self["status"] = Label(_("Patch status: checking installation..."))	
		self["checksum1label"] = Label(_("Patch MD5: "))
		self["checksum2label"] = Label(_("Installed MD5: "))	
		self["checksum1"] = Label(_("checking installation..."))
		self["checksum2"] = Label(_("checking installation..."))	
		self["key_red"] = Label(_("Close"))
		self["key_green"] = Label(_("Install"))
		self["key_yellow"] = Label(_("Uninstall"))
		self["key_blue"] = Label(_("About"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "MenuActions"],
		{		
			"red": self.keyRed, "cancel": self.keyRed,		
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue	
		}, -2)
			
		self.keyGreenTimer = eTimer(); self.keyGreenTimer.callback.append(self.keyGreenConfirmed)
		self.keyYellowTimer = eTimer(); self.keyYellowTimer.callback.append(self.keyYellowConfirmed)

		self.payloads ={
			self.patchVer:{
			"/usr/lib/enigma2/python/Components/AVSwitch.pyo":
			"7ede1ba4b9319e406b6d16132f8b5c85",	
			"/usr/lib/enigma2/python/Components/BeyonwizV2Patch.pyo":
			"82cfec8af5891df1c3a8a2e286b7a9fd",
			"/usr/lib/enigma2/python/Plugins/Extensions/AutoTimer/AutoTimerEditor.pyo":
			"400ba43d1902f2f7a1a166e0f02daae4",
			"/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.pyo":
			"bd5af2d2acf6dda597f02a92aee03a8f",
			"/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/VideoEnhancement.pyo":
			"ffd885426953b7b791209541ab351d95",
			"/usr/lib/enigma2/python/Screens/MovieSelection.pyo":
			"dd39a5e64f30e2c1fe2782a773265b9d",
			"/usr/lib/enigma2/python/Screens/VideoMode.pyo":
			"a25fc502501c0e4767d9ab32d1b321f4"			
			}
		}		
		self.cleanup ={
			self.patchVer:{
			"/usr/lib/enigma2/python/Components/BeyonwizV2Patch.pyo":
			"82cfec8af5891df1c3a8a2e286b7a9fd"
			}
		}

		self.onLayoutFinish.append(self.updatePatchStatus)
		log("__init__() finish")

	def keyRed(self):
		
		log("keyRed()")	
		cs = self["status"].getText(); bs = ("installing", "uninstalling", "checking") 
		for s in bs:
			if s in cs: log("keyRed() busy %s patch; returning" % s); return	
		
		self.close()
		
	def keyGreen(self):
		
		log("keyGreen()")		
		
		cs = self["status"].getText(); bs = ("installing", "uninstalling", "checking") 
		for s in bs:
			if s in cs: log("keyGreen() busy %s patch; returning" % s); return
			
		models = ("beyonwizv2", "beyonwizt2", "beyonwizt3", "beyonwizt4", "beyonwizu4")
		if (getBoxType() not in models) and (getMachineBuild() not in models):
			self.session.open(MessageBox,_("Unable to install the patch as your box " \
			"does not appear to be a Beyonwiz, and this patch is only for Beyonwiz models."),
			MessageBox.TYPE_INFO)
			return

		self.updatePatchStatus()
		
		confirmQuestions = [None,None,None,None]
		
		confirmQuestions[0] = "It is recommended to backup your system configuration " \
		"settings and prepare a recovery USB stick in case installation fails part way through.  " \
		"Instructions can be found at tiny.cc/BeyonwizPatch."
			
		if (self.patchStatus[self.patchVer] == "installed"):
			confirmQuestions[1] = "The patch is already installed."

		if getBoxType() != "beyonwizv2" and getMachineBuild() != "beyonwizv2":
			confirmQuestions[2] = "Your box appears to be a " + self.boxModel + ", but the patch was " \
			"primarily intended for the Beyonwiz V2."
				
		# if int(self.firmwareVer.replace(".","")) != 19320200328:
			# confirmQuestions[3] = "Your box is running firmware version " + self.firmwareVer + ", but " \
			# "the patch was primarily intended for version 19.3.20200328."
			
		if about.getImageVersionString() != "19.3":
			confirmQuestions[3] = "Your box is running firmware version " + about.getImageVersionString() \
			+ ", but the patch was primarily intended for version 19.3."
			
				
		if confirmQuestions[1] or confirmQuestions[2] or confirmQuestions[3]: singleQuestion = False
		else: singleQuestion = True
		
		confirmQuestion = "Please note:"	
		if singleQuestion: confirmQuestion += "\n\n" + confirmQuestions[0]
		else:
			questionNumber = 1
			for q in confirmQuestions:
				if q: confirmQuestion += "\n\n" + str(questionNumber) + ". " + q; questionNumber+=1
		
		if not confirmQuestions[1]: confirmQuestion += "\n\nAre you sure you want to install the patch?"
		else: confirmQuestion += "\n\nAre you sure you want to re-install the patch?"

		self.session.openWithCallback(self.keyGreenConfirm, MyMessageBox,
			_(confirmQuestion), MessageBox.TYPE_YESNO, default = False)

	def keyGreenConfirm(self, confirmed):
		
		log("keyGreenConfirm()")		
		if (confirmed):
			self["status"].setText("Patch status: installing...")
			self.iDialog = self.session.open(MessageBox, text=_("Installing patch..."),
			type=MessageBox.TYPE_INFO); self.iDialog.execEnd()
			self.keyGreenTimer.stop(); self.keyGreenTimer.start(1500, True)
			
	def keyGreenConfirmed(self):
		
		log("keyGreenConfirmed()")
		#self.iDialog.execBegin(); log("keyGreenConfirmed() returning"); return
		
		self.keyGreenTimer.stop()
		result = self.installPatch()
		self.updatePatchStatus()
		
		if result != "success":
			# self.uninstallPatch()
			# result += "\n\nPlease restart the box for any changes to take effect."
			self.iDialog["text"].setText(result)
			self.iDialog["InfoPixmap"].hide(); self.iDialog["ErrorPixmap"].show()
		
		elif result == "success":

			if self.patchStatus[self.patchVer] == "installed":
				log("keyGreenConfirmed() installation successful")
				self.iDialog["text"].setText("Patch installation was successful. " \
				"Please restart the box for the changes to take effect.")
				
			else:			
				log("keyGreenConfirmed() installation successful, but checksum unverified")
				self.iDialog["text"].setText("Patch installation appears successful, " \
				"however the checksums of the patched files could not be verified.\n\n" \
				"Please restart the box for changes to take effect.")
				
		self.iDialog.autoResize(); self.iDialog.execBegin()

	def keyYellow(self):
		
		log("keyYellow()")	
		cs = self["status"].getText(); bs = ("installing", "uninstalling", "checking") 
		for s in bs:
			if s in cs: log("keyYellow() busy %s patch; returning" % s); return
			
		self.updatePatchStatus()
		
		if self.patchStatus[self.patchVer] == "not installed":
			confirmQuestion = "The patch does not appear to be installed.\n" \
			"Run the uninstallation process anyway?"
		else: confirmQuestion = "Are you sure you want to uninstall the patch?"
		
		self.session.openWithCallback(self.keyYellowConfirm, MyMessageBox,
			_(confirmQuestion), MessageBox.TYPE_YESNO, default = False)
			
	def keyYellowConfirm(self, confirmed):
		
		log("keyYellowConfirm()")
		if confirmed:	
			self["status"].setText("Patch status: uninstalling...")			
			self.uDialog = self.session.open(MessageBox, text=_("Uninstalling patch..."),
			type=MessageBox.TYPE_INFO); self.uDialog.execEnd()
			self.keyYellowTimer.stop(); self.keyYellowTimer.start(1500, True)
			
	def keyYellowConfirmed(self):		
		
		log("keyYellowConfirmed()")
		self.keyYellowTimer.stop()
		result = self.uninstallPatch()
		self.updatePatchStatus()	
		
		if result == "no uninstall directory":
			log("keyYellowConfirmed() failed to uninstall patch; no uninstall directory")	
			self.uDialog["text"].setText("Unable to uninstall the patch as no original unpatched " \
			"files were found in /usr/beyonwizv2patch/uninstall")
			self.uDialog["InfoPixmap"].hide(); self.uDialog["ErrorPixmap"].show()
			
		elif result == "firmware mismatch":
			log("keyYellowConfirmed() failed to uninstall patch; firmware mismatch")		
			self.uDialog["text"].setText("Unable to uninstall the patch as the original unpatched " \
			"files found in /usr/beyonwizv2patch/uninstall appear to belong to a different firmware version.")
			self.uDialog["InfoPixmap"].hide(); self.uDialog["ErrorPixmap"].show()
	
		elif result != "success":
			log("keyYellowConfirmed() failed to uninstall patch")	
			self.uDialog["text"].setText("Failed to uninstall patch.\n\nReason: " \
			"failed copying %s\nto\n%s\n\nException: %s" % (result[0], result[1], result[2]))
			self.uDialog["InfoPixmap"].hide(); self.uDialog["ErrorPixmap"].show()
		
		elif result == "success" and self.patchStatus[self.patchVer] == "not installed":
			log("keyYellowConfirmed() successfully uninstalled patch")
			self.uDialog["text"].setText("The patch was successfully uninstalled.  Please restart " \
			"the box for the changes to take effect.")
		
		elif result == "success" and self.patchStatus[self.patchVer] == "unknown":
			log("keyYellowConfirmed() uninstalled patch, but couldn't verify checksums")
			self.uDialog["text"].setText("The patch appears to have been uninstalled, however " \
			"the checksums of the currently installed files could not be verified.  Please restart " \
			"the box for the changes to take effect.")
			
		elif result == "success" and self.patchStatus[self.patchVer] == "installed":
			log("keyYellowConfirmed() uninstalled patch, but checksums indicate otherwise")
			self.uDialog["text"].setText("The uninstallation process completed, " \
			"however the checksums of the currently installed files indicate the patch is still " \
			"installed. Please restart the box for any changes to take effect.")
		
		self.uDialog.autoResize(); self.uDialog.execBegin()

	def keyBlue(self):
	
		# self.updatePatchStatus()
		# for subdir, dirs, files in sorted(os.walk("/usr/beyonwizv2patch/uninstall")):
			# for file in sorted(files):
				# source = subdir + os.sep + file
				# try:
					# h = str(hashlib.md5(open(source,"rb").read()).hexdigest())
					# log("keyBlue() %s: %s" % (source, h))
				# except: pass
		
		log("keyBlue()")
		cs = self["status"].getText(); bs = ("installing", "uninstalling", "checking") 
		for s in bs:
			if s in cs: log("keyBlue() busy %s patch; returning" % s); return
			
		msgBox = self.session.open(MessageBox,_("Beyonwiz V2 Patch v1.0 by S.Z.\nTiny.cc/BeyonwizPatch"),
		MessageBox.TYPE_INFO); msgBox.setTitle(_("About"))

	def getChecksum(self, source, sourceType="file", algorithm="crc32"):		
		try:
			if sourceType == "file": input = open(source,"rb").read()
			elif sourceType == "string": input = bytes(str(source).encode("utf-8"))	
			if algorithm == "crc32": return str(hex(zlib.crc32(input)%(1<<32)))[2:-1]
			elif algorithm == "md5": return str(hashlib.md5(input).hexdigest())	
		except: return False
			
	def updatePatchStatus(self):

		# Populate:	{ 	this patch ver	:	installed / not installed / unknown
		#				payload file 1	:	md5 / nonexistent
		#				payload file n	:	md5 / nonexistent		
		#				other patch ver	:	installed / not installed / unknown
		#				other patch ver	:	installed / not installed / unknown		}
		patchStatus = {}
		for v in sorted(self.payloads):
			status = "installed"
			for f in sorted(self.payloads[v]):
				if not os.path.exists(f):
					if v == self.patchVer: patchStatus[f] = "nonexistent"
					status = "not installed"; continue		
				c = self.getChecksum(f, "file", "md5")
				if c:
					if v == self.patchVer: patchStatus[f] = c
					if c != self.payloads[v][f]: status = "not installed"
				else:
					status = "unknown"; break
			patchStatus[v] = status

	
		# Cumulative MD5 of patched files
		payloadsum = ""
		for f in sorted(self.payloads[self.patchVer]):	
			target = os.path.dirname(os.path.abspath(__file__)) + "/Payload" + f
			md5 = self.getChecksum(target, "file", "md5")
			if md5: payloadsum += md5
			else: payloadsum = "unknown"; break
		if payloadsum != "unknown":
			payloadmd5 = self.getChecksum(payloadsum, "string", "md5")
			if not payloadmd5: payloadmd5 = "unknown"
		else: payloadmd5 = "unknown"
		
	
		# Cumulative MD5 of installed files
		if patchStatus[self.patchVer] != "unknown":
			deployedsum = ""
			for f in sorted(self.payloads[self.patchVer]):
				if patchStatus[f] != "nonexistent": deployedsum += patchStatus[f]
			deployedmd5 = self.getChecksum(deployedsum, "string", "md5")
			if not deployedmd5: deployedmd5 = "unknown"
		else: deployedmd5 = "unknown"
	
			
		# Update GUI labels	
		if patchStatus[self.patchVer] == "installed":
			newStatus = "Patch status: installed."
		elif patchStatus[self.patchVer] == "not installed":
			newStatus = "Patch status: not installed."		
		elif patchStatus[self.patchVer] == "unknown":
			newStatus = "Patch status: failed verification."
		if (Installer.pendingRestart):
			newStatus = newStatus[:-1]; newStatus += "; pending restart."
		self["status"].setText(newStatus)		
		if payloadmd5 != "unknown":
			self["checksum1"].setText(payloadmd5)
		else: self["checksum1"].setText("failed to calculate.")
		if deployedmd5 != "unknown":
			self["checksum2"].setText(deployedmd5)
		else: self["checksum2"].setText("failed to calculate.")
		
		
		self.patchStatus = patchStatus
		log("updatePatchStatus() payload md5: %s" % payloadmd5)
		log("updatePatchStatus() deployed md5: %s" % deployedmd5)	
		for s in sorted(self.patchStatus):
			log("updatePatchStatus() %s: %s" % (s, self.patchStatus[s]))

	def uninstallPatch(self):		
		
		# log("uninstallPatch()")	
		# os.system("cp -rf /src/dir /dest/dir")

		if not os.path.exists("/usr/beyonwizv2patch/uninstall"):
			log("uninstallPatch() path /usr/beyonwizv2patch/uninstall doesn't exist; returning")
			return "no uninstall directory"
			
		if os.path.exists("/usr/beyonwizv2patch/uninstall.ver"):
			f = open("/usr/beyonwizv2patch/uninstall.ver"); v = f.read(); f.close()
			if v != self.firmwareVer:
				log("uninstallPatch() firmware mismatch; returning")
				return "firmware mismatch"
			
		result = "success"
		
		# Restore original files from /usr/beyonwizv2patch/uninstall
		for subdir, dirs, files in sorted(os.walk("/usr/beyonwizv2patch/uninstall")):
			for file in sorted(files):
				source = subdir + os.sep + file
				dest = source.replace("/usr/beyonwizv2patch/uninstall", "")
				destdir = os.path.dirname(dest)
				try:			
					log("uninstallPatch() copying %s to\n          %s" % (source,dest))
					if not os.path.exists(destdir): os.makedirs(destdir)
					if not os.path.exists(destdir): raise Exception("Failed to create directory %s" % destdir) 
					# try:
						# os.chmod(destdir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
						# os.chmod(dest, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
					# except: pass # stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP + stat.S_IROTH			
					copyfile(source, dest)
				except Exception as e:
					result = "failure"
					log("uninstallPatch() failed copying; exception:\n          %s" % e)
					break
			if result == "failure": break
			
		
		# Remove any redundant patch files
		if result == "success":
			for v in sorted(self.cleanup):
				for f in sorted(self.cleanup[v]):
					if os.path.exists(f) and self.getChecksum(f, "file", "md5") == self.cleanup[v][f]:				
						log("uninstallPatch() cleanup: removing %s" % f) 
						try:				
							os.remove(f)
							if os.path.exists(f): raise Exception("failed to remove %s" % f)			
						except Exception as e:					
							log("uninstallPatch() failed cleanup: %s" % e)
							source = f; dest = "Trash"; result = "failure"; break			
				if result == "failure": break
			
		if result == "success": Installer.pendingRestart = True; return "success"
		else: return [source, dest, str(e)]
	
	def installPatch(self):
			
		# Check payload md5s
		log("installPatch() checking payload md5s")
		for f in sorted(self.payloads[self.patchVer]):	
			source = os.path.dirname(os.path.abspath(__file__)) + "/Payload" + f
			md5 = self.getChecksum(source, "file", "md5")
			if md5 != self.payloads[self.patchVer][f]:
				log("installPatch() failed to verify md5 of %s" % source)	
				message = "Unable to install patch as a file's md5 checksum could not be " \
				"verified: " % source 
				return message
			else: log("installPatch() verified Payload%s: %s" % (f, md5))
		
		
			
		# Test path permissions
		log("installPatch() testing permissions"); loopIndex = 0
		for f in sorted(self.payloads[self.patchVer]):
			loopIndex+=1
			source = os.path.dirname(os.path.abspath(__file__)) + "/Payload" + f
			try:
				# try:
				#	os.chmod(os.path.dirname(f), stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
				#	os.chmod(f, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
				# except: pass # stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP + stat.S_IROTH
				timestamp = datetime.now().strftime("%H%M%S%f")
				if loopIndex == 1:
					dest = "/usr/PermissionTest" + timestamp + ".tst"
					log("installPatch() copying Payload%s to\n          %s" % (f, dest))
					copyfile(source, dest)
					if not os.path.exists(dest): raise Exception("unable to write to /usr")				
					else: os.remove(dest)
					if os.path.exists(dest): raise Exception("unable to delete from /usr")				
				destdir = os.path.dirname(f)
				dest = destdir + "/PermissionTest" + timestamp + ".tst"		
				log("installPatch() copying Payload%s to\n          %s" % (f, dest))
				copyfile(source, dest)
				if not os.path.exists(dest): raise Exception("unable to write to %s" % destdir)				
				else: os.remove(dest)
				if os.path.exists(dest): raise Exception("unable to delete from %s" % destdir)
			except Exception as e:
				log("installPatch() failed copying %s to\n          %s\n          " \
				"Exception: %s" % (source, dest, e))
				message = "Unable to install patch.  Reason: %s" % e
				return message
		log("installPatch() permission test successful")
		
		
		
		# Uninstall currently installed patch
		log("installPatch() uninstalling previous patch")
		result = self.uninstallPatch()	
		if result != "success" and result != "no uninstall directory" and result != "firmware mismatch":
			log("installPatch() failed to uninstall previous patch; returning")	
			message = "Unable to install patch as a previously installed patch failed to uninstall." \
			"\n\nReason: failed copying %s\n\nto %s\n\nException: %s" % (result[0], result[1], result[2])
			return message		
		elif result == "no uninstall directory":
			if self.patchStatus[self.patchVer] == "not installed":
				log("installPatch() no uninstall directory; continuing")
			else:
				log("installPatch() failed to uninstall previous patch; no uninstall files; returning")
				message = "Unable to install patch as a previously installed patch failed to uninstall." \
				"\n\nReason: no original unpatched files found in /usr/beyonwizv2patch/uninstall." \
				"\n\nTo uninstall the patch, you must reflash the original Beyonwiz firmware.  Instructions " \
				"can be found at tiny.cc/BeyonwizPatch."
				return message 			
		elif result == "firmware mismatch":
			if self.patchStatus[self.patchVer] == "not installed":
				log("installPatch() failed to uninstall previous patch; firmware mismatch; continuing")
			else:
				log("installPatch() failed to uninstall previous patch; firmware mismatch; returning")
				message = "Unable to install patch as a previously installed patch failed to uninstall." \
				"\n\nReason: the original unpatched files found in /usr/beyonwizv2patch/uninstall appear " \
				"to belong to a different firmware version." 
				return message						
		elif result == "success": log("installPatch() successfully uninstalled previous patch")
		
					
					
		# Delete unpatched files belonging to previously installed patch
		log("installPatch() deleting /usr/beyonwizv2patch/uninstall")
		if os.path.exists("/usr/beyonwizv2patch/uninstall"):		
			try: rmtree("/usr/beyonwizv2patch/uninstall")
			except: pass	
			if os.path.exists("/usr/beyonwizv2patch/uninstall"):		
				log("installPatch() failed to delete /usr/beyonwizv2patch/uninstall; returning")	
				message = "Unable to install patch as a previously installed patch failed to uninstall." \
				"\n\nReason: failed to delete /usr/beyonwizv2patch/uninstall"
				return message
			else: log("installPatch() deleted /usr/beyonwizv2patch/uninstall")			
		else: log("installPatch() /usr/beyonwizv2patch/uninstall doesn't exist; continuing")
		
	
	
		# Create folder for current unpatched files
		log("installPatch() creating /usr/beyonwizv2patch/uninstall")
		try: os.makedirs("/usr/beyonwizv2patch/uninstall")
		except: pass
		if not os.path.exists ("/usr/beyonwizv2patch/uninstall"):
			log("installPatch() failed to create /usr/beyonwizv2patch/uninstall; returning")		
			message = "Unable to install patch; failed to create uninstall directory: " \
			"/usr/beyonwizv2patch/uninstall"
			return message
		log("installPatch() created /usr/beyonwizv2patch/uninstall")
		
		
			
		# Backup current unpatched files to /usr/beyonwizv2patch/uninstall
		log("installPatch() backing up original files to /usr/beyonwizv2patch/uninstall")
		for source in sorted(self.payloads[self.patchVer]):		
			if not os.path.exists(source): continue	
			if source in self.cleanup[self.patchVer]: continue			
			dest = "/usr/beyonwizv2patch/uninstall" + source
			try:
				log("installPatch() copying %s to\n          %s" % (source, dest))
				if not os.path.exists(os.path.dirname(dest)): os.makedirs(os.path.dirname(dest))
				copyfile(source, dest)
				if not os.path.exists(dest):
					raise Exception("destination file did not appear after copying: %s" % dest)
			except Exception as e:
				log("installPatch() failed copying; exception:\n          %s;\n          ;returning" % e)
				message = "Unable to install patch; failed to backup original unpatched files." \
				"\n\nReason: %s" % e
				return message	
		try:
			log("installPatch() writing %s to /usr/beyonwizv2patch/uninstall.ver" % self.firmwareVer)
			f = open("/usr/beyonwizv2patch/uninstall.ver", "w"); f.write(self.firmwareVer); f.close()
			f = open("/usr/beyonwizv2patch/uninstall.ver"); uv = f.read(); f.close()
			if uv != self.firmwareVer:
				raise Exception("failed writing firmware version to /usr/beyonwizv2patch/uninstall.ver")
		except Exception as e:
			log("installPatch() exception: %s; returning" % e)
			message = "Unable to install patch.\n\nReason: %s" % e
			return message
		
		log("installPatch() finished backing up original files to /usr/beyonwizv2patch/uninstall")
		
		 

				
		# Copy patched files
		log("installPatch() copying patched files")
		for dest in sorted(self.payloads[self.patchVer]):		
			try:
				source = os.path.dirname(os.path.abspath(__file__)) + "/Payload" + dest
				log("installPatch() copying Payload%s to\n          %s" % (dest, dest))	
				destdir = os.path.dirname(dest)
				if not os.path.exists(destdir): os.makedirs(destdir)
				if not os.path.exists(destdir): raise Exception("Failed to create directory %s" % destdir)		
				copyfile(source, dest)
				if not os.path.exists(dest):
					raise Exception("destination file did not appear after copying: %s" % dest)
			except Exception as e:
				log("installPatch() failed to copy patched files; exception:\n          %s" % e)
				message = "Failed to install patch.\n\nReason: %s" % e
				return message
		
		
		Installer.pendingRestart = True; return "success"


class MyMessageBox(MessageBox):
	def alwaysOK(self):
		pass # avoid green keybounce causing unintentional confirm	
		
		
def startInstaller(session, **kwargs):
	log("****************")
	log("startInstaller()")
	session.open(Installer)
	
	
def Plugins(**kwargs):			
	DescriptorList = []   
	DescriptorList.append(
		PluginDescriptor(
			name="Beyonwiz V2 Patch",		
			where = [
					PluginDescriptor.WHERE_PLUGINMENU,
					# PluginDescriptor.WHERE_EXTENSIONSMENU
					],		
			description=_("Beyonwiz V2 Patch"),
			fnc=startInstaller,
			needsRestart=False
		)	
	)	
	return DescriptorList
	

def log(line):

	logFile = os.path.dirname(os.path.abspath(__file__)) + "/log.log"
	try:
		f = open(logFile, "a")
		f.write(datetime.now().strftime("%H:%M:%S") + "  " + line + "\n") #%f
		f.close()		
	except:
		pass

	
	