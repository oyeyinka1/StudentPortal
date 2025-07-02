import os, json
import datetime
from Modules.Utils import Utils

"""
File storage class for handling saving and loading of data in
storage json files
"""

def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(i) for i in obj]
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    else:
        return obj

class FileStorage:
    """
    constructor function
    """
    def __init__(self):
        self.file = False
        self.filePath = "./Modules/Storage/db.json"

        # specify class attributes to save to storage
        self.saveList = [
            'admissionApplications',
            'admins',
            'students'
        ]

    """
    read and load from the storage file
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
        saveObjectDict = saveObject.__dict__
        saveObject = {}

        # parse saveObject and collect only items in saveList
        for item in self.saveList:
            if not saveObjectDict.get(item):
                continue

            saveObject[item] = saveObjectDict[item]

        # dump save object to json
        self.file = json.dumps(saveObject, indent=4)

        # write json to file
        with open(self.filePath, 'w') as f:
            f.write(self.file)
            
        
Storage = FileStorage()
