# This script streams video over udp with rtp, using gstreamer.

# import the necessary packages
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import cv2
import sys

# initialize the camera and stream
camera = PiCamera(sensor_mode=4, resolution=(320,240), framerate=10)
#camera.resolution = (320,240)
#camera.framerate = 50
camera.start_preview()
camera.preview.fullscreen = False
camera.preview.window = (0, 0, 320, 240)
#camera.exposure_mode = "off"
#camera.iso = 800
camera.shutter_speed = 5000
#camera.video_denoise = False



rawCapture = PiRGBArray(camera, size=(320, 240))
stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)

# allow the camera to warmup and start the FPS counter
print("[INFO] sampling frames from `picamera` module...")
#time.sleep(2.0)
x = 0
sink = cv2.VideoWriter("appsrc ! queue ! rtpvrawpay ! udpsink host=192.168.1.112 port=5000 ", 0, 50.0, (320,240))
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
fps = FPS().start()

# loop over some frames
for (i, f) in enumerate(stream):
	# grab the frame from the stream and resize it to have a maximum
	# width of 400 pixels
	frame = f.array
	#hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	#mask = cv2.inRange(hsv, greenLower, greenUpper)
	#sink.write(frame)

	# check to see if the frame should be displayed to our screen
	if x == 0:
		#res = cv2.bitwise_and(frame, frame, mask=mask)
		sink.write(frame)
		print(camera.iso, camera.shutter_speed, camera.exposure_speed, camera.sensor_mode)
		#cv2.imshow("Frame", mask)
		#key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame and update
	# the FPS counter
	rawCapture.truncate(0)
	fps.update()
	x = x + 1
	if x >= 10:
		x = 0

	# check to see if the desired number of frames have been reached
	if i == 500:
		break

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
stream.close()
rawCapture.close()
camera.close()
