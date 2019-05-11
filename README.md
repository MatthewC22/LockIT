# LockIt Database / SETTINGS , LOCKITUSER tables

```python

#Author Matthew Clifford

import sqlite3

#make empployee.db
conn = sqlite3.connect('LockIT.db')

#add cursor to do sql statements
c =  conn.cursor()

#create settings table
c.execute("""CREATE TABLE SETTINGS (
			settingID INTEGER PRIMARY KEY,
			eyeIcon INTEGER NOT NULL,
			copyIcon INTEGER NOT NULL,
			timer INTEGER NOT NULL
		)""")

#create lockituser table
c.execute("""CREATE TABLE LOCKITUSER (
			userID INTEGER PRIMARY KEY,
			hint TEXT NOT NULL,
			passwordHash TEXT NOT NULL,
			salt TEXT NOT NULL
		)""")


#inserts into the LOCKITUSER table
c.execute("INSERT INTO LOCKITUSER VALUES (NULL, 'p4ssw0rd', 'f2613e46853708ad919c9280295eebc25affc15828571b320dc0d04dc0c3ce7ed00b8ea5504302f0334768aeeb3e68dc43c806d96a4070ffa0ea40a9a66d890e','e80e468016854372b63cf540139b57d0')")

#insert into SETTINGS table
c.execute("INSERT INTO SETTINGS VALUES (1, 1, 1,5)")

#insert into  SETTINGS table
#notice that even though settingID is NULL it auto-increments by default
c.execute("INSERT INTO SETTINGS VALUES (NULL, 0, 1, 10)")

#select all settings
c.execute("SELECT * FROM SETTINGS")
rows = c.fetchall()
for row in rows:
	print(row)

#select all lockituser
c.execute("SELECT * FROM LOCKITUSER")
rows = c.fetchall()
for row in rows:
	print(row)

#shows all existing tables in database
#c.execute("SELECT name FROM sqlite_master WHERE type='table';")
#print(c.fetchall())
#c.close()

#shows the structure of a table
#c.execute("SELECT sql FROM sqlite_master WHERE name='LOCKITUSER'")
#print(c.fetchall())
#c.close()

#save changes made
conn.commit()

#close database
conn.close()

#drop tables
#c.execute("DROP TABLE SETTINGS")
#c.execute("DROP TABLE LOCKITUSER")


```
