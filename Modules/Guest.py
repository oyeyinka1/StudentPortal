from rich.console import Console
import random, string, hashlib, datetime

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
            'logout': self.logout
        }

        self.states = [
            'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi',
            'Bayelsa', 'Benue', 'Borno', 'Cross River', 'Delta',
            'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'Gombe',
            'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina',
            'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa',
            'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo',
            'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe',
            'Zamfara', 'Abj'
        ]

        self.availableCourses = [
            'Computer Science', 'Software Engineering', 
            'Information Technology',
            'Cyber Security', 'Data Science'
        ]

        self.mainHandle = mainHandle
        self.mainHandleDict = mainHandle.__dict__
        
        self.loginCheck = self.mainHandleDict.get('loggedIn')
        self.command = self.mainHandleDict.get('command')
        self.commandArgs = self.mainHandleDict.get('commandArgs')
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
    """
    def checkStatus(self):
        print(f"Application status for {self.id}")

    """
    """
    def cancelApplication(self):
        pass

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
        email = input("Enter your email address: ").strip()

        # validating email input
        while True:
            if email == email.lower():
                if '@' in email and '.' in email:
                    if len(email) > 5:
                        break
                    else:
                        print("Invalid email address. Please enter a valid email address.")
                        email = input("Enter your email address: ").strip()
                else:
                    print("Invalid email address. Please enter a valid email address.")
                    email = input("Enter your email address: ").strip()
            else:
                print("Invalid email address. Email cannot be have capital letters")
                email = input("Enter your email address: ").strip()

            
        
        stateOfOrigin = input("Enter your State of Origin: ").capitalize()
        stateOfResidence = input("Enter your State of Residence: ").capitalize()

        # validating state of origin and residence input
        while True:
            if stateOfOrigin in self.states and stateOfResidence in self.states:
                break
            else:
                print("Invalid state of origin or residence. Please enter a valid state.")
                stateOfOrigin = input("Enter your State of Origin: ").capitalize()
                stateOfResidence = input("Enter your State of Residence: ").capitalize()
    
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


        courseOfChoice = input("Enter desired course of study: ").title().strip()


        # validating course of choice input
        while True:
            if courseOfChoice in self.availableCourses:
                break
            else:
                print("Sorry! Desired course entered is not available.\nPlease choose from the following courses:")
                for course in self.availableCourses:
                    print(f"\n\t- {course}")
                print("\nPlease enter a valid course of choice.")
                courseOfChoice = input("Enter desired course of study: ")

        
        jambScore = int(input("Enter your UTME score: "))

        # validating jamb score input
        while True:
            if jambScore >= 0 and jambScore <= 400:
                break
            else:
                print("Invalid JAMB score. Please enter a valid JAMB score between 0 and 400.")
                jambScore = int(input("Enter your UTME score: "))

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
                'stateOfResidence': stateOfResidence
                 }
        }

        self.admissionApplications.update(userApplication)

        console.print("[green]Congratulations, your application has been successfully received![/green]")
        console.print(f"Please, take note of your user id and password: \nID: [yellow]{id}[/yellow]\nPASSWORD: [yellow]{password}[/yellow]")

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
        if not self.mainHandle.loggedIn:
            console.print("[yellow]Oops, you need to be logged in to log out[/yellow]")
        else:
            self.cleanMainHandle()

    """
    delete unwanted variables, reset login \
    status for mainHandle and save application \
    state to file storage
    """
    def cleanMainHandle(self):
        try:
            del self.mainHandleDict['loggedInUser']
            del self.mainHandleDict[self.id]

            self.mainHandle.loggedIn = False
            self.mainHandle.prompt = self.mainHandle.defaultPrompt

            self.mainHandle.saveStorage()
        except:
            pass

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

            # set main handle class attributes
            self.mainHandle.loggedIn = True
            self.mainHandle.prompt = f"  | {userId} :>  "

    """
    unset values upon destruction
    """
    def __del__(self):
        self.cleanMainHandle()
