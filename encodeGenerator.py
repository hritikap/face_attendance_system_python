import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("D:\Data analyst\Python_projects\Attendance_detection\serviceaccountfirebasekey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://faceattendancesystem-7c518-default-rtdb.firebaseio.com/',
    'storageBucket':'faceattendancesystem-7c518.appspot.com'
})


#importing the attendees images

folderimage='D:\Data analyst\Python_projects\Attendance_detection\Images'
imagePathList=os.listdir(folderimage)
print(imagePathList)
imgList=[]
studentIds=[]

for path in imagePathList:
    imgList.append(cv2.imread(os.path.join(folderimage,path)))
    studentIds.append(os.path.splitext(path)[0])  #splits the path into two parts ie foldername and the file format(.png) and the index 0 selects the first path ie the foldername

    fileName=f'{folderimage}/{path}' # f creates a folder and then saves the images inside it
    Bucket=storage.bucket()
    blob=Bucket.blob(fileName)
    blob.upload_from_filename(fileName)

def findEncodings(imagePathList):
    encodeList=[]

    for img in imagePathList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    
    return encodeList
print('encoding started....')
encodeListKnown= findEncodings(imgList)
encodeListKnownIds=[encodeListKnown,studentIds]
print('encoding completed')

file=open('encodefile.p','wb')
pickle.dump(encodeListKnownIds,file)
file.close()
print('file saved')