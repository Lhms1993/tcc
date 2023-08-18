import cv2
import copy

from mfrc522 import SimpleMFRC522
from PyQt5 import QtCore, QtWidgets, QtGui, QtGui

from capture_image_to_create_user import CaptureImageToCreateUser
from user_manager import UserManager
from ui.createuserwindow import Ui_CreateUserWindow

INSTRUCTIONS = """O nome do usuário deve ter entre 10 e 100 caracteres.
Todas as 10 imagens de faces devem ser preenchidas.

"""
class ReadRFID(QtCore.QObject):
    rfid_found = QtCore.pyqtSignal(int)
    def __init__(self):
        super(ReadRFID, self).__init__()
        self.execute = True
        self.MIFAREReader = SimpleMFRC522()
        
    def run(self):
        while self.execute:
            rfid_id = self.MIFAREReader.read()[0]
            if rfid_id:
                self.rfid_found.emit(rfid_id)
    
    def stop(self):
        self.execute = False
                                

class CreateUserWindow(QtWidgets.QMainWindow, Ui_CreateUserWindow):
    def __init__(self, parent, new_user, user_name=None):
        super(CreateUserWindow, self).__init__()
        self.setupUi(self)
        self.main_window = parent
        self.user_manager = UserManager()
        if (not new_user) and self.user_manager.check_user(user_name):
            self.new_user = False
            self.user_name = user_name
        else:
            self.new_user = True
            self.user_name = ""
            
        
        self.face_list = {}
        self.create_global_variables_access_to_widgets()
        self.init_ui()

        self.show()
    
    def create_global_variables_access_to_widgets(self):
        global btn_face_normal_capture
        btn_face_normal_capture = self.btn_face_normal_capture

        global btn_face_normal_clear
        btn_face_normal_clear = self.btn_face_normal_clear

        global label_face_normal
        label_face_normal = self.label_face_normal

        global btn_face_sleepy_capture
        btn_face_sleepy_capture = self.btn_face_sleepy_capture

        global btn_face_sleepy_clear
        btn_face_sleepy_clear = self.btn_face_sleepy_clear

        global label_face_sleepy
        label_face_sleepy = self.label_face_sleepy

        global btn_face_happy_capture
        btn_face_happy_capture = self.btn_face_happy_capture

        global btn_face_happy_clear
        btn_face_happy_clear = self.btn_face_happy_clear

        global label_face_happy
        label_face_happy = self.label_face_happy

        global btn_face_wink_capture
        btn_face_wink_capture = self.btn_face_wink_capture

        global btn_face_wink_clear
        btn_face_wink_clear = self.btn_face_wink_clear

        global label_face_wink
        label_face_wink = self.label_face_wink

        global btn_face_surprised_capture
        btn_face_surprised_capture = self.btn_face_surprised_capture

        global btn_face_surprised_clear
        btn_face_surprised_clear = self.btn_face_surprised_clear

        global label_face_surprised
        label_face_surprised = self.label_face_surprised

        global btn_face_rightlight_capture
        btn_face_rightlight_capture = self.btn_face_rightlight_capture

        global btn_face_rightlight_clear
        btn_face_rightlight_clear = self.btn_face_rightlight_clear

        global label_face_rightlight
        label_face_rightlight = self.label_face_rightlight

        global btn_face_leftlight_capture
        btn_face_leftlight_capture = self.btn_face_leftlight_capture

        global btn_face_leftlight_clear
        btn_face_leftlight_clear = self.btn_face_leftlight_clear

        global label_face_leftlight
        label_face_leftlight = self.label_face_leftlight

        global btn_face_sad_capture
        btn_face_sad_capture = self.btn_face_sad_capture

        global btn_face_sad_clear
        btn_face_sad_clear = self.btn_face_sad_clear

        global label_face_sad
        label_face_sad = self.label_face_sad

        global btn_face_centerlight_capture
        btn_face_centerlight_capture = self.btn_face_centerlight_capture

        global btn_face_centerlight_clear
        btn_face_centerlight_clear = self.btn_face_centerlight_clear

        global label_face_centerlight
        label_face_centerlight = self.label_face_centerlight

        global btn_face_glasses_capture
        btn_face_glasses_capture = self.btn_face_glasses_capture

        global btn_face_glasses_clear
        btn_face_glasses_clear = self.btn_face_glasses_clear

        global label_face_glasses
        label_face_glasses = self.label_face_glasses
    
    def configure_reset_faces(self):
        for face_name in self.face_list.keys():
            globals()[f'btn_face_{face_name}_capture'].clicked.connect(
                lambda x, face_name=face_name: self.capture_face(face_name)
            )
            
            globals()[f'btn_face_{face_name}_clear'].clicked.connect(
                lambda x, face_name=face_name: self.clear_face(face_name)
            )

            if self.new_user:
                globals()[f'btn_face_{face_name}_clear'].setEnabled(False)
                globals()[f'btn_face_{face_name}_capture'].setEnabled(True)
            else:
                globals()[f'btn_face_{face_name}_clear'].setEnabled(True)
                globals()[f'btn_face_{face_name}_capture'].setEnabled(False)

    def init_ui(self):
        if self.new_user:
            self.face_list = {
                'normal': None,
                'sleepy': None,
                'happy': None,
                'wink': None,
                'surprised': None,
                'rightlight': None,
                'leftlight': None,
                'sad': None,
                'centerlight': None,
                'glasses': None
            }
        else:
            user_data = self.user_manager.read_user(user_name=self.user_name)

            user_birthday = QtCore.QDate(
                int(user_data['user_birthday'].split("/")[2]),
                int(user_data['user_birthday'].split("/")[1]),
                int(user_data['user_birthday'].split("/")[0])
            )

            self.date_user_birthday.setDate(user_birthday)
            self.txt_user_name.setText(user_data['user_name'])
            self.txt_user_rfid.setText(str(user_data['user_rfid']))
            self.face_list = user_data['face_list']
            self.fill_images_on_screen(self.face_list)
        
        self.configure_reset_faces()
        self.txt_instructions_to_create.setText(INSTRUCTIONS)

        regex = QtCore.QRegExp("[a-zA-Z ]+")
        validator = QtGui.QRegExpValidator(regex)
        self.txt_user_name.setValidator(validator)
        self.txt_user_name.setMaxLength(100)

        self.btn_capture_faces.setEnabled(True)
        self.btn_capture_faces.clicked.connect(self.capture_process)
        self.btn_save.clicked.connect(self.save_user)
        self.btn_cancel.clicked.connect(self.close)
        self.btn_input_rfid.clicked.connect(self.read_rfid)
    
    def read_rfid(self):
        self.thread = QtCore.QThread()
        self.rfid_worker = ReadRFID()
        self.rfid_worker.moveToThread(self.thread)
        self.thread.started.connect(self.rfid_worker.run)
        self.rfid_worker.rfid_found.connect(self.rfid_found)
        self.btn_input_rfid.setEnabled(False)
        self.thread.start()
    
    def rfid_found(self, rfid_id):
        self.rfid_worker.stop()
        self.txt_user_rfid.setText(str(rfid_id))
        self.btn_input_rfid.setEnabled(False)
    
    def capture_process(self):
        faces_to_capture = []
        for face_name in self.face_list.keys():
            if self.face_list[face_name] is None:
                faces_to_capture.append(face_name)

        if len(faces_to_capture) == 0:
            error_msg = "ERRO: Limpe as imagens que deseja substituir e depois faça a captura."
            self.txt_instructions_to_create.setText(INSTRUCTIONS+error_msg)
            return

        self.camera_window = CaptureImageToCreateUser(faces_to_capture)
        self.camera_window.signals.close.connect(self.fill_images_on_screen)
        self.camera_window.show()
        self.hide()
    
    def fill_images_on_screen(self, captured_images: dict):
        for face_name in captured_images.keys():
            if captured_images[face_name] is None:
                continue

            self.face_list[face_name] = captured_images[face_name]
            
            globals()[f'btn_face_{face_name}_capture'].setEnabled(False)
            globals()[f'btn_face_{face_name}_clear'].setEnabled(True)
            
            image = QtGui.QImage(
                self.face_list[face_name],
                self.face_list[face_name].shape[1],
                self.face_list[face_name].shape[0],
                QtGui.QImage.Format_RGB888
            )

            pixmap =  QtGui.QPixmap.fromImage(image)
            pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
            globals()[f'label_face_{face_name}'].setPixmap(pixmap)

        self.show()

    def capture_face(self, face_name):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            frame = cv2.imread(fileName, cv2.IMREAD_GRAYSCALE)
            
            self.face_list[face_name] = copy.copy(frame)
            globals()[f'btn_face_{face_name}_capture'].setEnabled(False)
            globals()[f'btn_face_{face_name}_clear'].setEnabled(True)
            
            pixmap = QtGui.QPixmap(fileName)
            pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
            globals()[f'label_face_{face_name}'].setPixmap(pixmap)

    def clear_face(self, face_name):
        globals()[f'label_face_{face_name}'].clear()
        globals()[f'btn_face_{face_name}_capture'].setEnabled(True)
        globals()[f'btn_face_{face_name}_clear'].setEnabled(False)
        self.face_list[face_name] = None
    
    def save_user(self):
        error_msg = ""
        if (not self.new_user) and (self.txt_user_name.text() != self.user_name):
            error_msg += "ERRO: O nome do usuário não poder ser editado. Exclua o usuário e crie um novo com o nome correto.\n"

        if len(self.txt_user_name.text()) < 10:
            error_msg += "ERRO: Nome curto demais. O nome do usuário deve conter, pelo menos, 10 caracteres.\n"
        
        if len(self.txt_user_rfid.text()) == 0:
            error_msg += "ERRO: É necessário cadastrar uma TAG RFID para o usuário"

        for frame in self.face_list.values():
            if frame is None:
                error_msg += "ERRO: É necessário capturar todas 10 faces para registar usuário.\n"
                break

        if error_msg:
            self.txt_instructions_to_create.setText(INSTRUCTIONS+error_msg)
            return

        user_data = {
            'user_name': self.txt_user_name.text(),
            'user_birthday': self.date_user_birthday.text(),
            'user_faces': self.face_list,
            'user_rfid': int(self.txt_user_rfid.text())
        }
        result, msg = self.user_manager.create_update_user(
            user_data=user_data, new_user=self.new_user    
        )

        self.txt_instructions_to_create.setText(INSTRUCTIONS+msg)
        

    def closeEvent(self, event) -> None:
        self.main_window.show()
        self.hide()