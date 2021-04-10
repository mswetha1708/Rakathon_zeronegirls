
from flask import Flask, render_template, Response,session
from camera import VideoCamera
from flask import request
import os
#from werkzeug import secure_filename
from pymysql import connect
# import smtplib
from flask_mail import Mail, Message
import math
app = Flask(__name__) 
  
app.secret_key = 'zerone_girls'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'zeronegirls@gmail.com'
app.config['MAIL_PASSWORD'] = '8CYbkpKa8X5mJpA'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

sleepcount = 0
yawncount = 0
totalduration = 0
def dbconnect(sql):
    result = []
    db = connect(host='remotemysql.com', database='NB3eKnXAHB', user='NB3eKnXAHB', password='xYqoFOfYSF')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    for i in cursor.fetchall():
        result.append(i)
    cursor.close()
    return result


@app.route('/')

@app.route('/login',methods=['GET', 'POST']) 
def login(): 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'classid' in request.form :
        print("HELLO")
        username = request.form['username'] 
        password = request.form['password']
        classid = request.form['classid']
        print(username)
        print(password)
        print(classid)
        sql = ("SELECT * FROM Login WHERE UserId = '%s' AND Password = '%s'" % (username, password, ))
        output = dbconnect(sql)
        msg=""
        if(output) :
            sql = ("INSERT INTO Classdetails(UserId,ClassId) VALUES ('%s',%d )" % (username,int(classid), ))
            dbconnect(sql)
            session['loggedin'] = True
            session['username'] = username
            session['id'] = classid
            msg = "Logged in successfully"
            return render_template('index.html')
        else :
        	msg = "Incorrect Username Password" 
        	return render_template('login.html',msg=msg)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    ##send mail to the registered email of the result by fetching result
    return redirect(url_for('login'))
@app.route('/index')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame_list = camera.get_frame()
        frame = frame_list[0]
        global sleepcount
        global yawncount
        global totalduration
        yawncount = frame_list[1]
        sleepcount = frame_list[2]
        totalduration = frame_list[3]
        print("totalduration")
        print(totalduration)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
ButtonPressed = 0        
@app.route('/button', methods=["GET", "POST"])
def button():
    if request.method == "POST":
        username = session['username']
        session.pop('loggedin', None)
        session.pop('username', None)
        ##send mail to the registered email of the result by fetching result
        sql = ("UPDATE  Classdetails set sleepcount=%d,yawncount=%d,totalduration=%d  where UserId = '%s' " % (sleepcount,yawncount,totalduration,username,))
        dbconnect(sql)
        sql = ("SELECT emailid FROM Login WHERE UserId = '%s' " % (username, ))
        output = dbconnect(sql)
        output_mail=output[0]
        print(type(output[0]))
        print(sleepcount)
        print(yawncount)
        print(totalduration)
        ####send mail
        sql = ("SELECT * FROM Classroom where TeacherId = '%s' " % (username, ))
        output = dbconnect(sql)
        if(len(output)==0):
            msg = Message('Feedback for the session [Student]', sender = 'zeronegirls@gmail.com', recipients = [output_mail[0]])
            msg.body = "Thanks for attending the session on Introduction to Computer Programming \n"
            msg.body = msg.body + "Teacher of the Class: Harini"+"\n"
            msg.body = msg.body + "Course Id of the class attended: 12"+"\n"
            if(totalduration!=0):
                percentage_sleep = (sleepcount+yawncount) / ( 2 * totalduration )
                sql = ("UPDATE  Classdetails set percentage_sleep = %d  where UserId = '%s'" % (percentage_sleep,username,))
                dbconnect(sql)
                msg.body = msg.body + "Percentage of your attentiveness in the class : "+ str(1.00 - percentage_sleep)
            else :
                percentage_sleep = 0
                sql = ("UPDATE  Classdetails set percentage_sleep = %d  where UserId = '%s'" % (percentage_sleep,username,))
                dbconnect(sql)
                msg.body = msg.body + "U have joined and left the session very quickly."
            mail.send(msg)
        #########delete data for class only when the teacher is leaving################
        sql = ("SELECT * FROM Classroom C,Login L,Classdetails D WHERE C.TeacherId = '%s' and C.ClassroomId = D.ClassId and C.TeacherId=D.UserId " % (username, ))
        output = dbconnect(sql)
        if(output):
            print("delete records belongong to the class and send mail")
            ###get the class id of the teacher leaving
            sql = ("SELECT ClassId FROM Classdetails WHERE UserId = '%s' " % (username, ))
            output = dbconnect(sql)
            output_class = output[0]
            print(int(output_class[0]))
            ######Send messages to the teacher by finding email id
            sql = ("SELECT emailid from Login where UserId = '%s'" %(username,))
            output = dbconnect(sql)
            output_mail = output[0]
            msg = Message('Feedback for the session [Instructor]', sender = 'zeronegirls@gmail.com', recipients = [output_mail[0]])
            ##############find the total people attending the session############
            sql = ("SELECT COUNT(UserId) FROM Classdetails WHERE ClassId = '%s' " % (int(output_class[0]), ))
            output = dbconnect(sql)
            output_strength = output[0]
            msg.body = "Thanks for attending the session on Introduction to Computer Programming. \n"
            msg.body = msg.body + "Number of Students attended the Class is: "+ str(output_strength[0])+".\n"
            msg.body = msg.body + "Course Id of the class conducted: "+str(output_class[0])+" \n"
            sql = ("SELECT AVG(percentage_sleep) FROM Classdetails WHERE ClassId = '%s' " % (int(output_class[0]), ))
            output = dbconnect(sql)
            output_percent = output[0]
            ################Average of the people attending####################
            if(math.ceil(output_percent[0])!=0):
                msg.body = msg.body + "Average attentiveness of the students who attended the session today: "+str(output_percent[0])+"."
            else :
                percentage_sleep = 0
                msg.body = msg.body + "Attentiveness of the students for this class is vey poor. "
            mail.send(msg)
            print("Mail sent")
            ####Delete the details of the class
            sql = ("DELETE FROM Classdetails where ClassId= %d" % (int(output_class[0]), ))
            dbconnect(sql)
        return render_template('login.html')
    return render_template('index.html')
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
   
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
