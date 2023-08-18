import cv2
import copy

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QVBoxLayout, QApplication, QHBoxLayout, QMessageBox

ALL_FACES = {
    "normal": {
        "msg": "Capture uma foto séria e de olhos abertos.",
        "frame": None
    },
    "sleepy": {
        "msg": "Capture uma foto séria e de olhos fechados.",
        "frame": None
    },
    "happy": {
        "msg": "Capture uma foto sorrindo e de olhos anertos.",
        "frame": None
    },
    "wink": {
        "msg": "Capture uma foto sorrindo e de olhos fechados.",
        "frame": None
    },
    "surprised": {
        "msg": "Capture uma foto esboçando a reação de surpresa.",
        "frame": None
    },
    "rightlight": {
        "msg": "Capture uma foto com o rosto levemente voltado para a esquerda.",
        "frame": None
    },
    "leftlight": {
        "msg": "Capture uma foto com o rosto levemente voltado para a direita.",
        "frame": None
    },
    "sad": {
        "msg": "Capture uma foto esboçando a reação de tristeza.",
        "frame": None
    },
    "centerlight": {
        "msg": "Capture uma foto esboçando a reação de raiva.",
        "frame": None
    },
    "glasses":{
        "msg": "Capture uma foto de óculos (exceto escuros). Se não tiver óculos, capture uma foto séria de olhos abertos.",
        "frame": None
    }
}


class Camera:

    def __init__(self, camera):
        self.camera = camera
        self.cap = None
        self.vc = None

    def openCamera(self):
        self.vc = cv2.VideoCapture(0)
        self.vc.set(3, 640)
        self.vc.set(4, 480)

        if not self.vc.isOpened():
            msgBox = QMessageBox()
            msgBox.setText("Falha ao abrir a câmera.")
            msgBox.exec_()
            return
    
    def closeCamera(self):
        if self.vc is not None:
            self.vc.release()

    def initialize(self):
        self.cap = cv2.VideoCapture(self.camera)


class Signals(QObject):
    close = pyqtSignal(dict)


class CaptureImageToCreateUser(QWidget):

    def __init__(self, faces_to_capture, camera=0):
        super().__init__()
        self.signals = Signals()
        self.camera = Camera(0)
        self.timer = QTimer()

        self.timer.timeout.connect(self.nextFrameSlot)
        self.frame = None
        
        self.capture_sequence = {}
        for face in faces_to_capture:
            self.capture_sequence[face] = copy.copy(ALL_FACES[face])
        self.face_to_capture = None        
       
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.btn_open_camera = QPushButton("Iniciar câmera")
        self.btn_to_capture = QPushButton("Capturar")
        self.btn_finish_capture = QPushButton("Finalizar captura")

        self.btn_open_camera.clicked.connect(self.start)

        self.btn_to_capture.clicked.connect(self.to_capture)
        self.btn_to_capture.setEnabled(False)

        self.btn_finish_capture.clicked.connect(self.close)

        button_layout.addWidget(self.btn_open_camera)
        button_layout.addWidget(self.btn_to_capture)
        button_layout.addWidget(self.btn_finish_capture)

        info_layout = QHBoxLayout()
        self.info_label = QLabel("")
        info_layout.addWidget(self.info_label)

        layout.addLayout(button_layout)
        layout.addLayout(info_layout)

        self.label = QLabel()
        self.label.setFixedSize(640, 480)

        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setWindowTitle("Capturar imagens para treinamento")
        self.setFixedSize(660, 580)

    def set_info_label(self):
        for face in self.capture_sequence.keys():
            if self.capture_sequence[face]['frame'] is None:
                self.face_to_capture = face
                self.info_label.setText(self.capture_sequence[face]['msg'])
                return
        
        self.info_label.setText("Fim das capturas de imagens para treinamento.")
        self.btn_to_capture.setEnabled(False)

    def start(self):
        self.btn_open_camera.setEnabled(False)

        self.camera.openCamera()
        self.timer.start(int(1000. / 24))
        
        self.set_info_label()
        self.btn_to_capture.setEnabled(True)

    def stop(self):
        self.btn_to_capture.setEnabled(False)

        self.camera.closeCamera()
        self.timer.stop()
        self.label.clear()

        self.btn_open_camera.setEnabled(True)

    def nextFrameSlot(self):
        rval, frame = self.camera.vc.read()
        if rval:
            frame = cv2.flip(frame, 180)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame = frame

            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label.setPixmap(pixmap)
        else:
            self.stop()
            self.info_label("Falha ao capturar obter imagem da câmera.")
    
    def to_capture(self):
        if self.frame is not None:
            self.capture_sequence[self.face_to_capture]['frame'] = self.frame
            self.set_info_label()
    
    def closeEvent(self, event):
        self.stop()

        face_list = {}
        for face in self.capture_sequence.keys():
            face_list[face] = self.capture_sequence[face]['frame']
        
        self.signals.close.emit(face_list)
