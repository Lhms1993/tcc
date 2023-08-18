import os
import re
import cv2
import sys
import json
from pathlib import Path

execution_dir = os.getcwd()
sys.path.append(execution_dir)

TRAIN_DATASET_DIR = "data/new_yale_faces"


class UserManager:
    def __init__(self) -> None:
        self.users_file = 'src/users.json'
        users_file_path = Path(self.users_file)
        self.user_db = {}
        if not users_file_path.is_file():
            self.users_data = {}
            with open(self.users_file, 'w') as file:
                json.dump(self.user_db, file, indent=4)
        else:
            with open(self.users_file) as file:
                self.user_db = json.load(file)
    
    def create_update_user(self, user_data, new_user):
        unformatted_user_name = user_data['user_name']
        user_birthday = user_data['user_birthday']
        user_rfid = user_data['user_rfid']
        user_faces = user_data['user_faces']

        formatted_user_name = ""
        for part_name in unformatted_user_name.split(" "):
            formatted_user_name += part_name[0].upper()+part_name[1:].lower()
        
        if new_user and (formatted_user_name in self.user_db.keys()):
            return (False, "ERRO: Usuário já registrado no sistema. Use um nome novo ou edite o usuário já existente.")
        elif (not new_user) and (formatted_user_name not in self.user_db.keys()):
            return (False, "ERRO: O nome do usuário não poder ser editado. Exclua o usuário e crie um novo com o nome correto.")
        
        user_faces_paths = []
        for user_face in user_faces.keys():
            filename = f"{TRAIN_DATASET_DIR}/{formatted_user_name}_{user_face}.png"
            user_faces_paths.append(filename)
            frame = user_faces[user_face]
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            cv2.imwrite(filename, frame)
        
        self.user_db[formatted_user_name] = {
            'user_birthday': user_birthday,
            'user_rfid': user_rfid,
            'user_faces': user_faces_paths
        }
        self.commit_changes()
        return True, "INFO: Usuário registrado com sucesso."

    def check_user(self, user_name):
        formatted_user_name = ""
        for part_name in user_name.split(" "):
            formatted_user_name += part_name[0].upper()+part_name[1:].lower()

        if formatted_user_name in self.user_db.keys():
            return True
        return False

    def read_user(self, user_name):
        formatted_user_name = ""
        for part_name in user_name.split(" "):
            formatted_user_name += part_name[0].upper()+part_name[1:].lower()

        face_list = {}
        for face_path in self.user_db[formatted_user_name]['user_faces']:
            face_name = face_path.split("_")[-1][:-4]
            frame = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            face_list[face_name] = frame

        user_data = {
            'user_name': user_name,
            'user_birthday': self.user_db[formatted_user_name]['user_birthday'],
            'user_rfid': self.user_db[formatted_user_name]['user_rfid'],
            'face_list': face_list
        }
        return user_data

    def read_user_data(self):
        user_data = {}
        print(self.user_db)
        for user_name in self.user_db.keys():
            formatted_name = " ".join(re.findall('[A-Z][^A-Z]*', user_name))
            user_data[formatted_name] = {
                'user_birthday': self.user_db[user_name]['user_birthday'],
                'user_rfid': self.user_db[user_name]['user_rfid']
            }
        
        return user_data

    def delete_user(self, user_name):
        formatted_user_name = ""
        for part_name in user_name.split(" "):
            formatted_user_name += part_name[0].upper()+part_name[1:].lower()

        for face_path in self.user_db[formatted_user_name]['user_faces']:
            os.remove(face_path)

        del self.user_db[formatted_user_name]
        self.commit_changes()

    def commit_changes(self):
        with open(self.users_file, 'w') as file:
            json.dump(self.user_db, file, indent=4)
