import hashlib
import json
from rich.console import Console

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
        

    """
    log the user into the portal
    """
    def loginGuest(self):
        userId = input("Enter your application ID: ")
        password = input("Enter your password: ")

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
