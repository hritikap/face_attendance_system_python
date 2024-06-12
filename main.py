import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import tempfile
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("D:\Data analyst\Python_projects\Attendance_detection\serviceaccountfirebasekey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://faceattendancesystem-7c518-default-rtdb.firebaseio.com/',
    'storageBucket':'faceattendancesystem-7c518.appspot.com'
})

bucket= storage.bucket()

cap= cv2.VideoCapture(0)
cap.set(3,640) #setswidth
cap.set(4,480)   #setsheight

imgBackground=cv2.imread('D:\Data analyst\Python_projects\Attendance_detection\Resources/background.png')

#importing the image modes into a list
folderModePath=('D:\Data analyst\Python_projects\Attendance_detection\Resources/Modes')
modePathList=os.listdir(folderModePath)
modeList=[]
for path in modePathList:
    modeList.append(cv2.imread(os.path.join(folderModePath,path)))

#load encoding file
file=open('encodefile.p','rb') #rb is used to read file
encodeListKnownIds= pickle.load(file)
file.close()
encodeListKnown,studentIds=encodeListKnownIds
print(studentIds)
modeType=0
counter=0
id=-1
imgStudent= []

while True:
    success, img= cap.read()

    #resizing image
    imgSmall=cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSmall=cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    faceCurFrame=face_recognition.face_locations(imgSmall)
    encodeCurFrame=face_recognition.face_encodings(imgSmall,faceCurFrame)


    imgBackground[162:162+480,55:55+640]=img  #to capture our image within the imagebackground frame
    imgBackground[44:44+633,808:808+414]=modeList[modeType] 

    #checking whether the faces matches with the stored one or not
    if faceCurFrame:
        for encodeFace,faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDistance=face_recognition.face_distance(encodeListKnown,encodeFace)

            # print('matches',matches)
            # print('facedis',faceDistance)

            matchIndex=np.argmin(faceDistance)
            print('matchindex',matchIndex)

            if matches[matchIndex]:
                print('known face detected')
                # print(studentIds[matchIndex])

                # to create a focus with green rect box around the face
                y1,x2,y2,x1=faceLoc
                y1,x2,y2,x1=y1 * 4,x2 * 4,y2 * 4,x1 * 4
                bbox= 55 + x1,162 + y1,x2 - x1,y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
        
                if counter == 0:
                    cvzone.putTextRect(imgBackground,'Loading',(275,400))
                    cv2.imshow('Face Attendance', imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType= 1

        if counter!= 0:

            if counter == 1:

                # get the data
                studentInfo=db.reference(f'Students/{id}').get()           
                print(studentInfo)

                # get the image from the firebase storage
                blob = bucket.get_blob(f'D:\Data analyst\Python_projects\Attendance_detection\Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent=cv2.imdecode(array,cv2.COLOR_BGR2RGB)

                # update data of attendance in database
                datetimeObject= datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                secondsElapsed= (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)

                # does another marking after 24 hrs ie 86400 seconds
                if secondsElapsed>86400:

                    ref=db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType=3
                    counter=0
                    imgBackground[44:44+633,808:808+414]=modeList[modeType]
            
            if modeType!=3:

                if 10<counter<20:
                    modeType=2
                    imgBackground[44:44+633,808:808+414]=modeList[modeType]
                
                if counter<=10:    
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground,str(studentInfo['Major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['standing']),(910,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['Starting_year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                
                #to center the text in Name
                    (w,h), _ =cv2.getTextSize(studentInfo['Name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset=(414-w)//2
                    cv2.putText(imgBackground,str(studentInfo['Name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)

                    imgBackground[175:175 + 216,909:909 + 216]=imgStudent
            
                counter+=1

            # resetting everything
                if counter>=20:
                    counter=0
                    modeType=0
                    studentInfo=[]
                    imgStudent=[]
                    imgBackground[44:44+633,808:808+414]=modeList[modeType]
    else:
        modeType=0
        counter=0

    
     
    cv2.imshow('Face Attendance', imgBackground)
    

    cv2.waitKey(1)

