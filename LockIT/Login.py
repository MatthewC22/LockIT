# Author Matthew Clifford
# Login Page
# you must install bcrypt module to run this code: pip install bcrypt

from tkinter import *
from tkinter import ttk
import sqlite3
import os
import webbrowser
import bcrypt
import Mainpage

cwd = os.getcwd()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class loginScreen:

    def showLoginScreen():
        global root
        root = Tk()
        root.title("LockIT 1.0")
        root.geometry("710x500")
        root.configure(background='#003152')

        windowWidth = root.winfo_reqwidth()
        windowHeight = root.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(root.winfo_screenwidth() / 4 - windowWidth / 2)
        positionDown = int(root.winfo_screenheight() / 4 - windowHeight / 2)

        # Positions the window in the center of the page.
        root.geometry("+{}+{}".format(positionRight, positionDown))

        ls = loginScreen(root)
        root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=resource_path('icon/favicon.png')))
        root.mainloop()

    def trimData(self, dataToTrim):
        Str1 = str(dataToTrim)
        Str2 = Str1.replace('(', '')
        Str3 = Str2.replace(')', '')
        Str4 = Str3.replace(',', '')
        Str5 = Str4.replace("'", '')
        dataTrimmed = Str5
        return dataTrimmed

    def checkIfPassMatch(self, event=None):
        conn = sqlite3.connect('LockIT.db')
        c = conn.cursor()
        c.execute("SELECT passwordHash FROM LOCKITUSER")
        hashValFromDb = c.fetchone()
        conn.close()
        # parse data
        hashVal = self.trimData(hashValFromDb)
        hashVal = hashVal.replace('b', '', 1)
        # compare password in db with entry
        print(hashVal)
        hashVal = hashVal.encode()
        print(hashVal)
        if (bcrypt.checkpw(str(self.enterMasterKey.get()).encode(), hashVal)):
            print("Both Entries Match!")
            root.MasterKey = self.enterMasterKey.get()
            root.destroy()
            Mainpage.showWindow()
        else:
            print("Entries Do not Match :(")
            errMsg = "Password entries do not match"
            self.errorMessage(errMsg)

    # Redirects to github project
    def onIconClick(self, event):
        url = 'https://github.com/MatthewC22/LockIT/tree/master'
        webbrowser.open(url)  # go to project on github

    # produces error message on screen
    def errorMessage(self, err):
        lbl = Label(root, fg="red", text=err, background='#003152')
        lbl.grid(row=3, column=1)
        root.after(1000, lbl.destroy)

    def getHintFromDB(self):
        # connects to and creates db if none exists
        conn = sqlite3.connect('LockIT.db')
        c = conn.cursor()
        c.execute("SELECT hint FROM LOCKITUSER")
        h = c.fetchone()
        conn.close()
        self.hint = self.trimData(h)

    def __init__(self, master):

        self.getHintFromDB()
        root.MasterKey = ""

        # LOCKIT title
        # titleLabel = Label(root, text="LOCKIT")
        # titleLabel.config(font=("Courier",35))
        # titleLabel.grid(row=0, column=0)

        # PATH title
        titleLabel = Label(root, text="Please Enter Password for Database.db", background='#003152', fg="white")
        titleLabel.config(font=("Courier", 11, 'bold', 'underline'))
        titleLabel.grid(row=1, column=1)

        # lock icon
        imgPath = resource_path('LockItLogoSmall.png')
        self.imageIcon = PhotoImage(file=imgPath)
        w1 = Label(root, image=self.imageIcon)
        w1.grid(row=0, column=1)

        # github icon
        githubImgPath = resource_path('github.gif')
        self.gitIcon = PhotoImage(file=githubImgPath)
        w2 = Label(root, image=self.gitIcon, cursor='hand2')
        w2.bind('<Button-1>', self.onIconClick)
        w2.grid(row=9, column=0)
        gitLabel1 = Label(root, text="\nOur Software is Open Source", font=("Verdana", 5), background='#003152',
                          fg="white")
        gitLabel1.grid(row=10, column=0)
        gitLabel2 = Label(root, text="Click to view the Code on Github\n", font=("Verdana", 5), background='#003152',
                          fg="white")
        gitLabel2.grid(row=11, column=0)

        # ok button
        loginButton = Button(root, text='Login', width=20, height=3, cursor='hand2', command=self.checkIfPassMatch,
                             font=("Courier", 8, "bold"), relief="groove")
        loginButton.grid(row=8, column=1)

        # cancel button
        # helpButton = Button(root, text='Cancel',width=20,height=3,cursor='hand2')
        # helpButton.grid(row=6,column=1)

        # Masterkey Registration entry
        enterMasterKeyLabel = Label(root, text="Enter Master Password", background='#003152', fg="white")
        enterMasterKeyLabel.config(font=("Courier", 11))
        enterMasterKeyLabel.grid(row=3, column=0)
        self.enterMasterKey = Entry(root, show="*")
        self.enterMasterKey.bind('<Return>', self.checkIfPassMatch)
        self.enterMasterKey.grid(row=3, column=1)

        # Hint
        hintLabel = Label(root, text="Hint: ", background='#003152', fg="white")
        hintLabel.config(font=("Courier", 11))
        hintLabel.grid(row=4, column=0)
        hintText = Label(root, text=self.hint, background='#003152', fg="white")
        hintText.config(font=("Courier", 11))
        hintText.grid(row=4, column=1)

    def getMasterKey(self):
        return root.MasterKey