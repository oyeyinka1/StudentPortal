import os
import json

"""
File storage class for handling saving and loading of data in
storage json files
"""

class FileStorage:
    """
    constructor function
    """
    def __init__(self):
        self.file = False
        self.filePath = "./Modules/Storage/db.json"

    """
    read and data from the storage file
    """

    def load(self):
        # check if file exists before loading/reading
        if os.path.exists(self.filePath):
            with open(self.filePath, 'r') as f:
                self.file = f.read()
                self.file = json.loads(self.file)

            return self.file

        return

    """
    save given object to the storage file
    first read the file if not empty, then append save object to file

    @self: referencing the class
    @saveObject: reference to instance of class whose __dict__ is to be saved
    """

    def save(self, saveObject):
        # get dictionary representation of saveObject
        saveObject = saveObject.__dict__

        self.file = json.dumps(saveObject)

        with open(self.filePath, 'w') as f:
            f.write(self.file)
            
        
storage = FileStorage()
