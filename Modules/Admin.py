import hashlib, datetime, os
from tabulate import tabulate
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
            'view my log': self.viewMyLog,
            'view admin log': self.viewAdminLog,
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

        # format header
        header = ["SN", "ID", "COURSE", "EMAIL"]
        data = []

        # print applications
        for key, value in applications.items():
            # get values
            subData = []
            sn = list(applications).index(key) + 1
            subData.append(sn)
            subData.append(value.get('id'))
            subData.append(value.get('courseOfChoice'))
            subData.append(value.get('email'))

            # append values to data
            data.append(subData)

        print(tabulate(data, headers=header, tablefmt="double_grid"))

        # save action to admin log
        self.adminLog("viewed admission applications")
        
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
    write admin action to the log file
    """
    def adminLog(self, action=None):
        action = action
        dateObject = datetime.datetime.now()
        date = dateObject.strftime("%d-%B-%Y")
        time = dateObject.strftime("%I:%M %p")
        filepath = "./Modules/Storage/admin_logs.txt"

        # format message to be logged
        message = f"[ADMIN] - {self.username}@{self.email}"\
            f" - ({action}) on ({date}) at ({time})\n"

        # write to file
        with open(filepath, 'a') as file:
            file.write(message)

    """
    view admin logs
    """
    def viewAdminLog(self):
        # check if log file exists
        filepath = "./Modules/Storage/admin_logs.txt"
        checkFile = os.path.exists(filepath)

        if checkFile:
            with open(filepath, 'r') as file:
                content = file.read()
                print('\n', content, sep="")
        else:
            console.print("[yellow]Oops, no logs have "\
                          "been kept for admins quite yet[/yellow]")

    """
    view logs for current admin
    """
    def viewMyLog(self):
        myActions = []
        myKey = f"{self.username}@{self.email}"
        filepath = "./Modules/Storage/admin_logs.txt"
        checkFile = os.path.exists(filepath)

        if checkFile:
            with open(filepath, 'r') as file:
                content = file.readlines()

            # loop through file list
            for i in content:
                log = i[:-1]
                
                # check if admin performed current action
                if myKey in log:
                    # append action to current admin actions
                    myActions.append(log)

            # print current admin actions if any
            if myActions:
                print()

                for j in myActions:
                    print(j)

                print()
            else:
                console.print("\n[yellow]Oops, you've performed "\
                              "no actions yet[/yellow]\n")
        else:
            console.print("\n[yellow]Oops, no logs have "\
                          "been kept for admins quite yet[/yellow]\n")

    """
    log current admin out
    """
    def logout(self):
        Utils.logout(self.mainHandle)
