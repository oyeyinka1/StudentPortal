from Modules.Utils import Utils
import hashlib
from rich.console import Console

console = Console()

"""
student class
"""
class Student:
    """
    constructor function
    """
    def __init__(self, mainHandle):
        self.studentCommands = {
            'login': self.login,
            'logout': self.logout
        }

        self.studentInfo = None
        self.mainHandle = mainHandle
        self.mainHandleDict = self.mainHandle.__dict__
        self.command = self.mainHandleDict.get('command')
        self.students = self.mainHandleDict.get('students')

        # execute given command
        self.executeCommand()

    """
    execute user command
    """
    def executeCommand(self):
        if self.command in self.studentCommands.keys():
            self.studentCommands.get(self.command)()

    """
    log the student into the portal
    """
    def login(self):
        matric = input("Enter your matriculation number: ")
        matric = Utils.cleanString(matric)

        password = input("Enter your password: ")
        password = Utils.cleanString(password)
        hashedPassword = hashlib.md5(password.encode()).hexdigest()

        if matric in self.students.keys():
            self.studentInfo = self.students.get(matric)

            if hashedPassword == self.studentInfo['password']:
                # Set login data in main handle
                self.mainHandleDict['loggedIn'] = True
                self.mainHandleDict['user'] = 'student'
                self.mainHandle.prompt = f"[purple]({matric})   [/purple]"

                console.print(f"[green]\n<< Welcome back, {self.studentInfo['firstName']}! >>\n[/green]")

                # delete studentSetup key/value of student dictionary
                if self.studentInfo.get("studentSetup"):
                    del self.studentInfo["studentSetup"]
            else:
                console.print("[red]\nInvalid Matriculation Number or Password[/red]\n")
        else:
            console.print("[red]\nInvalid Matriculation Number or Password[/red]\n")

    """
    log the current user out of the portal
    """
    def logout(self):
        Utils.logout(self.mainHandle)
