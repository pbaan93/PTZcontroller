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

from lib.imageWatcher import presetImageWatcher
class camFrame:
    def __init__(self, parent, camFrameColumn, camFrameRow, photoSize, camNr):
        self.presetImageWatchers = []
        self.camNr = camNr
        self.presets = 16
        self.labels = []  
        self.frames = []
        self.images = []
        self.photoSize = photoSize
        self.camFrame = Frame(parent, bg='white', borderwidth = 5, width=((self.photoSize[0]+2)*4), height=((self.photoSize[1]+2)*4))
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
        img = img.resize(self.photoSize, Image.ANTIALIAS)
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