from __future__ import print_function
import threading
import datetime
import imutils
import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import mediapipe as mp
import pyautogui
import simpleaudio as sa
from imutils.video import VideoStream
import argparse
import time


def start_program():
    #root = tk.Tk()
    #root.title('SnapMe')
    #root.iconbitmap('C:/Users/Xade/Downloads/dip_proj/Front-end/camera.ico')
    #root.geometry("800x800")
    #root.resizable(False, False)
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True,help="path to output directory to store snapshots")
    ap.add_argument("-p", "--picamera", type=int, default=-1,help="whether or not the Raspberry Pi camera should be used")
    args = vars(ap.parse_args())
    # initialize the video stream and allow the camera sensor to warmup
    print("[INFO] warming up camera...")
    vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
    time.sleep(2.0)
    # start the app
    pba = PhotoBoothApp(vs, args["output"])
    pba.root.mainloop()
    
    #btn = tk.Button(root,text="SnapEm!", command=takeSnapshot)
    #btn.pack()

class PhotoBoothApp:
	def __init__(self, vs, outputPath):
		# store the video stream object and output path, then initialize
		# the most recently read frame, thread for reading frames, and
		# the thread stop event
		self.vs = vs
		self.outputPath = outputPath
		self.frame = None
		self.thread = None
		self.stopEvent = None
		# initialize the root window and image panel
		self.root = tk.Tk()
		self.root.title('CaptureImg')
		self.root.iconbitmap('C:/Users/Xade/Downloads/dip_proj/Front-end/camera.ico')
		self.root.geometry("800x800")
		self.root.resizable(False, False)
		self.panel = None
		# create a button, that when pressed, will take the current
		# frame and save it to file
		btn = tk.Button(self.root, text="Capture!!",
			command=self.takeSnapshot)
		btn.pack(side="bottom", fill='x',expand="yes", padx=0,
			pady=0)
		# start a thread that constantly pools the video sensor for
		# the most recently read frame
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()
		# set a callback to handle when the window is closed
		self.root.wm_title("PyImageSearch PhotoBooth")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
	def videoLoop(self):
		# DISCLAIMER:
		# I'm not a GUI developer, nor do I even pretend to be. This
		# try/except statement is a pretty ugly hack to get around
		# a RunTime error that Tkinter throws due to threading
		try:
			# keep looping over frames until we are instructed to stop
			while not self.stopEvent.is_set():
				# grab the frame from the video stream and resize it to
				# have a maximum width of 300 pixels
				self.frame = self.vs.read()
				self.frame = imutils.resize(self.frame,height=700 , width=800)
		
				# OpenCV represents images in BGR order; however PIL
				# represents images in RGB order, so we need to swap
				# the channels, then convert to PIL and ImageTk format
				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)
		
				# if the panel is not None, we need to initialize it
				if self.panel is None:
					self.panel = tk.Label(image=image)
					self.panel.image = image
					self.panel.pack(side="left", padx=0, pady=0)
		
				# otherwise, simply update the panel
				else:
					self.panel.configure(image=image)
					self.panel.image = image
		except RuntimeError as e:
			print("[INFO] caught a RuntimeError")
	def takeSnapshot(self):
		# grab the current timestamp and use it to construct the
		# output path
		ts = datetime.datetime.now()
		filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
		p = os.path.sep.join((self.outputPath, filename))
		# save the file
		cv2.imwrite(p, self.frame.copy())
		print("[INFO] saved {}".format(filename))
	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("[INFO] closing...")
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()