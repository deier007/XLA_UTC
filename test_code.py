import tkinter as tk
import cv2
import numpy as np
import face_recognition
import os
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng với Menu")
        self.root.geometry("1080x720")

        # Biến toàn cục để lưu trữ đối tượng video capture và label_img
        self.cap = None
        self.label_img = None

        # Tạo label để hiển thị video stream
        self.label = tk.Label(self.root)
        self.label.pack()

        # Tạo menu bar
        self.menu_bar = tk.Menu(self.root)

        # Tạo menu Login
        self.login_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.login_menu.add_command(label="Login", command=self.login)

        # Tạo menu Setup
        self.setup_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.setup_menu.add_command(label="Setup Mcu", command=self.setup)

        # Tạo menu Library
        self.library_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.library_menu.add_command(label="Library", command=self.library)

        # Thêm các menu vào menu bar
        self.menu_bar.add_cascade(label="Login", menu=self.login_menu)
        self.menu_bar.add_cascade(label="Setup", menu=self.setup_menu)
        self.menu_bar.add_cascade(label="Library", menu=self.library_menu)

        # Cài đặt menu bar vào cửa sổ
        self.root.config(menu=self.menu_bar)

        # Load dữ liệu nhận diện khuôn mặt
        self.images = []
        self.classNames = []
        self.load_face_encodings()

    def load_face_encodings(self):
        path = 'ImagesBasic'  # Thư mục chứa ảnh mẫu
        myList = os.listdir(path)
        print(myList)
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            self.images.append(curImg)
            self.classNames.append(os.path.splitext(cl)[0])
        print(self.classNames)
        self.encodeListKnown = self.findEncodings(self.images)
        print("Encoder Completed")

    def findEncodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    # Hàm xử lý khi chọn Login - mở camera và hiển thị ảnh liên tục trên Label
    def login(self):
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Không thể mở camera")
            return

        # Gọi hàm cập nhật video liên tục
        self.update_frame()

    # Hàm cập nhật khung hình video liên tục
    def update_frame(self):
        ret, frame = self.cap.read()

        if ret:
            # Lật ảnh theo chiều ngang (có thể bỏ qua nếu không cần)
            frame = cv2.flip(frame, 1)

            # Chuyển đổi màu sắc từ BGR (OpenCV) sang RGB (Tkinter)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Phát hiện khuôn mặt trong ảnh
            facesCurFrame = face_recognition.face_locations(frame_rgb)
            encodeCurFrame = face_recognition.face_encodings(frame_rgb, facesCurFrame)

            for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = self.classNames[matchIndex].upper()
                    print(name)

                    # Vẽ khung và hiển thị tên
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.putText(frame, name, (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

            # Chuyển ảnh thành đối tượng Image từ Pillow
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)

            # Cập nhật ảnh lên label
            if self.label_img is None:
                self.label_img = self.label.configure(image=img_tk)
            else:
                self.label.configure(image=img_tk)

            # Đảm bảo ảnh không bị garbage collected
            self.label.img_tk = img_tk

        # Đặt lại hàm update_frame sau 10ms để tạo vòng lặp liên tục
        self.label.after(10, self.update_frame)

    # Hàm xử lý khi chọn Setup
    def setup(self):
        # Xóa nội dung hiện tại trên canvas
        self.label.configure(image="")
        self.label.img_tk = None
        self.label.create_text(540, 150, text="Đây là nội dung của SetUp", font=("Arial", 20, "bold"), fill="blue")
        self.label.create_rectangle(100, 200, 980, 500, outline="green", width=3)
        self.label.create_oval(100, 550, 980, 700, outline="red", width=3)

    # Hàm xử lý khi chọn Library và vẽ nội dung lên canvas
    def library(self):
        # Xóa nội dung hiện tại trên canvas
        self.label.configure(image="")
        self.label.img_tk = None
        self.label.create_text(540, 150, text="Đây là nội dung của Library", font=("Arial", 20, "bold"), fill="blue")
        self.label.create_rectangle(100, 200, 980, 500, outline="green", width=3)
        self.label.create_oval(100, 550, 980, 700, outline="red", width=3)

# Tạo cửa sổ chính
root = tk.Tk()

# Tạo đối tượng của lớp App
app = App(root)

# Chạy ứng dụng
root.mainloop()
