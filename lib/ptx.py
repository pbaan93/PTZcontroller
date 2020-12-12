import requests # to get image from the web
import shutil # to save it 

class PTZPostAPI:
	def __init__(self, camNr, ipAddress):
		self.camNr = camNr
		self.ipAddress = ipAddress

	#!!!!!!!!! This api endpoint has a bug in th current PTZ optics firmware
	# def saveSnapshot(self, presetNr):
	# 	url = "http://"+self.ipAddress+"/snapshot.jpg"
	# 	#url = "https://cdn.pixabay.com/photo/2018/03/02/10/03/wildlife-3192772_960_720.jpg"

	# 	try:
	# 		# Open the url image, set stream to True, this will return the stream content.
	# 		r = requests.get(url, stream = True, timeout=0.5)
	# 	except requests.exceptions.Timeout:
	# 		print('Timeout. Image Couldn\'t be retreived from: '+ url)
	# 	except:
	# 		print('Someting weird happend. Image Couldn\'t be retreived from: '+ url)
	# 	else:
	# 		# Check if the image was retrieved successfully
	# 		if r.status_code == 200:
	# 		    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
	# 		    r.raw.decode_content = True
			    
	# 		    # Open a local file with wb ( write binary ) permission.
	# 		    with open("previews"+str(self.camNr)+"/"+str(presetNr)+".jpg",'wb') as f:
	# 		        shutil.copyfileobj(r.raw, f)
			        
	# 		    print('Image sucessfully Downloaded: ',url, " Saved as:", str(presetNr)+".jpg")
	# 		else:
	# 		    print('Image Couldn\'t be retreived from: '+ url)

	def disableAutofocus(self):
		url = "http://"+self.ipAddress+"/cgi-bin/param.cgi?ptzcmd&lock_mfocus"
		#url = "https://cdn.pixabay.com/photo/2018/03/02/10/03/wildlife-3192772_960_720.jpg"

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
		url = "http://"+self.ipAddress+"/cgi-bin/ptzctrl.cgi?ptzcmd&posset&"+ str(presetNr)
		#url = "https://cdn.pixabay.com/photo/2018/03/02/10/03/wildlife-3192772_960_720.jpg"

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