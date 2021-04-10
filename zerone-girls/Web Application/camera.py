FC_lips = 0
FC_eyes = 0

import cv2
from imutils import face_utils
from collections import OrderedDict
import numpy as np
import dlib
import cv2
import math
#####Global Variables

facial_features_cordinates = {}
LIPS_THRESHOLD_FCOUNT = 5
EYE_THRESHOLD_FCOUNT = 50
Eye_list = []
Lips_list = []
sleep_count=0
yawn_count=0
# define a dictionary that maps the indexes of the facial
# landmarks to specific face regions
FACIAL_LANDMARKS_INDEXES = OrderedDict([
    ("Mouth", (48, 68)),
    ("Right_Eyebrow", (17, 22)),
    ("Left_Eyebrow", (22, 27)),
    ("Right_Eye", (36, 42)),
    ("Left_Eye", (42, 48)),
    ("Nose", (27, 35)),
    ("Jaw", (0, 17))
])

def distancefn(pt1,pt2):
  p1=list(pt1)
  p2=list(pt2)
  return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
  
  
def visualize_facial_landmarks(image, shape,colors=None, alpha=0.75):
    # create two copies of the input image -- one for the
    # overlay and one for the final output image
    overlay = image.copy()
    output = image.copy()
    global FC_eyes
    global FC_lips
    global sleep_count
    global yawn_count
    # if the colors list is None, initialize it with a unique
    # color for each facial landmark region
    if colors is None:
        colors = [(255, 255, 255), (79, 76, 240), (0, 0, 0),
                  (168, 100, 168), (158, 163, 32),
                  (163, 38, 32), (180, 42, 220)]

    # loop over the facial landmark regions individually
    for (i, name) in enumerate(FACIAL_LANDMARKS_INDEXES.keys()):
        # grab the (x, y)-coordinates associated with the
        # face landmark
        (j, k) = FACIAL_LANDMARKS_INDEXES[name]
        pts = shape[j:k]
        facial_features_cordinates[name] = pts
    ######Lips coordinates and distance
    Lips_cordinates= facial_features_cordinates["Mouth"]
    U_Lips_points=(Lips_cordinates[2]+Lips_cordinates[3]+Lips_cordinates[4]+Lips_cordinates[13]+Lips_cordinates[14]+Lips_cordinates[15])//6
    L_Lips_points=(Lips_cordinates[8]+Lips_cordinates[9]+Lips_cordinates[10]+Lips_cordinates[17]+Lips_cordinates[18]+Lips_cordinates[19])//6
    #print(tuple(L_Lips_points))
    #print(tuple(U_Lips_points))
    cv2.line(overlay, tuple(U_Lips_points), tuple(L_Lips_points),(0,0,0),2)
    p1=list(L_Lips_points)
    p2=list(U_Lips_points)
    distance= math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
    Lips_list.append(distance)
    if (distance > 18 ):
      if(LIPS_THRESHOLD_FCOUNT == FC_lips) :
      	yawn_count+=FC_lips
      	print("yawn_inc")
      	FC_lips+=1
      elif (FC_lips>EYE_THRESHOLD_FCOUNT):
      	yawn_count+=1
      	print("Mouth Open")
      	FC_lips+=1
      else:
      	FC_lips+=1
      	print("Count1")
    else :
    	FC_lips=0
    	print("Mouth closed")
    ###########Eyes coordinates and distance
    REyes_cordinates= facial_features_cordinates["Right_Eye"]
    LEyes_cordinates= facial_features_cordinates["Left_Eye"]
    LEAR= (distancefn(LEyes_cordinates[1],LEyes_cordinates[5]) + distancefn(LEyes_cordinates[2],LEyes_cordinates[4]))/(2*distancefn(LEyes_cordinates[0],LEyes_cordinates[3]))
    REAR= (distancefn(REyes_cordinates[1],REyes_cordinates[5]) + distancefn(REyes_cordinates[2],REyes_cordinates[4]))/(2*distancefn(REyes_cordinates[0],REyes_cordinates[3]))
    #print(LEAR)
    #print(REAR)
    Eye_list.append(LEAR+REAR/2)
    if (LEAR < 0.25 and REAR < 0.25 ): ###Eyes_closed  
      if(EYE_THRESHOLD_FCOUNT==FC_eyes) :
      	sleep_count+=FC_eyes
      	print("eyes count")
      	FC_eyes+=1
      elif (FC_eyes>EYE_THRESHOLD_FCOUNT):
      	sleep_count+=1
      	print("Eyes Closed")
      	FC_eyes+=1
      else :
      	FC_eyes +=1
      	print("FC increment")
    else :
    	FC_eyes = 0
    	print("Eyes Open")
    #cv2_imshow(overlay)
    return output

face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
ds_factor=0.6


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        # initialize dlib's face detector (HOG-based) and then create
        # the facial landmark predictor
        p = "shape_predictor_68_face_landmarks.dat"
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(p)

    def __del__(self):
    	print("yawn_count")
    	print(yawn_count)
    	print(len(Lips_list))
    	print("Sleep_count")
    	print((sleep_count))
    	print(len(Eye_list))
    	self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        face_rects=face_cascade.detectMultiScale(gray,1.3,5)
        for (x,y,w,h) in face_rects:
        	cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
        	break
        rects = self.detector(gray, 0)
    
        # loop over the face detections
        for (i, rect) in enumerate(rects):
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            output = visualize_facial_landmarks(image, shape)
        ret, jpeg = cv2.imencode('.jpg', image)
        camera_returns=[]
        camera_returns.append(jpeg.tobytes())
        camera_returns.append(yawn_count)
        camera_returns.append(sleep_count)
        camera_returns.append(len(Eye_list))
        return camera_returns
