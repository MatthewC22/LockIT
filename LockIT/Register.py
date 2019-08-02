# Author Matthew Clifford
# Setup Masterkey Page (Register)
# you must install bcrypt module to run this code: pip install bcrypt

from tkinter import *
from tkinter import ttk
import os
import webbrowser
import hashlib
import uuid
import bcrypt
import re
import sqlite3
import InitialSettings
import Database

cwd = os.getcwd()


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


# registerScreen class
class registerScreen:

    # Redirects to github project
    def onIconClick(self, event):
        url = 'https://github.com/MatthewC22/LockIT/tree/master'
        webbrowser.open(url)  # go to project on github

    # redirects user to info on how to register
    def displayHelpInfo(self):
        url = 'https://github.com/MatthewC22/LockIT/blob/help/README.md'
        webbrowser.open(url)  # go to LockIT help page

    def switchToInitSecurityPage(self):
        # switch initial security settings page
        import InitialSettings
        root.destroy()
        InitialSettings.InitialSettingScreen.showWindow()

    # saves the Record into LockIT.db
    def saveRecordToDb(self, hashedPw, hintEntry):

        # load database
        Database.load_database()

        # make connection to db
        conn = sqlite3.connect('LockIT.db')
        # add cursor
        c = conn.cursor()

        # insert(s)
        c.execute("INSERT INTO LOCKITUSER (userID,hint,passwordHash) VALUES (NULL, ?,?)",
                  (hintEntry, hashedPw))

        # select all
        c.execute("SELECT * FROM LOCKITUSER")
        rows = c.fetchall()
        for row in rows:
            print(row)

        # save changes made
        conn.commit()
        # close connection to db
        conn.close()

        # switch to initial security page
        self.switchToInitSecurityPage()

    # checks if the entry 1 and entry 2 are same
    def checkMkEntriesMatch(self):
        # convert entry1 to hashVal
        hashed = bcrypt.hashpw(str(self.entry1.get()).encode(), bcrypt.gensalt())
        # compare hashed with 2nd entry
        if (bcrypt.checkpw(str(self.entry2.get()).encode(), hashed)):
            # If they the same store the record into the db
            print("Both Entries Match!")
            # self.saveRecordToDb(hashed, str(self.hintEntry.get()))
            self.checkForMkSameAsHint(hashed)
        else:
            # error message to user (red highlighted)
            print("Entries Do not Match :(")
            errMsg = "Password entries do not match"
            self.errorMessage(errMsg)

    # produces error message on screen
    def errorMessage(self, err):
        lbl = Label(root, fg="red", text=err)
        lbl.grid(row=0, column=1)
        root.after(5000, lbl.destroy)

    # checks if the entry contains any special characters
    def checkMkForOneSpecialChar(self):
        # pattern for special chars
        regex = re.compile('[@_!#$%^&+,;=*()<>?/\\\\|}{\\[\\]~:-]')
        # searches the pattern
        if (regex.search(str(self.entry1.get())) == None):
            print("Special Char Test FAILED")  # error messagebox
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

        for l in str(self.entry1.get()):
            try:
                l = int(l)
                digit += 1
            except ValueError:
                pass  # it was string, not int.

        # next complexity test for special chars
        if (digit > 0):
            print("One number test PASSED")
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

        # parse string and count if upper,lower,space
        for l in str(self.entry1.get()):
            if (l.isupper()):
                upper += 1
            elif (l.islower()):
                lower += 1
            elif (l.isspace()):
                space += 1

        if (upper > 0 and lower > 0):
            print("Upper Case & Lower Case Test PASSED")
            # next complexity test
            self.checkMkForOneNumber()
        else:  # error
            print("Upper Case & Lower Case Test FAILED")
            errMsg = "Password must contain atleast one uppercase and one lowercase character"
            self.errorMessage(errMsg)

    def checkForMkSameAsHint(self, hashed):
        hint = self.hintEntry.get()
        mk = self.entry1.get()
        print(hint, mk)
        if (str(hint) == str(mk)):
            print("Hint and password Test FAILED")
            errMsg = "hint and password canot be the same"
            self.errorMessage(errMsg)
        # raise error
        else:
            self.saveRecordToDb(hashed, str(self.hintEntry.get()))

    # checks if password is of minimum length
    def checkMkEntryLength(self):
        minimum_password_length = 8
        # check length of entry
        pwLen = len(str(self.entry1.get()))
        if (pwLen >= minimum_password_length):
            print("Password Length Test PASSED")
            # next complexity test
            self.checkMkUpperAndLowerChars()
        else:
            # error messages
            print("Password Length Test FAILED")
            errMsg = "Password must contain atleast 8 characters"
            self.errorMessage(errMsg)

    def showRegisterWindow():
        # main program
        global root
        root = Tk()
        root.title("LockIT 1.0")
        root.geometry("1000x700")

        windowWidth = root.winfo_reqwidth()
        windowHeight = root.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(root.winfo_screenwidth() / 4 - windowWidth / 2)
        positionDown = int(root.winfo_screenheight() / 4 - windowHeight / 2)

        # Positions the window in the center of the page.
        root.geometry("+{}+{}".format(positionRight, positionDown))

        # connects to and creates db if none exists
        conn = sqlite3.connect('LockIT.db')
        # add cursor
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM LOCKITUSER")
            row = c.fetchone()
            if row:
                print(row)
                # switch to login page here if no exception raised
                # put here for testing (no login page functionaltiy as of right now)
                import InitialSettings
                root.destroy()
                InitialSettings.InitialSettingScreen.showWindow()

            else:
                raise NoDataFoundError

        except sqlite3.OperationalError:  # no table exists
            print("No lockituser table so go to register page")
            rs = registerScreen(root)
            root.mainloop()

        except NoDataFoundError:  # no data in table
            print("No data found in cursor, so go to register")
            rs = registerScreen(root)
            root.mainloop()

    def __init__(self, master):
        root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=resource_path('icon/favicon.png')))
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=4)

        # divide frame into 2 frames
        self.logoframe = Frame(root)
        self.contentframe = Frame(root)

        self.logoframe.grid(row=0, column=0, sticky="nsew")
        self.contentframe.grid(row=0, column=1, sticky="nsew")

        ##logoframe
        for row in range(5):
            self.logoframe.rowconfigure(row, weight=1)

        # LOCKIT title
        # logo
        path = resource_path('LockItLogoSmall.PNG')
        self.lockitlogo = PhotoImage(file=path)
        self.logo = Label(self.logoframe, image=self.lockitlogo)
        self.logo.image = self.lockitlogo
        # self.titleLabel = Label(self.logoframe, text="LOCKIT")
        # self.titleLabel.config(font=("Verdana",35))
        self.logo.grid(row=0, column=0)

        # github icon
        self.githubImgPath = resource_path('github.gif')
        self.gitIcon = PhotoImage(file=self.githubImgPath)
        self.w2 = Label(self.logoframe, image=self.gitIcon, cursor='hand2')
        self.w2.bind('<Button-1>', self.onIconClick)
        self.w2.grid(row=5, column=0)

        self.gitLabel1 = Label(self.logoframe, text="\nOur Software is Open Source")
        self.gitLabel1.grid(row=6, column=0)

        self.gitLabel2 = Label(self.logoframe, text="Click to view the Code on Github\n")
        self.gitLabel2.grid(row=7, column=0)

        # contentframe
        for row in range(8):
            self.contentframe.rowconfigure(row, weight=1)

        # prompt
        self.instructLabel = Label(self.contentframe, text="Setup Master Key\n")
        self.instructLabel.config(font=("Verdana", 12, 'bold', 'underline'))
        self.instructLabel.grid(row=0, column=0)

        # lock icon
        self.imgPath = resource_path('lock2.gif')
        self.imageIcon = PhotoImage(file=self.imgPath)
        self.w1 = Label(self.contentframe, image=self.imageIcon)
        self.w1.grid(row=0, column=1)

        # setup label & entry
        self.masterKeyLabel = Label(self.contentframe, text="Setup Master Password: ")
        self.masterKeyLabel.config(font=("Verdana", 11))
        self.masterKeyLabel.grid(row=1, column=0)
        self.entry1 = Entry(self.contentframe, show="*")
        self.entry1.grid(row=1, column=1)

        # repeat entry
        self.repeatLabel = Label(self.contentframe, text="Confirm Master Password: ")
        self.repeatLabel.config(font=("Verdana", 11))
        self.repeatLabel.grid(row=2, column=0)
        self.entry2 = Entry(self.contentframe, show="*")
        self.entry2.grid(row=2, column=1)

        # hint field
        self.hintSetupLabel = Label(self.contentframe, text="Setup Optional Hint")
        self.hintSetupLabel.config(font=("Verdana", 12, 'bold', 'underline'))
        self.hintSetupLabel.grid(row=4, column=0)
        self.hintLabel = Label(self.contentframe, text="Hint")
        self.hintLabel.config(font=("Verdana", 11))
        self.hintLabel.grid(row=5, column=0)
        self.hintEntry = Entry(self.contentframe)
        self.hintEntry.grid(row=5, column=1)

        # ok button
        self.okButton = Button(self.contentframe, text='Setup Key', width=20, height=3, cursor='hand2',
                               command=self.checkMkEntryLength)
        self.okButton.grid(row=6, column=0)

        # help button
        self.helpButton = Button(self.contentframe, text='Help', width=20, height=3, cursor='hand2',
                                 command=self.displayHelpInfo)
        self.helpButton.grid(row=6, column=1)





