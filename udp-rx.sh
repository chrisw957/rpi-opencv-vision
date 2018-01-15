#!/bin/sh
# This script will received the rtp/udp stream with gstreamer...
gst-launch-1.0 -v udpsrc port=5000 \
caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)RAW, sampling=(string)BGR, depth=(string)8, width=(string)320, height=(string)240, colorimetry=(string)SMPTE240M, payload=(int)96" ! \
rtpvrawdepay ! \
queue ! \
videorate ! \
videoconvert ! \
queue ! \
xvimagesink sync=false



