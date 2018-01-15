# This script will stream to GRIP on another workstation.
# Only works for single user.

#!/usr/bin/env python

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
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket as Socket
import os
import re
import io

camera = None


def getIP(iface):
	search_str = 'ip addr show eth0'.format(iface)
	ipv4 = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M), os.popen(search_str).read()).groups()[0]
	ipv6 = re.search(re.compile(r'(?<=inet6 )(.*)(?=\/)', re.M), os.popen(search_str).read()).groups()[0]
	return (ipv4, ipv6)


def setUpCameraPi():
	global camera
	camera = PiCamera(sensor_mode=4, resolution=(320,240), framerate=50)
	camera.resolution = (320,240)
	camera.start_preview()
	camera.preview.fullscreen = False
	camera.preview.window = (0, 0, 320, 240)
	camera.shutter_speed = 5000
	camera.brightness = 40

def compress(orig, comp):
	return float(orig) / float(comp)


class mjpgServer(BaseHTTPRequestHandler):
	ip = None
	hostname = None

	def do_GET(self):
		global camera
		print("do_GET")
		print('connection from:', self.address_string())

		if self.ip is None or self.hostname is None:
			self.ip, _ = getIP('eth0')
			self.hostname = Socket.gethostname()

		if self.path == '/mjpg':
			self.send_response(200)
			self.send_header(
				'Content-type',
				'multipart/x-mixed-replace; boundary=--jpgboundary'
			)
			self.end_headers()
			stream=io.BytesIO()

			try:
				start = time.time()
				for foo in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
					self.wfile.write(b'--jpgboundary')
					self.send_header('Content-type', 'image/jpeg')
					self.send_header('Content-length',len(stream.getvalue()))
					self.end_headers()
					self.wfile.write(stream.getvalue())
					stream.seek(0)
					stream.truncate()
					#time.sleep(0.5)
			except KeyboardInterrupt:
				pass
			return

		elif self.path == '/':
			# hn = self.server.server_address[0]
			port = self.server.server_address[1]
			ip = self.ip
			hostname = self.hostname

			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(bytes('<html><head></head><body>', "utf8"))
			self.wfile.write(bytes('<h1>{0!s}[{1!s}]:{2!s}</h1>'.format(hostname, ip, port), "utf8"))
			self.wfile.write(bytes('<img src="http://{}:{}/mjpg"/>'.format(ip, port), "utf8"))
			# self.wfile.write('<p>The mjpg stream can be accessed directly at:<ul>')
			# self.wfile.write('<li>http://{0!s}:{1!s}/mjpg</li>'.format(ip, port))
			# self.wfile.write('<li><a href="http://{0!s}:{1!s}/mjpg"/>http://{0!s}:{1!s}/mjpg</a></li>'.format(hostname, port))
			# self.wfile.write('</p></ul>')
			self.wfile.write(bytes('<p>This only handles one connection at a time</p>', "utf8"))
			self.wfile.write(bytes('</body></html>', "utf8"))

		else:
			print('error', self.path)
			self.send_response(404)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>')
			self.wfile.write('<h1>{0!s} not found</h1>'.format(self.path))
			self.wfile.write('</body></html>')


def handleArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--port', help='mjpeg publisher port, default is 9000', type=int, default=9000)
	parser.add_argument('-t', '--type', help='set camera type, either pi or cv, ex. -t pi', default='cv')
	parser.add_argument('-s', '--size', help='set size', nargs=2, type=int, default=(320, 240))

	args = vars(parser.parse_args())
	args['size'] = (args['size'][0], args['size'][1])
	return args


def main():
	args = handleArgs()

	try:
		win = args['size']
		setUpCameraPi()
		# server = HTTPServer(('0.0.0.0', args['port']), mjpgServer)
		ipv4, ipv6 = getIP('eth0')
		print('wlan0:', ipv4)
		mjpgServer.ip = ipv4
		mjpgServer.hostname = Socket.gethostname()
		server = HTTPServer((ipv4, args['port']), mjpgServer)
		print("server started on {}:{}".format(Socket.gethostname(), args['port']))
		server.serve_forever()

	except KeyboardInterrupt:
		print('KeyboardInterrupt')

	server.socket.close()


if __name__ == '__main__':
	main()
