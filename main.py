from Modules.FileStorage import FileStorage 

"""
User class
"""

class User:
    """
    constructor class
    """
    def __init__(self):
        """
        overwrites manually instantiated class attributes with class \
        attributes from last time state was saved - might result in state \
        errors
        """
        self.loadStorage()

        # instantiate class attributes
        self.shell = True
        self.user = 'guest'
        self.userInput = ""
        self.prompt = f"(pyShell <> {self.user}):   "

        """
        self.setPermissions: set user permissions
        self.runShell: run the shell of the program
        """
        self.setPermissions()
        self.runShell()


    """
    start up the python shell for input
    """
    def runShell(self):
        while self.shell:
            self.userInput = input(self.prompt)
            print(f"Hey, you said: {self.userInput}")

            self.shell = False
            

    """
    set user permissions for guest, admin and student
    """
    def setPermissions(self):
        try:
            if self.userPermissions:
                return
        except:
            pass

        self.userPermissions = {
            'guest': ['view'],
            'student': ['view'],
            'admin': []
        }

    """
    load data from file storage
    """
    def loadStorage(self):
        load = FileStorage.load()

        if load:    
            self.__dict__.update(load)

    """
    save to file storage upon exit of program
    """
    def __del__(self):
        FileStorage.save(self)


#initialize class
User()
