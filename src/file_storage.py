# standard library imports
import os, json, datetime

# local app imports
from src.utils import Utils

class FileStorage:
    """
    class for handling saving and loading of data in
    storage json files
    """

    def __init__(self) -> None:
        self.file = False
        self.file_path = "./src/storage/db.json"

        # specify class attributes to save to storage
        self.save_list = [
            'admins',
            'students',
            'admission_applications'
        ]

    def load(self) -> None:
        """
        read and load from the storage file
        """

        # check if file exists before loading/reading
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.file = f.read()
                self.file = json.loads(self.file)

            return self.file

        return

    def save(self, save_object = None) -> None:
        """
        save given object to the storage file
        first read the file if not empty, then append save object to file
        
        @self: referencing the class
        @save_object: reference to instance of class whose __dict__ is to be saved
        """

        # return if save object not passed
        if not save_object:
            return

        # get dictionary representation of save_object
        save_object_dict = save_object.__dict__
        save_object = {}

        # parse save_object and collect only items in save_list
        for item in self.save_list:
            if not save_object_dict.get(item):
                continue

            save_object[item] = save_object_dict[item]

        # dump save object to json
        self.file = json.dumps(save_object, indent=4)

        # write json to file
        with open(self.file_path, 'w') as f:
            f.write(self.file)
            
# instantiate class instance        
Storage = FileStorage()
