import re
import cv2
import pickle
import numpy as np

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, QRunnable, QObject, pyqtSignal, QThreadPool
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox

from insightface.app import FaceAnalysis

TRAINED_MODEL_FILE = 'src/faceID_model.pkl'
TRAINED_LABELS_FILE = 'src/faceID_model_labels.npy'
CONFIABILITY = 0.95
DIMENSION = (320, 243)


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
    result = pyqtSignal(bool, str, float)

class MakeInference(QRunnable):
    def __init__(self):
        super(MakeInference, self).__init__()
        print("1")
        self.model_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        print("2")
        self.model_app.prepare(ctx_id=0, det_size=(640, 640))
        print("3")
        with open(TRAINED_MODEL_FILE, 'rb') as file:
            self.model = pickle.load(file, encoding='utf-8')
        print("4")
        with open(TRAINED_LABELS_FILE, 'rb') as file:
            self.model_labels = np.load(TRAINED_LABELS_FILE)
        print("5")
        self.signals = Signals()
        self.frame = None
        self.execute = True
    
    def stop(self):
        self.execute = False
    
    def run(self):
        while self.execute:
            if self.frame is None:
                continue
            try:
                img_emb = self.model_app.get(self.frame)[0].embedding
                
                dists, inds = self.model.kneighbors(X=img_emb.reshape(1,-1), n_neighbors=3, return_distance=True)
                
                pred_labels = [self.model_labels[i] for i in inds[0]]
                
                matching_faces = np.sum([1 if d <= CONFIABILITY else 0 for d in dists[0]])
                if matching_faces <= 0:
                    self.signals.result.emit(False, "", 0)
                
                user_name, confiability = sorted(zip(pred_labels, dists[0]), key=lambda x: x[1], reverse=True)[0]
                formatted_name = " ".join(re.findall('[A-Z][^A-Z]*', user_name))
                confiability =  float("{:.2f}".format(confiability*100))
                self.signals.result.emit(True, formatted_name, confiability)
            except Exception as ex:
                print("Falha")
            

class IdentifyFaces(QWidget):

    def __init__(self, parent=None, camera=0):
        super().__init__()
        self.main_window = parent
        self.camera = Camera(0)
        self.timer = QTimer()
        self.make_inference = MakeInference()
        self.info_label = QLabel("")
        self.init_ui()
        self.start()

    def init_ui(self):
        self.timer.timeout.connect(self.nextFrameSlot)
       
        layout = QVBoxLayout()

        info_layout = QHBoxLayout()
        info_layout.addWidget(self.info_label)

        layout.addLayout(info_layout)

        self.label = QLabel()
        self.label.setFixedSize(640, 480)

        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setWindowTitle("Face Recognition App")
        self.setFixedSize(660, 580)
    
    def start(self):
        self.camera.openCamera()
        self.timer.start(int(1000. / 24))

        pool = QThreadPool.globalInstance()
        self.make_inference.signals.result.connect(self.result_inference)
        pool.start(self.make_inference)
    
    def result_inference(self, result, user_name, confiability):
        if result:
            print(f"Face encontrada: {user_name} - {confiability}%.")
        else:
            print(f"Face não encontrada.")

    def stop(self):
        self.camera.closeCamera()
        self.timer.stop()

        self.info_label.clear()
        self.label.clear()

    def nextFrameSlot(self):
        rval, frame = self.camera.vc.read()
        if rval:
            frame = cv2.flip(frame, 180)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_to_check = cv2.resize(frame, DIMENSION)
            self.make_inference.frame = frame_to_check

            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label.setPixmap(pixmap)
        else:
            self.stop()
            self.info_label("Falha ao capturar obter imagem da câmera.")
    
    def closeEvent(self, event):
        self.stop()
        self.make_inference.stop()
        self.main_window.show()
        self.hide()
