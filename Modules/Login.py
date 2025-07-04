import hashlib
import json
from rich.console import Console
from Modules.Utils import Utils

console = Console()


"""
class to handle user login
"""
class Login:
    """
    """
    def __init__(self, mainHandle):
        self.mainHandle = mainHandle
        self.mainHandleDict = mainHandle.__dict__
        self.user = self.mainHandleDict.get("user")
        self.admissionApplications = self.mainHandleDict.get("admissionApplications")
        self.students = self.mainHandleDict.get("students")

    """
    check if already admitted user is attempting \
    to login to guest account
    """
    def checkAdmittedStudent(self, userId):
        # check if students dictionary exists
        if not self.students:
            return False

        # check if user trying to login has been admitted
        for key, value in self.students.items():
            if value.get('applicationId') == userId and \
               value.get('studentSetup'):
                console.print("\n[yellow]You have been admitted.\nLogin "\
                              "to your student account using your "\
                              "matriculation number to continue[/yellow]\n")
                return True

        return False
        
    """
    log the user into the portal
    """
    def loginGuest(self):
        userId = input("Enter your application ID: ")
        userId = Utils.cleanString(userId)

        # check if user with user ID has been admitted
        if self.checkAdmittedStudent(userId):
            return

        password = input("Enter your password: ")
        password = Utils.cleanString(password)

        hashedPassword = hashlib.md5(password.encode()).hexdigest()


        if userId in self.admissionApplications:
            user = self.admissionApplications[userId]

            if hashedPassword == user['password']:
                # Set login data in main handle
                self.mainHandleDict['loggedInUser'] = user
                self.mainHandleDict['loggedInUser']['id'] = userId
                self.mainHandleDict['loggedIn'] = True
                self.mainHandleDict['user'] = 'guest'
                self.mainHandle.prompt = f"[yellow]({userId})   [/yellow]"

                console.print(f"[green]\n<< Welcome back, {user['firstName']}! >>\n[/green]")
                return True
            else:
                console.print("[red]\nInvalid ID or Password[/red]\n")
        else:
            console.print("[red]\nInvalid ID or Password[/red]\n")
            return False

    """
    """
    def loginAdmin(self):
        pass

    """
    """
    def loginStudent(self):
        pass
