import sqlite3




def load_database():

	# make empployee.db
	conn = sqlite3.connect('LockIT.db')

	# add cursor to do sql statements
	c = conn.cursor()

	# create settings table
	c.execute("""CREATE TABLE IF NOT EXISTS SETTINGS (
				settingID INTEGER PRIMARY KEY,
				eyeIcon INTEGER NOT NULL,
				copyIcon INTEGER NOT NULL,
				timer INTEGER NOT NULL,
				minutes INTEGER NOT NULL
			)""")

	# create lockituser table
	c.execute("""CREATE TABLE IF NOT EXISTS LOCKITUSER (
				userID INTEGER PRIMARY KEY,
				hint TEXT NOT NULL,
				passwordHash TEXT NOT NULL)""")

	# create security level table
	c.execute("""CREATE TABLE IF NOT EXISTS SECURITYLEVEL (
				S_LEVEL_ID INT(1),
				S_LEVEL_NAME VARCHAR(20) NOT NULL UNIQUE,
				S_LEVEL_DESC VARCHAR(100) NOT NULL UNIQUE,
				CONSTRAINT SECURITYLEVEL_SECURITYLEVEL_ID_PK PRIMARY KEY(S_LEVEL_ID)
			)""")

	# create category table
	c.execute("""CREATE TABLE IF NOT EXISTS CATEGORY(
	CATEGORY_ID INTEGER PRIMARY KEY,
	CATEGORY_NAME VARCHAR(35) NOT NULL UNIQUE,
	COLOUR_HEX TEXT NOT NULL UNIQUE)""")

	# create password table
	c.execute("""CREATE TABLE IF NOT EXISTS PASSWORD(
	ENTRY_ID INTEGER PRIMARY KEY,
	ENTRY_NAME VARCHAR(35) NOT NULL,
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
	PASS_KEY TEXT NOT NULL,
	CONSTRAINT PASSWORD_CATEGORY_FK FOREIGN KEY(CATEGORY)
	 REFERENCES CATEGORY(CATEGORY_ID),
	CONSTRAINT PASSWORD_S_LEVEL_FK FOREIGN KEY(S_LEVEL)
	 REFERENCES SECURITYLEVEL(S_LEVEL_ID))""")

	# create FOLDER table
	c.execute("""CREATE TABLE IF NOT EXISTS FOLDER (
				folder_Id INTEGER PRIMARY KEY,
				folder_Type VARCHAR NOT NULL,
				folder_Name VARCHAR NOT NULL,
				creation_Date VARCHAR NOT NULL)""")

	# create DOCUMENT table
	c.execute("""CREATE TABLE IF NOT EXISTS DOCUMENT(
		ID        INTEGER PRIMARY KEY,
		TITLE     TEXT NOT NULL,
		DOC       BLOB NOT NULL,
		SIZE      TEXT NOT NULL,
		TYPE      INT NOT NULL,
		DATEADDED DATE,
		FOLDERID  INT (3),
		CONSTRAINT DOCUMENT_FOLDERID_FK FOREIGN KEY (
			FOLDERID
		)REFERENCES FOLDER (ID))""")

	# create MEDIA table
	c.execute("""CREATE TABLE IF NOT EXISTS MEDIAS (
		ID        INTEGER PRIMARY KEY,
		TITLE     TEXT NOT NULL,
		MEDIA     BLOB NOT NULL,
		SIZE      TEXT NOT NULL,
		TYPE      INT NOT NULL,
		DATEADDED DATE NOT NULL,
		FOLDERID  INT (3),		
		CONSTRAINT MEDIA_FOLDERID_FK FOREIGN KEY (
			FOLDERID
		)REFERENCES FOLDER (ID))""")

	#inserts into the SECURITYLEVEL table 4 levels
	c.execute("INSERT INTO SECURITYLEVEL VALUES(1,'not secure','not generating security timer in the system')")
	c.execute("INSERT INTO SECURITYLEVEL VALUES(2,'low', 'generating security timer to 6 months in the system')")
	c.execute("INSERT INTO SECURITYLEVEL VALUES(3, 'medium', 'generating security timer to 3 months in the system')")
	c.execute("INSERT INTO SECURITYLEVEL VALUES(4,'high', 'generating security timer to 1 month in the system')")

	#inserts into the CATEGORY table 3 predefined categories
	c.execute("INSERT INTO CATEGORY VALUES(NULL,'SCHOOL','#ff6464')")
	c.execute("INSERT INTO CATEGORY VALUES(NULL,'HOME','#00bf00')")
	c.execute("INSERT INTO CATEGORY VALUES(NULL,'WORK','#5353ff')")




	# #select all lockituser
	c.execute("SELECT * FROM SETTINGS")
	rows = c.fetchall()
	for row in rows:
		print(row)



	#save changes made
	conn.commit()

	#close database
	conn.close()

