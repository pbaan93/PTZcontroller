from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import os, math
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib
import requests # to get image from the web
import shutil # to save it locally

from dotenv import load_dotenv
load_dotenv()
PTZ_1_IP = os.getenv('PTZ_1_IP')
PTZ_2_IP = os.getenv('PTZ_2_IP')
PTZ_3_IP = os.getenv('PTZ_3_IP')
# print(PTZ_1_IP)
# print(PTZ_2_IP)
# print(PTZ_3_IP)

photoSize = (120, 80)
#photoSize = (277, 173)

previewCam = 0
liveCam = 0

root = Tk()
root.title("PTZ controller")
root.geometry(str((photoSize[0]*4)+10)+"x"+str(3*((photoSize[1]*4)+10))+"+300+150")
root.resizable(width=False, height=False)

class presetImageWatcher:
    def __init__(self, positionNr, camNr):
        self.camNr = camNr
        self._cached_stamp = 0
        self.nr = positionNr
        self.filename = "previews"+str(self.camNr)+"/"+str(positionNr)+".jpg"

    def changed(self):
        my_file = Path("previews"+str(self.camNr)+"/"+str(self.nr)+".jpg")
        if my_file.is_file():
            stamp = os.stat(self.filename).st_mtime
            if stamp != self._cached_stamp:
                self._cached_stamp = stamp
                return True
            else:
                return False
        else:
            if self._cached_stamp != 0:
                self._cached_stamp = 0
                return True
            else:
                return False

class camFrame:
    def __init__(self, parent, camFrameColumn, camFrameRow, photoSize, camNr):
        self.presetImageWatchers = []
        self.camNr = camNr
        self.presets = 16
        self.labels = []  
        self.frames = []
        self.images = []
        self.photoSize = photoSize
        self.camFrame = Frame(root, bg='white', borderwidth = 5, width=((self.photoSize[0]+2)*4), height=((self.photoSize[1]+2)*4))
        self.camFrame.grid(column=camFrameColumn, row=camFrameRow) 
        self.presetPreview = 0
        self.presetProgramm = 0

        for i in range(self.presets):
            presetImageWatcher1 = presetImageWatcher(i,self.camNr)
            self.presetImageWatchers.append(presetImageWatcher1)

        img = Image.open("white.jpg")
        img = img.resize(self.photoSize, Image.ANTIALIAS)

        for presetNr in range(self.presets):
            self.images.append(img)
            photoImg = ImageTk.PhotoImage(img)
            frame = Frame(self.camFrame, borderwidth = 0)
            frame.grid(column=(presetNr%4), row=(math.ceil((presetNr+1)/4)))
            label = Label(frame, image=photoImg, bd=0, width=self.photoSize[0], height=self.photoSize[1])
            label.image = photoImg
            label.grid()
            self.frames.append(frame)
            self.labels.append(label)

    def highlight(self, color):
        self.camFrame.configure(bg=color)

    def highlightPresetPreview(self, presetNr):
        if presetNr!= 0:
	        self.frames[presetNr-1].configure(bg="green", borderwidth = 5)
	        self.labels[presetNr-1].configure(width=self.photoSize[0]-10, height=self.photoSize[1]-10)
        	self.presetPreview = presetNr

    def highlightPresetProgramm(self, presetNr):
        if presetNr!= 0:
	        self.frames[presetNr-1].configure(bg="red", borderwidth = 5)
	        self.labels[presetNr-1].configure(width=self.photoSize[0]-10, height=self.photoSize[1]-10)
        	self.presetProgramm = presetNr

    def removeAllHighlightedPresets(self):
        for presetNr in range(self.presets):
            self.frames[presetNr-1].configure(borderwidth=0)
            self.labels[presetNr-1].configure(width=self.photoSize[0], height=self.photoSize[1])

    def removeHighlightedFromPreset(self, presetNr):
        self.frames[presetNr-1].configure(borderwidth=0)
        self.labels[presetNr-1].configure(width=self.photoSize[0], height=self.photoSize[1])

    def removeHighlighted(self):
        self.camFrame.configure(bg="white")

    def updatePresetImage(self, presetNr):
        print("Updating preset image: "+ str(presetNr) + ", CAM: "+ str(self.camNr))
        my_file = Path("previews"+str(self.camNr)+"/"+str(presetNr)+".jpg")
        if my_file.is_file():
            img = Image.open("previews"+str(self.camNr)+"/"+str(presetNr)+".jpg").convert("RGBA")
            #img.putalpha(128)
            #img.putalpha(256)
        else:
            img = Image.open("white.jpg")
        img = img.resize(photoSize, Image.ANTIALIAS)
        self.images[presetNr-1] = img
        photoImg = ImageTk.PhotoImage(img)
        self.labels[presetNr-1].configure(image = photoImg)
        self.labels[presetNr-1].image = photoImg # keep a reference!

    def checkPresetImage(self, presetNr):
        # print("checking update: "+ str(presetNr))
        return self.presetImageWatchers[presetNr].changed()

    def checkAndUpdatePresetImages(self):
        for presetNr in range(self.presets):
            if(self.checkPresetImage(presetNr)):
                # print("To update: "+ str(presetNr))
                self.updatePresetImage(presetNr)

    def getPresetPreview(self):
    	return self.presetPreview

    def getPresetProgramm(self):
    	return self.presetProgramm

    def setTransparency(self, transparency):
        for presetNr in range(self.presets):
            img = self.images[presetNr-1]
            img.putalpha(transparency)
            photoImg = ImageTk.PhotoImage(img)
            self.labels[presetNr-1].configure(image = photoImg)
            self.labels[presetNr-1].image = photoImg # keep a reference!

cam1Frame = camFrame(root,0,0,photoSize,1)
cam2Frame = camFrame(root,0,1,photoSize,2)
cam3Frame = camFrame(root,0,2,photoSize,3)

def takeSnapshot(ptz,presetNr):
	ptz.disableAutofocus()
	ptz.savePreset(presetNr)
	ptz.saveSnapshot(presetNr)

class PTZ:
	def __init__(self, camNr, ipAddress):
		self.camNr = camNr
		self.ipAddress = ipAddress

	def saveSnapshot(self, presetNr):
		#image_url = "http://"+self.ipAddress+"/snapshot.jpg"
		image_url = "https://cdn.pixabay.com/photo/2018/03/02/10/03/wildlife-3192772_960_720.jpg"

		try:
			# Open the url image, set stream to True, this will return the stream content.
			r = requests.get(image_url, stream = True, timeout=0.5)
		except requests.exceptions.Timeout:
			print('Timeout. Image Couldn\'t be retreived from: '+ image_url)
		except:
			print('Someting weird happend. Image Couldn\'t be retreived from: '+ image_url)
		else:
			# Check if the image was retrieved successfully
			if r.status_code == 200:
			    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
			    r.raw.decode_content = True
			    
			    # Open a local file with wb ( write binary ) permission.
			    with open("previews"+str(self.camNr)+"/"+str(presetNr)+".jpg",'wb') as f:
			        shutil.copyfileobj(r.raw, f)
			        
			    print('Image sucessfully Downloaded: ',image_url, " Saved as:", str(presetNr)+".jpg")
			else:
			    print('Image Couldn\'t be retreived from: '+ image_url)

	def disableAutofocus(self):
		#image_url = "http://"+self.ipAddress+"/cgi-bin/param.cgi?ptzcmd&lock_mfocus"
		url = "https://cdn.pixabay.com/photo/2018/03/02/10/03/wildlife-3192772_960_720.jpg"

		try:
			# Open the url image, set stream to True, this will return the stream content.
			r = requests.get(url, timeout=0.5)
		except requests.exceptions.Timeout:
			print('Timeout. Image Couldn\'t be retreived from: '+ url)
		except:
			print('Someting weird happend. Image Couldn\'t be retreived from: '+ url)
		else:
			# Check if the image was retrieved successfully
			if r.status_code == 200:
			    print('Api call succes: ', url)
			else:
			    print('Image Couldn\'t be retreived from: '+ url)

	def savePreset(self, presetNr):
		#image_url = "http://"+self.ipAddress+"/cgi-bin/ptzctrl.cgi?ptzcmd&posset&"+ str(presetNr)
		url = "https://cdn.pixabay.com/photo/2018/03/02/10/03/wildlife-3192772_960_720.jpg"

		try:
			# Open the url image, set stream to True, this will return the stream content.
			r = requests.get(url, timeout=0.5)
		except requests.exceptions.Timeout:
			print('Timeout. Image Couldn\'t be retreived from: '+ url)
		except:
			print('Someting weird happend. Image Couldn\'t be retreived from: '+ url)
		else:
			# Check if the image was retrieved successfully
			if r.status_code == 200:
			    print('Api call succes: ', url)
			else:
			    print('Image Couldn\'t be retreived from: '+ url)

PTZ1 = PTZ(1,PTZ_1_IP)
PTZ2 = PTZ(2,PTZ_2_IP)
PTZ3 = PTZ(3,PTZ_3_IP)

class apiHandler(BaseHTTPRequestHandler):
	def do_GET(self):

		global previewCam
		global liveCam

		global cam1Frame
		global cam2Frame
		global cam3Frame

		path = self.path.split("?")[0]
		parsed_path = urllib.parse.urlsplit(self.path)
		query = urllib.parse.parse_qs(parsed_path.query)
		response = ""

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes("<html><head><title>Brandaris PTZ controll API</title></head>", "utf-8"))

		if(path=="/api/cam/set"):
			if "cam" in query: 
				cam = int(query['cam'][0])
				# print(cam)
				if previewCam==1:
					print("white 1")
					cam1Frame.removeHighlighted()
					cam1Frame.setTransparency(128)
				elif previewCam==2:
					print("white 2")
					cam2Frame.removeHighlighted()
					cam2Frame.setTransparency(128)
				elif previewCam==3:
					print("white 3")
					cam3Frame.removeHighlighted()
					cam3Frame.setTransparency(128)

				if cam == 0:
					previewCam = 0
				elif cam == 1:
					previewCam = 1
					cam1Frame.setTransparency(256)
					cam1Frame.highlight("green")
					response = "OK"
				elif cam == 2:
					previewCam = 2
					cam2Frame.setTransparency(256)
					cam2Frame.highlight("green")
					response = "OK"
				elif cam == 3:
					previewCam = 3
					cam3Frame.setTransparency(256)
					cam3Frame.highlight("green")
					response = "OK"
				else:
					response = "cam out of range"
			else:
				response = "forgot vars"

		elif(path=="/api/preset/set"):
			if "cam" in query: 
				if "preset" in query: 
					presetNr = int(query['preset'][0])
					cam = int(query['cam'][0])
					# print(cam)
					# print(presetNr)

					if cam == 1:
						cam1Frame.removeAllHighlightedPresets()
						cam1Frame.highlightPresetPreview(presetNr)
						response = "OK"
					elif cam == 2:
						cam2Frame.removeAllHighlightedPresets()
						cam2Frame.highlightPresetPreview(presetNr)
						response = "OK"
					elif cam == 3:
						cam3Frame.removeAllHighlightedPresets()
						cam3Frame.highlightPresetPreview(presetNr)
						response = "OK"
					else:
						response = "cam out of range"
				else:
					response = "forgot vars"
			else:
				response = "forgot vars"

		elif(path=="/api/preset/save"):
			if "cam" in query: 
				if "preset" in query: 
					presetNr = int(query['preset'][0])
					cam = int(query['cam'][0])
					# print(cam)
					# print(presetNr)

					if cam == 1:
						takeSnapshotThread = threading.Thread(name='takeSnapshotThread', target=takeSnapshot, args=(PTZ1,presetNr))
					elif cam == 2:
						takeSnapshotThread = threading.Thread(name='takeSnapshotThread', target=takeSnapshot, args=(PTZ2,presetNr))
					elif cam == 3:
						takeSnapshotThread = threading.Thread(name='takeSnapshotThread', target=takeSnapshot, args=(PTZ3,presetNr))
					takeSnapshotThread.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
					takeSnapshotThread.start()
					if cam == 1:
						cam1Frame.removeAllHighlightedPresets()
						cam1Frame.highlightPresetPreview(presetNr)
						response = "OK"
					elif cam == 2:
						cam2Frame.removeAllHighlightedPresets()
						cam2Frame.highlightPresetPreview(presetNr)
						response = "OK"
					elif cam == 3:
						cam3Frame.removeAllHighlightedPresets()
						cam3Frame.highlightPresetPreview(presetNr)
						response = "OK"
					else:
						response = "cam out of range"
				else:
					response = "forgot vars"
			else:
				response = "forgot vars"

		elif (path=="/api/preview-to-programm"):
			if liveCam==1:
				print("white 1")
				cam1Frame.removeHighlighted()
			elif liveCam==2:
				print("white 2")
				cam2Frame.removeHighlighted()
			elif liveCam==3:
				print("white 3")
				cam3Frame.removeHighlighted()

			if previewCam == 1:
				liveCam = 1
				cam1Frame.setTransparency(128)
				cam1Frame.highlight("red")
				cam1Frame.highlightPresetProgramm(cam1Frame.getPresetPreview())
				cam2Frame.highlightPresetPreview(cam2Frame.getPresetProgramm())
				cam3Frame.highlightPresetPreview(cam3Frame.getPresetProgramm())
				print("cam 1 to programm")
			elif previewCam == 2:
				liveCam = 2
				cam2Frame.setTransparency(128)
				cam2Frame.highlight("red")
				cam1Frame.highlightPresetPreview(cam1Frame.getPresetProgramm())
				cam2Frame.highlightPresetProgramm(cam2Frame.getPresetPreview())
				cam3Frame.highlightPresetPreview(cam3Frame.getPresetProgramm())
				print("cam 2 to programm")
			elif previewCam == 3:
				liveCam = 3
				cam3Frame.setTransparency(128)
				cam3Frame.highlight("red")
				cam1Frame.highlightPresetPreview(cam1Frame.getPresetProgramm())
				cam2Frame.highlightPresetPreview(cam2Frame.getPresetProgramm())
				cam3Frame.highlightPresetProgramm(cam3Frame.getPresetPreview())
				print("cam 3 to programm")
			previewCam=0
			response = "OK"
		else:
			response = "unknow api path"

		self.wfile.write(bytes("<body><p>"+response+"</p>", "utf-8"))
		self.wfile.write(bytes("</body></html>", "utf-8"))
        

def start_server(path, port=8000):

    httpd = HTTPServer(('', port), apiHandler)
    httpd.serve_forever()

def polAndUpdateImages():
	# print('pol')
	cam1Frame.checkAndUpdatePresetImages()
	cam2Frame.checkAndUpdatePresetImages()
	cam3Frame.checkAndUpdatePresetImages()
	threading.Timer(1, polAndUpdateImages).start()

polAndUpdateImagesThread = threading.Thread(name='polAndUpdateImages', target=polAndUpdateImages)
polAndUpdateImagesThread.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
polAndUpdateImagesThread.start()

port = 8000
webserverAPI = threading.Thread(name='webserverAPI', target=start_server, args=('.', port))
webserverAPI.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
webserverAPI.start()

root.mainloop()