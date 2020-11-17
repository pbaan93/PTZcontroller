# PTZcontroller
PTZ optics camera controller en preset viewer

make the program into an .exe with: "pyinstaller PTZcontroller.py --onefile"

### ToDo:
- add in screen numbers to the previews, 1-16
- make a nice PTZ optics API class
- take some parts from the main file and put them in a saparate module
- add gamepad controll
- add a PTZ simulation API for better testing

### notes:
- the PTZ snapshot API has some issues, could become unresponsive after a couple calls

### API list:
- http://localhost:8000/api/preset/set?cam=<cam-number>&preset=<preset-number>
- http://localhost:8000/api/preset/save?cam=<cam-number>&preset=<preset-number>
- http://localhost:8000/api/cam/set?cam=<cam-number>
- http://localhost:8000/api/preview-to-programm


