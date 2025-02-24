from collections import deque
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time

# Simulate command-line arguments
args = {"video": None, "buffer": 64}

# Color boundaries in HSV
colors = {
    "green": ((29, 86, 6), (64, 255, 255)),
    "blue": ((90, 50, 50), (130, 255, 255)),
    "red": ((0, 50, 50), (10, 255, 255)),
    "yellow": ((20, 100, 100), (30, 255, 255))
}

# Initialize tracked points
pts = {color: deque(maxlen=args["buffer"]) for color in colors}

# Start video capture
vs = VideoStream(src=0).start() if not args.get("video") else cv2.VideoCapture(args["video"])
time.sleep(2.0)

# Main loop
while True:
    # Read frame
    frame = vs.read()
    frame = frame[1] if args.get("video") else frame
    
    # If end of video stream, break
    if frame is None:
        break
    
    # Resize frame, apply Gaussian blur, and convert to HSV
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Loop through colors and track objects
    for color, (lower, upper) in colors.items():
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        # If contours are found, find the largest one and draw it
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                pts[color].appendleft(center)

                for i in range(1, len(pts[color])):
                    if pts[color][i - 1] is None or pts[color][i] is None:
                        continue
                    cv2.line(frame, pts[color][i - 1], pts[color][i], (0, 255, 0), 2)

    # Show the frame to the user
    cv2.imshow("Frame", frame)

    # If the 'q' key is pressed, break from the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup
vs.stop() if not args.get("video") else vs.release()
cv2.destroyAllWindows()
