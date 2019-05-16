#Author Matthew Clifford
#test pull
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


#create security level table
c.execute("""CREATE TABLE SECURITYLEVEL (
			S_LEVEL_ID INT(1),
			S_LEVEL_NAME VARCHAR(20) NOT NULL UNIQUE,
			S_LEVEL_DESC VARCHAR(100) NOT NULL UNIQUE,
			CONSTRAINT SECURITYLEVEL_SECURITYLEVEL_ID_PK PRIMARY KEY(S_LEVEL_ID)
		)""")

#create color table
c.execute("""CREATE TABLE COLOUR (
COLOUR_ID INT(4),
COLOUR_NAME VARCHAR(20) NOT NULL UNIQUE,
COLOUR_HEX TEXT NOT NULL UNIQUE,
CONSTRAINT COLOUR_COLOUR_ID_PK PRIMARY KEY(COLOUR_ID))""")

# create category table
c.execute("""CREATE TABLE CATEGORY(
CATEGORY_ID INTEGER PRIMARY KEY,
CATEGORY_NAME VARCHAR(35) NOT NULL UNIQUE,
COLOR_ID INT(4) NOT NULL UNIQUE,
USER_ID INT(3) NOT NULL,
CONSTRAINT CATEGORY_COLOR_ID_FK FOREIGN KEY(COLOR_ID)
 REFERENCES COLOR(COLOR_ID),
CONSTRAINT CATEGORY_USER_ID_FK FOREIGN KEY(USER_ID)
 REFERENCES LOCKITUSER(userID))""")

# create password table
c.execute("""CREATE TABLE PASSWORD(
ENTRY_ID INTEGER PRIMARY KEY,
ENTRY_NAME VARCHAR(35) NOT NULL UNIQUE,
WEBSITE VARCHAR(255),
USERNAME VARCHAR(50) NOT NULL,
PASSWORD TEXT NOT NULL,
SECURITY_QUEST TINYINT(1) NOT NULL,
NUM_SECURITY_ANSWER NUMERIC(1),
ANSWER_1 VARCHAR(50),
ANSWER_2 VARCHAR(50),
ANSWER_3 VARCHAR(50),
ANSWER_4 VARCHAR(50),
ANSWER_5 VARCHAR(50),
NOTES TEXT,
CATEGORY INT(2) NOT NULL,
S_LEVEL INT(1) NOT NULL,
DATE_CREATED DATE NOT NULL,
CONSTRAINT PASSWORD_CATEGORY_FK FOREIGN KEY(CATEGORY)
 REFERENCES CATEGORY(CATEGORY_ID),
CONSTRAINT PASSWORD_S_LEVEL_FK FOREIGN KEY(S_LEVEL)
 REFERENCES SECURITYLEVEL(S_LEVEL_ID))""")


# create FOLDER table
c.execute("""CREATE TABLE FOLDER (
			folder_Id INTEGER PRIMARY KEY,
			folder_Type VARCHAR NOT NULL,
			folder_Name VARCHAR NOT NULL,
			creation_Date VARCHAR NOT NULL)""")

# create DOCUMENT table
c.execute("""CREATE TABLE DOCUMENT(
    ID        INTEGER (3) PRIMARY KEY,
    NAME      VARCHAR (50) NOT NULL,
    SIZE      VARCHAR (10),
    TYPE      VARCHAR (5),
    FOLDERID  INT (3),
    USERID    INT (3),
    DATEADDED DATE,
    
    CONSTRAINT DOCUMENT_FOLDERID_FK FOREIGN KEY (
        FOLDERID
    )
    REFERENCES FOLDER (ID),
    CONSTRAINT DOCUMENT_USERID_FK FOREIGN KEY (
        USERID
    )
    REFERENCES LOCKITUSER (USERID))""") 

# create MEDIA table
c.execute("""CREATE TABLE MEDIAS (
    ID        INT (3),
    NAME      VARCHAR (50) NOT NULL,
    SIZE      VARCHAR (10),
    TYPE      VARCHAR (5),
    FOLDERID  INT (3),
    USERID    INT (3),
    DATEADDED DATE,
    CONSTRAINT MEDIA_ID_PK PRIMARY KEY (
        ID
    ),
    CONSTRAINT MEDIA_FOLDERID_FK FOREIGN KEY (
        FOLDERID
    )
    REFERENCES FOLDER (ID),
    CONSTRAINT MEDIA_USERID_FK FOREIGN KEY (
        USERID
    )
    REFERENCES LOCKITUSER (USERID) )""")


#inserts into the LOCKITUSER table
c.execute("INSERT INTO LOCKITUSER VALUES (NULL, 'p4ssw0rd', 'f2613e46853708ad919c9280295eebc25affc15828571b320dc0d04dc0c3ce7ed00b8ea5504302f0334768aeeb3e68dc43c806d96a4070ffa0ea40a9a66d890e','e80e468016854372b63cf540139b57d0')")

#insert into SETTINGS table
c.execute("INSERT INTO SETTINGS VALUES (1, 1, 1,5)")

#insert into  SETTINGS table
#notice that even though settingID is NULL it auto-increments by default
c.execute("INSERT INTO SETTINGS VALUES (NULL, 0, 1, 10)")


#inserts into the COLOURS table 20 colors
c.execute("INSERT INTO COLOUR VALUES(1,'RED','#e6194b')")
c.execute("INSERT INTO COLOUR VALUES(2,'GREEN','#3cb44b')")
c.execute("INSERT INTO COLOUR VALUES(3,'YELLOW','#ffe119')")
c.execute("INSERT INTO COLOUR VALUES(4,'BLUE','#4363d8')")
c.execute("INSERT INTO COLOUR VALUES(5,'ORANGE','#f58231')")
c.execute("INSERT INTO COLOUR VALUES(6,'PURPLE','#911eb4')")
c.execute("INSERT INTO COLOUR VALUES(7,'CYAN','#42d4f4')")
c.execute("INSERT INTO COLOUR VALUES(8,'MAGENTA','#f032e6')")
c.execute("INSERT INTO COLOUR VALUES(9,'LIME','#bfef45')")
c.execute("INSERT INTO COLOUR VALUES(10,'PINK','#fabebe')")
c.execute("INSERT INTO COLOUR VALUES(11,'TEAL','#469990')")
c.execute("INSERT INTO COLOUR VALUES(12,'LAVENDER','#e6beff')")
c.execute("INSERT INTO COLOUR VALUES(13,'BROWN','#9A6324')")
c.execute("INSERT INTO COLOUR VALUES(14,'BEIGE','#fffac8')")
c.execute("INSERT INTO COLOUR VALUES(15,'MAROON','#800000')")
c.execute("INSERT INTO COLOUR VALUES(16,'MINT','#aaffc3')")
c.execute("INSERT INTO COLOUR VALUES(17,'OLIVE','#808000')")
c.execute("INSERT INTO COLOUR VALUES(18,'APRICOT','#ffd8b1')")
c.execute("INSERT INTO COLOUR VALUES(19,'NAVY','#000075')")
c.execute("INSERT INTO COLOUR VALUES(20,'GREY','#a9a9a9')")

#inserts into the SECURITYLEVEL table 4 levels
c.execute("INSERT INTO SECURITYLEVEL VALUES(1,'not secure','not generating security timer in the system')")
c.execute("INSERT INTO SECURITYLEVEL VALUES(2,'low', 'generating security timer to 6 months in the system')")
c.execute("INSERT INTO SECURITYLEVEL VALUES(3, 'medium', 'generating security timer to 3 months in the system')")
c.execute("INSERT INTO SECURITYLEVEL VALUES(4,'high', 'generating security timer to 1 month in the system')")

#inserts into the CATEGORY table 3 predefined categories
c.execute("INSERT INTO CATEGORY VALUES(NULL,'SCHOOL',1,1)")
c.execute("INSERT INTO CATEGORY VALUES(NULL,'HOME',2,1)")
c.execute("INSERT INTO CATEGORY VALUES(NULL,'WORK',3,1)")


# inserts into the PASSWORD table
c.execute("INSERT INTO PASSWORD VALUES(NULL,'BLUE HOST','','DREAMTRIM',76543,1,5,'CHINA','ICE CREAM','PIZZA','ALISA','APPLE','TESTING NOTES',1,3,CURRENT_DATE)")

c.execute("INSERT INTO PASSWORD VALUES(NULL,'SENECA','https://my.senecacollege.ca','EGRINBERG',88765,0,0,'','','','','','',1,2,CURRENT_DATE)")

# inserts into the Folder table
c.execute("INSERT INTO FOLDER VALUES (007, 'Pictures', 'Office', CURRENT_DATE )")



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
