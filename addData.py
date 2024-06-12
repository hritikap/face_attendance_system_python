import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("D:\Data analyst\Python_projects\Attendance_detection\serviceaccountfirebasekey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://faceattendancesystem-7c518-default-rtdb.firebaseio.com/'
})
 # create a reference which will have id of all students
ref=db.reference('Students')
data={
    '001':{
        'Name':'Leonardo',
        'Major':'Computer Science',
        'Starting_year':2022,
        'total_attendance':20,
        'standing':'Good',
        'year':3,
        'last_attendance_time':'2024-04-03 21:45:00'
    },
    '002':{
        'Name':'Brad',
        'Major':'AI',
        'Starting_year':2023,
        'total_attendance':12,
        'standing':'Bad',
        'year':2,
        'last_attendance_time':'2024-04-03 21:45:00'
    },
    '003':{
        'Name':'Angelina',
        'Major':'DataBase',
        'Starting_year':2023,
        'total_attendance':11,
        'standing':'Bad',
        'year':2,
        'last_attendance_time':'2024-04-03 21:45:00'
    },
    '004':{
        'Name':'me',
        'Major':'DataBase',
        'Starting_year':2023,
        'total_attendance':22,
        'standing':'good',
        'year':2,
        'last_attendance_time':'2024-04-03 21:45:00'
    }
}

for key, value in data.items():
    ref.child(key).set(value)        #child is used to send a data in a specififc library