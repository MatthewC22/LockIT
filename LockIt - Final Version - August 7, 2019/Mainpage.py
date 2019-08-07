from tkinter import *
from tkinter import ttk
from tkinter.ttk import Progressbar
from tkinter.colorchooser import *
from tkinter import font
import os
import Login
from webbot import Browser

import tkinter as tk

from tkinter import filedialog

from tkinter.filedialog import askdirectory

import tkinter.messagebox
from validator_collection import checkers
import string
import secrets
import sqlite3
from datetime import date, datetime,timedelta
import webbrowser
from PIL import Image
from password_strength import PasswordPolicy,PasswordStats
from cryptography.fernet import Fernet
import pyperclip
import bcrypt



def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


def trimData(dataToTrim):
	Str1 = str(dataToTrim)
	Str2 = Str1.replace('(', '')
	Str3 = Str2.replace(')', '')
	Str4 = Str3.replace(',', '')
	Str5 = Str4.replace("'", '')
	dataTrimmed = Str5
	return dataTrimmed


def fetchTimerEnabledSetting():
	# make connection to db
	conn = sqlite3.connect('LockIT.db')
	# add cursor
	c = conn.cursor()

	c.execute("""SELECT timer FROM SETTINGS""")

	timer_setting = c.fetchone()

	# save changes made
	conn.commit()

	# close database
	conn.close()

	timer_setting_t = trimData(timer_setting)
	return int(timer_setting_t)


timer_setting = fetchTimerEnabledSetting()


def user_is_inactive():
	if timer_setting == 1 and minutes != 0:
		root.destroy()
		import Login
		Login.loginScreen.showLoginScreen()
		print("Auto-Logout Timer went off")


def fetchMinutes():
	# make connection to db
	conn = sqlite3.connect('LockIT.db')
	# add cursor
	c = conn.cursor()
	c.execute("""SELECT minutes FROM SETTINGS""")
	minutes = c.fetchone()
	# save changes made
	conn.commit()
	# close database
	conn.close()
	minutes_t = trimData(minutes)
	return int(minutes_t)


minutes = fetchMinutes()
timerObj = None


def reset_timer(event=None):
	global timerObj
	# cancel the previous event
	if timerObj is not None:
		root.after_cancel(timerObj)

	if (minutes == 0):
		pass
	# create new timerObj
	timerObj = root.after((int(minutes) * 60000), user_is_inactive)



def showhelp():

	documentation = resource_path("Documentation.pdf")
	os.startfile(documentation)


def showWindow():

	global root
	root = tk.Tk()
	#bind events
	root.bind_all('<Any-KeyPress>', reset_timer)
	root.bind_all('<Any-ButtonPress>', reset_timer)
	menu = Menu(root)
	root.configure(background="white")
	root.config(menu=menu)
	settingmenu = Menu(menu)
	menu.add_cascade(label='Setting', menu=settingmenu)
	settingmenu.add_command(label='Change Password', command=changemasterkey.showWindow)
	settingmenu.add_command(label='Security Settings',command=changesecuritysetting.showSecWindow)
	settingmenu.add_separator()
	settingmenu.add_command(label='Exit', command=root.quit)
	helpmenu = Menu(menu)
	menu.add_cascade(label='Help', menu=helpmenu)
	helpmenu.add_command(label='About',command=showhelp)

	root.geometry("1100x800")
	root.title("LockIt")

	#prints the master key as a string
	print(Login.loginScreen.getMasterKey(root))

	windowWidth = root.winfo_reqwidth()
	windowHeight = root.winfo_reqheight()

	# Gets both half the screen width/height and window width/height
	positionRight = int(root.winfo_screenwidth() / 4 - windowWidth / 2)
	positionDown = int(root.winfo_screenheight() / 4 - windowHeight / 2)

	# Positions the window in the center of the page.
	root.geometry("+{}+{}".format(positionRight, positionDown))

	main = MainView(root)
	main.pack(side="top", fill="both", expand=True)

	reset_timer()
	root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=resource_path('icon/favicon.png')))
	root.mainloop()


class changemasterkey:

	def trimData(self, dataToTrim):
		Str1 = str(dataToTrim)
		Str2 = Str1.replace('(', '')
		Str3 = Str2.replace(')', '')
		Str4 = Str3.replace(',', '')
		Str5 = Str4.replace("'", '')
		dataTrimmed = Str5
		return dataTrimmed

	def showWindow():
		cmk = changemasterkey(root)
		root.mainloop()

	# produces error message on screen
	def errorMessage(self, err):
		lbl = Label(self.changeMkPage, fg="red", text=err)
		lbl.pack()
		root.after(5000, lbl.destroy)

	# updates the the Record into LockIT.db
	def updateRecordInDb(self, hashedPw, hintEntry):

		# load database
		# import Database
		# Database.load_database()
		print("hashed pw = " + str(hashedPw))
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		c.execute("SELECT userID FROM LOCKITUSER")
		# fetch uID
		uId = c.fetchone()

		# save changes made
		conn.commit()
		# close connection to db
		conn.close()

		print("uid = " + str(uId))
		uId_t = self.trimData(uId)
		print("uid = " + str(uId_t))
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		# update(s)
		c.execute("""UPDATE LOCKITUSER SET hint = ? , passwordHash = ? WHERE userID = ? """,
				  (hintEntry, hashedPw, uId_t))

		# select all
		c.execute("SELECT * FROM LOCKITUSER")
		rows = c.fetchall()
		for row in rows:
			print(row)

		# save changes made
		conn.commit()
		# close connection to db
		conn.close()

		print("Master Key has been changed !")

		# close window
		self.changeMkPage.destroy()

	def checkForMkSameAsHint(self, hashed):
		hint = self.hintEntry.get()
		mk = self.newPassEntry.get()
		print(hint, mk)
		if (str(hint) == str(mk)):
			print("Hint and password Test FAILED")
			errMsg = "hint and password canot be the same"
			self.errorMessage(errMsg)
		# raise error
		else:
			self.updateRecordInDb(hashed, hint)

	# checks if the entry 1 and entry 2 are same
	def checkMkEntriesMatch(self):
		# convert entry1 to hashVal
		hashed = bcrypt.hashpw(str(self.newPassEntry.get()).encode(), bcrypt.gensalt())
		# compare hashed with 2nd entry
		if (bcrypt.checkpw(str(self.repeatNewPassEntry.get()).encode(), hashed)):
			# If they the same store the record into the db
			print("Both Entries Match!")
			# self.saveRecordToDb(hashed, str(self.hintEntry.get()))
			self.checkForMkSameAsHint(hashed)
		else:
			# error message to user (red highlighted)
			print("Entries Do not Match :(")
			errMsg = "Password entries do not match"
			self.errorMessage(errMsg)

	# checks if the entry contains any special characters
	def checkMkForOneSpecialChar(self):
		# pattern for special chars
		regex = re.compile('[@_!#$%^&+,;=*()<>?/\\\\|}{\\[\\]~:-]')
		# searches the pattern
		if ((regex.search(str(self.newPassEntry.get())) == None) and (
				regex.search(str(self.repeatNewPassEntry.get())) == None)):
			print("Special Char Tests FAILED")  # error messagebox
			errMsg = "Password must contain atleast one special character ($,#,@ ...)"
			self.errorMessage(errMsg)
		else:
			print("Special Char Test PASSED")
			# complexity tests passed
			# check if both entries match and commit to db
			self.checkMkEntriesMatch()

	# checks if the password has atleast one digit (0-9)
	def checkMkForOneNumber(self):
		# counters
		digit = 0
		digit2 = 0

		for l in str(self.newPassEntry.get()):
			try:
				l = int(l)
				digit += 1
			except ValueError:
				pass  # it was string, not int.

		for l in str(self.repeatNewPassEntry.get()):
			try:
				l = int(l)
				digit2 += 1
			except ValueError:
				pass  # it was string, not int.

		# next complexity test for special chars
		if (digit > 0 and digit2 > 0):
			print("One number tests PASSED")
			self.checkMkForOneSpecialChar()
		else:
			print("One number test FAILED")  # error messagebox
			errMsg = "Password must contain atleast one digit (0-9)"
			self.errorMessage(errMsg)

	# checks if the password has upper and lowercase characters
	def checkMkUpperAndLowerChars(self):
		# counters
		upper = 0
		lower = 0
		space = 0

		upper2 = 0
		lower2 = 0
		space2 = 0

		# parse string and count if upper,lower,space
		for l in str(self.newPassEntry.get()):
			if (l.isupper()):
				upper += 1
			elif (l.islower()):
				lower += 1
			elif (l.isspace()):
				space += 1

		for l in str(self.repeatNewPassEntry.get()):
			if (l.isupper()):
				upper2 += 1
			elif (l.islower()):
				lower2 += 1
			elif (l.isspace()):
				space2 += 1

		if (upper > 0 and lower > 0 and upper2 > 0 and lower2 > 0):
			print("Upper Case & Lower Case Tests PASSED")
			# next complexity test
			self.checkMkForOneNumber()
		else:  # error
			print("Upper Case & Lower Case Test FAILED")
			errMsg = "Password must contain atleast one uppercase and one lowercase character"
			self.errorMessage(errMsg)

	# checks if password is of minimum length
	def checkMkEntryLength(self):
		minimum_password_length = 8
		# check length of entry
		new_pwLen = len(str(self.newPassEntry.get()))
		newRepeat_pwLen = len(str(self.repeatNewPassEntry.get()))

		if ((new_pwLen >= minimum_password_length) and (newRepeat_pwLen >= minimum_password_length)):
			print("Password Length Tests PASSED")
			# next complexity test
			self.checkMkUpperAndLowerChars()
		else:
			# error messages
			print("Password Length Test FAILED")
			errMsg = "Password must contain atleast 8 characters"
			self.errorMessage(errMsg)

	def checkMasterKeyEntries(self):
		# old = self.oldPassEntry.get()
		# new = self.newPassEntry.get()
		# new_repeat = self.repeatNewPassEntry.get()
		# print(old, new, new_repeat)

		# check if old is correct (in the db)
		# fetch hashval from db, compare it with old

		# check if old entry exists
		print("old pass entry = " + str(self.oldPassEntry.get()))
		if (self.oldPassEntry.get() == ""):
			print("Old entry is blank :(")
			errMsg = "Please input old password"
			self.errorMessage(errMsg)
		else:
			conn = sqlite3.connect('LockIT.db')
			c = conn.cursor()
			c.execute("SELECT passwordHash FROM LOCKITUSER")
			hashValFromDb = c.fetchone()
			# save changes made
			conn.commit()
			conn.close()
			# parse data
			hashVal = self.trimData(hashValFromDb)
			hashVal = hashVal.replace('b', '', 1)
			# compare password in db with entry
			print(hashVal)
			hashVal = hashVal.encode()
			print(hashVal)
			if (bcrypt.checkpw(str(self.oldPassEntry.get()).encode(), hashVal)):
				# old is correct
				print("Both Entries Match!")
				# password complexity tests for 'new' (error on screen will be displayed if test fails)

				self.checkMkEntryLength()
			# otherwise update the database masterkey to a new masterkey (put in a new hashval and get rid the old one)
			# self.updateRecordInDb()
			else:
				# error
				print("Entries Do not Match :(")
				errMsg = "Incorrect old master password"
				self.errorMessage(errMsg)

	def __init__(self, master):
		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.changeMkPage = Toplevel()
		self.changeMkPage.geometry("600x400")
		self.changeMkPage.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.changeMkPage.resizable(0, 0)
		self.changeMkPage.title("Change Master Key")


		topFrame = Frame(self.changeMkPage)
		topFrame.pack(side=TOP)

		label1 = Label(topFrame, text="Change Master Key\n",
					   font="Helvetica 28 bold")
		label1.grid(row=0, column=0)

		centreFrame = Frame(self.changeMkPage)
		centreFrame.pack(side=TOP)

		oldPassLabel = Label(centreFrame, text="* Old Password", )
		oldPassLabel.grid(row=0, column=0)

		self.oldPassEntry = Entry(centreFrame, show="*")
		self.oldPassEntry.grid(row=0, column=1)

		newPassLabel = Label(centreFrame, text="* New Password", )
		newPassLabel.grid(row=1, column=0)

		self.newPassEntry = Entry(centreFrame, show="*")
		self.newPassEntry.grid(row=1, column=1)

		repeatNewPassLabel = Label(centreFrame, text="* Retype New Password", )
		repeatNewPassLabel.grid(row=2, column=0)

		self.repeatNewPassEntry = Entry(centreFrame, show="*")
		self.repeatNewPassEntry.grid(row=2, column=1)

		hintLabel = Label(centreFrame, text="* Type New Hint", )
		hintLabel.grid(row=3, column=0)

		self.hintEntry = Entry(centreFrame)
		self.hintEntry.grid(row=3, column=1)

		changePasswordButton = Button(self.changeMkPage, text="Change Master Key", cursor="hand2",
									  command=self.checkMasterKeyEntries, width=15, height=5)
		changePasswordButton.pack(side=BOTTOM)


class changesecuritysetting:

	def showSecWindow():
		ss = changesecuritysetting(root)
		root.mainloop()

	def applySettingsToDb(self):

		global minutes
		global timer_setting
		print("timer setting = " + str(self.timerSetting))

		#old minutes
		oldMinutes = fetchMinutes()
		print('old mins = ' + str(oldMinutes))

		if (int(self.timerSetting) == 1):
			self.minutesSetting = self.timer.get()
			print('new mins = ' + str(self.minutesSetting))	
			#print('mins = ' + str(self.minutesSetting))
			if (self.minutesSetting == 0):
				# get the old data from the table and set it to that
				self.minutesSetting = fetchMinutes()
		else:
			self.minutesSetting = 0
			print('new mins = ' + str(self.minutesSetting))	

		print(self.settingID, self.eyeSetting, self.copySetting, self.timerSetting, self.minutesSetting)
		# save to database
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("""UPDATE SETTINGS SET eyeIcon = ? , copyIcon = ?, timer = ?, minutes = ? WHERE settingID = ? """,
				  (self.eyeSetting, self.copySetting, self.timerSetting, self.minutesSetting, self.settingID))
		c.execute("SELECT * FROM SETTINGS")
		row = c.fetchall()
		print("Updated row data is " + str(row))
		minutes = fetchMinutes()
		timer_setting = fetchTimerEnabledSetting()
		# print("test minutes = " + str(minutes))
		# save changes made
		conn.commit()
		# close connection to db
		conn.close()

		#if minutes are different then software is updating minutes
		if (int(oldMinutes) != int(self.minutesSetting)):
			print('automatic logout settings were changed')
			#popup window (give the user an informing message in the popup window)
			tkinter.messagebox.showinfo("LockIT", "Any change to the Auto-Logout minutes requires a relog to take effect")

	def saveSettingsToDb(self):
		global minutes
		global timer_setting
		print("timer setting = " + str(self.timerSetting))

		#old minutes
		oldMinutes = fetchMinutes()
		print('old mins = ' + str(oldMinutes))

		if (int(self.timerSetting) == 1):
			#new minutes to be updated
			self.minutesSetting = self.timer.get()
			print('new mins = ' + str(self.minutesSetting))		
			
			if (self.minutesSetting == 0):
				# get the old data from the table and set it to that
				self.minutesSetting = fetchMinutes()
		else:
			self.minutesSetting = 0
			print('new mins = ' + str(self.minutesSetting))

		print(self.settingID, self.eyeSetting, self.copySetting, self.timerSetting, self.minutesSetting)
		# save to database
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("""UPDATE SETTINGS SET eyeIcon = ? , copyIcon = ?, timer = ?, minutes = ? WHERE settingID = ? """,
				  (self.eyeSetting, self.copySetting, self.timerSetting, self.minutesSetting, self.settingID))
		c.execute("SELECT * FROM SETTINGS")
		row = c.fetchall()
		print("Updated row data is " + str(row))
		minutes = fetchMinutes()
		timer_setting = fetchTimerEnabledSetting()
		# print("test minutes = " + str(minutes))`
		# save changes made
		conn.commit()
		# close connection to db
		conn.close()

		#if minutes are different then software is updating minutes
		if (int(oldMinutes) != int(self.minutesSetting)):
			print('automatic logout settings were changed')
			#popup window (give the user an informing message in the popup window)
			tkinter.messagebox.showinfo("LockIT", "Any change to the Auto-Logout minutes requires a relog to take effect")

		self.securitysetting.destroy()

	# cursor grabs data from security table and returns it
	def getDataFromInitSecurity(self):
		conn = sqlite3.connect('LockIT.db')
		c = conn.cursor()
		c.execute("SELECT settingID FROM SETTINGS WHERE settingID = 1")
		settingId_data = c.fetchall()
		c.execute("SELECT eyeIcon FROM SETTINGS WHERE settingID = 1")
		eye_data = c.fetchall()
		c.execute("SELECT copyIcon FROM SETTINGS WHERE settingID = 1")
		copy_data = c.fetchall()
		c.execute("SELECT timer FROM SETTINGS WHERE settingID = 1")
		timer_data = c.fetchall()
		c.execute("SELECT minutes FROM SETTINGS WHERE settingID = 1")
		minutes_data = c.fetchall()
		conn.close()
		return settingId_data, eye_data, copy_data, timer_data, minutes_data

	def trimData(self, dataToTrim):
		Str1 = str(dataToTrim)
		Str2 = Str1.replace('(', '')
		Str3 = Str2.replace(')', '')
		Str4 = Str3.replace(',', '')
		Str5 = Str4.replace('[', '')
		Str6 = Str5.replace(']', '')
		dataTrimmed = Str6
		return dataTrimmed

	def getOnOrOffFromData(self, eyeData, copyData, timerData):
		strEyeData = ""
		strCopyData = ""
		strTimerData = ""
		eyeData = self.trimData(eyeData)
		copyData = self.trimData(copyData)
		timerData = self.trimData(timerData)
		if (int(eyeData) != 0):
			strEyeData = "On"
		else:
			strEyeData = "Off"
		if (int(copyData) != 0):
			strCopyData = "On"
		else:
			strCopyData = "Off"
		if (int(timerData) != 0):
			strTimerData = "On"
		else:
			strTimerData = "Off"
		return strEyeData, strCopyData, strTimerData

	def __init__(self, master):

		# updater vars (all off initially)
		settingId_data = 0
		eye_data = 0
		copy_data = 0
		timer_data = 0
		minutes_data = 0
		strEyeData = ""
		strCopyData = ""
		strTimerData = ""
		strMinutesData = ""

		# set from data
		settingId_data, eye_data, copy_data, timer_data, minutes_data = self.getDataFromInitSecurity()

		self.settingID = self.trimData(settingId_data)
		self.eyeSetting = self.trimData(eye_data)
		self.copySetting = self.trimData(copy_data)
		self.timerSetting = self.trimData(timer_data)
		self.minutesSetting = self.trimData(minutes_data)

		print(self.settingID, self.eyeSetting, self.copySetting, self.timerSetting, self.minutesSetting)
		# button text will equal data from db
		strEyeData, strCopyData, strTimerData = self.getOnOrOffFromData(eye_data, copy_data, timer_data)
		##
		self.securitysetting = Toplevel()
		self.securitysetting.geometry("1000x700")
		self.securitysetting.resizable(0, 0)
		self.securitysetting.title("Security Settings")
		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		positionRight = int(root.winfo_screenwidth() / 4 - windowWidth / 2)
		positionDown = int(root.winfo_screenheight() / 4 - windowHeight / 2)

		# Positions the window in the center of the page.
		self.securitysetting.geometry("+{}+{}".format(positionRight, positionDown))

		self.logoframe = Frame(self.securitysetting)
		self.logoframe.columnconfigure(0, weight=1)

		self.content = Frame(self.securitysetting)

		for row in range(8):
			self.content.rowconfigure(row, weight=1)
			self.logoframe.rowconfigure(row, weight=1)
		for col in range(3):
			self.content.columnconfigure(col, weight=1)

		self.logoframe.pack(side='left', fill="both")
		self.content.pack(side='left', fill="both", expand=True)
		# logo
		path = resource_path('LockItLogoSmall.PNG')
		lockitlogo = PhotoImage(file=path)
		self.logo = Label(self.logoframe, image=lockitlogo)
		self.logo.image = lockitlogo

		self.master_access = Label(self.content, text="Enable Master Password Protection", font=("VerdanaBold", 12))
		# font.Font instead of tkFont.Fon
		f = font.Font(self.master_access, self.master_access.cget("font"))
		f.configure(underline=True)
		self.master_access.configure(font=f)
		self.viewData = Label(self.content,
							  text="Enables access to View Password/Media/Document Icon with Master Password")
		self.viewData_btn = Button(self.content, text=strEyeData, width=20, cursor="hand2", command=self.toggle)
		self.copyData = Label(self.content, text="Enables access to Copy Password with Master Password")
		self.copyData_btn = Button(self.content, text=strCopyData, width=20, cursor="hand2", command=self.toggle1)

		self.logout_section = Label(self.content, text="Enable Automatic Logout", font=("VerdanaBold", 12))
		# font.Font instead of tkFont.Fon
		f = font.Font(self.logout_section, self.logout_section.cget("font"))
		f.configure(underline=True)
		self.logout_section.configure(font=f)

		self.logout = Label(self.content,
							text="Enables automatic logout of the software after a certain amount of inactivity")
		self.logout_btn = Button(self.content, text=strTimerData, width=20, cursor="hand2", command=self.toggle2)
		self.timer_label = Label(self.content, text="Set number of minute(s) for automatic logout ( Changes to auto-logout require a relog to take effect )")
		self.timer = Spinbox(self.content, from_=1, to=10)

		self.save = Button(self.content, text="Save", command=self.saveSettingsToDb,
						   cursor="hand2")  # root.destroys itself and updates db
		self.apply = Button(self.content, text="Apply", command=self.applySettingsToDb,
							cursor="hand2")  # doesnt destory itself and updates db

		self.logo.grid(row=0, column=0, sticky="s")
		self.master_access.grid(row=0, column=1, sticky="nsew")
		self.viewData.grid(row=1, column=1, sticky="w")
		self.viewData_btn.grid(row=1, column=2, sticky="w")
		self.copyData.grid(row=2, column=1, sticky="w")
		self.copyData_btn.grid(row=2, column=2, sticky="w")
		self.logout_section.grid(row=3, column=1, sticky="nsew")
		self.logout.grid(row=4, column=1, sticky="w")
		self.logout_btn.grid(row=4, column=2, sticky="w")

		self.save.grid(row=6, column=2, sticky="ws", padx=5, pady=5)
		self.apply.grid(row=6, column=1, sticky="ws", padx=5, pady=5)

	def toggle(self):
		if self.viewData_btn.config('text')[-1] == 'On':
			self.viewData_btn.config(text='Off')
			self.eyeSetting = 0
			print("eyeSetting = " + str(self.eyeSetting))
		else:
			self.viewData_btn.config(text='On')
			self.eyeSetting = 1
			print("eyeSetting = " + str(self.eyeSetting))

	def toggle1(self):
		if self.copyData_btn.config('text')[-1] == 'On':
			self.copyData_btn.config(text='Off')
			self.copySetting = 0
			print("copySetting = " + str(self.copySetting))
		else:
			self.copyData_btn.config(text='On')
			self.copySetting = 1
			print("copySetting = " + str(self.copySetting))

	def toggle2(self):
		if self.logout_btn.config('text')[-1] == 'On':
			self.logout_btn.config(text='Off')
			self.timerSetting = 0
			self.timer_label.grid_forget()
			self.timer.grid_forget()

		else:
			self.logout_btn.config(text='On')
			self.timerSetting = 1
			self.timer_label.grid(row=5, column=1, sticky="w")
			self.timer.grid(row=5, column=2, sticky="w")


class Page(tk.Frame):
	def __init__(self, *args, **kwargs):
		tk.Frame.__init__(self, *args, **kwargs)

	def show(self):
		self.lift()

class MainView(tk.Frame):

	def __init__(self, *args, **kwargs):
		tk.Frame.__init__(self, *args, **kwargs)

		# Side bar buttons function definitions
		def on_pasbutton_enter(e):
			my_pass_button['background'] = '#F5F5F5'

		def on_pasbutton_leave(e):
			my_pass_button['background'] = 'white'

		def on_medbutton_enter(e):
			my_med_button['background'] = '#F5F5F5'

		def on_medbutton_leave(e):
			my_med_button['background'] = 'white'

		def on_docbutton_enter(e):
			my_doc_button['background'] = '#F5F5F5'

		def on_docbutton_leave(e):
			my_doc_button['background'] = 'white'

		# seperate main window in two frames

		self.buttonframe = tk.Frame(self, background="#003152")
		container = tk.Frame(self)
		self.buttonframe.pack(side="left", fill="both", expand=False)
		container.pack(side="left", fill="both", expand=True)

		# pages declarations
		p1 = PasswordPage(self)
		p2 = MediaPage(self)
		p3 = DocumentPage(self)

		p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

		# Button frame

		#logo
		path = resource_path('LockItLogo.PNG')
		lockitlogo = PhotoImage(file=path)
		logo = Label(self.buttonframe, image=lockitlogo,height=200, width=150)
		logo.image = lockitlogo
		logo.pack(side="top")

		my_pass_button = Button(self.buttonframe, text="Passwords", fg="black", bg="white", width=25, height=3,
								command=p1.lift, relief="groove", font=("Verdana", 9),cursor = "hand2")
		my_pass_button.bind("<Enter>", on_pasbutton_enter)
		my_pass_button.bind("<Leave>", on_pasbutton_leave)
		my_pass_button.pack(side="top")

		my_med_button = Button(self.buttonframe, text="Media", fg="black", bg="white", width=25, height=3,
							   command=p2.lift, relief="groove", font=("Verdana", 9),cursor = "hand2")
		my_med_button.bind("<Enter>", on_medbutton_enter)
		my_med_button.bind("<Leave>", on_medbutton_leave)
		my_med_button.pack(side="top")

		my_doc_button = Button(self.buttonframe, text="Documents", fg="black", bg="white", width=25, height=3,
							   command=p3.lift, relief="groove", font=("Verdana", 9),cursor = "hand2")
		my_doc_button.bind("<Enter>", on_docbutton_enter)
		my_doc_button.bind("<Leave>", on_docbutton_leave)
		my_doc_button.pack(side=TOP)

		p1.lift()


class PasswordPage(Page):
	def __init__(self, *args, **kwargs):
		Page.__init__(self, *args, **kwargs)

		self.policy = PasswordPolicy.from_names(
			length=6,  # min length: 6
			uppercase=1,  # need min. 1 uppercase letters
			numbers=1,  # need min. 2 digits
			special=1,  # need min. 2 special characters
			nonletters=2,  # need min. 2 non-letter characters (digits, specials, anything)
		)

		self.passwordScreen = Frame(self, background="white")
		self.passwordScreen.pack(fill="both", expand=True)
		self.passwordScreen.columnconfigure(0, weight=1)
		self.passwordScreen.rowconfigure(0, weight=1)

		self.frames = {}

		for F in (PasswordCategoryPage,ViewPasswords_InCategory,CreateNewPassword,ViewPassword,ModifyPassword):
			page_name = F.__name__
			frame = F(parent=self.passwordScreen, controller=self)
			self.frames[page_name] = frame


			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame("PasswordCategoryPage")

	# def show_frame(self, page_name, arg=None):
	# 	'''Show a frame for the given page name'''
	# 	frame = self.frames[page_name]
	# 	frame.tkraise()
	# 	return frame

	def show_frame(self, page_name):
		for frame in self.frames.values():
			frame.grid_remove()
		frame = self.frames[page_name]
		frame.grid()
		return frame

	def get_page(self, page_name):
		return self.frames[page_name]

class PasswordCategoryPage(tk.Frame):


	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		# main container
		self.passwordScreen = Frame(self, background="white")
		self.passwordScreen.pack(fill="both", expand=True)

		# separate screen in 3 frames
		self.buttonframe = tk.Frame(self.passwordScreen)
		self.contentframe = tk.Frame(self.passwordScreen)
		self.separator = tk.Frame(self.passwordScreen, bg="light grey")
		self.buttonframe.pack(side="left", fill="both", expand=False)
		self.separator.pack(side="left", fill="both", expand=False)
		self.contentframe.pack(side="left", fill="both", expand=True)

		self.contentframe.columnconfigure(0, weight=1)
		self.contentframe.rowconfigure(0, weight=1)
		self.contentframe.rowconfigure(1, weight=1)
		self.contentframe.rowconfigure(2, weight=12)

		# button frame
		space = tk.Label(self.buttonframe, height=1)
		space.pack(side="bottom")

		# top frame
		self.top = tk.Frame(self.contentframe, relief="groove")
		self.top.grid(column=0, row=0, sticky=(N, S, E, W))
		self.top.columnconfigure(0, weight=1)
		self.top.rowconfigure(0, weight=1)
		self.top.rowconfigure(1, weight=1)

		# Title
		self.Title = tk.Label(self.top, text="All Categories", font=("Verdana", 15), fg="white", bg="#003152", width=40)

		self.Title.grid(column=0, row=0, sticky=(N, S, E, W))




		# Buttons
		# images
		path = resource_path('added.png')
		self.addIcon = PhotoImage(file=path)
		self.add = Button(self.top, text="New Category", compound=RIGHT, font=("Verdana", 10), fg='black',
						 image=self.addIcon, cursor="hand2",command=self.addcategory)
		self.add.image = self.addIcon
		self.add.grid(column=0, row=1, sticky=(N, E))

		# passwords categories content

		self.labels = {}
		self.frames = {}

		#retrieve categories from database
		self.dict = self.get_categories()

		self.button = []

		self.load_categories(self.dict)

	# category labels function definitions
	def on_category_enter(self, event):
		event.widget['background'] = 'white'

	# category labels function definitions
	def on_category_leave(self, event):
		event.widget['background'] = 'light grey'

	#forger categories frame
	def forget_categories(self):

		for key, value in self.frames.items():
			self.frames[key].destroy()
		for key, value in self.labels.items():
			self.labels[key].destroy()
		# self.category_frame.destroy()
		self.container.destroy()


	#load categories to content frame
	def load_categories(self,categories):
		self.container = tk.Frame(self.contentframe)
		for r in range(5):
			self.container.columnconfigure(r, weight=1)
		for r in range(7):
			self.container.rowconfigure(r, weight=1)
		self.container.grid(column=0, row=2, sticky=(N, S, E, W))
		loop = 0
		i = 0
		for key, value in categories.items():
			self.name = key
			self.category_frame = Frame(self.container, bg=value, bd=1, relief="groove")
			self.category_name = Label(self.category_frame, text=self.name, font=("Verdana", 12, "bold"), bd=1, fg="black",
									   height=2, cursor='hand2')

			# Add the Label to the list
			self.frames[self.name]=self.category_frame
			self.labels[self.name]=self.category_name
			if (loop < 5 and i < 5):
				self.category_frame.grid(row=0, column=i, sticky=(N, S, E, W), padx=5, pady=5)
			elif (loop < 10 and i < 5):
				self.category_frame.grid(row=1, column=i, sticky=(N, S, E, W), padx=5, pady=5)
			elif (loop < 15 and i < 5):
				self.category_frame.grid(row=2, column=i, sticky=(N, S, E, W), padx=5, pady=5)

			self.category_frame.rowconfigure(0, weigh=1)
			self.category_frame.columnconfigure(0, weigh=1)
			self.category_name.grid(row=0, column=0, sticky=(W, E), padx=5, pady=5)
			self.category_name.bind("<Double-Button-1>", self.showPasswordPage)
			self.category_name.bind("<Button-3>", self.popup)
			self.category_name.bind("<Enter>", self.on_category_enter)
			self.category_name.bind("<Leave>", self.on_category_leave)
			loop = loop + 1
			i = i + 1
			if (i == 5):
				i = 0


	# Dropdown List
	def getColor(self):
		self.color = askcolor()
		if(self.color !=""):
			self.select_color['bg'] = self.color[-1]


	# function to retrieve categories from database
	def get_categories(self):
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		d = dict(c.execute("SELECT CATEGORY_NAME, COLOUR_HEX FROM CATEGORY", ()).fetchall())
		# return security level id from db

		conn.close()
		return d


	# function to show the menu options
	def popup(self, event):
		# create a popup menu
		self.category_clicked = ''
		self.aMenu = tk.Menu(self.passwordScreen, tearoff=0)
		self.aMenu.add_command(label='Modify Category', command=self.editcategory)
		self.aMenu.add_command(label='Delete Category', command=self.deletecategory)
		self.category_clicked = event.widget['text']
		self.aMenu.post(event.x_root, event.y_root)


	#function to add category
	def addcategory(self):

		self.add['state'] = DISABLED

		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.addcategoryWindow=Toplevel()
		self.addcategoryWindow.geometry("300x200")
		self.addcategoryWindow.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.addcategoryWindow.resizable(0, 0)
		self.addcategoryWindow.title("Add New Category")
		self.addcategoryWindow.wm_attributes('-topmost', 1)
		self.addcategoryWindow.protocol("WM_DELETE_WINDOW", self.closeWindow)

		for row in range(8):
			self.addcategoryWindow.rowconfigure(row, weight=1)
		for col in range(3):
			self.addcategoryWindow.columnconfigure(col, weight=1)


		# Labels
		self.CategoryName = Label(self.addcategoryWindow, text="Name",width=5, font=("Verdana", 13))
		self.Colourchoice = Label(self.addcategoryWindow, text="Colour",width=5, font=("Verdana", 13))
		self.catNameError = Label(self.addcategoryWindow, text="",width=25, anchor='w', fg='red')
		self.catNameError.config(font=("Verdana", 7))
		self.colorError = Label(self.addcategoryWindow, text="", anchor='w',width=25, fg='red',font=("Verdana", 7))


		# Buttons
		self.Save = Button(self.addcategoryWindow, text="Save", font=("Arial", 13, "italic"), relief="groove", background="#003152",
					  fg="white",command=self.cat_addvalidate)

		# Inputs
		self.Input = Entry(self.addcategoryWindow,width=25, relief="groove")
		self.color = ""



		self.select_color = Button(self.addcategoryWindow,text='Select New Color', font=("Verdana", 10, "italic"), relief="groove", command=self.getColor,
			   fg="grey")

		# Position
		self.CategoryName.grid(row=2,column=0,sticky="w")
		self.Input.grid(row=2,column=1,sticky="w")
		self.catNameError.grid(row=3, column=1, sticky="w")
		self.Colourchoice.grid(row=4,column=0,sticky="w")
		self.select_color.grid(row=4,column=1,sticky="w")
		self.colorError.grid(row=5,column=1,sticky="w")
		self.Save.grid(row=7,column=2,sticky="w")

	def closeWindow(self):
		self.addcategoryWindow.destroy()
		self.add['state'] = NORMAL


	# Create category in database
	def insert_category(self, catname, colorcode):


		conn = sqlite3.connect('LockIT.db')
		c = conn.cursor()
		c.execute("INSERT INTO CATEGORY VALUES(NULL,?,?)", (catname, colorcode,))

		conn.commit()
		# close database
		conn.close()

		self.addcategoryWindow.destroy()
		self.add['state'] = NORMAL
		# retrieve categories from database
		self.dict = self.get_categories()

		self.forget_categories()
		self.load_categories(self.dict)

	# function that validates the entries
	def cat_addvalidate(self):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 35

		if (self.catNameError.cget('text') != ''):
			self.catNameError['text'] = ''

		if (self.colorError.cget('text') != ''):
			self.colorError['text'] = ''

		# check length of entry

		catname = self.Input.get()
		en_len = len(str(catname))

		if (catname==""):
			num_errors += 1
			errMsg = "Please enter category name"
			self.catNameError['text'] = errMsg

		elif (en_len < min_entry_len):
			num_errors += 1
			errMsg = "Category must be at least 2 characters"
			self.catNameError['text'] = errMsg

		elif (en_len > max_entry_len):
			num_errors += 1
			errMsg = "Category can have maximum 35 characters."
			self.catNameError['text'] = errMsg
		else:
			# return category count from db
			catname = catname.upper()
			c.execute("SELECT COUNT(*) FROM CATEGORY WHERE CATEGORY_NAME=?", (catname,))
			rec1 = c.fetchone()
			cat_name_occur = int(rec1[0])
			c.execute("SELECT COUNT(*) FROM CATEGORY")
			rec2 = c.fetchone()
			cat_num = int(rec2[0])

			if (cat_name_occur >= 1):
				num_errors += 1
				errMsg = "Category name is a duplicate\nSelect a different name"
				self.catNameError['text'] = errMsg

			if (cat_num > 14):
				num_errors += 1
				errMsg = "Only 15 categories allowed,\n please delete 1"
				self.catNameError['text'] = errMsg

		if(self.color == ""):
			num_errors += 1
			errMsg = "Please select color"
			self.colorError['text'] = errMsg
		else:
			colorcode = self.color[-1]
			# return color count from db
			c.execute("SELECT COUNT(*) FROM CATEGORY WHERE COLOUR_HEX=?", (colorcode,))
			rec2 = c.fetchone()
			color_occur = int(rec2[0])

			if (color_occur >= 1):
				num_errors += 1
				errMsg = "Color is already used\nSelect a new color"
				self.colorError['text'] = errMsg


		# close connection to db
		conn.close()

		if (num_errors == 0):
			self.insert_category(catname, colorcode)

	# function to modify category name and color
	def editcategory(self):

		self.editcategoryWindow = Toplevel()
		self.editcategoryWindow.geometry("300x200")
		self.editcategoryWindow.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.editcategoryWindow.resizable(0, 0)
		self.editcategoryWindow.title("Edit Category " + self.category_clicked)
		self.editcategoryWindow.wm_attributes('-topmost', 1)

		for row in range(8):
			self.editcategoryWindow.rowconfigure(row, weight=1)
		for col in range(3):
			self.editcategoryWindow.columnconfigure(col, weight=1)

		# Labels
		self.CategoryName = Label(self.editcategoryWindow, text="Name", font=("Verdana", 13))
		self.Colourchoice = Label(self.editcategoryWindow, text="Colour", font=("Verdana", 13))
		self.catNameError = Label(self.editcategoryWindow, text="", anchor='w', fg='red')
		self.catNameError.config(font=("Verdana", 7))
		self.colorError = Label(self.editcategoryWindow, text="", anchor='w', fg='red', font=("Verdana", 7))

		# Buttons
		self.Save = Button(self.editcategoryWindow, text="Save", font=("Arial", 13, "italic"), relief="groove",
						   background="#003152",
						   fg="white", command=self.cat_editvalidate)

		# Inputs
		self.Input = Entry(self.editcategoryWindow, relief="groove")
		self.Input.insert(0, self.category_clicked)
		self.color = ""

		currentColor = self.get_colorDB(self.category_clicked)


		self.select_color = Button(self.editcategoryWindow, text='Select New Color', font=("Verdana", 10, "italic"),
								   relief="groove", command=self.getColor, fg="grey",bg=currentColor)

		# Position
		self.CategoryName.grid(row=2, column=0, sticky="w")
		self.Input.grid(row=2, column=1, sticky="w")
		self.catNameError.grid(row=3, column=1, sticky="w")
		self.Colourchoice.grid(row=4, column=0, sticky="w")
		self.select_color.grid(row=4, column=1, sticky="w")
		self.colorError.grid(row=5, column=1, sticky="w")
		self.Save.grid(row=7, column=2, sticky="w")


	def get_colorDB(self,category_name):
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		c.execute("SELECT COLOUR_HEX FROM CATEGORY WHERE CATEGORY_NAME=?", (category_name,))
		rec2 = c.fetchone()

		conn.close()

		return rec2

	# Edit category in database
	def edit_categoryDB(self, catname, colorcode=None):
		catclick = self.category_clicked
		conn = sqlite3.connect('LockIT.db')
		c = conn.cursor()
		if(colorcode==None):
			c.execute("UPDATE CATEGORY SET CATEGORY_NAME = ? WHERE CATEGORY_NAME =?",
					  (catname, catclick,))
		else:
			c.execute("UPDATE CATEGORY SET CATEGORY_NAME = ?, COLOUR_HEX = ? WHERE CATEGORY_NAME =?",
				  (catname, colorcode, catclick,))
		conn.commit()
		# close database
		conn.close()

		self.editcategoryWindow.destroy()
		self.forget_categories()
		self.dict = self.get_categories()
		self.load_categories(self.dict)

	# function that validates the entries
	def cat_editvalidate(self):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 35

		if (self.catNameError.cget('text') != ''):
			self.catNameError['text'] = ''

		if (self.colorError.cget('text') != ''):
			self.colorError['text'] = ''

		# check length of entry

		catname = self.Input.get()
		catname = catname.upper()

		en_len = len(str(catname))

		if(catname != self.category_clicked):

			if (catname == ""):
				num_errors += 1
				errMsg = "Please enter category name"
				self.catNameError['text'] = errMsg

			elif (en_len < min_entry_len):
				num_errors += 1
				errMsg = "Category must be at least 2 characters"
				self.catNameError['text'] = errMsg

			elif (en_len > max_entry_len):
				num_errors += 1
				errMsg = "Category can have maximum 35 characters."
				self.catNameError['text'] = errMsg
			else:
				# return category count from db
				catname = catname.upper()
				c.execute("SELECT COUNT(*) FROM CATEGORY WHERE CATEGORY_NAME=?", (catname,))
				rec1 = c.fetchone()
				cat_name_occur = int(rec1[0])

				if (cat_name_occur >= 1):
					num_errors += 1
					errMsg = "Category name is a duplicate\nSelect a different name"
					self.catNameError['text'] = errMsg

		if (self.color != ""):

			colorcode = self.color[-1]
			# return color count from db
			c.execute("SELECT COUNT(*) FROM CATEGORY WHERE COLOUR_HEX=?", (colorcode,))
			rec2 = c.fetchone()
			color_occur = int(rec2[0])

			if (color_occur >= 1):
				num_errors += 1
				errMsg = "Color is already used\nSelect a new color"
				self.colorError['text'] = errMsg

		# close connection to db
		conn.close()

		if (num_errors == 0):
			if(self.color == ""):
				self.edit_categoryDB(catname)
			else:
				self.edit_categoryDB(catname, colorcode)

	# function to delete category
	def deletecategory(self):

		question = "Would you like to delete this category?"
		answer = tkinter.messagebox.askquestion(self.category_clicked, question)
		if (answer == 'yes'):
			catclick = self.category_clicked
			conn = sqlite3.connect('LockIT.db')
			c = conn.cursor()

			# return category id from db
			c.execute("SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME=?", (catclick,))
			rec2 = c.fetchone()
			category_id = int(rec2[0])

			c.execute("SELECT COUNT(*) FROM PASSWORD WHERE CATEGORY =?", (category_id,))
			pass_num = c.fetchone()
			pass_num = int(pass_num[0])

			if (pass_num == 0):
				c.execute("DELETE FROM CATEGORY WHERE CATEGORY_NAME =?", (catclick,))
			else:
				answer = tkinter.messagebox.askquestion("Delete Category",
														"This category is not empty,all passwords will be deleted")
				if (answer == 'yes'):
					c.execute("DELETE FROM PASSWORD WHERE CATEGORY =?", (category_id,))
					c.execute("DELETE FROM CATEGORY WHERE CATEGORY_NAME =?", (catclick,))

			conn.commit()
			# close database
			conn.close()

			# retrieve categories from database

			self.forget_categories()
			self.dict = self.get_categories()
			self.load_categories(self.dict)


	def showPasswordPage(self, event):
		self.controller.show_frame("ViewPasswords_InCategory").set_category(event.widget['text'])


class ViewPasswords_InCategory(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.selected_category=""


		#return image
		self.back = PhotoImage(file=resource_path('return.png'))

		style = ttk.Style()
		style.configure("mystyle.Treeview", highlightthickness=0, bd=0,
						font=('Verdana', 11))  # Modify the font of the body
		style.configure("mystyle.Treeview.Heading", font=('Verdana', 13, 'bold'))  # Modify the font of the headings
		style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		# main container
		self.ViewPasswords_Screen = Frame(self)
		self.ViewPasswords_Screen.pack(fill="both", expand=True)

		# separate screen in 3 frames
		self.buttonframe = tk.Frame(self.ViewPasswords_Screen)
		self.contentframe = tk.Frame(self.ViewPasswords_Screen)
		self.separator = tk.Frame(self.ViewPasswords_Screen, bg="light grey")
		self.buttonframe.pack(side="left", fill="both", expand=False)
		self.separator.pack(side="left", fill="both", expand=False)
		self.contentframe.pack(side="left", fill="both", expand=True)

		self.contentframe.columnconfigure(0, weight=1)
		self.contentframe.rowconfigure(0, weight=1)
		self.contentframe.rowconfigure(1, weight=1)
		self.contentframe.rowconfigure(2, weight=8)
		self.contentframe.rowconfigure(3, weight=1)

		# button frame
		space = tk.Label(self.buttonframe, height=1)
		space.pack(side="bottom")

		# home banner

		self.home_label = tk.Label(self.contentframe, text='', font=("Verdana", 15,"bold"), background="white",
							  relief="groove", height=1)

		self.home_label.grid(column=0, row=0, sticky=(N, S, E, W))

		addNewPassButton = Button(self.contentframe, text="+ Add new password",cursor='hand2',
								  command=self.add_new_password)
		addNewPassButton.config(height=1,font=("Verdana", 10),fg="black", relief="groove",cursor="hand2", bg="white")
		addNewPassButton.grid(column=0, row=1, sticky=(N, S, E, W))


		# fetch data from password table
		# self.entry_name_data, self.website_data, self.username_data = self.fetchFromPassTable()

		# add columns the treeview
		self.treeview = ttk.Treeview(self.contentframe, style="mystyle.Treeview")
		self.treeview.grid(column=0, row=2, sticky=(N, S, E, W))
		self.treeview.config(columns=('website', 'user', 'password', 'timer'))
		self.treeview.tag_configure('odd', background='light blue')
		self.treeview.tag_configure('even', background='grey')
		self.treeview.column('website', width=250, anchor='w')
		self.treeview.column('#0', width=90, anchor='w')
		self.treeview.column('user', width=90, anchor='w')
		self.treeview.column('password', width=90, anchor='w')
		self.treeview.column('timer', width=90, anchor='w')
		self.treeview.heading('#0', text='Entry Name')
		self.treeview.heading('website', text='Website')
		self.treeview.heading('user', text='Username')
		self.treeview.heading('password', text='Password')
		self.treeview.heading('timer', text='Timer')
		self.treeview.bind("<Double-1>", self.showViewPassword)
		self.treeview.bind('<Button-3>', self.popup_password)


		return_button = Button(self.contentframe, text="Return", image=self.back, compound=tk.LEFT, fg="white",
							   bg='#003152', command=self.go_back)
		return_button.config(relief="groove", width=80, font=("Verdana", 10))
		return_button.grid(column=0, row=3, sticky=(W))

		return_button.image = self.back

	def add_new_password(self):
		self.controller.show_frame("CreateNewPassword").set_category(self.selected_category)


	# this is to update a column in a treeview, cant figure it out at the moment
	# self.treeview.set('row1','password',ogPassword)
	def go_back(self):
		self.treeview.delete(*self.treeview.get_children())
		self.controller.show_frame("PasswordCategoryPage")

	def insert_treeview_widget(self, entry_name_data, website_data,timer):
		self.treeview.insert("", 'end', entry_name_data, text=entry_name_data, values=(
			website_data, '********', '********', timer))


	# fetches data for entryname,website,username and returns it
	def fetchFromPassTable(self,category_id):

		#remove items in the tree
		self.treeview.delete(*self.treeview.get_children())
		# make connection to db
		conn = sqlite3.connect('LockIT.db',detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

		# make cursor
		c = conn.cursor()


		c.execute("SELECT ENTRY_NAME,WEBSITE,S_LEVEL,DATE_CREATED FROM PASSWORD WHERE CATEGORY=?", (category_id,))
		pass_info = c.fetchall()

		today = date.today()
		for row in pass_info:
			entry,web,sec_level,dateDB = row

			if(sec_level == 1):
				timer = "never expire"
			elif(sec_level == 2):
				six_months = timedelta(days=182)
				expire = dateDB+six_months
				print("expire in %d days" % ((expire - today).days))
				if((expire - today).days <= 0):
					timer = "Password is expired"
				else:
					timer = "expire in %d days" % ((expire - today).days)
			elif(sec_level == 3):
				three_months = timedelta(days=91)
				expire = dateDB + three_months
				if ((expire - today).days <= 0):
					timer = "Password is expired"
				else:
					timer = "expire in %d days" % ((expire - today).days)
			elif(sec_level == 4):
				one_months = timedelta(days=31)
				expire = dateDB + one_months
				if ((expire - today).days <= 0):
					timer = "Password is expired"
				else:
					timer = "expire in %d days" % ((expire - today).days)
			self.insert_treeview_widget(entry,web,timer)

		# close
		conn.close()


	# function to show the entry password page
	def showViewPassword(self, event):
		item = self.treeview.selection()[0]
		entryName = str(self.treeview.item(item, "text"))
		self.controller.show_frame("ViewPassword").pass_variables(self.home_label.cget('text'),entryName)

	# function to update ViewPasswords inside category page
	def set_category(self, category):
		self.home_label['text'] = category
		self.selected_category = category

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		# return security level id from db
		c.execute("SELECT COLOUR_HEX FROM CATEGORY WHERE CATEGORY_NAME=?", (category,))
		color = c.fetchone()

		# return category id from db
		c.execute("SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME=?", (self.selected_category,))
		rec2 = c.fetchone()
		self.category_id = int(rec2[0])

		# close connection to db
		conn.close()

		self.fetchFromPassTable(self.category_id)

		# set the category label background
		self.home_label['bg'] = color

	# function to show the menu options
	def popup_password(self, event):
		# print('we are in popup_password')
		self.x = root.winfo_x()
		self.y = root.winfo_y()

		item = self.treeview.item(self.treeview.focus())

		self.entryName = item['text']
		self.password = item['values'][2]
		print(self.password)


		# create a popup menu

		viewIcon = PhotoImage(file=resource_path('eyesmall.png'))
		copyIcon = PhotoImage(file=resource_path('copyIcon.png'))
		redirectIcon = PhotoImage(file=resource_path('redirectIcon.png'))

		self.aMenu = tk.Menu(self.ViewPasswords_Screen, tearoff=0)
		if(self.password=='********'):
			self.aMenu.add_command(label='Show Password', image=viewIcon, compound=tk.LEFT, command=self.show_password)
			self.aMenu.add_command(label='Copy Password', image=copyIcon, compound=tk.LEFT, command=self.copy_password)
			self.aMenu.add_command(label='Visit Website', image=redirectIcon, compound=tk.LEFT,
								   command=self.visit_website)
		else:
			self.aMenu.add_command(label='Hide Password', image=viewIcon, compound=tk.LEFT, command=self.hide_password)
			self.aMenu.add_command(label='Copy Password', image=copyIcon, compound=tk.LEFT, command=self.copy_password)
			self.aMenu.add_command(label='Visit Website', image=redirectIcon, compound=tk.LEFT,
								   command=self.visit_website)
		self.aMenu.image = viewIcon, copyIcon, redirectIcon

		# self.category_clicked = event.widget['text']
		self.aMenu.post(event.x_root, event.y_root)

	# function to show password on click
	def show_password(self):

		# show=1
		# make connection
		conn = sqlite3.connect('LockIT.db',detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
		# add cursor
		c = conn.cursor()
		# statements
		c.execute("SELECT PASS_KEY,PASSWORD,USERNAME,S_LEVEL,DATE_CREATED FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?", (self.entryName, self.category_id,))
		key,encrypted,username,sec_level,dateDB = c.fetchone()

		# close database
		conn.close()
		today = date.today()

		if (sec_level == 1):
			self.passwordExpired = "off"
		elif (sec_level == 2):
			six_months = timedelta(days=182)
			expire = dateDB + six_months
			if ((expire - today).days <= 0):
				self.passwordExpired = "on"
			else:
				self.passwordExpired = "off"
		elif (sec_level == 3):
			three_months = timedelta(days=91)
			expire = dateDB + three_months
			if ((expire - today).days <= 0):
				self.passwordExpired = "on"
			else:
				self.passwordExpired = "off"
		elif (sec_level == 4):
			one_months = timedelta(days=31)
			expire = dateDB + one_months
			if ((expire - today).days <= 0):
				self.passwordExpired = "on"
			else:
				self.passwordExpired = "off"

		if(self.passwordExpired == "on"):
			tkinter.messagebox.showerror("Error", "Your password is expired, please create new password for this entry")
		else:
			# decrypting
			keyS = key + Login.loginScreen.getMasterKey(root).encode()
			f2 = Fernet(keyS)
			decrypted = f2.decrypt(encrypted)
			self.original_password = decrypted.decode()
			user = f2.decrypt(username)
			userD = user.decode()
			self.getPassPopup(self.original_password,userD)


	#function to hide password
	def hide_password(self):
		self.treeview.set(self.entryName, 'password', '********')
		self.treeview.set(self.entryName, 'user', '********')

	def getPassPopup(self, ogPassword,ogUserName):  # temporary popup window to show password
		# cannot refer to self because showpassword() is called from diff class

		# self.setTreeview(ogPassword) 	###Error here  NameError: name 'self' is not defined

		viewData = self.grabSettingsData()
		# check if the passprovided and hash val in db are same , if same call toplevel
		# print(viewData)
		if (int(viewData) == 1):
			self.askForMP(ogPassword,ogUserName)
		else:
			# self.viewData(ogPassword)
			self.treeview.set(self.entryName, 'password', ogPassword)
			self.treeview.set(self.entryName, 'user', ogUserName)
			# windowObj.destroy()

	# function to delete category
	def copy_password(self):
		# copy=1
		# check settings for copy data security settings
		# make connection
		conn = sqlite3.connect('LockIT.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
		# add cursor
		c = conn.cursor()
		# statements
		c.execute("SELECT PASS_KEY,PASSWORD,S_LEVEL,DATE_CREATED FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?",
				  (self.entryName, self.category_id,))
		key,encrypted,sec_level, dateDB = c.fetchone()

		today = date.today()

		if (sec_level == 1):
			self.passwordExpired = "off"
		elif (sec_level == 2):
			six_months = timedelta(days=182)
			expire = dateDB + six_months
			if ((expire - today).days <= 0):
				self.passwordExpired = "on"
			else:
				self.passwordExpired = "off"
		elif (sec_level == 3):
			three_months = timedelta(days=91)
			expire = dateDB + three_months
			if ((expire - today).days <= 0):
				self.passwordExpired = "on"
			else:
				self.passwordExpired = "off"
		elif (sec_level == 4):
			one_months = timedelta(days=31)
			expire = dateDB + one_months
			if ((expire - today).days <= 0):
				self.passwordExpired = "on"
			else:
				self.passwordExpired = "off"

		if (self.passwordExpired == "on"):
			tkinter.messagebox.showerror("Error", "Your password is expired, please create new password for this entry")
		else:
			# decrypting
			keyS = key + Login.loginScreen.getMasterKey(root).encode()
			f2 = Fernet(keyS)
			decrypted = f2.decrypt(encrypted)
			self.original_password = decrypted.decode()


			# Copy Data
			c.execute("SELECT copyIcon FROM SETTINGS")
			copyIcon = c.fetchone()
			copyIcon = int(copyIcon[0])

			# close database
			conn.close()

			if (int(copyIcon) == 1):
				# ask for mp
				self.askForMPForCopy()
			else:
				# copy to clipboard
				pyperclip.copy(self.original_password)
				spam = pyperclip.paste()
				print(spam, 'is now in your clipboard')
				spam = spam + ' is now in your clipboard'
				tkinter.messagebox.showinfo("Copy Password", spam)

	def visit_website(self):
		# make connection
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		# statements
		c.execute("SELECT WEBSITE,USERNAME,PASSWORD,PASS_KEY FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?",
				  (self.entryName, self.category_id,))
		website,username,password,key = c.fetchone()
		website = str(website)

		# close database
		conn.close()

		if(website == ""):
			tkinter.messagebox.showwarning("Website", "There is no website for this entry")
		else:
			# decrypting
			keyS = key + Login.loginScreen.getMasterKey(root).encode()
			f2 = Fernet(keyS)
			decryptedP = f2.decrypt(password)
			password = decryptedP.decode()

			decryptedU = f2.decrypt(username)
			username = decryptedU.decode()

			web = Browser()
			web.go_to(website)

			if web.exists('Agree') == True:
				web.click('Agree')

			if web.exists('Sign in') == True:
				web.click('Sign in')
			elif web.exists('Sign In') == True:
				web.click('Sign In')
			elif web.exists('Log in') == True:
				web.click('Log in')
			elif web.exists('Login') == True:
				web.click('Login')

			if web.exists('Email') == True:
				web.type(username, into='Email')
			elif web.exists('Username') == True:
				web.type(username, into='Username')

			web.click('NEXT', tag='span')
			web.type(password, into='Password', id='passwordFieldId')  # specific selection
			web.click('NEXT', tag='span')  # you are logged in ^_^


	# prompts the user for the master password, displays error if not correct input
	def checkIfMatchForCopy(self, entryText, windowObj):

		# if not matching hash vals, then error
		conn = sqlite3.connect('LockIT.db')
		c = conn.cursor()
		c.execute("SELECT passwordHash FROM LOCKITUSER")
		hashValFromDb = c.fetchone()
		conn.close()
		# parse data
		hashVal = str(hashValFromDb[0])
		hashVal = hashVal.replace('b', '', 1)
		hashVal = hashVal.replace("'", '', 2)
		# compare password in db with entry
		# print(hashVal)
		hashVal = hashVal.encode()
		print(hashVal)
		if (bcrypt.checkpw(str(entryText.get()).encode(), hashVal)):
			print("Both Entries Match!")
			# copy to clipboard
			pyperclip.copy(self.original_password)
			spam = pyperclip.paste()
			spam = spam + ' is now in your clipboard'
			tkinter.messagebox.showinfo("Copy Password", spam)
			windowObj.destroy()
		else:
			print("Entries Do not Match :(")
			# give errror message
			errMsg = "Password entries do not match"
			lbl = Label(windowObj, fg="red", text=errMsg)
			lbl.grid(row=3, column=0,sticky='nsew')
			windowObj.after(5000, lbl.destroy)

	def askForMPForCopy(self):

		cpWin = tk.Toplevel()
		cpWin.geometry("200x150")
		cpWin.wm_title("LockIT")
		cpWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))

		for r in range(4):
			cpWin.rowconfigure(r,weight=1)
		cpWin.columnconfigure(0, weight=1)

		l = tk.Label(cpWin, text="Please Enter Master Password ",anchor='center')
		l.grid(row=0, column=0,sticky='nswe',padx=5,pady=5)
		e = tk.Entry(cpWin, width=20, show="*")
		e.grid(row=2, column=0,sticky='nswe',padx=5,pady=5)


		b = ttk.Button(cpWin, text="Submit",cursor="hand2", command=lambda: self.checkIfMatchForCopy(e, cpWin))
		b.grid(row=4, column=0,sticky='e',padx=5,pady=5)
		nb = ttk.Button(cpWin, text="Return",cursor="hand2", command=cpWin.destroy)
		nb.grid(row=4, column=0,sticky='w',padx=5,pady=5)

	def trimSettingsData(self, dataToTrim):
		# print('inside the trim2 function')
		Str1 = str(dataToTrim)
		Str2 = Str1.replace('(', '')
		Str3 = Str2.replace(')', '')
		Str4 = Str3.replace(',', '')
		Str5 = Str4.replace('[', '')
		Str6 = Str5.replace(']', '')
		dataTrimmed = Str6
		return dataTrimmed

	def grabSettingsData(self):
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# make cursor
		c = conn.cursor()

		# View Data
		c.execute("SELECT eyeIcon FROM SETTINGS")
		eyeIcon = c.fetchone()
		# save changes made
		conn.commit()
		# close database
		conn.close()

		# copyIcon=ViewPasswords_InCategory.trimSettingsData(copyIcon)
		eyeIcon = self.trimSettingsData(eyeIcon)

		return eyeIcon

	def checkIfMatch(self, entryText, ogPassword,ogUserName,windowObj):

		# if not matching hash vals, then error
		conn = sqlite3.connect('LockIT.db')
		c = conn.cursor()
		c.execute("SELECT passwordHash FROM LOCKITUSER")
		hashValFromDb = c.fetchone()
		conn.close()
		# parse data
		hashVal = self.trimSettingsData(hashValFromDb)
		hashVal = hashVal.replace('b', '', 1)
		hashVal = hashVal.replace("'", '', 2)
		# compare password in db with entry
		# print(hashVal)
		hashVal = hashVal.encode()
		print(hashVal)
		if (bcrypt.checkpw(str(entryText.get()).encode(), hashVal)):
			print("Both Entries Match!")

			self.treeview.set(self.entryName, 'password', ogPassword)
			self.treeview.set(self.entryName, 'user', ogUserName)
			windowObj.destroy()
		else:
			print("Entries Do not Match :(")
			errMsg = "Password entries do not match"
			lbl = Label(windowObj, fg="red", text=errMsg)
			lbl.grid(row=3, column=0,sticky='nsew')
			windowObj.after(5000, lbl.destroy)

	# prompts the user for the master password, displays error if not correct input
	def askForMP(self, ogPassword,ogUserName):
		mpWin = tk.Toplevel()
		mpWin.geometry("200x150")
		mpWin.wm_title("LockIT")
		mpWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))

		for r in range(4):
			mpWin.rowconfigure(r, weight=1)
		mpWin.columnconfigure(0, weight=1)

		l = tk.Label(mpWin, text="Please Enter Master Password ", anchor='center')
		l.grid(row=0, column=0, sticky='nswe', padx=5, pady=5)
		e = tk.Entry(mpWin, width=20, show="*")
		e.grid(row=2, column=0, sticky='nswe', padx=5, pady=5)

		b = ttk.Button(mpWin, text="Submit", cursor="hand2", command=lambda: self.checkIfMatch(e, ogPassword,ogUserName, mpWin))
		b.grid(row=4, column=0, sticky='e', padx=5, pady=5)
		nb = ttk.Button(mpWin, text="Return", cursor="hand2", command=mpWin.destroy)
		nb.grid(row=4, column=0, sticky='w', padx=5, pady=5)


class CreateNewPassword(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller


		self.style = ttk.Style()
		self.style.theme_use('default')
		self.style.configure("black.Horizontal.TProgressbar", background='#003152')
		# return image
		self.back = PhotoImage(file=resource_path('return.png'))
		self.save = PhotoImage(file=resource_path('save.png'))
		self.helpIcon = PhotoImage(file=resource_path('help.png'))
		# main container
		self.NewPassword_Screen = Frame(self)
		self.NewPassword_Screen.pack(fill="both", expand=True)

		# separate screen in 3 frames
		self.buttonframe = tk.Frame(self.NewPassword_Screen)
		self.contentframe = tk.Frame(self.NewPassword_Screen)
		self.separator = tk.Frame(self.NewPassword_Screen, bg="light grey")
		self.buttonframe.pack(side="left", fill="both", expand=False)
		self.separator.pack(side="left", fill="both", expand=False)
		self.contentframe.pack(side="left", fill="both", expand=True)

		self.contentframe.columnconfigure(0, weight=1)
		self.contentframe.rowconfigure(0, weight=1)
		self.contentframe.rowconfigure(1, weight=1)
		self.contentframe.rowconfigure(2, weight=8)
		self.contentframe.rowconfigure(3, weight=1)

		# button frame
		space = tk.Label(self.buttonframe, height=1)
		space.pack(side="bottom")


		# banner

		self.category_label = tk.Label(self.contentframe, text='', font=("Verdana", 15, "bold"), background="white",
								   relief="groove", height=1)

		self.category_label.grid(column=0, row=0, sticky=(N, S, E, W))


		# New Password Form Title
		self.formTitleLabel = Label(self.contentframe, text="Create New Password Entry",fg='black')
		self.formTitleLabel.config(font=("Verdana", 13))
		self.formTitleLabel.grid(column=0, row=1, sticky=(N, S, E, W))

		# New Password Form

		# Frame for the new password Form
		self.newPasswordFrame = Frame(self.contentframe, relief="groove")
		self.newPasswordFrame.grid(row=2, column=0, sticky="nsew")

		# Entry Name - label and input
		self.entryNameFrame = Frame(self.newPasswordFrame)
		self.entryNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.entryNameLabel = Label(self.entryNameFrame, width=200, image=self.helpIcon,compound=LEFT, text="Entry name: ", anchor='w')
		self.entryNameLabel.config(font=("Verdana", 10))
		self.entryNameLabel.image = self.helpIcon
		self.entryNameLabel.bind('<Button-1>', self.show_entryhelp)

		self.entryNameEntry = Entry(self.entryNameFrame, width=30)
		self.entryNameEntry.insert(0, "")

		self.entryNameError = Label(self.entryNameFrame, text="", anchor='w', fg='red')
		self.entryNameError.config(font=("Verdana", 8))

		self.entryNameLabel.grid(row=0,column=0,sticky='w')
		self.entryNameEntry.grid(row=0,column=1,sticky='w')
		self.entryNameError.grid(row=1,column=1,sticky='w')

		# Website  - label and input

		self.websiteNameFrame = Frame(self.newPasswordFrame)
		self.websiteNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.websiteNameLabel = Label(self.websiteNameFrame, width=200, image=self.helpIcon,compound=LEFT,cursor="hand2", text="Website(optional): ", anchor='w')
		self.websiteNameLabel.config(font=("Verdana", 10))
		self.websiteNameLabel.image = self.helpIcon
		self.websiteNameLabel.bind('<Button-1>', self.show_webhelp)

		self.websiteNameEntry = Entry(self.websiteNameFrame, width=30)
		self.websiteNameEntry.insert(0, "")

		self.websiteNameError = Label(self.websiteNameFrame, text="", anchor='w', fg='red')
		self.websiteNameError.config(font=("Verdana", 8))

		self.websiteNameLabel.grid(row=0,column=0,sticky='w')
		self.websiteNameEntry.grid(row=0,column=1,sticky='w')
		self.websiteNameError.grid(row=1,column=1,sticky='w')

		# Username  - label and input

		self.userNameFrame = Frame(self.newPasswordFrame)
		self.userNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.userNameLabel = Label(self.userNameFrame, text="Username: ",width=200, image=self.helpIcon,compound=LEFT, cursor="hand2",anchor='w')
		self.userNameLabel.config(font=("Verdana", 10))
		self.userNameLabel.image=self.helpIcon
		self.userNameLabel.bind('<Button-1>',self.show_userhelp)

		self.userNameEntry = Entry(self.userNameFrame, width=30)
		self.userNameEntry.insert(0, "")

		self.userNameError = Label(self.userNameFrame, text="", anchor='w', fg='red')
		self.userNameError.config(font=("Verdana", 8))

		self.userNameLabel.grid(row=0,column=0,sticky='w')
		self.userNameEntry.grid(row=0,column=1,sticky='w')
		self.userNameError.grid(row=1,column=1,sticky='w')

		# Password  - label

		self.passwordFrame = Frame(self.newPasswordFrame)
		self.passwordFrame.pack(side=TOP, fill=X, padx=5, pady=5)



		self.passwordLabel = Label(self.passwordFrame, text="Password: ",width=200, image=self.helpIcon,compound=LEFT, cursor="hand2", anchor='w')
		self.passwordLabel.config(font=("Verdana", 10))
		self.passwordLabel.bind('<Button-1>',self.show_passhelp)
		self.passwordLabel.image = self.helpIcon
		self.passwordLabel.grid(row=0,column=0,sticky='w')


		# Password  - input
		self.passwordEntry = Entry(self.passwordFrame, width=30,show='*')
		self.passwordEntry.bind('<KeyRelease>',self.check_pass_strenght)
		self.passwordEntry.grid(row=0,column=1,sticky='w')

		self.password_Error = Label(self.passwordFrame,width=30, text="", anchor='w', fg='red', font=("Verdana", 8))
		self.password_Error.grid(row=1,column=1,sticky='w')


		# Eye icon for viewing the password

		self.eyeIcon = PhotoImage(file=resource_path('icons8-show-password-20.png'))
		self.viewPasswordButton = Label(self.passwordFrame, width=30, image=self.eyeIcon,cursor="hand2")
		self.viewPasswordButton.bind('<Button-1>',self.show_password)
		self.viewPasswordButton.image = self.eyeIcon
		self.viewPasswordButton.grid(row=0,column=2,sticky='w',padx=5, pady=5)

		# Generate password button

		self.generatePasswordButton = Button(self.passwordFrame, width=30, fg='white', bg='#003152', relief="groove",
											 text="Generate Password",cursor="hand2",command=self.generate_password)
		self.generatePasswordButton.grid(row=0,column=3,sticky='w',padx=5, pady=5)



		# Password strenght label

		self.strenghPassword = {'Weak': 'Red', 'Moderate': 'Orange', 'Strong': 'Green'}
		self.passwordStrenghtLabel = Label(self.passwordFrame, width=22, text='Password Strength Meter', fg='grey',
										   anchor='center')
		self.passwordStrenghtLabel.grid(row=2, column=1, sticky='w')

		# password strenght meter

		self.passwordStrenghtMeter = Progressbar(self.passwordFrame,length=180, style='black.Horizontal.TProgressbar')
		self.passwordStrenghtMeter['value'] = 0
		self.passwordStrenghtMeter.grid(row=3,column=1,sticky='w')



		# Security Level Section

		self.securityLevel_Frame = Frame(self.newPasswordFrame)
		self.securityLevel_Frame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.securityLevel_Label = Label(self.securityLevel_Frame, width=200, image=self.helpIcon,compound=LEFT, cursor="hand2", text="Security Level: ", anchor='w')
		self.securityLevel_Label.config(font=("Verdana", 10))
		self.securityLevel_Label.bind('<Button-1>', self.show_sechelp)
		self.securityLevel_Label.image = self.helpIcon
		self.securityLevel_Label.grid(row=0,column=0,sticky='w')

		self.securityLevel_list = ["Select security level","not secure", "low", "medium", "high"]
		self.choice_var = tk.StringVar()
		self.choice_var.set(self.securityLevel_list[0])
		self.securityLevel_Menu = OptionMenu(self.securityLevel_Frame, self.choice_var, *self.securityLevel_list)
		self.securityLevel_Menu.config(width=22)
		self.securityLevel_Menu.grid(row=0,column=1,sticky='w')

		self.securityLevelError = Label(self.securityLevel_Frame, text="", anchor='w', fg='red')
		self.securityLevelError.config(font=("Verdana", 8))
		self.securityLevelError.grid(row=1,column=1,sticky='w')

		# Notes Section
		self.notes_Frame = Frame(self.newPasswordFrame)
		self.notes_Frame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.notes_Label = Label(self.notes_Frame, width=200, image=self.helpIcon,compound=LEFT, cursor="hand2", text="Notes: ", anchor='w')
		self.notes_Label.config(font=("Verdana", 10))
		self.notes_Label.bind('<Button-1>', self.show_notehelp)
		self.notes_Label.image = self.helpIcon
		self.notes_Label.pack(side=LEFT)

		self.notes_Entry = Text(self.notes_Frame, width=50, height=10)


		self.notes_Entry.pack(side=LEFT)

		# Security Question radio button
		self.secQuestionFrame = Frame(self.newPasswordFrame)
		self.secQuestionFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.secQuestionLabel = Label(self.secQuestionFrame, width=200, image=self.helpIcon,compound=LEFT, cursor="hand2", text="Security Questions: ", anchor='w')
		self.secQuestionLabel.config(font=("Verdana", 10))
		self.secQuestionLabel.bind('<Button-1>', self.show_secqhelp)
		self.secQuestionLabel.image = self.helpIcon
		self.secQuestionLabel.pack(side=LEFT)

		self.answer = IntVar()
		self.answerYes = Radiobutton(self.secQuestionFrame, text="Yes", variable=self.answer, value=1,
									 command=self.showSecAnswerSection).pack(side=LEFT)
		self.answerNo = Radiobutton(self.secQuestionFrame, text="No", variable=self.answer, value=2,
									command=self.hideAnswerSection).pack(side=LEFT)

		self.securityQuestionError = Label(self.secQuestionFrame, text="", anchor='w', fg='red')
		self.securityQuestionError.config(font=("Verdana", 8))
		self.securityQuestionError.pack(side=LEFT)

		# Number of Security Questions spinbox
		self.numSecQuestionFrame = Frame(self.newPasswordFrame)

		self.numSecQuestionLabel = Label(self.numSecQuestionFrame, width=200, image=self.helpIcon,compound=LEFT, cursor="hand2", text="Num. of Security Questions: ",
										 anchor='w')
		self.numSecQuestionLabel.config(font=("Verdana", 10))
		self.numSecQuestionLabel.bind('<Button-1>', self.show_nsecqhelp)
		self.numSecQuestionLabel.image = self.helpIcon
		self.numSecQuestionLabel.pack(side=LEFT)

		self.numQuestion = StringVar()
		self.numQuestion.set("0")

		self.numQuestionsSpinBox = Spinbox(self.numSecQuestionFrame, from_=0, to=5,textvariable=self.numQuestion, command=self.showSecurityAnswers)
		self.numQuestionsSpinBox.pack(side=LEFT)
		self.numQuestionsError = Label(self.numSecQuestionFrame, text="", anchor='w', fg='red',font=("Verdana", 8))
		self.numQuestionsError.pack(side=LEFT)
		# Security Answer Section

		self.securityAnswersFrame = Frame(self.newPasswordFrame)

		self.answerLabels = []
		self.answerEntries = []
		self.answerErrors = []

		for n in range(5):
			labelText = "Security Answer %2d: " % (n + 1)
			self.answerLabels.append(Label(self.securityAnswersFrame, text=labelText, font=("Verdana", 10)))
			# create entries list
			self.answerEntries.append(Entry(self.securityAnswersFrame, bg='white', width=40))
			self.answerErrors.append(
				Label(self.securityAnswersFrame, text="", anchor='w', fg='red', font=("Verdana", 8)))

		# Frame for footer buttons

		self.footerFrame = Frame(self.contentframe)
		self.footerFrame.grid(row=3, column=0, sticky="nsew")



		self.return_Button = Button(self.footerFrame,width=80, font=("Verdana", 10),image=self.back,compound=tk.LEFT,
									text="Return",fg='white', bg='#003152',relief="groove",cursor="hand2",command=self.go_back)
		self.return_Button.pack(side=LEFT, padx=5, pady=5)
		self.return_Button.image=self.back

		# save button
		self.save_Button = Button(self.footerFrame, width=80,font=("Verdana", 10),image=self.save,compound=tk.LEFT,
								  text="Save",fg='white',bg='#0E8C4A',relief="groove",cursor="hand2",command=self.validate)
		self.save_Button.pack(side=RIGHT, padx=5, pady=5)
		self.save_Button.image=self.save

	# function to update title category and color
	def set_category(self, category):
		self.category_label['text'] = category

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		# return security level id from db
		c.execute("SELECT COLOUR_HEX FROM CATEGORY WHERE CATEGORY_NAME=?", (category,))
		color = c.fetchone()

		# close connection to db
		conn.close()

		#set the category label background
		self.category_label['bg'] = color


	# function to show entry help
	def show_entryhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Entryname Help")

		Label(top, text="*Should be between 2 to 35 characters long", anchor='w').pack(side="top", fill="x",
																					   pady=10)
		Label(top, text="*Should be alphanumeric", anchor='w').pack(side="top", fill="x", pady=10)

		Label(top, text="*Should be unique in the category", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()
	# function to show website help
	def show_webhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Website Help")

		Label(top, text="*Optional field", anchor='w').pack(side="top", fill="x", pady=10)

		Label(top, text="*If specified, should use form http://", anchor='w').pack(side="top", fill="x",
																					   pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show username help
	def show_userhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Username Help")

		Label(top, text="*Should be between 2 to 50 characters long", anchor='w').pack(side="top", fill="x",
																					   pady=10)
		Label(top, text="*Should not contain spaces", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_passhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Password Help")

		Label(top, text="*Should be minimum 6 characters long", anchor='w').pack(side="top", fill="x",
																					   pady=10)
		Label(top, text="*Should have at least one number", anchor='w').pack(side="top", fill="x", pady=10)
		Label(top, text="*Should have at least one uppercase character", anchor='w').pack(
			side="top", fill="x", pady=10)
		Label(top, text="*Should have at least one special symbol", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_sechelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Security Level Help")

		Label(top, text="*Security level ‘not secure’ is not generating a security timer in the system", anchor='w').pack(side="top", fill="x",
																					   pady=10)
		Label(top, text="*Security level ‘low’ generating security timer to 6 months in the system", anchor='w').pack(side="top", fill="x", pady=10)
		Label(top, text="*Security level ‘medium’ generating security timer to 3 months in the system", anchor='w').pack(
			side="top", fill="x", pady=10)
		Label(top, text="*Security level ‘high’ generating security timer to 1 month in the system", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_notehelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Note Help")

		Label(top, text="*Note section is optional", anchor='w').pack(side="top", fill="x",
																					   pady=10)
		Label(top, text="*You can specify all the notes here", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_secqhelp(self, event):

		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Security Question Help")

		Label(top, text="*Please select 'Yes' if you have security questions", anchor='w').pack(side="top", fill="x", pady=10)


		button = Button(top, text="Ok", command=top.destroy)
		button.pack()


	# function to show password help
	def show_nsecqhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Number Sec. Question Help")

		Label(top, text="*Number of security answers should be selected", anchor='w').pack(side="top",
																										fill="x",
																										pady=10)

		Label(top, text="*Security answers should be between 2 to 50 characters long", anchor='w').pack(side="top", fill="x",
																					   pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show security answer section
	def showSecAnswerSection(self):
		self.numSecQuestionFrame.pack(side=TOP, fill=X, padx=5, pady=5)
		self.securityAnswersFrame.pack(side=TOP, fill=X, padx=5, pady=5)

	# function to hide security answer section
	def hideAnswerSection(self):
		self.numSecQuestionFrame.pack_forget()
		self.securityAnswersFrame.pack_forget()

	# function to show security answers entries
	def showSecurityAnswers(self):
		for n in range(5):
			self.answerEntries[n].delete(0, END)
			self.answerLabels[n].grid_forget()
			self.answerEntries[n].grid_forget()
			self.answerErrors[n].grid_forget()

		num_answer = int(self.numQuestionsSpinBox.get())

		for n in range(num_answer):

			self.answerLabels[n].grid(row=n, column=0)
			self.answerEntries[n].grid(row=n, column=1)
			self.answerErrors[n].grid(row=n, column=2)

	#function to show the entered password
	def show_password(self,event):
		if(self.passwordEntry.cget('show') == '*'):
			self.passwordEntry.config(show='')
		else:
			self.passwordEntry.config(show='*')


	def check_pass_strenght(self,event):

		password = self.passwordEntry.get()

		if(len(password) > 0):

			stats = PasswordStats(password)

			strength = stats.strength()

			if (strength < 0.34):
				self.passwordStrenghtMeter['value'] = 30
				self.passwordStrenghtLabel['text'] = "Weak"
				self.passwordStrenghtLabel['fg'] = self.strenghPassword['Weak']
				self.style.configure("black.Horizontal.TProgressbar", background='red')
			elif (strength > 0.34 and strength < 0.66):
				self.passwordStrenghtMeter['value'] = 60
				self.passwordStrenghtLabel['text'] = "Moderate"
				self.passwordStrenghtLabel['fg'] = self.strenghPassword['Moderate']
				self.style.configure("black.Horizontal.TProgressbar", background='yellow')
			elif (strength >= 0.66):
				self.passwordStrenghtMeter['value'] = 100
				self.passwordStrenghtLabel['text'] = "Strong"
				self.passwordStrenghtLabel['fg'] = self.strenghPassword['Strong']
				self.style.configure("black.Horizontal.TProgressbar", background='green')
		else:
			self.passwordStrenghtMeter['value'] = 0
			self.passwordStrenghtLabel['text'] = "Password Strength Meter"
			self.passwordStrenghtLabel['fg'] = 'grey'



	def generate_password(self):

		self.passwordEntry.delete(0,END)

		"""Generate a random password """
		stringSource = string.ascii_letters + string.digits + string.punctuation
		password = secrets.choice(string.ascii_lowercase)
		password += secrets.choice(string.ascii_uppercase)
		password += secrets.choice(string.digits)
		password += secrets.choice(string.punctuation)
		for i in range(12):
			password += secrets.choice(stringSource)
		char_list = list(password)
		secrets.SystemRandom().shuffle(char_list)
		password = ''.join(char_list)

		self.passwordEntry.insert(0,password)

		stats = PasswordStats(password)
		strength = stats.strength()

		if (strength < 0.34):
			self.passwordStrenghtMeter['value'] = 30
			self.passwordStrenghtLabel['text'] = "Weak"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Weak']
			self.style.configure("black.Horizontal.TProgressbar", background='red')
		elif (strength > 0.34 and strength < 0.66):
			self.passwordStrenghtMeter['value'] = 60
			self.passwordStrenghtLabel['text'] = "Moderate"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Moderate']
			self.style.configure("black.Horizontal.TProgressbar", background='yellow')
		elif (strength >= 0.66):
			self.passwordStrenghtMeter['value'] = 100
			self.passwordStrenghtLabel['text'] = "Strong"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Strong']
			self.style.configure("black.Horizontal.TProgressbar", background='green')


	# function that validates the entries
	def validate(self):

		category = self.category_label.cget('text').upper()

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 35

		if (self.entryNameError.cget('text') != ''):
			self.entryNameError['text'] = ''

		# check length of entry
		en_len = len(str(self.entryNameEntry.get()))
		entry_name = self.entryNameEntry.get()
		if (en_len == 0):
			num_errors += 1
			errMsg = "Please enter entry name"
			self.entryNameError['text'] = errMsg
		elif (en_len < min_entry_len):
			num_errors += 1
			errMsg = "Invalid entry name"
			self.entryNameError['text'] = errMsg

		elif (en_len > max_entry_len):
			num_errors += 1
			errMsg = "Invalid entry name"
			self.entryNameError['text'] = errMsg

		else:
			# check if has spaces and alphanumeric
			t = entry_name.split()
			if len(t) > 1:
				for i in t:
					if (i.isalnum() == FALSE):
						num_errors += 1
						errMsg = "Invalid entry name"
						self.entryNameError['text'] = errMsg
						break;
			else:
				if (entry_name.isalnum() == FALSE):
					num_errors += 1
					errMsg = "Invalid entry name"
					self.entryNameError['text'] = errMsg



		# check if entry name is unique in the category

		# return category id from db
		c.execute("SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME=?", (category,))
		rec2 = c.fetchone()
		category_id = int(rec2[0])

		# return count from db
		c.execute("SELECT COUNT(*) FROM PASSWORD WHERE CATEGORY=? AND ENTRY_NAME=?", (category_id,entry_name))
		rec1 = c.fetchone()
		num_occur = int(rec1[0])

		if(num_occur >= 1):
			num_errors += 1
			errMsg = "Entry name is already exist in this category"
			self.entryNameError['text'] = errMsg

		# Website validation
		website_name = self.websiteNameEntry.get()
		if (self.websiteNameError.cget('text') != ''):
			self.websiteNameError['text'] = ''

		if (website_name != ''):
			if (checkers.is_url(website_name) == FALSE):
				num_errors += 1
				errMsg = "Invalid website"
				self.websiteNameError['text'] = errMsg

		# value = validators.url('http://www.stackoverflow.com')
		# # value set to 'http://www.stackoverflow.com'
		#
		# value = validators.url('not a valid url')
		# # raises a validator_collection.errors.InvalidURLError (which is a ValueError)

		# Username validation
		user_name = self.userNameEntry.get()
		user_len = len(str(user_name))
		min_user_len = 2
		max_user_len = 50

		if (self.userNameError.cget('text') != ''):
			self.userNameError['text'] = ''

		# check length of username
		if (user_len == 0):
			num_errors += 1
			errMsg = "Please enter username"
			self.userNameError['text'] = errMsg
		elif (user_len < min_user_len):
			num_errors += 1
			errMsg = "Invalid username"
			self.userNameError['text'] = errMsg
		elif (user_len > max_user_len):
			num_errors += 1
			errMsg = "Invalid username"
			self.userNameError['text'] = errMsg
		else:
			# check if username has spaces
			u = user_name.split()
			if len(u) > 1:
				num_errors += 1
				errMsg = "Invalid username"
				self.userNameError['text'] = errMsg

		# password validation


		password = self.passwordEntry.get()

		res = self.controller.policy.test(password)


		if (self.password_Error.cget('text') != ''):
			self.password_Error['text'] = ''

		if (len(str(password)) == 0):
			num_errors += 1
			errMsg = "Please enter password"
			self.password_Error['text'] = errMsg
		elif(len(res) != 0):
			num_errors += 1
			errMsg = "Invalid password"
			self.password_Error['text'] = errMsg
		else:
			# count number of same passwords
			c.execute("SELECT PASSWORD,PASS_KEY FROM PASSWORD")
			passw = c.fetchall()

			list = []
			for var in passw:
				# decrypting
				keyS = var[1] + Login.loginScreen.getMasterKey(root).encode()
				f2 = Fernet(keyS)
				decrypted = f2.decrypt(var[0])
				original_password = decrypted.decode()
				list.append(original_password)

			num_occur = 0
			for p in list:
				if p == password:
					num_occur = num_occur + 1

			if (num_occur >= 3):
				num_errors += 1
				errMsg = "Password is already used 3 times"
				self.password_Error['text'] = errMsg



		# security level validation
		sec_level = self.choice_var.get()
		if (self.securityLevelError.cget('text') != 'Select security level'):
			self.securityLevelError['text'] = ''

		if (sec_level == 'Select security level'):
			num_errors += 1
			errMsg = "Please select security level"
			self.securityLevelError['text'] = errMsg

		# security question - yes/no validation
		answer = self.answer.get()



		if (self.securityQuestionError.cget('text') != ''):
			self.securityQuestionError['text'] = ''

		if (answer == 0):
			num_errors += 1
			errMsg = "Please select yes / no"
			self.securityQuestionError['text'] = errMsg

		# security answers validation

		if (self.numQuestionsError.cget('text') != ''):
			self.numQuestionsError['text'] = ''
		min_ans_len = 2
		max_ans_len = 50
		num_answer = 0
		if (answer == 1):
			num_answer = int(self.numQuestion.get())
			if(num_answer == 0):
				num_errors+=1
				errMsg = "Please select number of answers"
				self.numQuestionsError['text'] = errMsg
			else:
				for n in range(num_answer):
					if (self.answerErrors[n].cget('text') != ''):
						self.answerErrors[n]['text'] = ''
					if (len(str(self.answerEntries[n].get())) == 0):
						num_errors += 1
						errMsg = "Please enter security answer"
						self.answerErrors[n]['text'] = errMsg
					elif (len(str(self.answerEntries[n].get())) < min_ans_len):
						num_errors += 1
						errMsg = "Invalid answer"
						self.answerErrors[n]['text'] = errMsg
					elif (len(str(self.answerEntries[n].get())) > max_ans_len):
						num_errors += 1
						errMsg = "Invalid answer"
						self.answerErrors[n]['text'] = errMsg

		notes = self.notes_Entry.get('1.0', END)


		# close connection to db
		conn.close()

		if (num_errors == 0):

			self.saveRecordToDb(entry_name,website_name,user_name,password,answer,num_answer,str(self.answerEntries[0].get()),
								str(self.answerEntries[1].get()),str(self.answerEntries[2].get()),str(self.answerEntries[3].get()),str(self.answerEntries[4].get()),
								notes,category,sec_level)
			self.clear_entries()
			self.controller.show_frame("ViewPasswords_InCategory").set_category(category)

	# saves the Record into LockIT.db
	def saveRecordToDb(self, entryname,website,username,password,secquestion,num_answer,answer1,answer2,answer3,answer4,answer5,notes,category,sec_level):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		#return security level id from db
		c.execute("SELECT S_LEVEL_ID FROM SECURITYLEVEL WHERE S_LEVEL_NAME=?",(sec_level,))
		rec1 = c.fetchone()
		#selecting column value into varible
		sec_id = int(rec1[0])


		# return category id from db
		c.execute("SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME=?", (category,))
		rec2 = c.fetchone()
		category_id = int(rec2[0])

		#encrypt password
		p =str.encode(password)
		key = Fernet.generate_key()
		keyS = key + Login.loginScreen.getMasterKey(root).encode()
		print(key)
		f = Fernet(keyS)
		print(keyS)
		token = f.encrypt(p)
		print(token)

		#encrypt username
		user = str.encode(username)
		usertoken = f.encrypt(user)

		today = date.today()
		# inserts into the PASSWORD table
		c.execute("INSERT INTO PASSWORD VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
				  (entryname,website,usertoken,token,secquestion,num_answer,answer1,answer2,answer3,answer4,answer5,notes,category_id,sec_id,today,key))

		# select all
		c.execute("SELECT * FROM PASSWORD")
		rows = c.fetchall()
		for row in rows:
			print(row)

		# save changes made
		conn.commit()
		# close connection to db
		conn.close()

	#clears the create password page entries
	def clear_entries(self):
		self.entryNameEntry.delete(0,END)
		self.entryNameError['text'] = ''
		self.websiteNameEntry.delete(0,END)
		self.websiteNameError['text'] = ''
		self.userNameEntry.delete(0,END)
		self.userNameError['text'] = ''
		self.passwordEntry.delete(0,END)
		self.password_Error['text'] = ''
		self.choice_var.set(self.securityLevel_list[0])
		self.securityLevelError['text'] = ''
		self.notes_Entry.delete("1.0",END)
		self.answer.set(0)
		self.securityQuestionError['text'] = ''
		self.numQuestion.set("0")
		self.numQuestionsError['text'] = ''
		for n in range(5):
			self.answerEntries[n].delete(0,END)
			self.answerErrors[n]['text'] = ''
			self.answerLabels[n].grid_forget()
			self.answerEntries[n].grid_forget()
			self.answerErrors[n].grid_forget()
		self.hideAnswerSection()
		self.passwordStrenghtMeter['value'] = 0
		self.passwordStrenghtLabel['text'] = "Password Strength Meter"
		self.passwordStrenghtLabel['fg'] = 'grey'

	def go_back(self):
		self.clear_entries()
		self.controller.show_frame("ViewPasswords_InCategory")


class ViewPassword(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		# initialize variables
		self.categoryName = ""
		self.categoryId = ""
		self.entryName = ""

		# images
		self.back = PhotoImage(file=resource_path('return.png'))
		self.trash = PhotoImage(file=resource_path('delete.png'))
		self.edit = PhotoImage(file=resource_path('modify.png'))
		self.go = PhotoImage(file=resource_path('redirectIconBig.png'))
		self.error = PhotoImage(file=resource_path('exclamation.png'))

		# main container
		self.ViewPassword_Screen = Frame(self)
		self.ViewPassword_Screen.pack(fill="both", expand=True)

		# separate screen in 3 frames
		self.buttonframe = tk.Frame(self.ViewPassword_Screen)
		self.contentframe = tk.Frame(self.ViewPassword_Screen)
		self.separator = tk.Frame(self.ViewPassword_Screen, bg="light grey")
		self.buttonframe.pack(side="left", fill="both", expand=False)
		self.separator.pack(side="left", fill="both", expand=False)
		self.contentframe.pack(side="left", fill="both", expand=True)

		self.contentframe.columnconfigure(0, weight=1)
		self.contentframe.rowconfigure(0, weight=1)
		self.contentframe.rowconfigure(1, weight=1)
		self.contentframe.rowconfigure(2, weight=8)
		self.contentframe.rowconfigure(3, weight=1)

		# button frame
		space = tk.Label(self.buttonframe, height=1)
		space.pack(side="bottom")

		# banner

		self.category_label = tk.Label(self.contentframe, text='', font=("Verdana", 15, "bold"), background="white",
									   relief="groove", height=1)

		self.category_label.grid(column=0, row=0, sticky=(N, S, E, W))

		# New Password Form Title
		self.formTitle = "View " + "Entry"
		self.formTitleLabel = Label(self.contentframe, text=self.formTitle, fg='black')
		self.formTitleLabel.config(font=("Verdana", 13))
		self.formTitleLabel.grid(column=0, row=1, sticky=(N, S, E, W))

		# New Password Form

		# Frame for the new password Form
		self.newPasswordFrame = Frame(self.contentframe)
		self.newPasswordFrame.grid(row=2, column=0, sticky="nsew")


		# Entry Name - label and input

		self.entryNameFrame = Frame(self.newPasswordFrame)
		self.entryNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.entryNameLabel = Label(self.entryNameFrame, width=22, text="Entry name: ", anchor='w')
		self.entryNameLabel.config(font=("Verdana", 10))

		self.entryNameEntry = Entry(self.entryNameFrame, width=30)


		self.entryNameLabel.pack(side=LEFT)
		self.entryNameEntry.pack(side=LEFT)

		# Website  - label and input

		self.websiteNameFrame = Frame(self.newPasswordFrame)
		self.websiteNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.websiteNameLabel = Label(self.websiteNameFrame, width=22, text="Website(optional): ", anchor='w')
		self.websiteNameLabel.config(font=("Verdana", 10))

		self.websiteNameEntry = Entry(self.websiteNameFrame, width=30)

		self.websiteNameLabel.pack(side=LEFT)
		self.websiteNameEntry.pack(side=LEFT)

		self.goto_web = Label(self.websiteNameFrame, width=30, image=self.go,cursor="hand2")
		self.goto_web.bind('<Button-1>', self.go_web)
		self.goto_web.image = self.go
		self.goto_web.pack(fill=Y, side=LEFT, padx=5, pady=5)

		# Username  - label and input

		self.userNameFrame = Frame(self.newPasswordFrame)
		self.userNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.userNameLabel = Label(self.userNameFrame, width=22, text="Username: ", anchor='w')
		self.userNameLabel.config(font=("Verdana", 10))

		self.userNameEntry = Entry(self.userNameFrame, width=30)

		self.userNameLabel.pack(side=LEFT)
		self.userNameEntry.pack(side=LEFT)

		# Password  - label

		self.passwordFrame = Frame(self.newPasswordFrame)
		self.passwordFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.passwordLabel = Label(self.passwordFrame, width=22, text="Password: ", anchor='w')
		self.passwordLabel.config(font=("Verdana", 10))
		self.passwordLabel.pack(side=LEFT)


		# Password  - input
		self.passwordEntry = Entry(self.passwordFrame, width=30,show='*')
		self.passwordEntry.pack(side=LEFT)

		# Eye icon for viewing the password

		self.eyeIcon = PhotoImage(file=resource_path('icons8-show-password-20.png'))
		self.viewPasswordButton = Label(self.passwordFrame, width=30, image=self.eyeIcon,cursor="hand2")
		self.viewPasswordButton.bind('<Button-1>', self.show_password)
		self.viewPasswordButton.image = self.eyeIcon
		self.viewPasswordButton.pack(fill=Y, side=LEFT, padx=5, pady=5)

		self.passwordExpired = Label(self.passwordFrame,width=30,image=self.error,cursor='hand2')
		self.passwordExpired.bind('<Button-1>',self.show_password_expired)
		self.passwordExpired.image=self.error
		self.passwordExpired.pack(fill=Y, side=LEFT, padx=5, pady=5)
		# Security Level Section

		self.securityLevel_Frame = Frame(self.newPasswordFrame)
		self.securityLevel_Frame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.securityLevel_Label = Label(self.securityLevel_Frame, width=22, text="Security Level: ", anchor='w')
		self.securityLevel_Label.config(font=("Verdana", 10))
		self.securityLevel_Label.pack(side=LEFT)

		self.securityLevel_list = ["Select security level", "not secure", "low", "medium", "high"]
		self.choice_var = tk.StringVar()
		self.choice_var.set(self.securityLevel_list[0])
		self.securityLevel_Menu = OptionMenu(self.securityLevel_Frame, self.choice_var, *self.securityLevel_list)
		self.securityLevel_Menu.config(width=22)
		self.securityLevel_Menu.pack(side=LEFT)

		# Notes Section

		self.notes_Frame = Frame(self.newPasswordFrame)
		self.notes_Frame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.notes_Label = Label(self.notes_Frame, width=22, text="Notes: ", anchor='w')
		self.notes_Label.config(font=("Verdana", 10))
		self.notes_Label.pack(side=LEFT)

		self.notes_Entry = Text(self.notes_Frame, width=50, height=10)
		self.notes_Entry.pack(side=LEFT)



		# Security Question radio button

		self.secQuestionFrame = Frame(self.newPasswordFrame)
		self.secQuestionFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.secQuestionLabel = Label(self.secQuestionFrame, width=22, text="Security Questions: ", anchor='w')
		self.secQuestionLabel.config(font=("Verdana", 10))
		self.secQuestionLabel.pack(side=LEFT)

		self.answer = IntVar()
		self.answerYes = Radiobutton(self.secQuestionFrame, text="Yes", variable=self.answer, value=1)
		self.answerYes.pack(side=LEFT)
		self.answerNo = Radiobutton(self.secQuestionFrame, text="No", variable=self.answer, value=2)
		self.answerNo.pack(side=LEFT)

		# Number of Security Questions spinbox

		self.numSecQuestionFrame = Frame(self.newPasswordFrame)
		self.numSecQuestionFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.numSecQuestionLabel = Label(self.numSecQuestionFrame, width=30, text="Number of Security Questions: ",
										 anchor='w')
		self.numSecQuestionLabel.config(font=("Verdana", 10))
		self.numSecQuestionLabel.pack(side=LEFT)

		self.numQuestion = StringVar()
		self.numQuestion.set("0")

		self.numQuestionsSpinBox = Spinbox(self.numSecQuestionFrame, from_=0, to=5, textvariable=self.numQuestion)
		self.numQuestionsSpinBox.pack(side=LEFT)


		# Security Answer Section

		self.securityAnswersFrame = Frame(self.newPasswordFrame)
		self.securityAnswersFrame.pack(side=TOP, fill=X, padx=5, pady=5)


		# Frame for footer buttons

		self.footerFrame = Frame(self.contentframe)
		self.footerFrame.grid(row=3, column=0, sticky="nsew")

		# return button

		self.return_Button = Button(self.footerFrame, width=80,font=("Verdana", 10), image=self.back, compound=tk.LEFT,
									text="Return", fg='white', bg='#003152', cursor="hand2",relief="groove",command=self.go_back)
		self.return_Button.pack(side=LEFT, padx=5, pady=5)
		self.return_Button.image = self.back

		# edit button
		self.edit_Button = Button(self.footerFrame, width=80,font=("Verdana", 10), image=self.edit, compound=tk.LEFT,
									text="Modify", fg='white', bg='#116936', relief="groove",cursor="hand2",
								  command=self.modify)
		self.edit_Button.pack(side=RIGHT, padx=5, pady=5)
		self.edit_Button.image=self.edit

		# delete button

		self.delete_Button = Button(self.footerFrame, width=80,font=("Verdana", 10), image=self.trash, compound=tk.LEFT,
									text="Delete", fg='white', bg='#A91010', relief="groove",cursor="hand2",command=self.delete_password)
		self.delete_Button.pack(side=RIGHT, padx=5, pady=5)
		self.delete_Button.image=self.trash

	def go_back(self):
		self.clear_entries()
		self.controller.show_frame("ViewPasswords_InCategory")

	def modify(self):
		self.controller.show_frame("ModifyPassword").pass_variables(self.category_label.cget('text'), self.entryName)

	# function to show the entered password
	def show_password(self, event):
		if (self.passwordEntry.cget('show') == '*'):
			if(self.timer=="off"):
				tkinter.messagebox.showerror("Error", "Your password is expired, please create new password for this entry")
			else:
				self.passwordEntry.config(show='')
		else:
			self.passwordEntry.config(show='*')
	def show_password_expired(self,event):
		tkinter.messagebox.showerror("Error", "Your password is expired, please create new password for this entry")
	#function that opens the website
	def go_web(self,event):

		# make connection
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		# statements
		c.execute("SELECT WEBSITE,USERNAME,PASSWORD,PASS_KEY FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?",
				  (self.entryName, self.category_id,))
		website, username, password, key = c.fetchone()
		website = str(website)

		# close database
		conn.close()

		if (website == ""):
			tkinter.messagebox.showwarning("Website", "There is no website for this entry")
		else:
			# decrypting
			keyS = key + Login.loginScreen.getMasterKey(root).encode()
			f2 = Fernet(keyS)
			decryptedP = f2.decrypt(password)
			password = decryptedP.decode()

			decryptedU = f2.decrypt(username)
			username = decryptedU.decode()

			web = Browser()
			web.go_to(website)

			if web.exists('Agree') == True:
				web.click('Agree')

			if web.exists('Sign in') == True:
				web.click('Sign in')
			elif web.exists('Sign In') == True:
				web.click('Sign In')
			elif web.exists('Log in') == True:
				web.click('Log in')
			elif web.exists('Login') == True:
				web.click('Login')

			if web.exists('Email') == True:
				web.type(username, into='Email')
			elif web.exists('Username') == True:
				web.type(username, into='Username')

			web.click('NEXT', tag='span')
			web.type(password, into='Password', id='passwordFieldId')  # specific selection
			web.click('NEXT', tag='span')  # you are logged in ^_^

	#this function deletes password entry
	def delete_password(self):
		question = "Would you like to delete this password entry?"
		answer = tkinter.messagebox.askquestion(self.entryName, question)
		if (answer == 'yes'):

			conn = sqlite3.connect('LockIT.db')
			c = conn.cursor()
			c.execute("DELETE FROM PASSWORD WHERE ENTRY_NAME=? and CATEGORY=?", (self.entryName, self.categoryId))

			conn.commit()
			# close database
			conn.close()
			# clear modify page
			self.clear_entries()

			# show viepasswords inside category page
			self.controller.show_frame("ViewPasswords_InCategory").set_category(self.categoryName)

	# function to update title category,color and password details
	def pass_variables(self, category,entry_name):
		self.entryName = entry_name
		self.categoryName = category
		self.category_label['text'] = category
		# make connection to db
		conn = sqlite3.connect('LockIT.db',detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
		# add cursor
		c = conn.cursor()

		# return color of the categoty from db
		c.execute("SELECT COLOUR_HEX FROM CATEGORY WHERE CATEGORY_NAME=?", (category,))
		color = c.fetchone()

		# return category id from db
		c.execute("SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME=?", (category,))
		rec2 = c.fetchone()
		category_id = int(rec2[0])
		self.categoryId= category_id

		# decrypt password
		c.execute("SELECT PASS_KEY,PASSWORD FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?",
				  (self.entryName, self.categoryId,))
		key, encrypted = c.fetchone()
		# decrypting
		keyS = key + Login.loginScreen.getMasterKey(root).encode()
		f2 = Fernet(keyS)
		decrypted = f2.decrypt(encrypted)
		self.original_password = decrypted.decode()

		# return password details
		c.execute("SELECT ENTRY_NAME,WEBSITE,USERNAME,PASSWORD,SECURITY_QUEST,NUM_SECURITY_ANSWER,ANSWER_1,ANSWER_2,"
				  "ANSWER_3,ANSWER_4,ANSWER_5,NOTES,S_LEVEL,DATE_CREATED"
				  " FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?", (self.entryName,self.categoryId))
		pass_details = c.fetchone()

		print(pass_details)
		self.entryNameEntry.insert(0,pass_details[0])
		self.entryNameEntry.config(state='readonly')

		self.websiteNameEntry.insert(0,pass_details[1])
		self.websiteNameEntry.config(state='readonly')

		# decrypt username
		user = f2.decrypt(pass_details[2])
		userD = user.decode()

		self.userNameEntry.insert(0,userD)
		self.userNameEntry.config(state='readonly')

		self.passwordEntry.insert(0,self.original_password)
		self.passwordEntry.config(state='readonly')

		today = date.today()
		sec_level = pass_details[12]
		dateDB = pass_details[13]
		self.passwordExpired.pack_forget()
		if(sec_level==1):
			self.choice_var.set(self.securityLevel_list[1])
			self.passwordExpired.pack_forget()
			self.timer = "on"
		elif(sec_level == 2):
			self.choice_var.set(self.securityLevel_list[2])
			six_months = timedelta(days=182)
			expire = dateDB + six_months
			if ((expire - today).days <= 0):
				self.passwordExpired.pack(fill=Y, side=LEFT, padx=5, pady=5)
				self.timer = "off"
			else:
				self.passwordExpired.pack_forget()
				self.timer = "on"
		elif (sec_level == 3):
			self.choice_var.set(self.securityLevel_list[3])
			three_months = timedelta(days=91)
			expire = dateDB + three_months
			if ((expire - today).days <= 0):
				self.passwordExpired.pack(fill=Y, side=LEFT, padx=5, pady=5)
				self.timer = "off"
			else:
				self.passwordExpired.pack_forget()
				self.timer = "on"
		elif (sec_level == 4):
			one_months = timedelta(days=31)
			self.choice_var.set(self.securityLevel_list[4])
			expire = dateDB + one_months
			if ((expire - today).days <= 0):
				self.passwordExpired.pack(fill=Y, side=LEFT, padx=5, pady=5)
				self.timer = "off"
			else:
				self.passwordExpired.pack_forget()
				self.timer = "on"
		self.securityLevel_Menu.configure(state="disabled")


		self.notes_Entry.insert("1.0",pass_details[11])
		self.notes_Entry.config(state=DISABLED)

		self.answer.set(pass_details[4])
		self.answerYes.config(state=DISABLED)
		self.answerNo.config(state=DISABLED)

		self.numSecurityAnswers = pass_details[5]

		if(self.numSecurityAnswers == 0):
			self.numSecQuestionFrame.pack_forget()
		else:
			self.numQuestion.set(pass_details[5])
			self.numQuestionsSpinBox.config(state=DISABLED)
			self.answerEntries = []
			self.answerLabels = []
			i = 6
			for n in range(self.numSecurityAnswers):
				labelText = "Security Answer %2d: " % (n + 1)
				self.answerLabels.append(Label(self.securityAnswersFrame, text=labelText, font=("Verdana", 10)))
				self.answerEntries.append(Entry(self.securityAnswersFrame,width=40))
				self.answerEntries[n].insert(0, pass_details[i])
				self.answerEntries[n].config(state=DISABLED)
				self.answerLabels[n].grid(row=n,column=0)
				self.answerEntries[n].grid(row=n, column=1)
				i = i+1

		# close connection to db
		conn.close()

		# set the category label background
		self.category_label['bg'] = color

	# clears the view password page entries
	def clear_entries(self):
		self.entryNameEntry.config(state=NORMAL)
		self.entryNameEntry.delete(0, END)
		self.websiteNameEntry.config(state=NORMAL)
		self.websiteNameEntry.delete(0, END)
		self.userNameEntry.config(state=NORMAL)
		self.userNameEntry.delete(0, END)
		self.passwordEntry.config(state=NORMAL)
		self.passwordEntry.delete(0, END)
		self.securityLevel_Menu.configure(state=NORMAL)
		self.choice_var.set(self.securityLevel_list[0])
		self.notes_Entry.config(state=NORMAL)
		self.notes_Entry.delete("1.0", END)

		self.answer.set(0)
		self.answerYes.config(state=NORMAL)
		self.answerNo.config(state=NORMAL)

		self.numQuestionsSpinBox.config(state=NORMAL)
		self.numQuestion.set("1")
		for n in range(self.numSecurityAnswers):
			self.answerLabels[n].grid_forget()
			self.answerEntries[n].config(state=NORMAL)
			self.answerEntries[n].delete(0, END)
			self.answerEntries[n].destroy()


class ModifyPassword(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		self.style = ttk.Style()
		self.style.theme_use('default')
		self.style.configure("black.Horizontal.TProgressbar", background='light blue')

		# initialize variables
		self.categoryName = ""
		self.categoryId = ""
		self.entryName = ""

		# images
		self.back = PhotoImage(file=resource_path('return.png'))
		self.trash = PhotoImage(file=resource_path('delete.png'))
		self.save = PhotoImage(file=resource_path('save.png'))
		self.helpIcon = PhotoImage(file=resource_path('help.png'))

		# main container
		self.ModifyPassword_Screen = Frame(self)
		self.ModifyPassword_Screen.pack(fill="both", expand=True)

		# separate screen in 3 frames
		self.buttonframe = tk.Frame(self.ModifyPassword_Screen)
		self.contentframe = tk.Frame(self.ModifyPassword_Screen)
		self.separator = tk.Frame(self.ModifyPassword_Screen, bg="light grey")
		self.buttonframe.pack(side="left", fill="both", expand=False)
		self.separator.pack(side="left", fill="both", expand=False)
		self.contentframe.pack(side="left", fill="both", expand=True)

		self.contentframe.columnconfigure(0, weight=1)
		self.contentframe.rowconfigure(0, weight=1)
		self.contentframe.rowconfigure(1, weight=1)
		self.contentframe.rowconfigure(2, weight=8)
		self.contentframe.rowconfigure(3, weight=1)

		# button frame
		space = tk.Label(self.buttonframe, height=1)
		space.pack(side="bottom")

		# banner

		self.category_label = tk.Label(self.contentframe, text='', font=("Verdana", 15, "bold"), background="white",
									   relief="groove", height=1)

		self.category_label.grid(column=0, row=0, sticky=(N, S, E, W))

		# New Password Form Title
		self.formTitle = "Modify " + "Entry"
		self.formTitleLabel = Label(self.contentframe, text=self.formTitle, fg='black')
		self.formTitleLabel.config(font=("Verdana", 13))
		self.formTitleLabel.grid(column=0, row=1, sticky=(N, S, E, W))

		# New Password Form

		# Frame for the new password Form
		self.newPasswordFrame = Frame(self.contentframe)
		self.newPasswordFrame.grid(row=2, column=0, sticky="nsew")

		# Entry Name - label and input

		self.entryNameFrame = Frame(self.newPasswordFrame)
		self.entryNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.entryNameLabel = Label(self.entryNameFrame, width=200, image=self.helpIcon, compound=LEFT,
									text="Entry name: ", anchor='w')
		self.entryNameLabel.config(font=("Verdana", 10))
		self.entryNameLabel.image = self.helpIcon
		self.entryNameLabel.bind('<Button-1>', self.show_entryhelp)

		self.entryNameEntry = Entry(self.entryNameFrame, width=30)

		self.entryNameError = Label(self.entryNameFrame, text="", anchor='w', fg='red')
		self.entryNameError.config(font=("Verdana", 8))

		self.entryNameLabel.grid(row=0, column=0, sticky='w')
		self.entryNameEntry.grid(row=0, column=1, sticky='w')
		self.entryNameError.grid(row=1, column=1, sticky='w')

		# Website  - label and input

		self.websiteNameFrame = Frame(self.newPasswordFrame)
		self.websiteNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.websiteNameLabel = Label(self.websiteNameFrame, width=200, image=self.helpIcon, compound=LEFT,
									  cursor="hand2", text="Website(optional): ", anchor='w')
		self.websiteNameLabel.config(font=("Verdana", 10))
		self.websiteNameLabel.image = self.helpIcon
		self.websiteNameLabel.bind('<Button-1>', self.show_webhelp)

		self.websiteNameEntry = Entry(self.websiteNameFrame, width=30)

		self.websiteNameError = Label(self.websiteNameFrame, text="", anchor='w', fg='red')
		self.websiteNameError.config(font=("Verdana", 8))

		self.websiteNameLabel.grid(row=0, column=0, sticky='w')
		self.websiteNameEntry.grid(row=0, column=1, sticky='w')
		self.websiteNameError.grid(row=1, column=1, sticky='w')

		# Username  - label and input

		self.userNameFrame = Frame(self.newPasswordFrame)
		self.userNameFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.userNameLabel = Label(self.userNameFrame, text="Username: ", width=200, image=self.helpIcon, compound=LEFT,
								   cursor="hand2", anchor='w')
		self.userNameLabel.config(font=("Verdana", 10))
		self.userNameLabel.image = self.helpIcon
		self.userNameLabel.bind('<Button-1>', self.show_userhelp)

		self.userNameEntry = Entry(self.userNameFrame, width=30)

		self.userNameError = Label(self.userNameFrame, text="", anchor='w', fg='red')
		self.userNameError.config(font=("Verdana", 8))

		self.userNameLabel.grid(row=0, column=0, sticky='w')
		self.userNameEntry.grid(row=0, column=1, sticky='w')
		self.userNameError.grid(row=1, column=1, sticky='w')

		# Password  - label

		self.passwordFrame = Frame(self.newPasswordFrame)
		self.passwordFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.passwordLabel = Label(self.passwordFrame, text="Password: ", width=200, image=self.helpIcon, compound=LEFT,
								   cursor="hand2", anchor='w')
		self.passwordLabel.config(font=("Verdana", 10))
		self.passwordLabel.bind('<Button-1>', self.show_passhelp)
		self.passwordLabel.image = self.helpIcon
		self.passwordLabel.grid(row=0, column=0, sticky='w')

		# Password  - input
		self.passwordEntry = Entry(self.passwordFrame, width=30, show='*')
		self.passwordEntry.bind('<KeyRelease>', self.check_pass_strenght)
		self.passwordEntry.grid(row=0, column=1, sticky='w')

		# Eye icon for viewing the password

		self.eyeIcon = PhotoImage(file=resource_path('icons8-show-password-20.png'))
		self.viewPasswordButton = Label(self.passwordFrame, width=30, image=self.eyeIcon, cursor="hand2")
		self.viewPasswordButton.bind('<Button-1>', self.show_password)
		self.viewPasswordButton.image = self.eyeIcon
		self.viewPasswordButton.grid(row=0, column=2, sticky='w', padx=5, pady=5)

		# Generate password button

		self.generatePasswordButton = Button(self.passwordFrame, width=30, fg='white', bg='#003152', relief="groove",
											 text="Generate Password", cursor="hand2", command=self.generate_password)
		self.generatePasswordButton.grid(row=0, column=3, sticky='w', padx=5, pady=5)

		self.password_Error = Label(self.passwordFrame, text="", anchor='w', fg='red', font=("Verdana", 8))
		self.password_Error.grid(row=1, column=1, sticky='w')

		# Password strenght label

		self.strenghPassword = {'Weak': 'Red', 'Moderate': 'Orange', 'Strong': 'Green'}
		self.passwordStrenghtLabel = Label(self.passwordFrame, width=22, text='Password Strength Meter', fg='grey',
										   anchor='center')
		self.passwordStrenghtLabel.grid(row=2, column=1, sticky='w')

		# password strenght meter

		self.passwordStrenghtMeter = Progressbar(self.passwordFrame, length=180, style='black.Horizontal.TProgressbar')
		self.passwordStrenghtMeter['value'] = 0
		self.passwordStrenghtMeter.grid(row=3, column=1, sticky='w')

		# Security Level Section

		self.securityLevel_Frame = Frame(self.newPasswordFrame)
		self.securityLevel_Frame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.securityLevel_Label = Label(self.securityLevel_Frame, width=200, image=self.helpIcon, compound=LEFT,
										 cursor="hand2", text="Security Level: ", anchor='w')
		self.securityLevel_Label.config(font=("Verdana", 10))
		self.securityLevel_Label.bind('<Button-1>', self.show_sechelp)
		self.securityLevel_Label.image = self.helpIcon
		self.securityLevel_Label.grid(row=0, column=0, sticky='w')

		self.securityLevel_list = ["Select security level", "not secure", "low", "medium", "high"]
		self.choice_var = tk.StringVar()
		self.choice_var.set(self.securityLevel_list[0])
		self.securityLevel_Menu = OptionMenu(self.securityLevel_Frame, self.choice_var, *self.securityLevel_list)
		self.securityLevel_Menu.config(width=22)
		self.securityLevel_Menu.grid(row=0, column=1, sticky='w')

		self.securityLevelError = Label(self.securityLevel_Frame, text="", anchor='w', fg='red')
		self.securityLevelError.config(font=("Verdana", 8))
		self.securityLevelError.grid(row=1, column=1, sticky='w')

		# Notes Section

		self.notes_Frame = Frame(self.newPasswordFrame)
		self.notes_Frame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.notes_Label = Label(self.notes_Frame, width=200, image=self.helpIcon, compound=LEFT, cursor="hand2",
								 text="Notes: ", anchor='w')
		self.notes_Label.config(font=("Verdana", 10))
		self.notes_Label.bind('<Button-1>', self.show_notehelp)
		self.notes_Label.image = self.helpIcon
		self.notes_Label.pack(side=LEFT)

		self.notes_Entry = Text(self.notes_Frame, width=50, height=10)

		self.notes_Entry.pack(side=LEFT)

		# Security Question radio button

		self.secQuestionFrame = Frame(self.newPasswordFrame)
		self.secQuestionFrame.pack(side=TOP, fill=X, padx=5, pady=5)

		self.secQuestionLabel = Label(self.secQuestionFrame, width=200, image=self.helpIcon, compound=LEFT,
									  cursor="hand2", text="Security Questions: ", anchor='w')
		self.secQuestionLabel.config(font=("Verdana", 10))
		self.secQuestionLabel.bind('<Button-1>', self.show_secqhelp)
		self.secQuestionLabel.image = self.helpIcon
		self.secQuestionLabel.pack(side=LEFT)

		self.answer = IntVar()
		self.answerYes = Radiobutton(self.secQuestionFrame, text="Yes", variable=self.answer, value=1,
									 command=self.showSecAnswerSection).pack(side=LEFT)
		self.answerNo = Radiobutton(self.secQuestionFrame, text="No", variable=self.answer, value=2,
									command=self.hideAnswerSection).pack(side=LEFT)

		self.securityQuestionError = Label(self.secQuestionFrame, text="", anchor='w', fg='red')
		self.securityQuestionError.config(font=("Verdana", 8))
		self.securityQuestionError.pack(side=LEFT)

		# Number of Security Questions spinbox

		self.numSecQuestionFrame = Frame(self.newPasswordFrame)


		self.numSecQuestionLabel = Label(self.numSecQuestionFrame, width=200, image=self.helpIcon, compound=LEFT,
										 cursor="hand2", text="Num. of Security Questions: ",
										 anchor='w')
		self.numSecQuestionLabel.config(font=("Verdana", 10))
		self.numSecQuestionLabel.bind('<Button-1>', self.show_nsecqhelp)
		self.numSecQuestionLabel.image = self.helpIcon
		self.numSecQuestionLabel.pack(side=LEFT)

		self.numQuestion = StringVar()
		self.numQuestion.set("1")

		self.numQuestionsSpinBox = Spinbox(self.numSecQuestionFrame, from_=0, to=5, textvariable=self.numQuestion,
										   command=self.showSecurityAnswers)
		self.numQuestionsSpinBox.pack(side=LEFT)
		self.numQuestionsError = Label(self.numSecQuestionFrame, text="", anchor='w', fg='red', font=("Verdana", 8))
		self.numQuestionsError.pack(side=LEFT)

		# Security Answer Section

		self.securityAnswersFrame = Frame(self.newPasswordFrame)

		self.answerLabels = []
		self.answerEntries = []
		self.answerErrors = []

		for n in range(5):
			labelText = "Security Answer %2d: " % (n + 1)
			self.answerLabels.append(Label(self.securityAnswersFrame, text=labelText, font=("Verdana", 10)))
			# create entries list
			self.answerEntries.append(Entry(self.securityAnswersFrame, bg='white', width=40))
			self.answerErrors.append(
				Label(self.securityAnswersFrame, text="", anchor='w', fg='red', font=("Verdana", 8)))

		# Frame for footer buttons

		self.footerFrame = Frame(self.contentframe)
		self.footerFrame.grid(row=3, column=0, sticky="nsew")

		# return button

		self.return_Button = Button(self.footerFrame, width=80, font=("Verdana", 10), image=self.back, compound=tk.LEFT,
									text="Return", fg='white', bg='#003152', relief="groove", cursor="hand2",
									command=self.go_back)
		self.return_Button.pack(side=LEFT, padx=5, pady=5)
		self.return_Button.image = self.back

		# save button
		self.save_Button = Button(self.footerFrame, width=80, font=("Verdana", 10), image=self.save, compound=tk.LEFT,
								  text="Save", fg='white', bg='#0E8C4A', relief="groove", cursor="hand2",
								  command=self.validate)

		self.save_Button.pack(side=RIGHT, padx=5, pady=5)
		self.save_Button.image = self.save

		# delete button

		self.delete_Button = Button(self.footerFrame, width=80, font=("Verdana", 10), image=self.trash,
									compound=tk.LEFT, cursor="hand2",
									text="Delete", fg='white', bg='#A91010', relief="groove",
									command=self.delete_password)
		self.delete_Button.pack(side=RIGHT, padx=5, pady=5)
		self.delete_Button.image = self.trash

	# function to show entry help
	def show_entryhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Entryname Help")

		Label(top, text="*Should be between 2 to 35 characters long", anchor='w').pack(side="top", fill="x",
																					   pady=10)
		Label(top, text="*Should be alphanumeric", anchor='w').pack(side="top", fill="x", pady=10)

		Label(top, text="*Should be unique in the category", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show website help
	def show_webhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Website Help")

		Label(top, text="*Optional field", anchor='w').pack(side="top", fill="x", pady=10)

		Label(top, text="*If specified, should use form http://", anchor='w').pack(side="top", fill="x",
																				   pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show username help
	def show_userhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Username Help")

		Label(top, text="*Should be between 2 to 50 characters long", anchor='w').pack(side="top", fill="x",
																					   pady=10)
		Label(top, text="*Should not contain spaces", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_passhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Password Help")

		Label(top, text="*Should be minimum 6 characters long", anchor='w').pack(side="top", fill="x",
																				 pady=10)
		Label(top, text="*Should have at least one number", anchor='w').pack(side="top", fill="x", pady=10)
		Label(top, text="*Should have at least one uppercase character", anchor='w').pack(
			side="top", fill="x", pady=10)
		Label(top, text="*Should have at least one special symbol", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_sechelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Security Level Help")

		Label(top, text="*Security level ‘not secure’ is not generating a security timer in the system",
			  anchor='w').pack(side="top", fill="x",
							   pady=10)
		Label(top, text="*Security level ‘low’ generating security timer to 6 months in the system", anchor='w').pack(
			side="top", fill="x", pady=10)
		Label(top, text="*Security level ‘medium’ generating security timer to 3 months in the system",
			  anchor='w').pack(
			side="top", fill="x", pady=10)
		Label(top, text="*Security level ‘high’ generating security timer to 1 month in the system", anchor='w').pack(
			side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_notehelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Note Help")

		Label(top, text="*Note section is optional", anchor='w').pack(side="top", fill="x",
																	  pady=10)
		Label(top, text="*You can specify all the notes here", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_secqhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Security Question Help")

		Label(top, text="*Please select 'Yes' if you have security questions", anchor='w').pack(side="top", fill="x", pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show password help
	def show_nsecqhelp(self, event):
		top = Toplevel()

		top.geometry("+{}+{}".format(event.x_root, event.y_root))
		top.title("Number Sec. Question Help")

		Label(top, text="*Number of security answers should be selected", anchor='w').pack(side="top",
																						   fill="x",
																						   pady=10)
		Label(top, text="*Security answers should be between 2 to 50 characters long", anchor='w').pack(side="top",
																										fill="x",
																										pady=10)

		button = Button(top, text="Ok", command=top.destroy)
		button.pack()

	# function to show the entered password
	def show_password(self, event):
		if (self.passwordEntry.cget('show') == '*'):

			self.passwordEntry.config(show='')
		else:
			self.passwordEntry.config(show='*')

	def check_pass_strenght(self, event):
		password = self.passwordEntry.get()

		if (len(password) > 0):
			stats = PasswordStats(password)
			complex = self.controller.policy.test(password)
			print(complex)

			strength = stats.strength()

			if (strength < 0.34):
				self.passwordStrenghtMeter['value'] = 30
				self.passwordStrenghtLabel['text'] = "Weak"
				self.passwordStrenghtLabel['fg'] = self.strenghPassword['Weak']
				self.style.configure("black.Horizontal.TProgressbar", background='red')
			elif (strength > 0.34 and strength < 0.66):
				self.passwordStrenghtMeter['value'] = 60
				self.passwordStrenghtLabel['text'] = "Moderate"
				self.passwordStrenghtLabel['fg'] = self.strenghPassword['Moderate']
				self.style.configure("black.Horizontal.TProgressbar", background='yellow')
			elif (strength >= 0.66):
				self.passwordStrenghtMeter['value'] = 100
				self.passwordStrenghtLabel['text'] = "Strong"
				self.passwordStrenghtLabel['fg'] = self.strenghPassword['Strong']
				self.style.configure("black.Horizontal.TProgressbar", background='green')
		else:
			self.passwordStrenghtMeter['value'] = 0
			self.passwordStrenghtLabel['text'] = "Password Strength Meter"
			self.passwordStrenghtLabel['fg'] = 'grey'

	def generate_password(self):

		self.passwordEntry.delete(0, END)

		"""Generate a random password """
		stringSource = string.ascii_letters + string.digits + string.punctuation
		password = secrets.choice(string.ascii_lowercase)
		password += secrets.choice(string.ascii_uppercase)
		password += secrets.choice(string.digits)
		password += secrets.choice(string.punctuation)
		for i in range(12):
			password += secrets.choice(stringSource)
		char_list = list(password)
		secrets.SystemRandom().shuffle(char_list)
		password = ''.join(char_list)

		self.passwordEntry.insert(0, password)

		stats = PasswordStats(password)
		strength = stats.strength()

		if (strength < 0.34):
			self.passwordStrenghtMeter['value'] = 30
			self.passwordStrenghtLabel['text'] = "Weak"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Weak']
			self.style.configure("black.Horizontal.TProgressbar", background='red')
		elif (strength > 0.34 and strength < 0.66):
			self.passwordStrenghtMeter['value'] = 60
			self.passwordStrenghtLabel['text'] = "Moderate"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Moderate']
			self.style.configure("black.Horizontal.TProgressbar", background='yellow')
		elif (strength >= 0.66):
			self.passwordStrenghtMeter['value'] = 100
			self.passwordStrenghtLabel['text'] = "Strong"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Strong']
			self.style.configure("black.Horizontal.TProgressbar", background='green')

	# function that opens the website
	def go_web(self, event):
		url = self.websiteNameEntry.get()
		if (url != ''):
			webbrowser.open(url)  # go to project on github

	# function to show security answer section
	def showSecAnswerSection(self):
		self.numSecQuestionFrame.pack(side=TOP, fill=X, padx=5, pady=5)
		self.securityAnswersFrame.pack(side=TOP, fill=X, padx=5, pady=5)

	# function to hide security answer section
	def hideAnswerSection(self):
		self.numSecQuestionFrame.pack_forget()
		self.securityAnswersFrame.pack_forget()

	# function to show security answers entries
	def showSecurityAnswers(self):
		for n in range(5):
			self.answerEntries[n].delete(0, END)
			self.answerLabels[n].grid_forget()
			self.answerEntries[n].grid_forget()
			self.answerErrors[n].grid_forget()

		num_answer = int(self.numQuestionsSpinBox.get())

		for n in range(num_answer):
			self.answerLabels[n].grid(row=n, column=0)
			self.answerEntries[n].grid(row=n, column=1)
			self.answerErrors[n].grid(row=n, column=2)

	# this function deletes password entry
	def delete_password(self):
		question = "Would you like to delete this password entry?"
		answer = tkinter.messagebox.askquestion(self.entryName, question)
		if (answer == 'yes'):
			conn = sqlite3.connect('LockIT.db')
			c = conn.cursor()
			c.execute("DELETE FROM PASSWORD WHERE ENTRY_NAME=? and CATEGORY=?", (self.entryName, self.categoryId))

			conn.commit()
			# close database
			conn.close()
			# clear modify page
			self.clear_entries()
			# clear view page
			self.controller.show_frame("ViewPassword").clear_entries()
			# show viepasswords inside category page
			self.controller.show_frame("ViewPasswords_InCategory").set_category(self.categoryName)

	# function to update title category,color and password details
	def pass_variables(self, category, entry_name):

		self.category_label['text'] = category
		self.categoryName = category
		self.entryName = entry_name

		# make connection to db
		conn = sqlite3.connect('LockIT.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
		# add cursor
		c = conn.cursor()

		# return color of the categoty from db
		c.execute("SELECT COLOUR_HEX FROM CATEGORY WHERE CATEGORY_NAME=?", (self.categoryName,))
		color = c.fetchone()

		# return category id from db
		c.execute("SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME=?", (self.categoryName,))
		rec2 = c.fetchone()
		category_id = int(rec2[0])
		self.categoryId = category_id

		# decrypt password
		c.execute("SELECT PASS_KEY,PASSWORD FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?",
				  (self.entryName, self.categoryId,))
		key, encrypted = c.fetchone()
		# decrypting
		keyS = key + Login.loginScreen.getMasterKey(root).encode()
		f2 = Fernet(keyS)
		decrypted = f2.decrypt(encrypted)
		self.original_password = decrypted.decode()

		# return password details
		c.execute("SELECT ENTRY_NAME,WEBSITE,USERNAME,PASSWORD,SECURITY_QUEST,NUM_SECURITY_ANSWER,ANSWER_1,ANSWER_2,"
				  "ANSWER_3,ANSWER_4,ANSWER_5,NOTES,S_LEVEL,DATE_CREATED"
				  " FROM PASSWORD WHERE ENTRY_NAME=? AND CATEGORY=?", (self.entryName, self.categoryId))
		pass_details = c.fetchone()

		self.current_entryname = pass_details[0]
		self.current_password = self.original_password

		print(pass_details)
		self.entryNameEntry.insert(0, pass_details[0])

		self.websiteNameEntry.insert(0, pass_details[1])

		#decrypt username
		user = f2.decrypt(pass_details[2])
		userD =  user.decode()

		self.userNameEntry.insert(0, userD)

		self.passwordEntry.insert(0, self.current_password)

		stats = PasswordStats(pass_details[3])
		strength = stats.strength()

		if (strength < 0.34):
			self.passwordStrenghtMeter['value'] = 30
			self.passwordStrenghtLabel['text'] = "Weak"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Weak']
			self.style.configure("black.Horizontal.TProgressbar", background='red')
		elif (strength > 0.34 and strength < 0.66):
			self.passwordStrenghtMeter['value'] = 60
			self.passwordStrenghtLabel['text'] = "Moderate"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Moderate']
			self.style.configure("black.Horizontal.TProgressbar", background='yellow')
		elif (strength >= 0.66):
			self.passwordStrenghtMeter['value'] = 100
			self.passwordStrenghtLabel['text'] = "Strong"
			self.passwordStrenghtLabel['fg'] = self.strenghPassword['Strong']
			self.style.configure("black.Horizontal.TProgressbar", background='green')

		sec_level = pass_details[12]
		dateDB = pass_details[13]
		today = date.today()
		if (self.generatePasswordButton['bg'] == 'red'):
			self.generatePasswordButton['bg'] = '#003152'
			self.generatePasswordButton['fg'] = 'white'

		if (sec_level == 1):
			self.choice_var.set(self.securityLevel_list[1])


		elif (sec_level == 2):
			self.choice_var.set(self.securityLevel_list[2])
			six_months = timedelta(days=182)
			expire = dateDB + six_months
			if ((expire - today).days <= 0):
				self.generatePasswordButton['bg'] = 'red'
				self.generatePasswordButton['fg'] = 'white'
			else:
				self.generatePasswordButton['bg'] = '#003152'

		elif (sec_level == 3):
			self.choice_var.set(self.securityLevel_list[3])
			three_months = timedelta(days=91)
			expire = dateDB + three_months
			if ((expire - today).days <= 0):
				self.generatePasswordButton['bg'] = 'red'
				self.generatePasswordButton['fg'] = 'white'
			else:
				self.generatePasswordButton['bg'] = '#003152'

		elif (sec_level == 4):

			self.choice_var.set(self.securityLevel_list[4])
			one_months = timedelta(days=31)
			expire = dateDB + one_months
			if ((expire - today).days <= 0):
				self.generatePasswordButton['bg'] = 'red'
				self.generatePasswordButton['fg'] = 'white'
			else:
				self.generatePasswordButton['bg'] = '#003152'

		self.notes_Entry.insert("1.0", pass_details[11])

		self.answer.set(pass_details[4])

		if (pass_details[5] == 0):

			self.numSecQuestionFrame.pack_forget()
		else:

			self.numSecurityAnswers = pass_details[5]
			self.numQuestion.set(pass_details[5])
			self.numSecQuestionFrame.pack(side=TOP, fill=X, padx=5, pady=5)
			self.securityAnswersFrame.pack(side=TOP, fill=X, padx=5, pady=5)

			i = 6
			for n in range(self.numSecurityAnswers):
				self.answerLabels[n].grid(row=n, column=0)
				self.answerEntries[n].grid(row=n, column=1)
				self.answerErrors[n].grid(row=n, column=2)
				self.answerEntries[n].insert(0, pass_details[i])
				i = i + 1

		# close connection to db
		conn.close()

		# set the category label background
		self.category_label['bg'] = color

	# function that validates the entries
	def validate(self):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 35

		if (self.entryNameError.cget('text') != ''):
			self.entryNameError['text'] = ''

		# check length of entry
		en_len = len(str(self.entryNameEntry.get()))
		entry_name = self.entryNameEntry.get()

		if (entry_name != self.current_entryname):
			if (en_len == 0):
				num_errors += 1
				errMsg = "Please enter entry name"
				self.entryNameError['text'] = errMsg
			elif (en_len < min_entry_len):
				num_errors += 1
				errMsg = "Invalid entry name"
				self.entryNameError['text'] = errMsg

			elif (en_len > max_entry_len):
				num_errors += 1
				errMsg = "Invalid entry name"
				self.entryNameError['text'] = errMsg

			else:
				# check if has spaces and alphanumeric
				t = entry_name.split()
				if len(t) > 1:
					for i in t:
						if (i.isalnum() == FALSE):
							num_errors += 1
							errMsg = "Invalid entry name"
							self.entryNameError['text'] = errMsg
							break;
				else:
					if (entry_name.isalnum() == FALSE):
						num_errors += 1
						errMsg = "Invalid entry name"
						self.entryNameError['text'] = errMsg

			# check if entry name is unique in the category

			# return count from db
			c.execute("SELECT COUNT(*) FROM PASSWORD WHERE CATEGORY=? AND ENTRY_NAME=?", (self.categoryId, entry_name))
			rec1 = c.fetchone()
			num_occur = int(rec1[0])

			if (num_occur >= 1):
				num_errors += 1
				errMsg = "Entry name is already exist in this category"
				self.entryNameError['text'] = errMsg

		# Website validation
		website_name = self.websiteNameEntry.get()
		if (self.websiteNameError.cget('text') != ''):
			self.websiteNameError['text'] = ''

		if (website_name != ''):
			if (checkers.is_url(website_name) == FALSE):
				num_errors += 1
				errMsg = "Invalid website"
				self.websiteNameError['text'] = errMsg

		# Username validation
		user_name = self.userNameEntry.get()
		user_len = len(str(user_name))
		min_user_len = 2
		max_user_len = 50

		if (self.userNameError.cget('text') != ''):
			self.userNameError['text'] = ''

		# check length of username
		if (user_len == 0):
			num_errors += 1
			errMsg = "Please enter username"
			self.userNameError['text'] = errMsg
		elif (user_len < min_user_len):
			num_errors += 1
			errMsg = "Invalid username"
			self.userNameError['text'] = errMsg

		elif (user_len > max_user_len):
			num_errors += 1
			errMsg = "Invalid username"
			self.userNameError['text'] = errMsg
		else:
			# check if username has spaces
			u = user_name.split()
			if len(u) > 1:
				num_errors += 1
				errMsg = "Invalid username"
				self.userNameError['text'] = errMsg

		# password validation

		password = self.passwordEntry.get()
		res = self.controller.policy.test(password)

		if (password != self.current_password):

			if (self.password_Error.cget('text') != ''):
				self.password_Error['text'] = ''

			if (len(str(password)) == 0):
				num_errors += 1
				errMsg = "Please enter password"
				self.password_Error['text'] = errMsg
			elif (len(res) != 0):
				num_errors += 1
				errMsg = "Invalid password"
				self.password_Error['text'] = errMsg

			else:
				# count number of same passwords
				c.execute("SELECT PASSWORD,PASS_KEY FROM PASSWORD")
				passw = c.fetchall()

				list = []
				for var in passw:
					# decrypting
					keyS = var[1] + Login.loginScreen.getMasterKey(root).encode()
					f2 = Fernet(keyS)
					decrypted = f2.decrypt(var[0])
					original_password = decrypted.decode()
					list.append(original_password)

				num_occur = 0
				for p in list:
					if p == password:
						num_occur = num_occur + 1

				if (num_occur >= 3):
					num_errors += 1
					errMsg = "Password is already used 3 times"
					self.password_Error['text'] = errMsg

		# security level validation
		sec_level = self.choice_var.get()
		if (self.securityLevelError.cget('text') != 'Select security level'):
			self.securityLevelError['text'] = ''

		if (sec_level == 'Select security level'):
			num_errors += 1
			errMsg = "Please select security level"
			self.securityLevelError['text'] = errMsg

		# security question - yes/no validation
		answer = self.answer.get()

		if (self.securityQuestionError.cget('text') != ''):
			self.securityQuestionError['text'] = ''

		if (answer == 0):
			num_errors += 1
			errMsg = "Please select yes / no"
			self.securityQuestionError['text'] = errMsg

		# security answers validation
		if (self.numQuestionsError.cget('text') != ''):
			self.numQuestionsError['text'] = ''
		min_ans_len = 2
		max_ans_len = 50
		num_answer = 0
		if (answer == 1):
			num_answer = int(self.numQuestion.get())
			if (num_answer == 0):
				num_errors += 1
				errMsg = "Please select number of answers"
				self.numQuestionsError['text'] = errMsg
			else:
				for n in range(num_answer):
					if (self.answerErrors[n].cget('text') != ''):
						self.answerErrors[n]['text'] = ''
					if (len(str(self.answerEntries[n].get())) == 0):
						num_errors += 1
						errMsg = "Please enter security answer"
						self.answerErrors[n]['text'] = errMsg
					elif (len(str(self.answerEntries[n].get())) < min_ans_len):
						num_errors += 1
						errMsg = "Invalid security answer"
						self.answerErrors[n]['text'] = errMsg
					elif (len(str(self.answerEntries[n].get())) > max_ans_len):
						num_errors += 1
						errMsg = "Invalid security answer"
						self.answerErrors[n]['text'] = errMsg

		notes = self.notes_Entry.get('1.0', END)

		# close connection to db
		conn.close()

		if (num_errors == 0):
			self.updateRecordToDb(entry_name, website_name, user_name, password, answer, num_answer,
								  str(self.answerEntries[0].get()),
								  str(self.answerEntries[1].get()), str(self.answerEntries[2].get()),
								  str(self.answerEntries[3].get()), str(self.answerEntries[4].get()),
								  notes, self.categoryId, sec_level)
			self.clear_entries()
			self.controller.show_frame("ViewPassword").clear_entries()
			self.controller.show_frame("ViewPasswords_InCategory").set_category(self.categoryName)

	# saves the Record into LockIT.db
	def updateRecordToDb(self, entryname, website, username, password, secquestion, num_answer, answer1, answer2,
						 answer3, answer4, answer5, notes, category, sec_level):
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		# return security level id from db
		c.execute("SELECT S_LEVEL_ID FROM SECURITYLEVEL WHERE S_LEVEL_NAME=?", (sec_level,))
		rec1 = c.fetchone()
		# selecting column value into varible
		sec_id = int(rec1[0])

		# encrypt password
		p = str.encode(password)
		key = Fernet.generate_key()
		keyS = key + Login.loginScreen.getMasterKey(root).encode()
		print(key)
		f = Fernet(keyS)
		print(keyS)
		token = f.encrypt(p)
		print(token)

		# encrypt username
		user = str.encode(username)
		usertoken = f.encrypt(user)

		if (password != self.current_password):
			today = date.today()
			c.execute(
				"UPDATE PASSWORD SET ENTRY_NAME=?,WEBSITE=?,USERNAME=?,PASSWORD=?,SECURITY_QUEST=?,NUM_SECURITY_ANSWER=?,"
				"ANSWER_1=?,ANSWER_2=?,ANSWER_3=?,ANSWER_4=?,ANSWER_5=?,NOTES=?,S_LEVEL=?,DATE_CREATED=?,PASS_KEY=? WHERE CATEGORY=? AND ENTRY_NAME=?",
				(entryname, website, usertoken, token, secquestion, num_answer, answer1, answer2, answer3, answer4,
				 answer5, notes, sec_id, today, key, self.categoryId, self.current_entryname))
		else:
			c.execute(
				"UPDATE PASSWORD SET ENTRY_NAME=?,WEBSITE=?,USERNAME=?,PASSWORD=?,SECURITY_QUEST=?,NUM_SECURITY_ANSWER=?,"
				"ANSWER_1=?,ANSWER_2=?,ANSWER_3=?,ANSWER_4=?,ANSWER_5=?,NOTES=?,S_LEVEL=?,PASS_KEY=? WHERE CATEGORY=? AND ENTRY_NAME=?",
				(entryname, website, usertoken, token, secquestion, num_answer, answer1, answer2, answer3, answer4,
				 answer5, notes, sec_id, key, self.categoryId, self.current_entryname))

		# select all
		c.execute("SELECT * FROM PASSWORD")
		rows = c.fetchall()
		for row in rows:
			print(row)

		# save changes made
		conn.commit()
		# close connection to db
		conn.close()

	# clears the modify password page entries
	def clear_entries(self):

		self.entryNameEntry.delete(0, END)
		self.entryNameError['text'] = ''
		self.websiteNameEntry.delete(0, END)
		self.websiteNameError['text'] = ''
		self.userNameEntry.delete(0, END)
		self.userNameError['text'] = ''
		self.passwordEntry.delete(0, END)
		self.password_Error['text'] = ''
		self.choice_var.set(self.securityLevel_list[0])
		self.securityLevelError['text'] = ''
		self.notes_Entry.delete("1.0", END)

		self.answer.set(0)
		self.securityQuestionError['text'] = ''
		self.numQuestion.set("0")
		self.numQuestionsError['text'] = ''

		for n in range(5):
			self.answerEntries[n].delete(0, END)
			self.answerErrors[n]['text'] = ''
			self.answerLabels[n].grid_forget()
			self.answerEntries[n].grid_forget()
			self.answerErrors[n].grid_forget()
		self.hideAnswerSection()

	def go_back(self):
		self.clear_entries()
		self.controller.show_frame("ViewPassword")


class MediaPage(Page):
	def __init__(self, *args, **kwargs):
		Page.__init__(self, *args, **kwargs)

		# position the pop up windows in the middle

		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		# icons
		# images
		path2 = "medias.png"
		dropdown = "dropdown.png"
		self.lockitmedia = PhotoImage(file=resource_path(path2))
		self.folder = PhotoImage(file=resource_path("folder.png"))
		self.dropdownicon = PhotoImage(file=resource_path(dropdown))

		# main frame
		self.mediaScreen = Frame(self)
		self.mediaScreen.pack(fill="both", expand=True)

		# seperate main window in two frames

		self.buttonframe = tk.Frame(self.mediaScreen)
		self.container = tk.Frame(self.mediaScreen)
		self.separator = tk.Frame(self.mediaScreen)

		self.buttonframe.pack(side="left", fill="both", expand=False)
		self.separator.pack(side="left", fill="both", expand=False)
		self.container.pack(side="left", fill="both", expand=True)



		# button frame
		space = tk.Label(self.buttonframe, height=1)
		space.pack(side="bottom")



		# container frame
		self.container.columnconfigure(0, weight=1)
		self.container.rowconfigure(0, weight=1)
		self.container.rowconfigure(1, weight=2)
		self.container.rowconfigure(2, weight=1)

		# separate container in 3 frames
		self.header = Frame(self.container)
		self.media_files = Frame(self.container)
		self.media_folders = Frame(self.container)

		self.header.grid(row=0, column=0, sticky="nwse")
		self.media_files.grid(row=1, column=0, sticky="nwse")
		self.media_folders.grid(row=2, column=0, sticky="nwse")

		# header frame configuration layout
		self.header.rowconfigure(0, weight=1)
		self.header.rowconfigure(1, weight=1)
		self.header.columnconfigure(0, weight=1)
		self.header.columnconfigure(1, weight=1)
		self.header.columnconfigure(2, weight=1)

		# Title page
		self.titleFrame = Frame(self.header)
		self.titleFrame.grid(row=0, column=0, columnspan=3, sticky=(N, S, E, W))
		self.titleFrame.rowconfigure(0, weight=1)
		self.titleFrame.columnconfigure(0, weight=1)
		self.search_bar = tk.Label(self.titleFrame, text="Media", font=("Verdana", 15), fg="white",bg="#003152", width=60)
		self.search_bar.grid(column=0, row=0, sticky=(N, S, E, W))

		# navigation header frame
		self.actionframe = Frame(self.header)
		self.actionframe.grid(column=0, row=1, sticky="w")
		self.actionframe.rowconfigure(0, weight=1)
		self.actionframe.columnconfigure(0, weight=1)
		self.actionframe.columnconfigure(1, weight=1)
		self.actionframe.columnconfigure(2, weight=1)

		# media action menu

		self.mb = Label(self.actionframe, text="My Media", cursor="hand2", image=self.dropdownicon, compound=RIGHT,
						font=("Verdana", 9))
		self.mb.image = self.dropdownicon
		self.mb.bind("<Enter>", self.on_enter)
		self.mb.bind("<Leave>", self.on_leave)
		self.mb.bind('<Button-1>', self.show_menu)
		self.mb.grid(column=0, row=0, sticky='w', padx=5)

		# media files frame - where images located - configuration layout
		self.media_files.rowconfigure(0, weight=1)
		self.media_files.rowconfigure(1, weight=1)
		self.media_files.rowconfigure(2, weight=10)
		self.media_files.columnconfigure(0, weight=1)

		# title media files
		self.msTitle = Label(self.media_files, text="Files", font=("Verdana", 10))
		self.msTitle.grid(column=0, row=0, sticky=(W), padx=5)

		# seperator media files
		self.ms = ttk.Separator(self.media_files, orient=HORIZONTAL)
		self.ms.grid(column=0, row=1, sticky=(E, W))

		# media folders frame - where folders  located - configuration layout
		self.media_folders.rowconfigure(0, weight=1)
		self.media_folders.rowconfigure(1, weight=1)
		self.media_folders.rowconfigure(2, weight=10)
		self.media_folders.columnconfigure(0, weight=1)

		# title media folders
		self.fsTitle = Label(self.media_folders, text="Folders", font=("Verdana", 10))
		self.fsTitle.grid(column=0, row=0, sticky=(W), padx=5)

		# seperator media folders
		self.fs = ttk.Separator(self.media_folders, orient=HORIZONTAL)
		self.fs.grid(column=0, row=1, sticky=(E, W))

		self.media_labels = {}
		self.folder_labels = {}
		self.folder_id = 0

		self.loadmedia()
		self.loadfolders()

	# drop down menu
	def on_enter(self, event):

		event.widget['background'] = 'gray99'

	def on_leave(self, event):
		event.widget['background'] = 'SystemButtonFace'

	# function to show the menu options
	def show_menu(self, event):

		self.dropmenu = tk.Menu(self.mediaScreen, tearoff=0)
		self.dropmenu.add_command(label="Add New File", command=self.addnewmedia)
		self.dropmenu.add_command(label="Add New Folder", command=self.addfolder)
		self.dropmenu.post(event.x_root, event.y_root)

	# function to show add file  menu options
	def show_addfile(self, event):
		self.dropmenuaf = tk.Menu(self.mediaScreen, tearoff=0)
		self.dropmenuaf.add_command(label="Add New File", command=self.addnewmedia)
		self.dropmenuaf.post(event.x_root, event.y_root)

	def forgetmenu(self):
		self.mb.destroy()

	def return_home(self, event):
		self.folder_id = 0
		self.forgetmenu()
		self.loadmenu()
		self.clear_media()
		self.loadmedia()
		self.loadfolders()

	def loadmenu(self, foldername=NONE):

		if (self.folder_id == 0):
			self.myFiles.destroy()
			self.conn.grid_forget()
			self.mb = Label(self.actionframe, text="My Media", cursor="hand2", image=self.dropdownicon, compound=RIGHT,
							font=("Verdana", 9))
			self.mb.image = self.dropdownicon
			self.mb.bind("<Enter>", self.on_enter)
			self.mb.bind("<Leave>", self.on_leave)
			self.mb.bind('<Button-1>', self.show_menu)
			self.mb.grid(column=0, row=0, sticky='w', padx=5)
		else:

			self.myFiles = Label(self.actionframe, cursor="hand2", text="My Media", font=("Verdana", 9))
			self.myFiles.image = self.dropdownicon
			self.myFiles.bind("<Enter>", self.on_enter)
			self.myFiles.bind("<Leave>", self.on_leave)
			self.myFiles.bind("<Button-1>", self.return_home)
			self.myFiles.grid(column=0, row=0, sticky='w', padx=5)

			self.conn = Label(self.actionframe, text=" > ", font=("Verdana", 9))
			self.conn.grid(column=1, row=0, sticky='w', padx=5)

			# media action menu
			self.mb = Label(self.actionframe, text=foldername, cursor="hand2", image=self.dropdownicon, compound=RIGHT,
							font=("Verdana", 9))
			self.mb.image = self.dropdownicon
			self.mb.bind("<Enter>", self.on_enter)
			self.mb.bind("<Leave>", self.on_leave)
			self.mb.bind('<Button-1>', self.show_addfile)
			self.mb.grid(column=2, row=0, sticky='w', padx=5)

	def loadmedia(self):

		# content frame - where images located
		self.content_frame = Frame(self.media_files, relief="sunken")
		self.content_frame.grid(column=0, row=2, sticky=(N, S, E, W))

		scrollable_body = Scrollable(self.content_frame, width=32)

		# content frame
		for col in range(8):
			self.content_frame.columnconfigure(col, weight=1)
		for row in range(8):
			self.content_frame.rowconfigure(row, weight=1)

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("SELECT * FROM MEDIAS WHERE FOLDERID=?", (self.folder_id,))
		rows = c.fetchall()
		column = 0
		rowgrid = 0
		for row in rows:

			self.Titles = Label(scrollable_body, text=row[1], cursor="hand2", image=self.lockitmedia, width=100,
								compound=TOP)
			self.media_labels[row[1]] = self.Titles
			self.Titles.bind('<Button-3>', self.popup_file)
			self.Titles.bind('<Double-1>', self.viewmedia)
			self.Titles.image = self.lockitmedia
			self.Titles.grid(row=rowgrid, column=column, sticky='w')

			column = column + 1
			if (column > 8):
				column = 0
				rowgrid = rowgrid + 1

		conn.close()
		scrollable_body.update()

	def loadfolders(self):

		self.folder_frame = Frame(self.media_folders, relief="sunken")
		self.folder_frame.grid(column=0, row=2, sticky=(N, S, E, W))

		scrollable_body = Scrollable(self.folder_frame, width=32)

		# content frame
		for col in range(8):
			self.folder_frame.columnconfigure(col, weight=1)
		for row in range(2):
			self.folder_frame.rowconfigure(row, weight=1)

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("SELECT folder_Name FROM FOLDER where folder_Type=?", ("Media",))
		rows = c.fetchall()
		column = 0
		rowgrid = 0
		for row in rows:

			self.Titles = Label(scrollable_body, text=row[0], cursor="hand2", image=self.folder, width=100,
								compound=TOP)
			self.folder_labels[row[0]] = self.Titles
			self.Titles.bind('<Button-3>', self.popup_folder)
			self.Titles.bind('<Double-1>', self.viewfolder)
			self.Titles.image = self.lockitmedia
			self.Titles.grid(row=rowgrid, column=column, sticky='w')

			column = column + 1
			if (column > 8):
				column = 0
				rowgrid = rowgrid + 1

		conn.close()
		scrollable_body.update()

	def clear_media(self):

		for key, value in self.media_labels.items():
			self.media_labels[key].destroy()
		for key, value in self.folder_labels.items():
			self.folder_labels[key].destroy()

		self.content_frame.destroy()
		self.folder_frame.destroy()

	# function to add new media file
	def addnewmedia(self):

		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.addmedia = Toplevel()
		self.addmedia.geometry("300x200")
		self.addmedia.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.addmedia.resizable(0, 0)
		self.addmedia.title("Add New Media File")
		self.addmedia.wm_attributes('-topmost', 1)
		print(self.addmedia.winfo_toplevel)

		for row in range(9):
			self.addmedia.rowconfigure(row, weight=1)
		for col in range(3):
			self.addmedia.columnconfigure(col, weight=1)

		# Labels
		# TitleName = Label(self.addmedia, text="Insert File", font=("Verdana", 13))

		self.filepath = Entry(self.addmedia, width=30, fg="black")
		self.filepath.insert(0, "Chosen File")
		self.filename = ""
		self.saveas = Entry(self.addmedia, width=30, fg="black")
		self.saveas.insert(0, "Save as")
		self.saveas.bind("<FocusIn>", self.clear_saveas)
		self.errors = Label(self.addmedia, fg="red",text="",font=("Verdana", 9))

		# Buttons
		Computer = Button(self.addmedia, text="Browse From Computer", font=("Verdana", 13, "italic"),
						  relief="groove",
						  background="light blue", fg="grey", width=18, command=self.OpenFile)

		self.save = Button(self.addmedia, text="Save", font=("Verdana", 13, "italic"), relief="groove",
						   background="light blue", fg="grey", width=18, command=self.savefileDB)

		# Position

		self.filepath.grid(row=2, column=1, sticky="nsew")
		self.saveas.grid(row=3, column=1, sticky="nsew")
		Computer.grid(row=5, column=1, sticky="nsew")
		self.save.grid(row=6, column=1, sticky="nsew")
		self.errors.grid(row=7, column=1, sticky="nsew")

	def clear_saveas(self, event):
		self.saveas.delete(0, END)

	def checkIfMatchForCopy(self, entryText, windowObj, file_selected, folder_id):

		# if not matching hash vals, then error
		conn = sqlite3.connect('LockIT.db')
		c = conn.cursor()
		c.execute("SELECT passwordHash FROM LOCKITUSER")
		hashValFromDb = c.fetchone()
		# parse data
		hashVal = str(hashValFromDb[0])
		hashVal = hashVal.replace('b', '', 1)
		hashVal = hashVal.replace("'", '', 2)
		# compare password in db with entry
		# print(hashVal)
		hashVal = hashVal.encode()
		print(hashVal)
		if (bcrypt.checkpw(str(entryText.get()).encode(), hashVal)):
			print("Both Entries Match!")
			c.execute("SELECT MEDIA, TITLE FROM MEDIAS where TITLE=? and FOLDERID=?", (file_selected, folder_id))

			ablob, name = c.fetchone()

			file = self.write_file(ablob, name)


			conn.close()

			image = Image.open(file).show()
			windowObj.destroy()
		else:
			print("Entries Do not Match :(")
			# give errror message
			errMsg = "Password entries do not match"
			lbl = Label(windowObj, fg="red", text=errMsg)
			lbl.grid(row=3, column=0,sticky='nsew')
			windowObj.after(5000, lbl.destroy)

	def askForMPForCopy(self, file_selected, folder_id):


		cpWin = tk.Toplevel()
		cpWin.geometry("200x150")
		cpWin.wm_title("LockIT")
		cpWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))

		for r in range(4):
			cpWin.rowconfigure(r,weight=1)
		cpWin.columnconfigure(0, weight=1)

		l = tk.Label(cpWin, text="Please Enter Master Password ",anchor='center')
		l.grid(row=0, column=0,sticky='nswe',padx=5,pady=5)
		e = tk.Entry(cpWin, width=20, show="*")
		e.grid(row=2, column=0,sticky='nswe',padx=5,pady=5)


		b = ttk.Button(cpWin, text="Submit",cursor="hand2", command=lambda: self.checkIfMatchForCopy(e, cpWin, file_selected, folder_id))
		b.grid(row=4, column=0,sticky='e',padx=5,pady=5)
		nb = ttk.Button(cpWin, text="Return",cursor="hand2", command=cpWin.destroy)
		nb.grid(row=4, column=0,sticky='w',padx=5,pady=5)


	# function to view media file
	def viewmedia(self, event):
		#simpledialog.askstring("View File", "Master key required")
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		# statements
		c.execute("SELECT EYEICON FROM SETTINGS")
		permission = c.fetchone()

		if(permission[0] == 1):
			file_selected = event.widget['text']
			self.askForMPForCopy(file_selected, self.folder_id)


		else:
			file_selected = event.widget['text']

			# select all
			c.execute("SELECT MEDIA, TITLE FROM MEDIAS where TITLE=? and FOLDERID=?", (file_selected, self.folder_id))

			ablob, name = c.fetchone()

			file = self.write_file(ablob, name)

			conn.close()

			image = Image.open(file).show()

	def viewfolder(self, event):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		folderclicked = event.widget['text']
		print(folderclicked)

		# return folder id
		c.execute("SELECT folder_Id FROM FOLDER where folder_Name=? and folder_Type=?", (folderclicked, "Media"))
		f = c.fetchone()
		print(f)
		self.folder_id = f[0]
		conn.close()

		self.forgetmenu()
		self.loadmenu(folderclicked)
		self.clear_media()
		self.loadmedia()
		self.loadfolders()

	def OpenFile(self):

		self.addmedia.wm_attributes('-topmost', 0)

		self.filename = filedialog.askopenfilename(initialdir="/Pictures", title="Select file",
												   filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))

		self.addmedia.wm_attributes('-topmost', 1)

		self.filepath.delete(0, END)
		self.filepath.insert(0, self.filename)

	def savefileDB(self):

		if (self.filename == "Chosen File"):
			self.errors['text'] = "Please Choose file"
			self.errors.after(1000, self.clear)

		elif (self.filename == ""):
			self.errors['text'] = "Please Choose file"
			self.errors.after(1000, self.clear)

		else:
			stringafter = re.split('/', self.filename)[-1]
			type = stringafter.split(".")

			photo = self.convertToBinaryData(self.filename)
			Getsize = os.stat(self.filename)
			size = self.convert_bytes(Getsize.st_size)
			saveas = self.saveas.get()

			# make connection to db
			conn = sqlite3.connect('LockIT.db')
			# add cursor
			c = conn.cursor()
			c.execute("SELECT COUNT(*) FROM MEDIAS WHERE TITLE=? AND FOLDERID=?", (saveas, self.folder_id))
			names = c.fetchone()
			unique = int(names[0])

			if (unique >= 1):
				self.errors['text'] = "Name already exists"
				self.saveas.delete(0, END)
				self.errors.after(1000, self.clear)

			elif (len(self.saveas.get()) <= 0):
				self.errors['text'] = "Name required."
				self.saveas.delete(0, END)
				self.errors.after(1000, self.clear)
			else:
				c.execute("INSERT INTO MEDIAS (ID,TITLE,MEDIA,SIZE,TYPE,FOLDERID,DATEADDED) VALUES (NULL,?,?,?,?,?,?)",
						  (saveas, photo, size, type[1], self.folder_id, datetime.now()))
				# commit changes
				conn.commit()
				# close connection
				conn.close()
				self.addmedia.destroy()

				self.clear_media()
				self.loadmedia()
				self.loadfolders()

	def clear(self):
		self.errors['text'] = ""


	def convert_bytes(self, num):
		"""
		this function will convert bytes to MB.... GB... etc
		"""
		for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
			if num < 1024.0:
				return "%3.1f %s" % (num, x)
			num /= 1024.0


	def write_file(self, data, filename):
		# Convert binary data to proper format and write it on Hard Disk
		with open(filename, 'wb') as file:
			file.write(data)
		return filename


	def convertToBinaryData(self, filename):
		# Convert digital data to binary format
		with open(filename, 'rb') as file:
			binaryData = file.read()
		return binaryData


	# function to show the menu options
	def popup_file(self, event):
		# create a popup menu

		self.aMenuFile = tk.Menu(self.mediaScreen, tearoff=0)
		self.filename = event.widget['text']
		print(self.filename)

		self.rename = "Rename file"
		self.send = "Send file"
		self.delete = "Delete file"

		self.aMenuFile.add_command(label=self.rename, command=self.renamemedia)
		self.aMenuFile.add_command(label=self.send, command=lambda: self.sendmedia(self.filename))
		self.aMenuFile.add_command(label=self.delete, command=self.deletemedia)

		self.aMenuFile.post(event.x_root, event.y_root)


	# function to show the menu options
	def popup_folder(self, event):
		self.foldername = event.widget['text']
		self.aMenuFolder = tk.Menu(self.mediaScreen, tearoff=0)
		self.rename = "Rename folder"
		self.delete = "Delete folder"
		self.aMenuFolder.add_command(label=self.rename, command=self.renamefolder)
		self.aMenuFolder.add_command(label=self.delete, command=self.deletefolder)

		self.aMenuFolder.post(event.x_root, event.y_root)


	def renamemedia(self):
		self.renameMedia = Toplevel()
		self.renameMedia.geometry("300x200")
		self.renameMedia.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.renameMedia.resizable(0, 0)
		self.renameMedia.title("Rename Media File")

		path2 = "icons8-document-90.png"
		lockitmedia = PhotoImage(file=resource_path(path2))

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		c.execute("SELECT * FROM MEDIAS WHERE TITLE=? AND FOLDERID=?", (self.filename, self.folder_id))
		rows = c.fetchone()

		# Labels

		Name = Label(self.renameMedia, text="Name: " + rows[1], font=("Verdana", 8))
		Size = Label(self.renameMedia, text="Size:   " + rows[3], font=("Verdana", 8))
		Type = Label(self.renameMedia, text="Type:  " + rows[4], font=("Verdana", 8))
		Date = Label(self.renameMedia, text="Date:  " + rows[5], font=("Verdana", 8))
		self.errors = Label(self.renameMedia, text='', fg="red")
		panel2 = Label(self.renameMedia, image=lockitmedia, height=100, width=100)
		panel2.image = lockitmedia
		self.Input = Entry(self.renameMedia, relief="groove")

		self.Input.bind("<FocusIn>", self.clear_input)

		name = self.Input.get()
		self.Input.insert(0, "Enter New Name")
		# Buttons
		Save = Button(self.renameMedia, text="Save", font=("Arial", 13, "italic"), relief="groove",
					  background="light blue", fg="grey", command=self.setname)

		# Position

		panel2.place(bordermode=INSIDE, y=25)
		Name.place(x=110, y=40)
		Size.place(x=110, y=60)
		Type.place(x=110, y=80)
		Date.place(x=110, y=100)
		self.errors.place(x=110, y=120)
		Save.place(bordermode=INSIDE, y=147, x=13)
		self.Input.place(y=150, x=117, width=148, height=22)

		conn.close()


	def setname(self):
		name = self.Input.get()

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("SELECT COUNT(*) FROM MEDIAS WHERE TITLE=? AND FOLDERID=?", (name,self.folder_id))
		title = c.fetchone()
		names = int(title[0])
		print(len(self.Input.get()))
		if (names >= 1):
			self.errors['text'] = "Name already exists."
			self.Input.delete(0, END)
			self.errors.after(1000, self.clear)

		elif (len(self.Input.get()) <= 0):
			self.errors['text'] = "Name required."
			self.Input.delete(0, END)
			self.errors.after(1000, self.clear)

		else:
			c.execute("UPDATE MEDIAS SET TITLE=? WHERE TITLE=? AND FOLDERID=?", (name, self.filename, self.folder_id))

			print(name)

			conn.commit()
			conn.close()
			self.renameMedia.destroy()

			self.clear_media()
			self.loadmedia()
			self.loadfolders()


	def sendMediaToPc(self, directory_name, fileName):
		conn = sqlite3.connect('LockIT.db')
		cursor = conn.cursor()
		# select blob from database where title = filename
		# write the blob to a file in specified directory
		# write the photo to the selected directory

		cursor.execute("SELECT TYPE FROM MEDIAS WHERE TITLE = ? AND FOLDERID=?", (fileName, self.folder_id))
		t = cursor.fetchone()
		type = t[0]

		extention = "." + type
		with open((directory_name + "/" + fileName + extention), "wb") as output_file:
			cursor.execute("SELECT MEDIA FROM MEDIAS WHERE TITLE = ? AND FOLDERID=?", (fileName, self.folder_id))
			ablob = cursor.fetchone()

			output_file.write(ablob[0])
		conn.commit()
		conn.close()
		self.send.destroy()
		spam = fileName + ' is saved in ' + directory_name
		tkinter.messagebox.showinfo(fileName, spam)


	def OpenDir(self, fileName):
		# open the dir and save the dir name
		directory = askdirectory()
		print(directory)
		print(fileName)
		# pass dir name to sendmediatopc
		self.sendMediaToPc(directory, fileName)


	# function to send media file
	def sendmedia(self, filename):
		self.send = Toplevel()
		self.send.geometry("300x200")
		self.send.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.send.resizable(0, 0)
		self.send.title("Send Media File")

		path2 = "icons8-document-90.png"
		lockitmedia = PhotoImage(file=resource_path(path2))

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		c.execute("SELECT * FROM MEDIAS WHERE TITLE=? AND FOLDERID=?", (self.filename, self.folder_id))
		rows = c.fetchone()
		conn.close()

		# Labels

		Name = Label(self.send, text="Name: " + rows[1], font=("Verdana", 8))
		Size = Label(self.send, text="Size:   " + rows[3], font=("Verdana", 8))
		Type = Label(self.send, text="Type:  " + rows[4], font=("Verdana", 8))
		Date = Label(self.send, text="Date:  " + rows[5], font=("Verdana", 8))

		panel2 = Label(self.send, image=lockitmedia, height=100, width=100)
		panel2.image = lockitmedia

		# Buttons
		# make commands for the buttons

		Computer = Button(self.send, text="Computer", font=("Arial", 13, "italic"), relief="groove",
						  background="light blue",
						  fg="grey", command=lambda: self.OpenDir(filename))

		# Position

		panel2.place(bordermode=INSIDE, y=20)
		Name.place(x=110, y=30)
		Size.place(x=110, y=50)
		Type.place(x=110, y=70)
		Date.place(x=110, y=90)

		Computer.place(y=155, x=90)


	# function to delete media file
	def deletemedia(self):
		answer = tkinter.messagebox.askquestion(self.filename, 'Would you like to delete this file')
		if (answer == 'yes'):
			conn = sqlite3.connect('LockIT.db')
			c = conn.cursor()
			c.execute("DELETE FROM MEDIAS WHERE TITLE=? AND FOLDERID=?", (self.filename, self.folder_id))
			conn.commit()
			# close database
			conn.close()
			# clear media
			self.clear_media()
			# reload media
			self.loadmedia()
			self.loadfolders()


	# function to add new folder
	def addfolder(self):
		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.addfolderWin = Toplevel()
		self.addfolderWin.geometry("300x200")
		self.addfolderWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.addfolderWin.resizable(0, 0)
		self.addfolderWin.title("Add New Folder")
		self.addfolderWin.wm_attributes('-topmost', 1)

		for row in range(8):
			self.addfolderWin.rowconfigure(row, weight=1)

		self.addfolderWin.columnconfigure(0, weight=1)
		self.addfolderWin.columnconfigure(1, weight=1)

		# Labels
		self.FolderName = Label(self.addfolderWin, text="Folder Name", font=("Verdana", 10))
		self.folderNameError = Label(self.addfolderWin, text="", anchor='e', fg='red')
		self.folderNameError.config(font=("Verdana", 7))

		# Buttons
		self.Save = Button(self.addfolderWin, text="Save", font=("Arial", 13, "italic"), relief="groove",
						   background="light blue", fg="grey", command=self.fold_addvalidate)

		# Inputs
		self.Input = Entry(self.addfolderWin, relief="groove")

		# Position
		self.FolderName.grid(row=2, column=0, sticky="w", padx=5, pady=5)
		self.Input.grid(row=2, column=1, sticky="w")
		self.folderNameError.grid(row=4, column=1, sticky="w")
		self.Save.grid(row=7, column=1, sticky="e", padx=5, pady=5)


	def insert_folder(self, foldname):
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("INSERT INTO FOLDER VALUES(NULL,'Media',?,CURRENT_DATE )", (foldname,))
		c.execute("SELECT * FROM FOLDER")
		res = c.fetchall()
		print(res)
		conn.commit()
		# close database
		conn.close()
		self.addfolderWin.destroy()
		self.clear_media()
		self.loadmedia()
		self.loadfolders()


	def fold_addvalidate(self):
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 20

		if (self.folderNameError.cget('text') != ''):
			self.folderNameError['text'] = ''

		# check length of entry
		foldname = self.Input.get()
		en_len = len(str(foldname))

		if (foldname == ""):
			num_errors += 1
			errMsg = "Please enter folder name"
			self.folderNameError['text'] = errMsg

		elif (en_len < min_entry_len):
			num_errors += 1
			errMsg = "Folder must be\n at least 2 characters"
			self.folderNameError['text'] = errMsg

		elif (en_len > max_entry_len):
			num_errors += 1
			errMsg = "Folder can have\n maximum 20 characters."
			self.folderNameError['text'] = errMsg
		else:
			# return folder count from db
			foldname = foldname.upper()
			c.execute("SELECT COUNT(*) FROM FOLDER WHERE folder_Name=? and folder_Type=?", (foldname, "Media"))
			rec1 = c.fetchone()
			fold_name_occur = int(rec1[0])

			if (fold_name_occur >= 1):
				num_errors += 1
				errMsg = "Folder name is a duplicate\n select a different name"
				self.folderNameError['text'] = errMsg

			# check if it has spaces and alphabetic
			t = foldname.split()
			if len(t) > 1:
				for i in t:
					if (i.isalpha() == FALSE):
						num_errors += 1
						errMsg = "Entry name is not alphbetical"
						self.folderNameError['text'] = errMsg
						break;
			else:
				if (foldname.isalpha() == FALSE):
					num_errors += 1
					errMsg = "Entry name is not alphabetical"
					self.folderNameError['text'] = errMsg

		# close connection to db
		conn.close()

		if (num_errors == 0):
			self.insert_folder(foldname.upper())


	# function to rename folder
	def renamefolder(self):
		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.renamefolderWin = Toplevel()
		self.renamefolderWin.geometry("300x200")
		self.renamefolderWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.renamefolderWin.resizable(0, 0)
		self.renamefolderWin.title("Rename Folder")
		self.renamefolderWin.wm_attributes('-topmost', 1)

		for row in range(8):
			self.renamefolderWin.rowconfigure(row, weight=1)

		self.renamefolderWin.columnconfigure(0, weight=1)
		self.renamefolderWin.columnconfigure(1, weight=1)

		# Labels
		self.FolderName = Label(self.renamefolderWin, text="Folder Name", font=("Verdana", 10))

		self.folderNameError = Label(self.renamefolderWin, text="", anchor='e', fg='red')
		self.folderNameError.config(font=("Verdana", 7))

		# Buttons
		self.Save = Button(self.renamefolderWin, text="Save", font=("Arial", 13, "italic"), relief="groove",
						   background="light blue", fg="grey", command=self.fold_editvalidate)

		# Inputs
		self.Input = Entry(self.renamefolderWin, relief="groove")
		self.Input.insert(0, "Enter New Name")
		self.Input.bind("<FocusIn>", self.clear_input)

		# Position
		self.FolderName.grid(row=2, column=0, sticky="w", padx=5, pady=5)
		self.Input.grid(row=2, column=1, sticky="w")
		self.folderNameError.grid(row=4, column=1, sticky="w")
		self.Save.grid(row=7, column=1, sticky="e", padx=5, pady=5)


	def rename_folder(self, foldname):
		foldclick = self.foldername
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("UPDATE FOLDER SET folder_Name = ? WHERE folder_Name =? ", (foldname, foldclick))
		conn.commit()
		# close database
		conn.close()
		self.renamefolderWin.destroy()
		self.clear_media()
		self.loadmedia()
		self.loadfolders()


	def fold_editvalidate(self):
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 20

		if (self.folderNameError.cget('text') != ''):
			self.folderNameError['text'] = ''

		# check length of entry
		foldname = self.Input.get()
		en_len = len(str(foldname))

		if (foldname == ""):
			num_errors += 1
			errMsg = "Please enter folder name"
			self.folderNameError['text'] = errMsg

		elif (en_len < min_entry_len):
			num_errors += 1
			errMsg = "Folder must be\n at least 2 characters"
			self.folderNameError['text'] = errMsg

		elif (en_len > max_entry_len):
			num_errors += 1
			errMsg = "Folder can have\n maximum 20 characters."
			self.folderNameError['text'] = errMsg
		else:
			# return folder count from db
			foldname = foldname.upper()
			c.execute("SELECT COUNT(*) FROM FOLDER WHERE folder_Name=? and folder_Type=?", (foldname, "Media"))
			rec1 = c.fetchone()
			fold_name_occur = int(rec1[0])

			if (fold_name_occur >= 1):
				num_errors += 1
				errMsg = "Folder name is a duplicate\n select a different name"
				self.folderNameError['text'] = errMsg

			# check if it has spaces and alphabetic
			t = foldname.split()
			if len(t) > 1:
				for i in t:
					if (i.isalpha() == FALSE):
						num_errors += 1
						errMsg = "Entry name is not alphbetical"
						self.folderNameError['text'] = errMsg
						break;
			else:
				if (foldname.isalpha() == FALSE):
					num_errors += 1
					errMsg = "Entry name is not alphabetical"
					self.folderNameError['text'] = errMsg

		# close connection to db
		conn.close()

		if (num_errors == 0):
			self.rename_folder(foldname.upper())


	# function to delete folder
	def deletefolder(self):
		foldclick = self.foldername
		answer = tkinter.messagebox.askquestion(foldclick, 'Would you like to delete this folder')
		if answer == 'yes':
			print('we are in')
			# make connection to db
			conn = sqlite3.connect('LockIT.db')
			# add cursor
			c = conn.cursor()

			# return folder id
			c.execute("SELECT folder_Id FROM FOLDER where folder_Name=? AND folder_Type=?", (foldclick, "Media"))
			f = c.fetchone()
			folderId = f[0]

			c.execute("SELECT COUNT(*) FROM MEDIAS WHERE FOLDERID =?", (folderId,))
			med_num = c.fetchone()
			med_num = int(med_num[0])

			if (med_num == 0):
				c.execute("DELETE FROM FOLDER WHERE folder_Name =? and folder_Type=?", (foldclick, "Media"))
			else:
				answer = tkinter.messagebox.askquestion(foldclick,
														"This folder is not empty,all media files will be deleted")
				if (answer == 'yes'):
					c.execute("DELETE FROM MEDIAS WHERE FOLDERID =?", (folderId,))
					c.execute("DELETE FROM FOLDER WHERE folder_Name =? and folder_Type=?", (foldclick, "Media"))

			conn.commit()
		# close database
		conn.close()
		self.clear_media()
		# reload media
		self.loadmedia()
		self.loadfolders()


	# clear input
	def clear_input(self, event):
		self.Input.delete(0, END)


class DocumentPage(Page):
	def __init__(self, *args, **kwargs):
		Page.__init__(self, *args, **kwargs)

		# position the pop up windows in the middle
		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		# images
		path2 = "icons8-document-90.png"
		dropdown = "dropdown.png"
		self.lockitmedia = PhotoImage(file=resource_path(path2))
		self.folder = PhotoImage(file=resource_path("folder.png"))
		self.dropdownicon = PhotoImage(file=resource_path(dropdown))

		self.documentScreen = Frame(self, bg='light grey')
		self.documentScreen.pack(fill="both", expand=True)

		# seperate main window in two frames

		self.buttonframe = tk.Frame(self.documentScreen)
		self.container = tk.Frame(self.documentScreen)
		self.separator = tk.Frame(self.documentScreen, bg="light grey")

		self.buttonframe.pack(side="left", fill="both", expand=False)
		self.separator.pack(side="left", fill="both", expand=False)
		self.container.pack(side="left", fill="both", expand=True)


		# button frame
		space = tk.Label(self.buttonframe, height=1)
		space.pack(side="bottom")



		# container frame
		self.container.columnconfigure(0, weight=1)
		self.container.rowconfigure(0, weight=1)
		self.container.rowconfigure(1, weight=2)
		self.container.rowconfigure(2, weight=1)


		# separate container in 3 frames
		self.header = Frame(self.container)
		self.doc_files = Frame(self.container)
		self.doc_folders = Frame(self.container)

		self.header.grid(row=0, column=0, sticky="nwse")
		self.doc_files.grid(row=1, column=0, sticky="nwse")
		self.doc_folders.grid(row=2, column=0, sticky="nwse")

		# header frame configuration layout
		self.header.rowconfigure(0, weight=1)
		self.header.rowconfigure(1, weight=1)
		self.header.columnconfigure(0, weight=1)
		self.header.columnconfigure(1, weight=1)
		self.header.columnconfigure(2, weight=1)

		# Title page
		self.titleFrame = Frame(self.header)
		self.titleFrame.grid(row=0, column=0, columnspan=3, sticky=(N, S, E, W))
		self.titleFrame.rowconfigure(0, weight=1)
		self.titleFrame.columnconfigure(0, weight=1)
		self.search_bar = tk.Label(self.titleFrame, text="Documents",  font=("Verdana", 15), fg="white",bg="#003152", width=60)
		self.search_bar.grid(column=0, row=0, sticky=(N, S, E, W))

		# navigation header frame
		self.actionframe = Frame(self.header)
		self.actionframe.grid(column=0, row=1, sticky="w")
		self.actionframe.rowconfigure(0, weight=1)
		self.actionframe.columnconfigure(0, weight=1)
		self.actionframe.columnconfigure(1, weight=1)
		self.actionframe.columnconfigure(2, weight=1)

		# media action menu

		self.mb = Label(self.actionframe, text="My Documents", cursor="hand2", image=self.dropdownicon, compound=RIGHT,
						font=("Verdana", 9))
		self.mb.image = self.dropdownicon
		self.mb.bind("<Enter>", self.on_enter)
		self.mb.bind("<Leave>", self.on_leave)
		self.mb.bind('<Button-1>', self.show_menu)
		self.mb.grid(column=0, row=0, sticky='w', padx=5)

		# document files frame - where documents located - configuration layout
		self.doc_files.rowconfigure(0, weight=1)
		self.doc_files.rowconfigure(1, weight=1)
		self.doc_files.rowconfigure(2, weight=10)
		self.doc_files.columnconfigure(0, weight=1)

		# title document files
		self.msTitle = Label(self.doc_files, text="Files", font=("Verdana", 10))
		self.msTitle.grid(column=0, row=0, sticky=(W), padx=5)

		# seperator document files
		self.ms = ttk.Separator(self.doc_files, orient=HORIZONTAL)
		self.ms.grid(column=0, row=1, sticky=(E, W))

		# document folders frame - where folders  located - configuration layout
		self.doc_folders.rowconfigure(0, weight=1)
		self.doc_folders.rowconfigure(1, weight=1)
		self.doc_folders.rowconfigure(2, weight=10)
		self.doc_folders.columnconfigure(0, weight=1)

		# title document folders
		self.fsTitle = Label(self.doc_folders, text="Folders", font=("Verdana", 10))
		self.fsTitle.grid(column=0, row=0, sticky=(W), padx=5)

		# seperator document folders
		self.fs = ttk.Separator(self.doc_folders, orient=HORIZONTAL)
		self.fs.grid(column=0, row=1, sticky=(E, W))

		self.document_labels = {}
		self.folder_labels = {}
		self.folder_id = 0

		self.loaddoc()
		self.loadfolders()

	# drop down menu
	def on_enter(self, event):

		event.widget['background'] = 'gray99'

	def on_leave(self, event):
		event.widget['background'] = 'SystemButtonFace'

	# function to show the menu options
	def show_menu(self, event):

		self.dropmenu = tk.Menu(self.documentScreen, tearoff=0)
		self.dropmenu.add_command(label="Add New File", command=self.addnewdocument)
		self.dropmenu.add_command(label="Add New Folder", command=self.addfolder)
		self.dropmenu.post(event.x_root, event.y_root)

	# function to show add file  menu options
	def show_addfile(self, event):
		self.dropmenuaf = tk.Menu(self.documentScreen, tearoff=0)
		self.dropmenuaf.add_command(label="Add New File", command=self.addnewdocument)
		self.dropmenuaf.post(event.x_root, event.y_root)

	def forgetmenu(self):
		self.mb.destroy()

	def return_home(self, event):
		self.folder_id = 0
		self.forgetmenu()
		self.loadmenu()
		self.clear_doc()
		self.loaddoc()
		self.loadfolders()

	def loadmenu(self, foldername=NONE):

		if (self.folder_id == 0):
			self.myFiles.destroy()
			self.conn.grid_forget()
			self.mb = Label(self.actionframe, text="My Documents", cursor="hand2", image=self.dropdownicon,
							compound=RIGHT, font=("Verdana", 9))
			self.mb.image = self.dropdownicon
			self.mb.bind("<Enter>", self.on_enter)
			self.mb.bind("<Leave>", self.on_leave)
			self.mb.bind('<Button-1>', self.show_menu)
			self.mb.grid(column=0, row=0, sticky='w', padx=5)
		else:

			self.myFiles = Label(self.actionframe, cursor="hand2", text="My Documents", font=("Verdana", 9))
			self.myFiles.image = self.dropdownicon
			self.myFiles.bind("<Enter>", self.on_enter)
			self.myFiles.bind("<Leave>", self.on_leave)
			self.myFiles.bind("<Button-1>", self.return_home)
			self.myFiles.grid(column=0, row=0, sticky='w', padx=5)

			self.conn = Label(self.actionframe, text=" > ", font=("Verdana", 9))
			self.conn.grid(column=1, row=0, sticky='w', padx=5)

			# media action menu
			self.mb = Label(self.actionframe, text=foldername, cursor="hand2", image=self.dropdownicon, compound=RIGHT,
							font=("Verdana", 9))
			self.mb.image = self.dropdownicon
			self.mb.bind("<Enter>", self.on_enter)
			self.mb.bind("<Leave>", self.on_leave)
			self.mb.bind('<Button-1>', self.show_addfile)
			self.mb.grid(column=2, row=0, sticky='w', padx=5)

	def loaddoc(self):

		# content frame - where  document located
		self.content_frame = Frame(self.doc_files, relief="sunken")
		self.content_frame.grid(column=0, row=2, sticky=(N, S, E, W))

		scrollable_body = Scrollable(self.content_frame, width=32)

		# content frame
		for col in range(8):
			self.content_frame.columnconfigure(col, weight=1)
		for row in range(8):
			self.content_frame.rowconfigure(row, weight=1)

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("SELECT * FROM DOCUMENT WHERE FOLDERID=?", (self.folder_id,))
		rows = c.fetchall()
		column = 0
		rowgrid = 0
		for row in rows:

			self.Titles = Label(scrollable_body, text=row[1], cursor="hand2", image=self.lockitmedia, width=100,
								compound=TOP)
			self.document_labels[row[1]] = self.Titles
			self.Titles.bind('<Button-3>', self.popup_file)
			self.Titles.bind('<Double-1>', self.viewdocument)
			self.Titles.image = self.lockitmedia
			self.Titles.grid(row=rowgrid, column=column)

			column = column + 1
			if (column > 8):
				column = 0
				rowgrid = rowgrid + 1

		conn.close()
		scrollable_body.update()

	def loadfolders(self):

		# content frame - where folders located
		self.folder_frame = Frame(self.doc_folders, relief="sunken")
		self.folder_frame.grid(column=0, row=2, sticky=(N, S, E, W))

		scrollable_body = Scrollable(self.folder_frame, width=32)

		# content frame
		for col in range(8):
			self.folder_frame.columnconfigure(col, weight=1)
		for row in range(2):
			self.folder_frame.rowconfigure(row, weight=1)

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("SELECT folder_Name FROM FOLDER where folder_Type=?", ("Document",))
		rows = c.fetchall()
		column = 0
		rowgrid = 0
		for row in rows:

			self.Titles = Label(scrollable_body, text=row[0], cursor="hand2", image=self.folder, width=100,
								compound=TOP)
			self.folder_labels[row[0]] = self.Titles
			self.Titles.bind('<Button-3>', self.popup_folder)
			self.Titles.bind('<Double-1>', self.viewfolder)
			self.Titles.image = self.lockitmedia
			self.Titles.grid(row=rowgrid, column=column, sticky='w')

			column = column + 1
			if (column > 8):
				column = 0
				rowgrid = rowgrid + 1

		conn.close()
		scrollable_body.update()

	def clear_doc(self):

		for key, value in self.document_labels.items():
			self.document_labels[key].destroy()
		for key, value in self.folder_labels.items():
			self.folder_labels[key].destroy()

		self.content_frame.destroy()
		self.folder_frame.destroy()

	# function to add new media file
	def addnewdocument(self):


		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.adddocument = Toplevel()
		self.adddocument.geometry("300x200")
		self.adddocument.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.adddocument.resizable(0, 0)
		self.adddocument.title("Add New Document File")
		self.adddocument.wm_attributes('-topmost', 1)
		self.adddocument.protocol("WM_DELETE_WINDOW", self.closeWindow)



		for row in range(9):
			self.adddocument.rowconfigure(row, weight=1)
		for col in range(3):
			self.adddocument.columnconfigure(col, weight=1)

		# Labels
		# TitleName = Label(self.adddocument, text="Insert File", font=("Verdana", 13))

		self.filepath = Entry(self.adddocument, width=30, fg="black")
		self.filepath.insert(0, "Chosen File")
		self.filename = ""
		self.saveas = Entry(self.adddocument, width=30, fg="black")
		self.saveas.insert(0, "Save as")
		self.saveas.bind("<FocusIn>", self.clear_saveas)
		self.errors = Label(self.adddocument, fg="red", text="", font=("Verdana", 9))

		# Buttons
		Computer = Button(self.adddocument, text="Browse From Computer", font=("Verdana", 13, "italic"),
						  relief="groove",
						  background="light blue", fg="grey", width=18, command=self.OpenFile)


		self.save = Button(self.adddocument, text="Save", font=("Verdana", 13, "italic"), relief="groove",
						   background="light blue", fg="grey", width=18, command=self.savefileDB)

		# Position

		self.filepath.grid(row=2, column=1, sticky="nsew")
		self.saveas.grid(row=3, column=1, sticky="nsew")
		Computer.grid(row=5, column=1, sticky="nsew")
		self.save.grid(row=6, column=1, sticky="nsew")
		self.errors.grid(row=7, column=1, sticky="nsew")

	def closeWindow(self):
		self.adddocument.destroy()
		self.dropmenu.entryconfig("Add New File", state="normal")


	def clear_saveas(self, event):
		self.saveas.delete(0, END)

	def checkIfMatchForCopy(self, entryText, windowObj, file_selected, folder_id):

		# if not matching hash vals, then error
		conn = sqlite3.connect('LockIT.db')
		c = conn.cursor()
		c.execute("SELECT passwordHash FROM LOCKITUSER")
		hashValFromDb = c.fetchone()
		# parse data
		hashVal = str(hashValFromDb[0])
		hashVal = hashVal.replace('b', '', 1)
		hashVal = hashVal.replace("'", '', 2)
		# compare password in db with entry
		# print(hashVal)
		hashVal = hashVal.encode()
		print(hashVal)
		if (bcrypt.checkpw(str(entryText.get()).encode(), hashVal)):
			print("Both Entries Match!")
			c.execute("SELECT DOC, TITLE,TYPE FROM DOCUMENT where TITLE=? and FOLDERID=?", (file_selected, folder_id))

			ablob, name, type = c.fetchone()
			name = name + "." + type

			# True
			file = self.write_file(ablob, name)

			conn.close()
			os.startfile(name)

			windowObj.destroy()
		else:
			print("Entries Do not Match :(")
			# give errror message
			errMsg = "Password entries do not match"
			lbl = Label(windowObj, fg="red", text=errMsg)
			lbl.grid(row=3, column=0,sticky='nsew')
			windowObj.after(5000, lbl.destroy)

	def askForMPForCopy(self, file_selected, folder_id):


		cpWin = tk.Toplevel()
		cpWin.geometry("200x150")
		cpWin.wm_title("LockIT")
		cpWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))

		for r in range(4):
			cpWin.rowconfigure(r,weight=1)
		cpWin.columnconfigure(0, weight=1)

		l = tk.Label(cpWin, text="Please Enter Master Password ",anchor='center')
		l.grid(row=0, column=0,sticky='nswe',padx=5,pady=5)
		e = tk.Entry(cpWin, width=20, show="*")
		e.grid(row=2, column=0,sticky='nswe',padx=5,pady=5)


		b = ttk.Button(cpWin, text="Submit",cursor="hand2", command=lambda: self.checkIfMatchForCopy(e, cpWin, file_selected, folder_id))
		b.grid(row=4, column=0,sticky='e',padx=5,pady=5)
		nb = ttk.Button(cpWin, text="Return",cursor="hand2", command=cpWin.destroy)
		nb.grid(row=4, column=0,sticky='w',padx=5,pady=5)


	# function to view document
	def viewdocument(self, event):

		# simpledialog.askstring("View File", "Master key required")
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		# statements
		c.execute("SELECT EYEICON FROM SETTINGS")
		permission = c.fetchone()

		if (permission[0] == 1):
			file_selected = event.widget['text']
			self.askForMPForCopy(file_selected, self.folder_id)

		else:

			file_selected = event.widget['text']

			# select all
			c.execute("SELECT DOC,TITLE,TYPE FROM DOCUMENT where TITLE=? and FOLDERID=?", (file_selected,self.folder_id))

			ablob,name,type = c.fetchone()
			name = name  + "." + type

			# True
			file = self.write_file(ablob, name)

			os.startfile(name)
			conn.close()


	# function to view folder

	def viewfolder(self, event):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		folderclicked = event.widget['text']
		print(folderclicked)

		# return folder id
		c.execute("SELECT folder_Id FROM FOLDER where folder_Name=? and folder_Type=?", (folderclicked, "Document"))
		f = c.fetchone()
		print(f)
		self.folder_id = f[0]
		conn.close()

		self.forgetmenu()
		self.loadmenu(folderclicked)
		self.clear_doc()
		self.loaddoc()
		self.loadfolders()

	def OpenFile(self):

		self.adddocument.wm_attributes('-topmost', 0)

		self.filename = filedialog.askopenfilename(initialdir="/Documents", title="Select file",
												   filetypes=(("pdf files", "*.pdf*"),("docx files", "*.docx"), ("text files", "*.txt*"),("excel files", "*.xlsx*")))


		self.adddocument.wm_attributes('-topmost', 1)
		name = re.split('/', self.filename)[-1]

		self.filepath.delete(0, END)
		self.filepath.insert(0, name)


	def savefileDB(self):

		if (self.filename == "Chosen File"):
			self.errors['text'] = "Please Choose file"
			self.errors.after(1000, self.clear)

		elif (self.filename == ""):
			self.errors['text'] = "Please Choose file"
			self.errors.after(1000, self.clear)

		else:
			stringafter = re.split('/', self.filename)[-1]
			type = stringafter.split(".")

			document = self.convertToBinaryData(self.filename)
			Getsize = os.stat(self.filename)
			size = self.convert_bytes(Getsize.st_size)
			saveas = self.saveas.get()

			# make connection to db
			conn = sqlite3.connect('LockIT.db')
			# add cursor
			c = conn.cursor()
			c.execute("SELECT COUNT(*) FROM DOCUMENT WHERE TITLE=? AND FOLDERID=?", (saveas, self.folder_id))
			names = c.fetchone()
			unique = int(names[0])

			if (unique >= 1):
				self.errors['text'] = "Name already exists"
				self.saveas.delete(0, END)
				self.errors.after(1000, self.clear)

			elif (len(self.saveas.get()) <= 0):
				self.errors['text'] = "Name required."
				self.saveas.delete(0, END)
				self.errors.after(1000, self.clear)


			else:
				c.execute("INSERT INTO DOCUMENT (ID,TITLE,DOC,SIZE,TYPE,FOLDERID,DATEADDED) VALUES (NULL, ?,?,?,?,?,?)",
						  (saveas, document, size, type[1], self.folder_id, datetime.now()))

				conn.commit()

				conn.close()
				self.adddocument.destroy()
				self.dropmenu.entryconfig("Add New File", state="normal")

				self.clear_doc()
				self.loaddoc()
				self.loadfolders()


	#clear error field
	def clear(self):
		self.errors['text'] = ""

	def convert_bytes(self, num):
		"""
		this function will convert bytes to MB.... GB... etc
		"""
		for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
			if num < 1024.0:
				return "%3.1f %s" % (num, x)
			num /= 1024.0

	def write_file(self, data, filename):
		# Convert binary data to proper format and write it on Hard Disk
		with open(filename, 'wb') as file:
			file.write(data)
		return data

	def convertToBinaryData(self, filename):
		# Convert digital data to binary format
		with open(filename, 'rb') as file:
			binaryData = file.read()
		return binaryData

	def readFile(self, filename):

		f = open(filename, "r")
		text = f.read()
		return text

	# function to show the menu options
	def popup_file(self, event):
		# create a popup menu

		self.filename = event.widget['text']

		self.rename = "Rename file"
		self.send = "Send file"
		self.delete = "Delete file"

		self.aMenuFile = tk.Menu(self.documentScreen, tearoff=0)

		self.aMenuFile.add_command(label=self.rename, command=self.renamedoc)
		self.aMenuFile.add_command(label=self.send, command=lambda: self.senddoc(self.filename))
		self.aMenuFile.add_command(label=self.delete, command=self.deletedoc)

		self.aMenuFile.post(event.x_root, event.y_root)

	# function to show the menu options
	def popup_folder(self, event):
		self.foldername = event.widget['text']
		self.aMenuFolder = tk.Menu(self.documentScreen, tearoff=0)
		self.rename = "Rename folder"
		self.delete = "Delete folder"
		self.aMenuFolder.add_command(label=self.rename, command=self.renamefolder)
		self.aMenuFolder.add_command(label=self.delete, command=self.deletefolder)

		self.aMenuFolder.post(event.x_root, event.y_root)

	def renamedoc(self):

		self.rename = Toplevel()
		self.rename.geometry("300x200")
		self.rename.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.rename.resizable(0, 0)
		self.rename.title("Rename Document")

		path2 = "icons8-document-90.png"
		lockitmedia = PhotoImage(file=resource_path(path2))

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		c.execute("SELECT * FROM DOCUMENT WHERE TITLE=? AND FOLDERID=?", (self.filename, self.folder_id))
		rows = c.fetchone()

		# Labels

		Name = Label(self.rename, text="Name: " + rows[1], font=("Verdana", 8))
		Size = Label(self.rename, text="Size:   " + rows[3], font=("Verdana", 8))
		Type = Label(self.rename, text="Type:  " + rows[4], font=("Verdana", 8))
		Date = Label(self.rename, text="Date:  " + rows[5], font=("Verdana", 8))
		panel2 = Label(self.rename, image=lockitmedia, height=100, width=100)
		panel2.image = lockitmedia
		self.Input = Entry(self.rename, relief="groove")
		self.Input.insert(0, "Enter New Name")
		self.Input.bind("<FocusIn>", self.clear_input)
		self.errors = Label(self.rename, fg="red", text="", font=("Verdana", 9))

		name = self.Input.get()

		# Buttons
		Save = Button(self.rename, text="Save", font=("Arial", 13, "italic"), relief="groove",
					  background="light blue", fg="grey", command=self.setname)

		# Position

		panel2.place(bordermode=INSIDE, y=25)
		Name.place(x=110, y=40)
		Size.place(x=110, y=60)
		Type.place(x=110, y=80)
		Date.place(x=110, y=100)
		self.errors.place(x=110, y=120)
		Save.place(bordermode=INSIDE, y=147, x=13)
		self.Input.place(y=150, x=117, width=148, height=22)

		conn.close()

	def setname(self):

		name = self.Input.get()

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("SELECT COUNT(*) FROM DOCUMENT WHERE TITLE=? AND FOLDERID=?", (name,self.folder_id))
		title = c.fetchone()
		names = int(title[0])
		print(names)

		if (names >= 1):
			self.errors['text'] = "Name already exists."
			self.Input.delete(0, END)
			self.errors.after(1000, self.clear)

		elif (len(self.Input.get()) <= 0):
			self.errors['text'] = "Name required."
			self.Input.delete(0, END)
			self.errors.after(1000, self.clear)

		else:
			c.execute("UPDATE DOCUMENT SET TITLE=? WHERE TITLE=? AND FOLDERID=?", (name, self.filename, self.folder_id))
			print(name)

			conn.commit()
			conn.close()
			self.rename.destroy()

			self.clear_doc()
			self.loaddoc()
			self.loadfolders()

	def sendDocToPc(self, directory_name, fileName):
		print(fileName)
		print(directory_name)
		conn = sqlite3.connect('LockIT.db')
		cursor = conn.cursor()
		# select blob from database where title = filename
		# write the blob to a file in specified directory
		# write the photo to the selected directory

		cursor.execute("SELECT TYPE FROM DOCUMENT WHERE TITLE = ? AND FOLDERID=?", (fileName, self.folder_id))
		t = cursor.fetchone()
		type = t[0]

		extention = "." + type
		with open((directory_name + "/" + fileName + extention), "wb") as output_file:
			cursor.execute("SELECT DOC FROM DOCUMENT WHERE TITLE = ? AND FOLDERID=?", (fileName, self.folder_id))
			ablob = cursor.fetchone()

			output_file.write(ablob[0])
		conn.commit()
		conn.close()
		self.send.destroy()
		spam = fileName + ' is saved in ' + directory_name
		tkinter.messagebox.showinfo(fileName, spam)

	def OpenDir(self, fileName):
		# open the dir and save the dir name
		directory = askdirectory()
		print(directory)
		print(fileName)
		# pass dir name to sendmediatopc
		self.sendDocToPc(directory, fileName)

	# function to send document file
	def senddoc(self, filename):
		self.send = Toplevel()
		self.send.geometry("300x200")
		self.send.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.send.resizable(0, 0)
		self.send.title("Send Document")

		path2 = "icons8-document-90.png"
		lockitmedia = PhotoImage(file=resource_path(path2))

		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		c.execute("SELECT * FROM DOCUMENT WHERE TITLE=? AND FOLDERID=?", (self.filename, self.folder_id))
		rows = c.fetchone()
		conn.close()

		# Labels

		Name = Label(self.send, text="Name: " + rows[1], font=("Verdana", 8))
		Size = Label(self.send, text="Size:   " + rows[3], font=("Verdana", 8))
		Type = Label(self.send, text="Type:  " + rows[4], font=("Verdana", 8))
		Date = Label(self.send, text="Date:  " + rows[5], font=("Verdana", 8))

		panel2 = Label(self.send, image=lockitmedia, height=100, width=100)
		panel2.image = lockitmedia

		# Buttons

		Computer = Button(self.send, text="Computer", font=("Arial", 13, "italic"), relief="groove",
						  background="light blue",
						  fg="grey", command=lambda: self.OpenDir(filename))

		# Position

		panel2.place(bordermode=INSIDE, y=20)
		Name.place(x=110, y=30)
		Size.place(x=110, y=50)
		Type.place(x=110, y=70)
		Date.place(x=110, y=90)

		Computer.place(y=155, x=90)

	# function to delete document file
	def deletedoc(self):

		answer = tkinter.messagebox.askquestion(self.filename, 'Would you like to delete this file')
		if (answer == 'yes'):
			conn = sqlite3.connect('LockIT.db')
			c = conn.cursor()
			c.execute("DELETE FROM DOCUMENT WHERE TITLE=? AND FOLDERID=?", (self.filename, self.folder_id))
			conn.commit()
			# close database
			conn.close()
			# clear media
			self.clear_doc()
			# reload media
			self.loaddoc()
			self.loadfolders()

	# function to add new folder
	def addfolder(self):

		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.addfolderWin = Toplevel()
		self.addfolderWin.geometry("300x200")
		self.addfolderWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.addfolderWin.resizable(0, 0)
		self.addfolderWin.title("Add New Folder")
		self.addfolderWin.wm_attributes('-topmost', 1)

		for row in range(8):
			self.addfolderWin.rowconfigure(row, weight=1)

		self.addfolderWin.columnconfigure(0, weight=1)
		self.addfolderWin.columnconfigure(1, weight=1)

		# Labels
		self.FolderName = Label(self.addfolderWin, text="Folder Name", font=("Verdana", 10))
		self.folderNameError = Label(self.addfolderWin, text="", anchor='e', fg='red')
		self.folderNameError.config(font=("Verdana", 7))

		# Buttons
		self.Save = Button(self.addfolderWin, text="Save", font=("Arial", 13, "italic"), relief="groove",
						   background="light blue", fg="grey", command=self.fold_addvalidate)

		# Inputs
		self.Input = Entry(self.addfolderWin, relief="groove")

		# Position
		self.FolderName.grid(row=2, column=0, sticky="w", padx=5, pady=5)
		self.Input.grid(row=2, column=1, sticky="w")
		self.folderNameError.grid(row=4, column=1, sticky="w")
		self.Save.grid(row=7, column=1, sticky="e", padx=5, pady=5)

	# function to add new folder into DB
	def insert_folder(self, foldname):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("INSERT INTO FOLDER VALUES(NULL,'Document',?,CURRENT_DATE )", (foldname,))
		c.execute("SELECT * FROM FOLDER")
		res = c.fetchall()
		print(res)
		conn.commit()
		# close database
		conn.close()
		self.addfolderWin.destroy()
		self.clear_doc()
		self.loaddoc()
		self.loadfolders()

	# function to validate the entry in add new folder
	def fold_addvalidate(self):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 20

		if (self.folderNameError.cget('text') != ''):
			self.folderNameError['text'] = ''

		# check length of entry
		foldname = self.Input.get()
		en_len = len(str(foldname))

		if (foldname == ""):
			num_errors += 1
			errMsg = "Please enter folder name"
			self.folderNameError['text'] = errMsg

		elif (en_len < min_entry_len):
			num_errors += 1
			errMsg = "Folder must be\n at least 2 characters"
			self.folderNameError['text'] = errMsg

		elif (en_len > max_entry_len):
			num_errors += 1
			errMsg = "Folder can have\n maximum 20 characters."
			self.folderNameError['text'] = errMsg
		else:
			# return folder count from db
			foldname = foldname.upper()
			c.execute("SELECT COUNT(*) FROM FOLDER WHERE folder_Name=? and folder_Type=?", (foldname, 'Document'))
			rec1 = c.fetchone()
			fold_name_occur = int(rec1[0])

			if (fold_name_occur >= 1):
				num_errors += 1
				errMsg = "Folder name is a duplicate\n select a different name"
				self.folderNameError['text'] = errMsg

			# check if it has spaces and alphabetic
			t = foldname.split()
			if len(t) > 1:
				for i in t:
					if (i.isalpha() == FALSE):
						num_errors += 1
						errMsg = "Entry name is not alphbetical"
						self.folderNameError['text'] = errMsg
						break;
			else:
				if (foldname.isalpha() == FALSE):
					num_errors += 1
					errMsg = "Entry name is not alphabetical"
					self.folderNameError['text'] = errMsg

		# close connection to db
		conn.close()

		if (num_errors == 0):
			self.insert_folder(foldname.upper())

	# function to rename folder
	def renamefolder(self):

		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		self.positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
		self.positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)

		self.renamefolderWin = Toplevel()
		self.renamefolderWin.geometry("300x200")
		self.renamefolderWin.geometry("+{}+{}".format(self.positionRight, self.positionDown))
		self.renamefolderWin.resizable(0, 0)
		self.renamefolderWin.title("Rename Folder")
		self.renamefolderWin.wm_attributes('-topmost', 1)

		for row in range(8):
			self.renamefolderWin.rowconfigure(row, weight=1)

			self.renamefolderWin.columnconfigure(0, weight=1)
			self.renamefolderWin.columnconfigure(1, weight=1)

			# Labels
			self.FolderName = Label(self.renamefolderWin, text="Folder Name", font=("Verdana", 10))

			self.folderNameError = Label(self.renamefolderWin, text="", anchor='e', fg='red')
			self.folderNameError.config(font=("Verdana", 7))

			# Buttons
			self.Save = Button(self.renamefolderWin, text="Save", font=("Arial", 13, "italic"), relief="groove",
							   background="light blue", fg="grey", command=self.fold_editvalidate)

			# Inputs
			self.Input = Entry(self.renamefolderWin, relief="groove")
			self.Input.insert(0, "Enter New Name")
			self.Input.bind("<FocusIn>", self.clear_input)

			# Position
			self.FolderName.grid(row=2, column=0, sticky="w", padx=5, pady=5)
			self.Input.grid(row=2, column=1, sticky="w")
			self.folderNameError.grid(row=4, column=1, sticky="w")
			self.Save.grid(row=7, column=1, sticky="e", padx=5, pady=5)

	# function to rename folder
	def rename_folder(self, foldname):
		foldclick = self.foldername
		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()
		c.execute("UPDATE FOLDER SET folder_Name = ? WHERE folder_Name =? ", (foldname, foldclick))
		conn.commit()
		# close database
		conn.close()
		self.renamefolderWin.destroy()
		self.clear_doc()
		self.loaddoc()
		self.loadfolders()

	def fold_editvalidate(self):

		# make connection to db
		conn = sqlite3.connect('LockIT.db')
		# add cursor
		c = conn.cursor()

		num_errors = 0

		# entry name validation
		min_entry_len = 2
		max_entry_len = 20

		if (self.folderNameError.cget('text') != ''):
			self.folderNameError['text'] = ''

		# check length of entry
		foldname = self.Input.get()
		en_len = len(str(foldname))

		if (foldname == ""):
			num_errors += 1
			errMsg = "Please enter folder name"
			self.folderNameError['text'] = errMsg

		elif (en_len < min_entry_len):
			num_errors += 1
			errMsg = "Folder must be\n at least 2 characters"
			self.folderNameError['text'] = errMsg

		elif (en_len > max_entry_len):
			num_errors += 1
			errMsg = "Folder can have\n maximum 20 characters."
			self.folderNameError['text'] = errMsg
		else:
			# return folder count from db
			foldname = foldname.upper()
			c.execute("SELECT COUNT(*) FROM FOLDER WHERE folder_Name=? and folder_Type=?", (foldname, "Document"))
			rec1 = c.fetchone()
			fold_name_occur = int(rec1[0])

			if (fold_name_occur >= 1):
				num_errors += 1
				errMsg = "Folder name is a duplicate\n select a different name"
				self.folderNameError['text'] = errMsg

			# check if it has spaces and alphabetic
			t = foldname.split()
			if len(t) > 1:
				for i in t:
					if (i.isalpha() == FALSE):
						num_errors += 1
						errMsg = "Entry name is not alphbetical"
						self.folderNameError['text'] = errMsg
						break;
			else:
				if (foldname.isalpha() == FALSE):
					num_errors += 1
					errMsg = "Entry name is not alphabetical"
					self.folderNameError['text'] = errMsg

		# close connection to db
		conn.close()

		if (num_errors == 0):
			self.rename_folder(foldname.upper())

	# function to delete folder
	def deletefolder(self):
		foldclick = self.foldername
		answer = tkinter.messagebox.askquestion(foldclick, 'Would you like to delete this folder')
		if answer == 'yes':

			# make connection to db
			conn = sqlite3.connect('LockIT.db')
			# add cursor
			c = conn.cursor()

			# return folder id
			c.execute("SELECT folder_Id FROM FOLDER where folder_Name=? AND folder_Type=?", (foldclick, "Document"))
			f = c.fetchone()
			folderId = f[0]

			c.execute("SELECT COUNT(*) FROM DOCUMENT WHERE FOLDERID =?", (folderId,))
			med_num = c.fetchone()
			med_num = int(med_num[0])

			if (med_num == 0):
				c.execute("DELETE FROM FOLDER WHERE folder_Name =? and folder_Type=?", (foldclick, "Document"))
			else:
				answer = tkinter.messagebox.askquestion(foldclick,
														"This folder is not empty,all document files will be deleted")
				if (answer == 'yes'):
					c.execute("DELETE FROM DOCUMENT WHERE FOLDERID =?", (folderId,))
					c.execute("DELETE FROM FOLDER WHERE folder_Name =? and folder_Type=?", (foldclick, "Document"))

		conn.commit()
		# close database
		conn.close()
		self.clear_doc()
		# reload media
		self.loaddoc()
		self.loadfolders()

	# clear input
	def clear_input(self, event):
		self.Input.delete(0, END)



class Scrollable(ttk.Frame):
	"""
	   Make a frame scrollable with scrollbar on the right.
	   After adding or removing widgets to the scrollable frame,
	   call the update() method to refresh the scrollable area.
	"""

	def __init__(self, frame, width=16):

		scrollbar = tk.Scrollbar(frame, width=width)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

		self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		scrollbar.config(command=self.canvas.yview)

		self.canvas.bind("<Configure>", self.__fill_canvas)

		# base class initialization
		tk.Frame.__init__(self, frame)

		# assign this obj (the inner frame) to the windows item of the canvas
		self.windows_item = self.canvas.create_window(0,0, window=self, anchor=tk.NW)


	def __fill_canvas(self, event):
		"Enlarge the windows item to the canvas width"

		canvas_width = event.width
		self.canvas.itemconfig(self.windows_item, width = canvas_width)

	def update(self):
		"Update the canvas and the scrollregion"

		self.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))

