import cv2
import numpy as np
import face_recognition
import os
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ****************************************************************************************************
# Load images from the folder
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

# Function to encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print("Encoder Completed")

# ****************************************************************************************************
# Define a video capture object
cap = cv2.VideoCapture(0)

# Set video capture properties (optional, to set width and height)
width, height = 600, 400
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# ****************************************************************************************************
# Create a GUI app
app = tk.Tk()
app.title("Face Recognition App")
app.geometry("800x600")

# Bind the app with Escape keyboard to quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())

# ****************************************************************************************************
# Create a label to display the camera feed
label_widget = Label(app)
label_widget.pack()

# ****************************************************************************************************
# Function to open the camera and process each frame
def open_camera():
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        return

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Resize image for faster processing
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.putText(img, name, ((x1 + 6), y1 - 6), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
            
            # If the name is found in classNames, transition to Library screen
            if name in classNames:
                print(f"{name} found, moving to Library")
                show_library_screen(name)
                return
        else:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.putText(img, "Unknown", ((x1 + 6), y1 - 6), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

    # Convert the image to a format that Tkinter can display
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    captured_image = Image.fromarray(image)
    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Display the image on the Tkinter label
    label_widget.photo_image = photo_image
    label_widget.configure(image=photo_image)

    # Repeat the process after every 10ms
    label_widget.after(10, open_camera)

# ****************************************************************************************************
# Function to show the library screen
# Function to show the library screen
def show_library_screen(user_name):
    # Stop the camera by releasing the capture object
    cap.release()
    
    # Hide the camera feed
    label_widget.pack_forget()

    # Create a new screen to display the library
    library_frame = Frame(app)
    library_frame.pack(fill="both", expand=True)

    # Add a welcome message
    welcome_label = Label(library_frame, text=f"Welcome {user_name}, Here are some books!", font=("Arial", 20))
    welcome_label.pack(pady=20)

    # Add a table for books
    tree = ttk.Treeview(library_frame, columns=("No.", "Book Title"), show="headings")
    tree.heading("No.", text="No.")
    tree.heading("Book Title", text="Book Title")

    books = [("1", "Python Programming"), ("2", "Data Science"), ("3", "Machine Learning")]

    for book in books:
        tree.insert("", "end", values=book)

    tree.pack(pady=20)

    # Add a "Get" button
    def on_get_button_click():
        # Disable the "Get" and "Back to Camera" buttons
        get_button.config(state="disabled")
        back_button.config(state="disabled")

        # Show "In progress" label
        progress_label = Label(library_frame, text="In progress...", font=("Arial", 16))
        progress_label.pack(pady=20)

        # After 4 seconds, hide the progress label and delete the book
        library_frame.after(4000, lambda: [progress_label.pack_forget(),
                                          remove_book_from_tree(),
                                          get_button.config(state="normal"),
                                          back_button.config(state="normal")])

    def remove_book_from_tree():
        # Remove the first book from the tree (example: the first one in the list)
        if len(books) > 0:
            book_to_remove = books[0]  # Remove the first book (for example)
            for item in tree.get_children():
                if tree.item(item, "values")[0] == book_to_remove[0]:  # Match by the book number
                    tree.delete(item)
                    books.remove(book_to_remove)  # Remove from the book list
                    break

    get_button = Button(library_frame, text="Get", command=on_get_button_click)
    get_button.pack(pady=20)

    # Add a back button to go back to camera feed
    def go_back_to_camera():
        # Release the camera capture when going back to camera view
        cap.release()

        # Hide the library frame
        library_frame.pack_forget()

        # Initialize the video capture again and open the camera feed
        # cap.open(0)
        # open_camera()  # Start camera feed again

    back_button = Button(library_frame, text="Back to Camera", command=go_back_to_camera)
    back_button.pack(pady=20)

# ****************************************************************************************************
# Create the menu bar
menubar = Menu(app)

# Function for 'Login' action
def login_action():
    print("Login clicked")
    cap.open(0)
    open_camera()

# Function for 'SetUp' action
def setup_action():
    print("Setup clicked")
    # Implement Setup functionality here

# Function for 'Library' action
def library_action():
    print("Library clicked")
    # Implement Library functionality here

# Create 'File' menu
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Login", command=login_action)

setup_menu = Menu(menubar, tearoff=0)
setup_menu.add_command(label="SetUp", command=setup_action)

library_menu = Menu(menubar, tearoff=0)
library_menu.add_command(label="Library", command=library_action)

menubar.add_cascade(label="Login", menu=file_menu)
menubar.add_cascade(label="SetUp", menu=setup_menu)
menubar.add_cascade(label="Library", menu=library_menu)

# Add menu to the window
app.config(menu=menubar)

# Run the GUI main loop
app.mainloop()

# ****************************************************************************************************
# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
