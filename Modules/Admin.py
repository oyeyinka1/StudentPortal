import hashlib
from Modules.Utils import Utils
from rich.console import Console

# get instance of Console
console = Console()

"""
class to handle admin commands and \
functionalities
"""
class Admin:
    """
    contructor function of class
    """
    def __init__(self, mainHandle):
        self.adminCommands = {
            'login': self.login,
            'logout': self.logout,
            'view applications': self.viewApplications
        }

        self.mainHandle = mainHandle
        self.mainHandleDict = mainHandle.__dict__        
        self.command = self.mainHandleDict.get('command')
        self.admissionApplications = self.mainHandleDict.get('admissionApplications')

        # check if there is a logged in user and set user data
        if self.mainHandle.loggedIn:
            self.setLoggedInData(self.mainHandleDict.get('loggedInUser'))

        # execute given user command
        self.executeCommand()

    """
    execute user command
    """
    def executeCommand(self):
        if self.command in self.adminCommands.keys():
            self.adminCommands.get(self.command)()

    """
    view admission applications
    """
    def viewApplications(self):
        # get current applications
        applications = self.mainHandleDict.get('admissionApplications')

        # check if there are available applications
        if not applications:
            console.print("\n[yellow]There are no "\
                          "available applications"\
                          "at the moment!\n[/yellow]")
            return

        # print header
        console.print("\n[purple]SN\t\t\t"\
                      "ID\t\t\t"\
                      "COURSE\t\t\t\t\t"\
                      "EMAIL\n[/purple]")

        # print applications
        for key, value in applications.items():
            # get values
            sn = list(applications).index(key) + 1
            id = value.get('id')
            course = value.get('courseOfChoice')
            email = value.get('email')

            # print values
            print(f"{sn}\t\t\t"\
                  f"{id}\t\t\t"\
                  f"{course}\t\t\t"\
                  f"{email}")

        # print newline
        print()

            

    """
    log in as admin
    """
    def login(self):
        # get admin dictionary
        admins = self.mainHandleDict.get('admins')

        # get username and password of admin
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        # hash user password
        password = hashlib.md5(password.encode())
        password = password.hexdigest()

        # check if admin exists and log admin in
        if username in admins.keys():
            if password == admins[username]['password']:
                # call set logged in data method
                self.setLoggedInData(admins.get(username))

                # print login successful message
                console.print("\n[green]Login Succesful![green]\n")
            else:
                console.print("\n[red]Invalid username or password![/red]\n")
        else:
            console.print("\n[red]Invalid username or password![/red]\n")

    """
    set login data for current admin
    """
    def setLoggedInData(self, admin):
        # set admin attributes for current admin
        self.email = admin.get('email')
        self.username = admin.get('username')
        self.password = admin.get('password')
        self.lastName = admin.get('lastName')
        self.firstName = admin.get('firstName')
        self.middleName = admin.get('middleName')

        # set mainHandle attributes for login
        self.mainHandle.user = 'admin'
        self.mainHandle.loggedIn = True
        self.mainHandle.loggedInUser = admin
        self.mainHandle.prompt = f"[red]({self.username}@admin):  [/red]"
        
    """
    log current admin out
    """
    def logout(self):
        Utils.logout(self.mainHandle)
