from rich.console import Console
import random, string, hashlib, datetime, re, json
from Modules.Utils import Utils

# create object instance of console
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
            'cancel application': self.cancelApplication,
            'view programmes': self.viewProgrammes,
            'view courses': self.viewProgrammes
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

        # check if user has been admitted and start student enrollment
        if self.applicationStatus == 'admitted':
            self.registerStudent()
        else:
            console.print(f"\nHello, {self.firstName}! \nYour application status is: "\
                          f"[red]{self.applicationStatus}[/red]\n")

    """
    register newly admitted student
    """
    def registerStudent(self):
        pass

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
    validate the state
    """
    def getValidState(self, prompt):
        while True:
            state = input(prompt).capitalize()
            if state in self.states:
                return state
            print("\n[yellow]Invalid state. Please enter a valid state.[/yellow]\n")

    """
    validate course of choice
    """
    def getValidCourse(self):
        programInfo = Utils.loadCourses()
        schools = programInfo.keys()

        departments = []
        self.chosenCourseInfo = None

        print("\nHere's a list of available programmes:")
        for x in schools:
            # get school dict
            school = programInfo.get(x)

            # print school/faculty name
            console.print(f"\n\n[purple]SCHOOLS:\t\t"\
                          "DEPARTMENTS:[/purple]")
            console.print(f"\n[green]{x}[/green]")

            for y in school:
                # get department dict
                dept = school.get(y)

                # get department and course code for printing
                deptName = dept.get('course')
                courseCode = dept.get('course code')

                """
                append values to departments list \
                will contain department dictionaries
                """
                departments.append(dept)

                # print departments in the school
                print(f"\t\t\t({courseCode}) - {deptName}")

        console.print(f"\n[red]INFO[/red] You can enter course name or course code.")

        while True:
            course = input("Enter desired course of study: ").lower().strip()

            for dept in departments:
                if course == dept['course'].lower() or \
                   course == dept['course code'].lower():
                    self.chosenCourseInfo = dept
                    break

            if not self.chosenCourseInfo:
                console.print("\n[yellow]Invalid course chosen![/yellow]\n")
            else:
                return self.chosenCourseInfo.get('course')

    """
    view programmes on offer by the school
    """
    def viewProgrammes(self):
        programInfo = Utils.loadCourses()
        schools = programInfo.keys()

        print("\nHere's a list of available programmes:")
        for x in schools:
            # get school dict
            school = programInfo.get(x)

            # print school/faculty name
            console.print(f"\n\n[purple]SCHOOLS:\t\t"\
                          "DEPARTMENTS:[/purple]")
            console.print(f"\n[green]{x}[/green]")

            for y in school:
                # get department dict
                dept = school.get(y)

                # get department and course code for printing
                deptName = dept.get('course')
                courseCode = dept.get('course code')

                # print departments in the school
                print(f"\t\t\t({courseCode}) - {deptName}")
    

    """
    validate jamb score of applicant
    """
    def getValidJamb(self):
        # get the cut off mark for chosen course
        courseCutOff = self.chosenCourseInfo.get('cut off')

        while True:
            try:
                score = int(input("Enter your UTME score: "))
                if 0 <= score <= 400:
                    if score < courseCutOff:
                        console.print(f"[yellow]Sorry, your UTME score of "\
                                      f"\b{score} is less than the cut off mark "\
                                      f"\b{courseCutOff}")
                        return None
                    else:
                        return score
            except:
                pass

            console.print("\n[yellow]Invalid JAMB score.[/yellow]\n"\
                          "Please enter a valid JAMB score between 0 and 400.\n")

    """
    handle admission application for guests
    """
    def applyAdmission(self):
        # check and stop user from applying if logged in
        if self.loginCheck:
            console.print(f"[red]\nOops, you can't apply while logged in!\n[/red]")
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
        while not Utils.isValidEmail(email):
            print("Invalid email address. Please enter a valid email.")
            email = input("Enter your email address: ").strip()
        
        # ensure email is unique
        Utils.ensureUniqueEmail(email)
            
        # loading available states as a list from states-and-cities.json
        self.states = Utils.loadStates('name')

        # print states
        console.print("\n[blue]Here are the valid states:[/blue]")
        for state in self.states:
            console.print(f"\t- {state}")

        stateOfOrigin = self.getValidState("Enter your State of Origin: ")
        stateOfResidence = self.getValidState("Enter your State of Residence: ")

        # collect and validate date of birth
        while True:
            # collect date of birth
            dateOfBirth = input("Enter your Date of Birth (DD-MM-YYYY): ")

            if len(dateOfBirth) == 8 or len(dateOfBirth) == 10:
                # strip possible dashes <-> from date of birth
                if '-' in dateOfBirth:
                    dateOfBirth = dateOfBirth.replace('-', '')

                # split date of birth into day, month and year
                try:
                    dayOfBirth = int(dateOfBirth[0:2])
                    monthOfBirth = int(dateOfBirth[2:4])
                    yearOfBirth = int(dateOfBirth[4:])
                    currentYear = datetime.datetime.now().year

                    # checking if user is within the age limit of 16-30 years
                    if 16 <= (currentYear - yearOfBirth) <= 30:
                        # make date of birth into a datetime object to validate date
                        dateOfBirth = datetime.date(yearOfBirth, monthOfBirth, dayOfBirth)
                        break
                    else:
                        console.print("\n[yellow]You must be between 16 and "\
                                      "30 years old to apply![/yellow]\n")
                        continue
                except:
                    console.print("\n[yellow]Invalid date. "\
                          "\nPlease enter a valid date of birth.[/yellow]\n")
                    continue
            else:
                console.print("\n[yellow]Oops, invalid value.\nTry again![/yellow]\n")
                continue

        dateOfBirth = f"{dayOfBirth:02}-{monthOfBirth:02}-{yearOfBirth}"

        # validate chosen course and Jamb score
        courseOfChoice = self.getValidCourse()
        jambScore = self.getValidJamb()

        # cancel application is UTME score is less than cutoff
        if not jambScore:
            console.print("[red]Sorry, you cannot continue with"\
                          " this application!\n[/red]")
            return

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
                'applicationStatus': "Pending",
                'id': id
                 }
        }

        self.admissionApplications.update(userApplication)

        # print confirmation message upon successful application
        console.print("\n[green]Congratulations, your application "\
                      "has been successfully received![/green]\n")
        console.print(f"Please, take note of your user id and password: "\
                      f"\nID: [yellow]{id}[/yellow]\nPASSWORD: [yellow]{password}[/yellow]\n")

        # save program state after application
        self.mainHandleDict.update(userApplication)
        self.mainHandle.saveStorage()

    """
    log the user into the portal
    """
    def login(self):
        # check if user is already logged in
        if self.loginCheck:
            console.print(f"[yellow]\nWhoa there, {self.firstName}\n"\
                          f"You're already logged in!\n[/yellow]")
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
                    console.print(f"[green]\n<< Welcome back, {self.firstName}!>>\n[/green]")
                else:
                    console.print("[red]\nInvalid ID or Password[/red]\n")
            else:
                console.print("[red]\nInvalid ID or Password\n[/red]")

    """
    log the current user out of the portal
    """
    def logout(self):
        if not self.loginCheck:
            console.print("[yellow]Oops, you need to be logged in to log out[/yellow]")
        else:
            self.mainHandle.loggedIn = False
            self.mainHandle.prompt = self.mainHandle.defaultPrompt
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
        self.mainHandle.saveStorage()
