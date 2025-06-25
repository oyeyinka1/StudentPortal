from Modules.FileStorage import FileStorage
from Modules.Guest import Guest
import random, string, hashlib

"""
User class
"""

class User:
    """
    constructor class
    """
    def __init__(self):
        # attributes that should rely solely on file storage
        self.admissionApplications = {}

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
        self.prompt = f"(pyShell | {self.user}):   "

        """
        self.setPermissions: set user permissions
        self.runShell: run the shell of the program
        self.setAcceptedCommands: instantiates class attribute of \
                                  accepted commands
        """
        self.setPermissions()
        self.setAcceptedCommands()

        self.runShell()


    """
    start up the python shell for input
    """
    def runShell(self):
        while self.shell:
            self.userInput = input(self.prompt)

            # call method to handle user inpu
            self.parseInput()
            

    """
    handle the user input and call appropriate command to handle
    """
    def parseInput(self):
        self.userInput = self.userInput.strip()
        self.userInput = self.userInput.split()

        """
        check if entered commands is in list of accepted commands \
        then, check if current use has the permission to run entered \
        command - if true, call function to handle entered command

        """
        if self.userInput[0] in self.acceptedCommands.keys():
            if self.userInput[0] in self.userPermissions[self.user].keys():
                self.acceptedCommands[self.userInput[0]]()
            else:
                print("Sorry, you don't have permissions to run this command!")
        else:
            print("Invalid command entered!")


    """
    log the user into the portal
    """
    def login(self):
        # handle login for guest
        if self.user == 'guest':
            userId = input(f"Enter your application ID: ")
            password = input("Enter your password: ")

            hashedPassword = hashlib.md5(password.encode())
            hashedPassword = hashedPassword.hexdigest()

            if userId in self.admissionApplications.keys():
                if hashedPassword == self.admissionApplications[userId]['password']:
                    # instantiate guest class to handle curently logged in guest
                    Guest(self.admissionApplications[userId], userId)
                else:
                    print("Invalid ID or Password")
            else:
                print("Invalid ID or Password")


    """
    handle admission application for guests
    """
    def applyAdmission(self):
        id = f"UID{random.randint(0,9999):04}"

        while id in self.admissionApplications.keys():
            id = f"UID{random.randint(0,9999):04}"

        # randomly generate and hash generated password for user
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        hashedPassword = hashlib.md5(password.encode())
        hashedPassword = hashedPassword.hexdigest()

        firstName = input("Enter your First Name: ")
        lastName = input("Enter your Last name: ")
        middleName = input("Enter your Middle Name (leave blank if not applicable): ")
        email = input("Enter your email address: ")
        stateOfOrigin = input("Enter your State of Origin: ")
        stateOfResidence = input("Enter your State of Residence: ")
        dateOfBirth = input("Enter your Date of Birth (DD|MM|YYYY): ")
        courseOfChoice = input("Enter desired course of study: ")
        jambScore = input("Enter your UTME score: ")

        userApplication = {
            id: {
                'firstname': firstName,
                'lastname': lastName,
                'middlename': middleName,
                'email': email,
                'stateoforigin': stateOfOrigin,
                'state of residence': stateOfResidence,
                'dateofbirth': dateOfBirth,
                'courseofchoice': courseOfChoice,
                'jambscore': jambScore,
                'password': hashedPassword
                 }
        }

        self.admissionApplications.update(userApplication)

        print("Congratulations, your application has been successfully received!")
        print(f"Please, take note of your user id and password: \nID: {id}\nPASSWORD: {password}")

        # save program state after application
        self.save()

    """
    exit the shell
    """
    def exit(self):
        self.shell = False

    """
    """
    def info(self):
        pass


    """
    sets accepted commands as a class attribute
    """
    def setAcceptedCommands(self):
        self.acceptedCommands = {
            'login': self.login,
            'exit': self.exit,
            'apply': self.applyAdmission,
            'info': self.info
        }

        
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
            'guest': {
                'view': ['students', 'schools', 'departments', 'cut-off'],
                'apply': ['admission'],
                'login': True,
                'exit': True,
                'info': True
            },
            'student': {
                'view': ['students', 'schools', 'departments', 'results', ],
            },
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
    strip unwanted values in <self> and save state
    """
    def save(self):
        """
        delete acceptedCommands from instance \
        because it's not json serializable
        """
        del self.__dict__['acceptedCommands']
        FileStorage.save(self)

        # set accepted commands after saving
        self.setAcceptedCommands()

    """
    save to file storage upon exit of program
    """
    def __del__(self):
        self.save()

#initialize class
User()
