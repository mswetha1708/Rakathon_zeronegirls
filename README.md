# Theme : Education
### Problem Statement
- Students learning online are exposed to more distractions than face-face classes.
 - Managing technological distractions can be challenging when students need to use their phone or computer to study/attend lectures and complete the coursework. 
-  The course instructor is remotely located somewhere it is hard to monitor all the students while taking classes. Moreover the course instructor cannot see the video feed of all the students while taking classes.

### Solution 
Our idea is to develop a real-time distraction detection tool that monitors the attentiveness of the students in a video sequence to help the students and the instructor

# Files
-  The folder ***templates*** contain all the html pages used to render our website
-  The file ***camera. py***  takes the live video from webcam as input, frame-by-frame and computes yawn count, sleep count by comparing the eye aspect ratio and lip distance with a threshold. This file uses Facial Landmark detection using dlib facial landmark detection
- The file ***main. py*** contains the code for establishing a database connection using Flask
-  shape_predictor_68_face_landmarks.dat is the dataset used for the 68 face landmark detection
