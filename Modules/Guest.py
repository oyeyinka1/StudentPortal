from rich.console import Console
import random, string, hashlib, datetime, re, json
from Modules import utils

console = Console()

"""
guest class to handle guest native commands
"""

class Guest:
    """
    constructor
    """
    def __init__(self, mainHandle):
        self.guestCommands = {
            'apply': self.applyAdmission,
            'login': self.login,
            'logout': self.logout,
            'check status': self.checkStatus,
            'cancel application': self.cancelApplication
        }

        self.mainHandle = mainHandle
        self.mainHandleDict = mainHandle.__dict__        
        self.loginCheck = self.mainHandleDict.get('loggedIn')
        self.command = self.mainHandleDict.get('command')
        self.admissionApplications = self.mainHandleDict.get('admissionApplications')

        # check if there is a logged in user and set user data
        if self.loginCheck:
            self.setLoggedInData(self.mainHandleDict.get('loggedInUser')['id'])

        # execute given user command
        self.executeCommand()

    """
    execute user command
    """
    def executeCommand(self):
        if self.command in self.guestCommands.keys():
            self.guestCommands.get(self.command)()

    """
    check application status
    """
    def checkStatus(self):
        # check if user is logged in first
        if not self.loginCheck:
            console.print("[red]Oops, you need to be logged in to do that![/red]")
            return

        print(f"Hello, {self.firstName}! \nYour application status is: {self.applicationStatus}")

    """
    cancel application to school
    """
    def cancelApplication(self):
        # check if user is logged in first
        if not self.loginCheck:
            console.print("[red]Oops, you need to be logged in to do that![/red]")
            return

        confirmationKeys = ['y', 'n', 'yes', 'no']

        while True:
            confirmation = input(f"Are you sure you want to cancel "
            f"your application? [Y (Yes) | N (No)]:  ")

            try:
                confirmation = str(confirmation).lower()
                
                if confirmation in confirmationKeys:
                    if confirmation == 'y' or confirmation == 'yes':
                        # print goodbye message
                        console.print(f"Sorry to see you go, {self.firstName}.\n[blue]"\
                                      f"Goodluck with future applications.[/blue]\n")

                        # delete application from application dictionary and save storage
                        del self.mainHandleDict.get('admissionApplications')[self.id]
                        self.cleanMainHandle()
                        break
                    else:
                        console.print(f"[yellow]Operation Cancelled![/yellow]")
                        break
                else:
                    console.print("[yellow]Invalid value![/yellow]")
            except:
                console.print("[yellow]Invalid value![/yellow]")
                continue            

    """
    handle admission application for guests
    """
    def applyAdmission(self):
        # check and stop user from applying if logged in
        if self.loginCheck:
            console.print(f"[red]Oops, you can't apply while logged in![/red]")
            return

        id = f"UID{random.randint(0,9999):04}"

        # ensure generated ID is unique
        while id in self.admissionApplications.keys():
            id = f"UID{random.randint(0,9999):04}"

        # randomly generate and hash generated password for user
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        hashedPassword = hashlib.md5(password.encode())
        hashedPassword = hashedPassword.hexdigest()

        firstName = input("Enter your First Name: ")
        lastName = input("Enter your Last name: ")
        middleName = input("Enter your Middle Name (leave blank if not applicable): ")
        
        email = input("Enter your email address: ").strip()

        # validating email input
        while not utils.is_valid_email(email):
            print("Invalid email address. Please enter a valid email.")
            email = input("Enter your email address: ").strip()
            

            
        """loading available states as a list from states-and-cities.json"""
        self.states = utils.loadFromFiles('./Modules/Misc/states-and-cities.json', 'name')

        # print states
        console.print("\n[blue]Here are the valid states:[/blue]")
        for state in self.states:
            console.print(f"\t- {state}")

        def getValidState(prompt):
            while True:
                state = input(prompt).capitalize()
                if state in self.states:
                    return state
                print("Invalid state. Please enter a valid state.")

        stateOfOrigin = getValidState("Enter your State of Origin: ")
        stateOfResidence = getValidState("Enter your State of Residence: ")
    
        dateOfBirth = input("Enter your Date of Birth (DD-MM-YYYY): ")

        # validating date of birth input
        while True:
            if len(dateOfBirth) == 8:
                # split date of birth into day, month and year
                try:
                    dayOfBirth = int(dateOfBirth[0:2])
                    monthOfBirth = int(dateOfBirth[2:4])
                    yearOfBirth = int(dateOfBirth[4:])

                    currentYear = datetime.datetime.now().year

                    """checking if user is within the age limit of 16-30 years"""
                    if 16 <= (currentYear - yearOfBirth) <= 30:

                        # make date of birth into a datetime object to validate date
                        dateOfBirth = datetime.date(yearOfBirth, monthOfBirth, dayOfBirth)
                        break
                    else:
                        print("You must be between 16 and 30 years old to apply.")
                        dateOfBirth = input("Enter your Date of Birth (DD-MM-YYYY): ")
                except:
                    print("Invalid date. Please enter a valid date of birth.")
                    dateOfBirth = input("Enter your Date of Birth (DD-MM-YYYY): ")
            else:
                print("Oops, invalid value.\nTry again!\n")
                dateOfBirth = input("Enter your Date of Birth (DD-MM-YYYY): ")

        dateOfBirth = f"{dayOfBirth:02}-{monthOfBirth:02}-{yearOfBirth}"

        # load available courses from courses.json   
        self.availableCourses = utils.loadFromFiles('./Modules/Misc/courses.json')

        # print available courses
        console.print("\n[blue]Available courses for admission:[/blue]")
        for course in self.availableCourses:
            console.print(f"\t- {course}")

        # validating course of choice input
        def validateCourse():
            course = input("Enter desired course of study: ").title().strip()

            # loop until a valid course is entered
            while course not in self.availableCourses:
                print("Sorry! Desired course entered is not available.\nPlease choose from the following courses:")
                for dept in self.availableCourses:
                    print(f"\n\t- {dept}")
                print("\nPlease enter a valid course of choice.")
                course = input("Enter desired course of study: ").title().strip()

            return course

        courseOfChoice = validateCourse()

        # validating jamb score input
        def getValidJamb():
            while True:
                try:
                    score = int(input("Enter your UTME score: "))
                    if 0 <= score <= 400:
                        return score
                except:
                    pass
                print("Invalid JAMB score. Please enter a valid JAMB score between 0 and 400.")

        jambScore = getValidJamb()


        userApplication = {
            id: {
                'email': email,
                'lastName': lastName,
                'firstName': firstName,
                'jambScore': jambScore,
                'middleName': middleName,
                'password': hashedPassword,
                'dateOfBirth': dateOfBirth,
                'stateOfOrigin': stateOfOrigin,
                'courseOfChoice': courseOfChoice,
                'stateOfResidence': stateOfResidence,
                'applicationStatus': "Pending"
                 }
        }

        self.admissionApplications.update(userApplication)

        console.print("\n[green]Congratulations, your application has been successfully received![/green]\n")
        console.print(f"Please, take note of your user id and password: \nID: [yellow]{id}[/yellow]\nPASSWORD: [yellow]{password}[/yellow]\n")

        # save program state after application
        self.mainHandleDict.update(userApplication)
        self.mainHandle.saveStorage()

    """
    log the user into the portal
    """
    def login(self):
        # check if user is already logged in
        if self.loginCheck:
            console.print(f"[yellow]Whoa there, you're already logged in, {self.firstName}![/yellow]")
        else:            
            userId = input(f"Enter your application ID: ")
            password = input("Enter your password: ")

            hashedPassword = hashlib.md5(password.encode())
            hashedPassword = hashedPassword.hexdigest()
            
            if userId in self.admissionApplications.keys():
                if hashedPassword == self.admissionApplications[userId]['password']:
                    # set values for logged in user
                    self.setLoggedInData(userId)
                    
                    # print welcome message
                    console.print(f"[green]<< Welcome back, {self.firstName}!>>[/green]")
                else:
                    console.print("[red]Invalid ID or Password[/red]")
            else:
                console.print("[red]Invalid ID or Password[/red]")

    """
    log the current user out of the portal
    """
    def logout(self):
        if not self.loginCheck:
            console.print("[yellow]Oops, you need to be logged in to log out[/yellow]")
        else:
            self.cleanMainHandle()

    """
    delete unwanted variables, reset login \
    status for mainHandle and save application \
    state to file storage
    """
    def cleanMainHandle(self):
        cleanList = ['loggedInUser']

        # fail silently if self.id doesn't exist
        try:
            cleanList.append(self.id)
        except:
            pass

        for i in cleanList:
            try:
                del self.mainHandleDict[i]
            except:
                pass

        self.mainHandle.loggedIn = False
        self.mainHandle.prompt = self.mainHandle.defaultPrompt

        # save storage
        self.mainHandle.saveStorage()

    """
    refresh data if user is logged in
    """
    def setLoggedInData(self, userId):
        user = self.mainHandleDict['admissionApplications'].get(userId)

        if user:
            # set logged in user value for logged in user
            if not self.mainHandleDict.get('loggedInUser'):
                self.mainHandleDict['loggedInUser'] = user
                self.mainHandleDict['loggedInUser']['id'] = userId

            self.id = userId
            self.firstName = user.get('firstName')
            self.lastName = user.get('lastName')
            self.middleName = user.get('middleName')
            self.email = user.get('email')
            self.stateOfOrigin = user.get('stateOfOrigin')
            self.stateOfResidence = user.get('stateOfResidence')
            self.dateOfBirth = user.get('dateOfBirth')
            self.courseOfChoice = user.get('courseOfChoice')
            self.jambScore = user.get('jambScore')
            self.password = user.get('password')
            self.applicationStatus = user.get('applicationStatus')

            # set main handle class attributes
            self.mainHandle.loggedIn = True
            self.mainHandle.prompt = f"  | {userId} :>  "

    """
    unset values upon destruction
    """
    def __del__(self):
        self.cleanMainHandle()
