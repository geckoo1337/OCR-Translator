# OCR-Translator - everything we need as dependencies
# However, there is a conflict using Cuda, Torch and sometimes other dependencies. 
# In this case, the best way is to uninstall Torch applying instead its nightly version : 
# uv pip uninstall torch
# uv install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
import cv2
import easyocr
import sys
# Qt for a clean user interface
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from deep_translator import GoogleTranslator # translator
import numpy as np
# initialize EasyOCR - True using CUDA or False using CPU 
reader = easyocr.Reader(['ru','en'], True)
# Using CPU. Note: This module is much faster with a GPU.
# buttons info
stop_feeding = "Translate"
start_feeding = "Start Cam"
exit_button = "Close App"
# simple boolean to get filter mode
myFilter = False

class OCR_Translator(QMainWindow):
   
    def __init__(self):
        super().__init__()
        # Qt windows Interface
        width = 1250
        height = 550
        # setting the fixed width & height of window
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.setWindowTitle("Optical Character Recognition Translator")
        self.setGeometry(200, 200, height, width)
        # style sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #171e30;
            }
            /* text fields */            
            QTextEdit {
                background-color: #131c31;
                color: #d4d6ff;
                border: 2px solid #5c6bff;
                border-radius: 10px;
                font: 15pt 'Calibri';
            }
            /* start & stop button */               
            QPushButton#start_stop_button {
                background-color: #8292ff;
                color: #1f283e;
                font: 16pt 'Trebuchet MS';
                border: none;
                border-radius: 10px;
                margin: 5px 2px;
                padding: 10px 50px;
            }
                           
            QPushButton#start_stop_button:hover {
                background-color: #87ffff;
            }
            /* close button */ 
            QPushButton#exit_button {
                background-color: #8292ff;
                color: #1f283e;
                font: 16pt 'Trebuchet MS';
                border: none;
                border-radius: 10px;
                margin: 5px 2px;
                padding: 10px 50px;
            }
            QPushButton#exit_button:hover {
                background-color: #f100cc;
            }
            /* close button */              
            QPushButton#filter_button {
                background-color: #8292ff;
                color: #1f283e;
                font: 16pt 'Trebuchet MS';
                border: none;
                border-radius: 10px;
                margin: 5px 2px;
                padding: 10px 50px;
            }
            QPushButton#filter_button:hover {
                background-color: #87ffff;
            }
            /* main app features */              
            QLabel {
                background-color: #1eFF2e;
                border: 1px solid #6272a4;
            }

            start
        """)
        self.video_running = True
        self.initUI()
    # initialize UI
    def initUI(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        # layouts
        self.main_layout = QHBoxLayout()    # Horizontal layout for main window
        self.video_layout = QVBoxLayout()   # Vertical layout for video frame
        self.text_layout = QVBoxLayout()    # Vertical layout for text field and buttons
        # video frame label
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        # text_field for result
        self.text_field1 = QTextEdit(self)
        self.text_field1.setReadOnly(True)
        self.text_layout.addWidget(self.text_field1)
        # text_field for full recognized text
        self.text_field2 = QTextEdit(self)
        self.text_field2.setReadOnly(True)
        self.text_layout.addWidget(self.text_field2)
        # buttons layout
        buttons_layout = QHBoxLayout()
        # start_stop_button
        self.start_stop_button = QPushButton(stop_feeding, self)
        self.start_stop_button.setObjectName("start_stop_button")
        self.start_stop_button.setFixedSize(250, 60)
        self.start_stop_button.clicked.connect(self.toggle_video_feed)
        buttons_layout.addWidget(self.start_stop_button)
        # exit_button
        self.exit_button = QPushButton(exit_button, self)
        self.exit_button.setObjectName("exit_button")
        self.exit_button.setFixedSize(250, 60)
        self.exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.exit_button)
        # filter_button
        self.filter_button = QPushButton("#", self)
        self.filter_button.setObjectName("filter_button")
        self.filter_button.setFixedSize(60, 60)
        self.filter_button.clicked.connect(self.applyFilter)
        buttons_layout.addWidget(self.filter_button)
        # add buttons layout to text layout
        self.text_layout.addLayout(buttons_layout)
        # add video layout and text layout to main layout
        self.main_layout.addLayout(self.video_layout)
        self.main_layout.addLayout(self.text_layout)
        self.central_widget.setLayout(self.main_layout)
        # video feed capture using OpenCv
        self.cap = cv2.VideoCapture(0)
        # setting timer for video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(10)
    # OCR
    def recognize_text(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray)
        global recognized_text
        recognized_text = "" # buffer
        # text recognition with easyOCR
        for (bbox, text, _) in results:
            # bounding box and label
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=1)
            recognized_text += text + "\n" # for broken boxes
        # clean up fields
        self.text_field1.clear()
        self.text_field2.clear()
        # here we can check available entries which are in the buffer
        self.text_field1.append(recognized_text.strip()) # text brut
        return frame

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            # convert frame to RGB or HSV for displaying in PyQt5
            if myFilter is True:
                frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # process frame to recognize text and draw bounding boxes
            frame_with_boxes = self.recognize_text(frame)
            # converting frame to QImage
            h, w, ch = frame_with_boxes.shape
            bytes_per_line = ch * w
            # convert frame to Qt format 
            convert_to_Qt_format = QImage(frame_with_boxes.data, w, h, bytes_per_line, QImage.Format_RGB888)
            c = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.video_label.setPixmap(QPixmap.fromImage(c))
            
    def toggle_video_feed(self):
        self.video_running = not self.video_running
        if self.video_running:
            self.timer.start(10)
            self.start_stop_button.setText(stop_feeding)
        else:
            self.timer.stop()
            self.start_stop_button.setText(start_feeding)
            # catch the frame and translate the Russian text to English language
            translation = GoogleTranslator(source='ru', target='en').translate(recognized_text)
            self.text_field2.append(translation) # translated text
    # invert boolean for image filter
    def applyFilter(self):
        if self.video_running:
            global myFilter
            myFilter = not myFilter
        else:
            return
    # close app
    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()
# run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCR_Translator()
    window.show()
    sys.exit(app.exec_())
# EOF
