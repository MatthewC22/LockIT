### This is just a demo of hello world as a .exe in Python 

.exe was made using pyinstaller - https://pyinstaller.readthedocs.io/en/stable/

To get pyinstaller...go to your comamnd prompt or linux terminal and enter the following pip command:
```  
pip install pyinstaller
```
After it has finished installing.. type the following pyinstaller command to test it was installed correct and to get all the different usages of the command.
```
pyinstaller -h
```
Make a hello.cpp file and enter
```python
print("Hello")
input("Please Input ENTER")
```
Save it.. we will finally use pyinstaller to create an exe from this file we created

in the command prompt or terminal in the directory where the file is located.. enter the following pyinstaller command on your file
```
pyinstaller -f hello.py
```
After this you will have a executable file for a  "Hello" program.

Run it to make sure it worked
