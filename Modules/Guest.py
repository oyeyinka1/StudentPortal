"""
guest class to handle guest login
"""

class Guest:
    """
    constructor
    """
    def __init__(self, guestData, guestId):
        self.shell = True
        self.id = guestId
        self.data = guestData
        self.prompt = f"  | {self.id} :>  "
        self.acceptedCommands = {
            'check status': self.checkStatus,
            'cancel application': self.cancelApplication,
            'logout': self.logout
        }

        # start up the guest shell
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
        if self.userInput in self.acceptedCommands.keys():
            self.acceptedCommands[self.userInput]()
        else:
            print("Invalid command entered!")

    """
    """
    def logout(self):
        confirm = input("Are you sure you want to logout? Y(yes) | N(no) :  ")

        if confirm.upper() == "Y":
            self.shell = False
        elif confirm.upper == "N":
            return
        else:
            print("Invalid option chosen!")
    
    """
    """
    def checkStatus(self):
        pass

    """
    """
    def cancelApplication(self):
        pass
