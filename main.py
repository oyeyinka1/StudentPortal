from rich.console import Console
from Modules.FileStorage import Storage
from Modules.Guest import Guest
from Modules.Admin import Admin
from Modules.Utils import Utils

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
    constructor class`
    """
    def __init__(self):
        # attributes that should rely solely on file Storage
        self.admissionApplications = {}

        # load data from file storage
        self.loadStorage()

        # instantiate class attributes
        self.shell = True
        self.userInput = ""
        self.prompt = f"[blue](pyShell):   [/blue]"
        self.defaultPrompt = f"[blue](pyShell):   [/blue]"

        # class attributes to handle login
        self.user = None
        self.loggedIn = None
        self.loggedInUser = None
        
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
    route user command to appropriate handler function/class
    """
    def parseInput(self):
        # trim excess whitespace from user input
        self.command = Utils.cleanString(self.userInput)

        userCommands = []
        users = ['guest', 'admin', 'student']
        shellCommands = self.shellNativeCommands.keys()

        # get all user commands
        for i in users:
            command = self.userPermissions[i].keys()
            for j in command:
                userCommands.append(j)

        # check if command is shell native and run
        if self.command in shellCommands:
            self.shellNativeCommands.get(self.command)()
            return

        # check if command is non existent at all
        if self.command not in shellCommands and \
           self.command not in userCommands:
            console.print("\n[red]ERROR[/red]\nInvalid command entered!\n")
            return

        # check if command exists but user is not logged in
        if self.command in userCommands and not self.loggedIn:
            console.print("\n[red]ERROR[/red]\nYou do not have "\
                  "permissions to run this command!\n")
            return

        """
        run command if it is not shell native \
        but exists and user is logged in
        """
        if self.command in userCommands and self.loggedIn:
            if self.command not in self.userPermissions[self.user].keys():
                console.print("\n[red]ERROR[/red]\nYou do not have "\
                      "permissions to run this command!\n")
                return
            else:
                self.userHandle.get(self.user)(self)
                return

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
        # print all available shell native commands
        console.print("[blue]\nAvailable shell commands:[/blue]")
        for command in self.shellNativeCommands.keys():
            console.print(f"[green]{command}[/green]")

        # print available user commands if logged in
        if self.__dict__.get('user'):
            console.print("\n[blue]Available user commands:[/blue]")
            for command in self.userPermissions[self.user].keys():
                console.print(f"[green]{command}[/green]")

        # print new line
        print()


    """
    log the user in
    """
    def login(self):
        # check if there is a logged in user
        if self.loggedIn:
            console.print("[yellow]\nOops!\nAlready "\
                          "logged in\n[/yellow]")
            return

        users = ['guest', 'admin', 'student']

        console.print("\nUSER MODES")
        console.print("[yellow]GUEST[/yellow]\t"\
                      "[red]ADMIN[/red]\t"\
                      "[purple]STUDENT[/purple]\n")

        while True:
            userMode = input("Enter user mode: ").lower().strip()

            # allow user to abort login
            if userMode == 'cancel':
                return

            if userMode not in users:
                console.print("\n[red]ERROR[/red]\n"\
                              "Invalid user mode!\n"\
                              "[yellow]Type `cancel` to "\
                              "abort login\n[/yellow]")
            else:
                break

        # call appropriate user class to handle login
        self.userHandle.get(userMode)(self)

    """
    view available courses
    """
    def viewCourses(self):
        # call view programmes method of utils
        Utils.viewProgrammes()

    """
    apply for admission
    """
    def apply(self):
        # call guest class to handle admission application
        Guest(self)

    """
    sets shell essential attributes
    """
    def setShellEssentials(self):
        # set shell native commands to be handled by this class
        self.shellNativeCommands = {
            'exit': self.exit,
            'info': self.info,
            'login': self.login,
            'apply': self.apply,
            'view courses': self.viewCourses,
            'view programmes': self.viewCourses
        }

        # set user native commands to be handled by user classes
        self.userHandle = {
            'guest': Guest,
            'admin': Admin
        }

        # set permissions for hierarchy of users
        self.userPermissions = {
            'guest': {
                'logout': True,
                'check status': True,
                'cancel application': True,
            },
            'admin': {
                'admit': True,
                'reject': True,
                'logout': True,
                'view my log': True,
                'view admin log': True,
                'view applications': True,
                'view students': True,    
                'view schools status': True,
                'export students': True
            },
            'student': {
                'view': ['students', 'schools', 'departments', 'results', ],
            }
        }

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
        # save to file Storage
        Storage.save(self)

    """
    save to file Storage upon exit of program
    """
    def __del__(self):
        self.saveStorage()

#initialize class
Shell()
