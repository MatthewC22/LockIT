#!/usr/bin/python

from tkinter import *
import sqlite3
import os
from tkinter import font




#def storeInitialSecurity():
#	import Mainpage
#	root.destroy()  # This will destroy the signup window. :)
#	Mainpage.showWindow()
	
def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)

class NoDataFoundError(Exception):
	pass

class InitialSettingScreen:
	#shows security setting window
	def showWindow():
		global root
		root = Tk()
		root.title("Initial Security Settings")
		root.geometry("1000x700")
		root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=resource_path('icon/favicon.png')))
		windowWidth = root.winfo_reqwidth()
		windowHeight = root.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		positionRight = int(root.winfo_screenwidth() / 4 - windowWidth / 2)
		positionDown = int(root.winfo_screenheight() / 4 - windowHeight / 2)

		# Positions the window in the center of the page.
		root.geometry("+{}+{}".format(positionRight, positionDown))

		root.resizable(0, 0)
		#connects to and creates db if none exists
		conn = sqlite3.connect('LockIT.db')
		#add cursor
		c =  conn.cursor()
		try:
			c.execute("SELECT * FROM SETTINGS")
			row = c.fetchone()
			if 	row:#data exists
				print(row)
				#switch to login page if no exception raised
				import Login
				root.destroy()
				Login.loginScreen.showLoginScreen()
				#import Mainpage
				#root.destroy()
				#Mainpage.showWindow()

			else: #no data
				raise NoDataFoundError

		except sqlite3.OperationalError:
			print("No settings table so go to initial settings page")
			initialSecurity = InitialSettingScreen(root)
			root.mainloop()
		except NoDataFoundError: #no data in table 
			print("No data in settings table so go to initial settings page")
			initialSecurity = InitialSettingScreen(root)
			root.mainloop()

	#switches screen to mainpage
	def switchToMainPage(self):
		import Mainpage
		root.destroy()  # This will destroy the settings window. :)
		Mainpage.showWindow()
	
	#stores initial security settings to db
	def saveInitialSecurity(self):
		#make connection to db
		conn = sqlite3.connect('LockIT.db')
		
		#add cursor
		c =  conn.cursor()

		#create table
		c.execute("""CREATE TABLE IF NOT EXISTS SETTINGS (
						settingID INTEGER PRIMARY KEY,
						eyeIcon INTEGER NOT NULL,
						copyIcon INTEGER NOT NULL,
						timer INTEGER NOT NULL,
						minutes INTEGER NOT NULL
						)""")     

		
		c.execute("""SELECT *
					FROM SETTINGS
			""")

		
		cur = c.fetchall()
		
		i=0

		for row in cur:
			i = i + 1;

		print("count is " + str(i))

		#no rows
		if (i <= 0):
			#insert(s)
			if (self.timerSetting == 1):
				self.minutesSetting = self.timer.get()
			else:
				self.minutesSetting = 0

			print('timer minutes = ' + str(self.minutesSetting))

			c.execute("INSERT INTO SETTINGS (settingID, eyeIcon, copyIcon, timer,minutes) VALUES (NULL,?,?,?,?)",
						(self.eyeSetting, self.copySetting, self.timerSetting, self.minutesSetting))
		
		#select all
		c.execute("SELECT * FROM SETTINGS")
		rows = c.fetchall()
		for row in rows:
			print(row)

		#save changes made
		conn.commit()
		
		#close connection to db
		conn.close()

		#switch to Login page
		import Login
		root.destroy()
		Login.loginScreen.showLoginScreen()
		#import Mainpage
		#root.destroy()  # This will destroy the signup window. :)
		#Mainpage.showWindow()

	
	def __init__(self, master):
		#all settings off initially
		self.eyeSetting = 0
		self.copySetting = 0
		self.timerSetting = 0
		self.minutesSetting = 0

		self.logoframe = Frame(root)
		self.logoframe.columnconfigure(0, weight=1)

		self.content = Frame(root)

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
		self.viewData_btn = Button(self.content,text="Off", width=20, cursor="hand2", command=self.toggle)
		self.copyData = Label(self.content, text="Enables access to Copy Password with Master Password")
		self.copyData_btn = Button(self.content,text="Off", width=20, cursor="hand2", command=self.toggle1)

		self.logout_section = Label(self.content, text="Enable Automatic Logout", font=("VerdanaBold", 12))
		# font.Font instead of tkFont.Fon
		f = font.Font(self.logout_section, self.logout_section.cget("font"))
		f.configure(underline=True)
		self.logout_section.configure(font=f)

		self.logout = Label(self.content,
							text="Enables automatic logout of the software after a certain amount of inactivity")
		self.logout_btn = Button(self.content,width=20,text="Off", cursor="hand2", command=self.toggle2)
		self.timer_label = Label(self.content, text="Set number of minute for automatic logout")
		self.timer = Spinbox(self.content, from_=1, to=10)

		self.save = Button(self.content, text="Save",width=20, height=3, command=self.saveInitialSecurity,
						   cursor="hand2")  # root.destroys itself and updates db


		self.logo.grid(row=0, column=0, sticky="s")
		self.master_access.grid(row=0, column=1, sticky="nsew")
		self.viewData.grid(row=1, column=1, sticky="w")
		self.viewData_btn.grid(row=1, column=2, sticky="w")
		self.copyData.grid(row=2, column=1, sticky="w")
		self.copyData_btn.grid(row=2, column=2, sticky="w")
		self.logout_section.grid(row=3, column=1, sticky="nsew")
		self.logout.grid(row=4, column=1, sticky="w")
		self.logout_btn.grid(row=4, column=2, sticky="w")

		self.save.grid(row=6, column=2, sticky="w", padx=5, pady=5)



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

