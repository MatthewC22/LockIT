#delete tables script

import sqlite3

#make empployee.db
conn = sqlite3.connect('LockIT.db')

#add cursor to do sql statements
c =  conn.cursor()

#drop tables
c.execute("DROP TABLE SETTINGS")
c.execute("DROP TABLE LOCKITUSER")
c.execute("DROP TABLE SECURITYLEVEL")
c.execute("DROP TABLE CATEGORY")
c.execute("DROP TABLE PASSWORD")
c.execute("DROP TABLE FOLDER")
c.execute("DROP TABLE DOCUMENT")
c.execute("DROP TABLE MEDIAS")

#save changes made
conn.commit()

#close database
conn.close()
