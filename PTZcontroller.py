from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import os, math
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib
import requests # to get image from the web
import shutil # to save it 

from lib.camFrame import camFrame
from lib.ptx import PTZPostAPI

from dotenv import load_dotenv
load_dotenv()
PTZ_1_IP = os.getenv('PTZ_1_IP')
PTZ_2_IP = os.getenv('PTZ_2_IP')
PTZ_3_IP = os.getenv('PTZ_3_IP')
# print(PTZ_1_IP)
# print(PTZ_2_IP)
# print(PTZ_3_IP)

#photoSize = (120, 80)
photoSize = (240, 160)

previewCam = 0
liveCam = 0

root = Tk()
root.title("PTZ controller")
root.geometry(str((photoSize[0]*4)+10)+"x"+str(3*((photoSize[1]*4)+10))+"+300+150")
root.resizable(width=False, height=False)

list_frames = []
list_frames.append(camFrame(root,0,0,photoSize,1))
list_frames.append(camFrame(root,0,1,photoSize,2))
list_frames.append(camFrame(root,0,2,photoSize,3))

def takeSnapshot(ptz,presetNr):
	ptz.disableAutofocus()
	ptz.savePreset(presetNr)
	# ptz.saveSnapshot(presetNr)

list_cams = []
list_cams.append(PTZPostAPI(1,PTZ_1_IP))
list_cams.append(PTZPostAPI(2,PTZ_2_IP))
list_cams.append(PTZPostAPI(3,PTZ_3_IP))

class apiHandler(BaseHTTPRequestHandler):


	def do_GET(self):

		global liveCam
		global previewCam
		path = self.path.split("?")[0]
		parsed_path = urllib.parse.urlsplit(self.path)
		query = urllib.parse.parse_qs(parsed_path.query)
		response = ""

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes("<html><head><title>PTZ controll API</title></head>", "utf-8"))

# CAM = 1, 
		if(path=="/api/cam/set"):
			if "cam" in query: 
				cam = int(query['cam'][0])
				if cam < 1 or cam > len(list_cams):
					response = "Cam out of range"
					return
			
				response = "OK"
				if previewCam!=0:
					list_frames[previewCam-1].removeHighlighted()
					list_frames[previewCam-1].setTransparency(128)
				previewCam = cam
				list_frames[cam-1].setTransparency(256)
				list_frames[cam-1].highlight("green")
				
			else:
				response = "forgot vars"

		elif(path=="/api/preset/set"):
			if "cam" in query: 
				if "preset" in query: 
					presetNr = int(query['preset'][0])
					cam = int(query['cam'][0])
					if cam < 0 or cam > len(list_cams):
						response = "Cam out of range"
						return

					list_frames[cam-1].removeAllHighlightedPresets()
					list_frames[cam-1].highlightPresetPreview(presetNr)
					response = "OK"
					
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
					if cam < 0 or cam > len(list_cams):
						response = "Cam out of range"
						return
					takeSnapshotThread = threading.Thread(name='takeSnapshotThread', target=takeSnapshot, args=(list_cams[cam-1],presetNr))
					
					takeSnapshotThread.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
					takeSnapshotThread.start()
					
					list_frames[cam-1].removeAllHighlightedPresets()
					list_frames[cam-1].highlightPresetPreview(presetNr)
				else:
					response = "forgot vars"
			else:
				response = "forgot vars"

		elif (path=="/api/preview-to-program"):
			
			list_frames[liveCam-1].removeHighlighted()
			liveCam = previewCam

			list_frames[liveCam-1].setTransparency(128)
			list_frames[liveCam-1].highlight("red")

			if previewCam == 1:
				list_frames[0].highlightPresetProgramm(list_frames[0].getPresetPreview())
				list_frames[1].highlightPresetPreview(list_frames[1].getPresetProgramm())
				list_frames[2].highlightPresetPreview(list_frames[2].getPresetProgramm())
				print("cam 1 to program")
			elif previewCam == 2:
				list_frames[0].highlightPresetPreview(list_frames[0].getPresetProgramm())
				list_frames[1].highlightPresetProgramm(list_frames[1].getPresetPreview())
				list_frames[2].highlightPresetPreview(list_frames[2].getPresetProgramm())
				print("cam 2 to program")
			elif previewCam == 3:
				list_frames[0].highlightPresetPreview(list_frames[0].getPresetProgramm())
				list_frames[1].highlightPresetPreview(list_frames[1].getPresetProgramm())
				list_frames[2].highlightPresetProgramm(list_frames[2].getPresetPreview())
				print("cam 3 to program")

			previewCam=0

			response = "OK"

		else:
			response = "unknow api path"

		self.wfile.write(bytes("<body><p>"+response+"</p>", "utf-8"))
		self.wfile.write(bytes("</body></html>", "utf-8"))

	# def do_PUT(self):
	# 	global liveCam
	# 	global previewCam
	# 	path = self.path.split("?")[0]
	# 	parsed_path = urllib.parse.urlsplit(self.path)
	# 	query = urllib.parse.parse_qs(parsed_path.query)
	# 	response = ""
	# 	self.send_response(200)
	# 	self.send_header("Content-type", "text/html")
	# 	self.end_headers()
	# 	self.wfile.write(bytes("<html><head><title>PTZ controll API</title></head>", "utf-8"))
	# 	if (path=="/api/cam/snapshot"):
			
	# 		if "cam" in query: 
	# 			cam = int(query['cam'][0])
	# 			if cam < 1 or cam > len(list_cams):
	# 				response = "Cam out of range"
	# 				return
	# 			print("PUT snapshot")
	# 			print("cam: " + str(cam))
	# 		response = "OK"
	# 	else:
	# 		response = "unknow api path"
	# 	self.wfile.write(bytes("<body><p>"+response+"</p>", "utf-8"))
	# 	self.wfile.write(bytes("</body></html>", "utf-8"))

def start_server(path, port=8000):
    httpd = HTTPServer(('', port), apiHandler)
    httpd.serve_forever()

def polAndUpdateImages():
	# print('pol')
	list_frames[0].checkAndUpdatePresetImages()
	list_frames[1].checkAndUpdatePresetImages()
	list_frames[2].checkAndUpdatePresetImages()
	if Path('new_snapshot.jpg').is_file():
		# print ("File exist")
		shutil.move("new_snapshot.jpg", "previews"+str(previewCam)+"/"+str(list_frames[previewCam-1].getPresetPreview())+".jpg")
	else:
		pass
		# print ("File not exist")
	threading.Timer(1, polAndUpdateImages).start()

polAndUpdateImagesThread = threading.Thread(name='polAndUpdateImages', target=polAndUpdateImages)
polAndUpdateImagesThread.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
polAndUpdateImagesThread.start()

port = 8000
webserverAPI = threading.Thread(name='webserverAPI', target=start_server, args=('.', port))
webserverAPI.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
webserverAPI.start()

root.mainloop()