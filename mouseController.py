#importing the basic files to be required
import pygame,sys,cv2
import numpy as np
from threading import Thread
from pymouse import *

#-->-->Camera initialization part
camera_port = 0
camera = cv2.VideoCapture(camera_port)
camera.set(3, 640)
camera.set(4, 480)
m = PyMouse()
print m.position()

#class containing all the variables and funcitons used for motion detection 
class motion(object):
	prevCX = 0
	prevCY = 0
	initialized = 0

	def _init_(self):
		self.prevCX = 0
		self.prevCY = 0
		self.initialized = 0

	#-->-->Basic function to detect color and the motion
	def detectColor(self,img):
		#---->---->check where the color is
		#converting bgr to hsv
		hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
		#defining the range of the color to be detected
		lower_blue = np.array([110,50,50], dtype = np.uint8)
		upper_blue = np.array([130,255,255], dtype = np.uint8)
		#threshold the image to get only blue colors
		mask = cv2.inRange(hsv,lower_blue,upper_blue)
		#finding the contours
		contours , hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		#finding the contour with the largest area
		if len(contours)>0:
			maxarea = 0
			maxIndex = 0
			for i in range(len(contours)):
				cnt = contours[i]
				cntArea = cv2.contourArea(cnt)
				if cntArea>maxarea:
					maxarea = cntArea
					maxIndex = i
			#now considering the contours with the largest area
			maxcnt = contours[maxIndex]
			hull = cv2.convexHull(maxcnt)
			#checking wether the color spotted is a blue cap only
			if maxarea>200:
				#checking if the movement is towards the correct direction 
				x,y,w,h = cv2.boundingRect(maxcnt)
				#cx = center of the contour x-coordinate
				cx = int((x+w)/2)
				cy = int((y+h)/2)
				m.move(cx,cy)
				if self.initialized==0:
					self.prevCY = cy
					self.prevCX = cx
					self.initialized = 1
				else:
					mysum = abs(cy-self.prevCY)+abs(cx-self.prevCX)
					self.prevCX = cx
					self.prevCY = cy
					if mysum>=25:
						m.click(self.prevCX,self.prevCY,1)	
			#drawing that contour on the image and the mask
			cv2.drawContours(mask,[hull],-1,(0,255,0),1)
			cv2.drawContours(mask,[maxcnt],-1,(0,255,0),1)
			cv2.drawContours(img,[maxcnt],-1,(0,0,255),1)
			cv2.drawContours(img,[hull],-1,(255,0,0),2)
		cv2.imshow("GestureMusic",img)
		return 1


	#-->-->Camera display part
	#part which shows webcam
	def webcamLive(self):
		retval , img = camera.read()
		while retval:
			#reading image from the camera
			action = self.detectColor(img)
			keypress = cv2.waitKey(10)
			retval,img = camera.read()
			if keypress==27:
				break

obj = motion()
obj.webcamLive()
camera.release()
cv2.destroyAllWindows()


