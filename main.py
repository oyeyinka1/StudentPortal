from rich.console import Console
from Modules.FileStorage import Storage
from Modules.Guest import Guest

import random, string, hashlib

console = Console()
"""
shell class

receives user commands, formats, parses and calls \
corresponding methods/classes to handle user-given \
command
"""

class Shell:
    """
    constructor class
    """
    def __init__(self):
        # attributes that should rely solely on file Storage
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
        self.loggedIn = False
        self.prompt = f"[blue](pyShell | {self.user}):   [/blue]"
        self.defaultPrompt = f"[blue](pyShell | {self.user}):   [/blue]"

        """
        self.runShell: run the shell of the program
        self.setshellEssentialss: instantiates essential \
                                  class attributes
        """
        self.setShellEssentials()
        self.runShell()


    """
    start up the python shell for input
    """
    def runShell(self):
        try:
            while self.shell:
                self.userInput = str(console.input(self.prompt))
                 # call method to handle user input
                self.parseInput()
        except KeyboardInterrupt:
            # catch keyboard interrupt before exiting shell
            console.print("\n[red]Exiting shell...[/red]")
            self.shell = False
            
    """
    handle the user input and call appropriate command to handle
    """
    def parseInput(self):
        self.userInput = self.userInput.strip()
        self.userInput = self.userInput.split()

        # break string into command and args
        self.command = self.userInput[0]
        self.args = self.userInput[1:]

        """
        run given command if it's a shell native command \
        otherwise check command in user permissions list and \
        run corresponding function for command
        """
        if self.command not in  self.shellNativeCommands.keys() and \
           self.command not in self.userPermissions[self.user].keys():
            console.print("[red]Invalid command entered![/red]")
            return

        if self.command in self.shellNativeCommands.keys():
            self.shellNativeCommands.get(self.command)()
            return

        if self.command in self.userPermissions[self.user].keys():
            self.userHandle.get(self.user)(self)
        else:
            print("Sorry, you don't have permissions to run this command!")
            

    """
    exit the shell
    """
    def exit(self):
        self.shell = False
        self.saveStorage()

    """
    print all available shell native commands
    """
    def info(self):
        pass


    """
    sets shell essential attributes
    """
    def setShellEssentials(self):
        # set shell native commands to be handled by this class
        self.shellNativeCommands = {
            'exit': self.exit,
            'info': self.info
        }

        # set user native commands to be handled by user classes
        self.userHandle = {
            'guest': Guest
        }

        # set permissions for hierarchy of users
        checkUserPermissions = self.__dict__.get('userPermissions')
        if not checkUserPermissions:
            self.userPermissions = {
                'guest': {
                    'view': ['students', 'schools', 'departments', 'cut-off'],
                    'apply': ['admission'],
                    'login': True,
                    'logout': True
                },
                'student': {
                    'view': ['students', 'schools', 'departments', 'results', ],
                },
                'admin': []
            }

    """
    deletes non-serializable class attributes from the \
    class __dict__ attribute
    """
    def unsetShellEssentials(self):
        unsetValues = [
            'userHandle',
            'shellNativeCommands',
            'loggedInUser'
        ]

        for value in unsetValues:
            try:
                del self.__dict__[value]
            except:
                pass

    """
    load data from file Storage
    """
    def loadStorage(self):
        load = Storage.load()

        if load:    
            self.__dict__.update(load)

    """
    strip unwanted values in <self> and save to Storage
    """
    def saveStorage(self):
        # unset shell essentials
        self.unsetShellEssentials()

        # save to file Storage
        Storage.save(self)

        # set shell essentials
        self.setShellEssentials()

    """
    save to file Storage upon exit of program
    """
    def __del__(self):
        self.saveStorage()

#initialize class
Shell()
