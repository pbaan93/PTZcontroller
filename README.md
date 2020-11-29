# PTZcontroller
PTZ optics camera controller en preset viewer

make the program into an .exe with: "pyinstaller PTZcontroller.py --onefile"

### ToDo:
- add in screen numbers to the previews, 1-16
- make a nice PTZ optics API class
- add gamepad controll
- add a PTZ simulation API for better testing
- make number of presets and cams variable
- make everyting resizable (fullscreen)

### notes:
- the PTZ snapshot API has an issues, becomes unresponsive when zoomed in realy far
- kept PTZ recall API call separate from this program to still be able to continue using the PTZ during a livestream without this program

### API list:
Postman: https://www.getpostman.com/collections/d09ed401964fd131d828

- http://localhost:8000/api/preset/set?cam=(cam-number)&preset=(preset-number)
- http://localhost:8000/api/preset/save?cam=(cam-number)&preset=(preset-number)
- http://localhost:8000/api/cam/set?cam=(cam-number)
- http://localhost:8000/api/preview-to-program