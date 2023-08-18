import os
import sys

# FACE IMPORTS
import time
import pickle
from PIL import Image
import numpy as np
from typing import List

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor

from insightface.app import FaceAnalysis
from sklearn.neighbors import NearestNeighbors
from ui.traininglogswindow import Ui_MainWindow

TRAIN_DATASET_DIR = 'data/new_yale_faces'
TRAINED_MODEL_FILE = 'src/faceID_model.pkl'
TRAINED_LABELS_FILE = 'src/faceID_model_labels.npy'

execution_dir = os.getcwd()
sys.path.append(execution_dir)

class Signals(QObject):
    completed = pyqtSignal()

class TrainingThread(QtCore.QRunnable):
    def __init__(self, output_text_edit):
        super(TrainingThread, self).__init__()
        self.output_logger = output_text_edit
        self.eval_set = list()
        self.eval_labels = list()
        self.probe_set = list()
        self.probe_labels = list()
        self.evaluation_embs = None
        self.evaluation_labels = None
        self.probe_embs = None
        self.inds = None
        self.nn = NearestNeighbors(n_neighbors=3, metric="cosine")

        self.signals = Signals()
        
    def run(self):
        self.insightface_model()
        self.output_logger.moveCursor(QTextCursor.End)
        # self.show_dataset_images()
        
        self.generate_probe_eval()
        self.output_logger.moveCursor(QTextCursor.End)
        
        self.check_values()
        self.output_logger.moveCursor(QTextCursor.End)
        
        self.training_model()
        self.output_logger.moveCursor(QTextCursor.End)
        
        self.make_inference()
        self.output_logger.moveCursor(QTextCursor.End)
        
        self.evaluate_metrics()
        self.output_logger.moveCursor(QTextCursor.End)

        self.signals.completed.emit()
    
    def insightface_model(self):
        self.output_logger.append("Prepare Insightface model - START")
        try:
            self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
            self.face_app.prepare(ctx_id=0, det_size=(640, 640))
            self.output_logger.append("Prepare Insightface model - FINSH")
            return True
        except Exception as ex:
            self.output_logger.append(f"Prepare Insightface model - ERROR: {ex}")
            return False
    
    def create_probe_eval(self, files: List):
        # pick random index between 0 and len(files)-1
        random_idx = np.random.randint(0,len(files))
        probe_img_fpaths = [files[random_idx]]
        eval_img_fpaths = [files[idx] for idx in range(len(files)) if idx != random_idx]
        
        return probe_img_fpaths, eval_img_fpaths

    def generate_embs(self, img_fpaths: List[str]):
        embs_set = list()
        embs_label = list()
        for i, img_fpath in enumerate(img_fpaths):  
            time.sleep(0.010)
            # read grayscale img
            img = Image.open(os.path.join(TRAIN_DATASET_DIR, img_fpath)) 
            img_arr = np.asarray(img)  
            
            # convert grayscale to rgb
            im = Image.fromarray((img_arr * 255).astype(np.uint8))
            rgb_arr = np.asarray(im.convert('RGB'))
        
            # generate Insightface embedding
            emb_res = self.face_app.get(rgb_arr)
            try:
                res = emb_res[0].embedding
                # append emb to the eval set
                embs_set.append(res)
                # append label to eval_label set
                embs_label.append(img_fpath.split("_")[0])
            except:
                self.output_logger.append(f'No embedding found for this image: {img_fpath}')
        return embs_set, embs_label

    def generate_probe_eval(self):
        files = os.listdir(TRAIN_DATASET_DIR)
        files.sort()
        IMAGES_PER_IDENTITY = 11
        for i in range(1, len(files), IMAGES_PER_IDENTITY): # ignore the README.txt file at files[0]

            # print(i)
            image_title = files[i:i+IMAGES_PER_IDENTITY][0].split('_')[0]
            self.output_logger.append(f"Calculate probabilities and evaluators of {image_title} images - START")
            probe, eval = self.create_probe_eval(files[i:i+IMAGES_PER_IDENTITY])
            
            # store eval embs and labels
            self.eval_set_t, self.eval_labels_t = self.generate_embs(eval)
            self.eval_set.extend(self.eval_set_t)
            self.eval_labels.extend(self.eval_labels_t)
            
            # store probe embs and labels
            self.probe_set_t, self.probe_labels_t = self.generate_embs(probe)
            self.probe_set.extend(self.probe_set_t)
            self.probe_labels.extend(self.probe_labels_t)
            self.output_logger.append(f'Calculate probabilities and evaluators of {image_title} images - FINISH')
            self.output_logger.moveCursor(QTextCursor.End)

    def check_values(self):
        self.output_logger.append('Check probabilities and evaluators values - START')
        assert len(self.eval_set) == len(self.eval_labels)
        assert len(self.probe_set) == len(self.probe_labels)

        self.evaluation_embs, self.evaluation_labels = self.eval_set, self.eval_labels
        self.probe_embs, self.probe_labels = self.probe_set, self.probe_labels

        assert len(self.evaluation_embs) == len(self.evaluation_labels)
        assert len(self.probe_embs) == len(self.probe_labels)
        self.output_logger.append('Check probabilities and evaluators values - FINISH')
    
    def training_model(self):
        # Train KNN classifier
        self.output_logger.append('Train model - START')
        self.nn.fit(X=self.evaluation_embs)
        self.output_logger.append('Train model - FINISH')

        # Optional - saving and loading model
        # save the model to disk
        self.output_logger.append('Save file of model - START')
        with open(TRAINED_MODEL_FILE, 'wb') as file:
            pickle.dump(self.nn, file)

        with open(TRAINED_LABELS_FILE, 'wb') as file:
            np.save(file, np.array(self.evaluation_labels))

        self.output_logger.append('Save file of model - FINISH')
        
    def make_inference(self):
        self.output_logger.append('Make inference IDs - START')
        dists, self.inds = self.nn.kneighbors(X=self.probe_embs, n_neighbors=2, return_distance=True)
        self.output_logger.append('Make inference IDs - FINISH')
    
    def evaluate_metrics(self):
        # p@k
        self.output_logger.append('Evaluate metrics - START')
        p_at_k = np.zeros(len(self.probe_embs))
        for i in range(len(self.probe_embs)):
            true_label = self.probe_labels[i]
            pred_neighbr_idx = self.inds[i]
            
            pred_labels = [self.evaluation_labels[id] for id in pred_neighbr_idx]
            pred_is_labels = [1 if label == true_label else 0 for label in pred_labels]
            
            p_at_k[i] = np.mean(pred_is_labels)
            
        p_at_k.mean()
        self.output_logger.append('Evaluate metrics - FINISH')

class StartTrainingNetworkWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent):
        super(StartTrainingNetworkWindow, self).__init__()
        self.setupUi(self)
        self.main_window = parent

        self.btn_back_page.setEnabled(False)
        self.btn_back_page.clicked.connect(self.close_window)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        pool = QtCore.QThreadPool.globalInstance()
        runnable = TrainingThread(self.txt_training_logs)
        runnable.signals.completed.connect(self.finished_training)
        pool.start(runnable)
        
        self.show()
    
    def finished_training(self):
        self.btn_back_page.setEnabled(True)
    
    def closeEvent(self, event) -> None:
        event.ignore()
    
    def close_window(self):
        print('start_train_network')
        self.main_window.show()
        self.hide()