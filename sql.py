import cv2
import numpy as np
import face_recognition
import os
import pyodbc
import time
import datetime
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ****************************************************************************************************

# Tạo kết nối SQL với Python:
conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};\
    Server=LAMP;\
    Database=doan;\
    Trusted_Connection=yes;'
)

# ****************************************************************************************************

def gettime():
    now = datetime.datetime.utcnow()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    return now
print(gettime())

# ****************************************************************************************************
#
path = 'ImagesBasic'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print("Encoder Completed")

# ****************************************************************************************************


# Define a video capture object
cap = cv2.VideoCapture(0)

# Declare the width and height in variables
width, height = 600, 400

# Set the width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# ****************************************************************************************************
# Create a GUI app
app = tk.Tk()
app.geometry("1000x800")
# Bind the app with Escape keyboard to
# quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())

# ****************************************************************************************************
# Create a frame for the Treeview and Scrollbar
data_in = []
def create_treeview(root, columns):
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=50)
    return tree

def insert_data(tree, data):
    for row in data:
        tree.insert("", "end", values=row)

# ****************************************************************************************************

# Connect to the databas
def getdata():
    cursor = conn.cursor()
    # Fetch data from the SQLite table
    cursor.execute("SELECT * FROM SinhVien_login")
    data = cursor.fetchall()
    return data
# Close the database connection
data = getdata()
print(data)

formatted_data = [
    (
        item[0],
        item[1],
        item[2],
        item[3],
        item[4],
        item[5]
    )
    for item in data
]

print(formatted_data)

# ****************************************************************************************************
def delete_data():
    # Delete all existing items in the Treeview
    for item in tree.get_children():
        tree.delete(item)


def show_data():
    delete_data()
    for item in formatted_data:
        tree.insert("", "end", values=item)



# Create Treeview
columns = ["ID", "Name", "Code", "Start Time", "End Time", "Status"]
tree = ttk.Treeview(app, columns=columns, show="headings")
# Set column headings
for col in columns:
    tree.heading(col, text=col)
# Set column widths
for col in columns:
    tree.column(col, width=100)
# Add a vertical scrollbar
scrollbar = ttk.Scrollbar(app, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
# Place Treeview and scrollbar in the window
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
show_data()
# ****************************************************************************************************
# Create a label and display it on app
label_widget = Label(app)
label_widget.pack()
# Create a function to open camera and
def open_camera():
    success,img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

    for encodeFace,faceLoc in zip(encodeCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(255,0,255),2)

            cv2.putText(img,name,((x1+6),y1-6), cv2.FONT_HERSHEY_PLAIN,1,(0,0,255),2)

            # xử lí database

            # Nhập mã sinh viên
            student_id = name
            # Check if the student hasn't logged in within 3 minutes
            check_timeout_query = f"SELECT * FROM Sinhvien_login WHERE MSV = '{student_id}' AND check_out = 0 AND DATEDIFF(SECOND, time_in, GETDATE()) > 180"
            cursor = conn.cursor()
            cursor.execute(check_timeout_query)
            timeout_rows = cursor.fetchall()
            if not timeout_rows:
                # kiểm tra xem sinh viên đó đã đăng nhập cqhưa
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM Sinhvien_login WHERE MSV = '{student_id}'")
                rows = cursor.fetchall()
                show_data()

                if rows:
                    print("Sinh vien da dang nhap tu truoc.")

                    # Kiem tra xem có phải là sinh viên điểm danh ra ngoài
                    check_out_query = f"SELECT * FROM Sinhvien_login WHERE MSV = '{student_id}' AND check_out = 1 ORDER BY time_out DESC "
                    cursor.execute(check_out_query)
                    check_out_rows = cursor.fetchall()

                    if not check_out_rows:
                        # Cập nhật thời gian ra cho sinh viên
                        update_out_query = f"UPDATE Sinhvien_login SET time_out = '{gettime()}', check_out = 1 WHERE MSV = '{student_id}'"
                        cursor.execute(update_out_query)
                        conn.commit()
                        print("Time updated successfully.")
                    else:
                        print("Cannot update. Car has not checked in yet.")
                        # Check if the car is checked in
                        check_in_second = f"SELECT * FROM Sinhvien_login WHERE MSV = '{student_id}' AND check_out = 0"
                        cursor.execute(check_in_second)
                        rows = cursor.fetchall()
                        if len(rows) > 0:
                            print("Sinh vine ra lần tiếp")
                            result_update_out_second = f"UPDATE Sinhvien_login SET time_out = '{gettime()}', check_out = 1 WHERE MSV = '{student_id}' AND check_out = 0"
                            cursor.execute(result_update_out_second)
                            conn.commit()
                        else:
                            print("Xe vào lần tiếp")
                            sql_check_exit = f"SELECT * FROM SinhVien WHERE MSV = '{student_id}'"
                            cursor.execute(sql_check_exit)
                            rows_check_exit = cursor.fetchall()
                            if len(rows_check_exit) == 0:
                                print("HEllo")
                            else:
                                insert_first = f"INSERT INTO Sinhvien_login (TenSinhVien,MSV) SELECT TenSinhVien,MSV FROM SinhVien WHERE MSV = '{student_id}'"
                                if cursor.execute(insert_first):
                                    print("Thêm record thành công")

                                    result_update_second = f"UPDATE Sinhvien_login SET time_in = '{gettime()}', check_out = 0 WHERE ID = (SELECT MAX(ID) FROM Sinhvien_login WHERE MSV = '{student_id}')"
                                    cursor.execute(result_update_second)
                                    conn.commit()

                                    print("Thêm Time thành công")

                else:
                    print("Sinh vien chưa đăng nhập")

                    # Check if the car is in the database
                    check_exit_query = f"SELECT * FROM SinhVien WHERE MSV = '{student_id}'"
                    cursor.execute(check_exit_query)
                    check_exit_rows = cursor.fetchall()
                    if not check_exit_rows:
                        print("Unknow students ID.")
                    else:
                     # Insert into Sinhvien_login table
                        insert_first_query = f"INSERT INTO Sinhvien_login (TenSinhVien,MSV) SELECT TenSinhVien,MSV FROM SinhVien WHERE MSV = '{student_id}'"
                        cursor.execute(insert_first_query)
                        conn.commit()
                        #
                        # Update the time_in
                        update_second_query = f"UPDATE Sinhvien_login SET time_in = '{gettime()}', check_out = 0 WHERE ID = (SELECT MAX(ID) FROM Sinhvien_login WHERE MSV = '{student_id}')"
                        cursor.execute(update_second_query)
                        conn.commit()
                    print("Added record and updated time successfully.")

                # Close the connection

              # Kết thúc xử lí database
        else:
            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(255,0,255),2)

            cv2.putText(img,"Unknown",((x1+6),y1-6), cv2.FONT_HERSHEY_PLAIN,1,(0,0,255),2)

    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Capture the latest frame and transform to image
    captured_image = Image.fromarray(image)

    # Convert captured image to photoimage
    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Displaying photoimage in the label
    label_widget.photo_image = photo_image

    # Configure image in the label
    label_widget.configure(image=photo_image)

    # Repeat the same process after every 10 seconds
    label_widget.after(10, open_camera)


# Create a button to open the camera in GUI app
button1 = Button(app, text="Open Camera", command=open_camera)
button1.pack()

# Create an infinite loop for displaying app on screen
app.mainloop()

