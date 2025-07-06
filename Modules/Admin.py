from tabulate import tabulate
from Modules.Utils import Utils
from rich.console import Console
import hashlib, datetime, os, random

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
            'admit': self.admitStudent,
            'reject': self.rejectStudent,
            'view my log': self.viewMyLog,
            'view admin log': self.viewAdminLog,
            'view applications': self.viewApplications,
            'view schools status': self.school,
            'view students': self.viewStudents,
            'view school stats': self.schoolStats,
        }

        self.mainHandle = mainHandle
        self.courses = Utils.loadCourses()
        self.mainHandleDict = mainHandle.__dict__
        self.command = self.mainHandleDict.get('command')
        self.admissionApplications = self.mainHandleDict.get('admissionApplications')

        # set root admin if db file does not exist
        if not self.mainHandleDict.get('admins'):
            self.mainHandleDict['admins'] = Utils.rootAdmin()
        
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
    """
    def school(self):
        pass

    """
    helper function for the admitStudent method
    """
    def _admit(self, applicantId):
        # check if application exists
        if applicantId not in self.admissionApplications.keys():
            console.print("\n[red]ERROR[/red]\nInvalid UID!\n")
        # check if applicant has already been admitted
        elif applicantId in self.admissionApplications.keys() and \
             self.admissionApplications.get(applicantId)['applicationStatus'] == 'admitted':
            console.print(f"Applicant with UID: [yellow]{applicantId}[/yellow]"\
                          " has already been admitted")
        else:
            # get applicant info
            applicantInfo = self.admissionApplications.get(applicantId)
            matricTail = applicantInfo.get('courseCode')[0:2]
            digits = f"{random.randint(0,99999):05}"
            matric = f"{datetime.datetime.now().year}/1/{digits}{matricTail}"
            admissionDate = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            # set student info
            student = {
                'applicationId': applicantInfo.get('id'),
                'email': applicantInfo.get('email'),
                'firstName': applicantInfo.get('firstName'),
                'middleName': applicantInfo.get('middleName'),
                'lastName': applicantInfo.get('lastName'),
                'dateOfBirth': applicantInfo.get('dateOfBirth'),
                'stateOfOrigin': applicantInfo.get('stateOfOrigin'),
                'stateOfResidence': applicantInfo.get('stateOfResidence'),
                'jambScore': applicantInfo.get('jambScore'),
                'school': applicantInfo.get('school'),
                'department': applicantInfo.get('courseOfChoice'),
                'courseCode': applicantInfo.get('courseCode'),
                'applicationDate': applicantInfo.get('applicationDate'),
                'password': applicantInfo.get('password'),
                'matricNo': matric,
                'admissionDate': admissionDate,
            }

            # update admission application status
            self.admissionApplications[applicantId]['applicationStatus'] = "admitted"
            
            # add matric number to application data for easy password change and lookup
            self.admissionApplications[applicantId]['matricNo'] = matric

            # create students attribute of main handle if it does not exist
            if not self.mainHandleDict.get('students'):
                self.mainHandleDict['students'] = {}

            self.mainHandleDict['students'].update({matric: student})
                
            # print success message
            console.print(f"\n[green]SUCCESS[/green]\n{applicantInfo.get('firstName')} "\
                          f"{applicantInfo.get('lastName')} has been admitted successfully!\n"
                          f"Matric No: {matric}\n")

            # log admin action
            self.adminLog(f"admitted {applicantId} "\
                          f"with matric no: {matric}")
            return True

    """
    admit student
    """
    def admitStudent(self):
        modeList = ['single', 'batch', 'all']

        # check if there are current admission applications
        if not self.admissionApplications:
            console.print("\n[yellow]INFO[/yellow]\nThere"\
                          " are no applications currently!\n")
            return

        # print mode of admission
        console.print("\n[yellow]ADMISSION MODES[/yellow]\n")
        print(
            "[SINGLE] - Admit a single student\n",
            "[BATCH]  - Admit multiple students\n",
            "[ALL]    - Admit all applied students\n",
            sep=""
        )

        # collect input for admission mode
        while True:
            mode = input("Enter Admission Mode: ")
            mode = mode.lower()

            if mode not in modeList:
                console.print("\n[red]ERROR[/red]\nInvalid mode selected\n")
            else:
                break

        # prompt to print admission applications 
        while True:
            tableConfirm = input("View applications? [Y | N]:  ").strip().lower()

            if tableConfirm == "y" or \
               tableConfirm == "yes":
                self.viewApplications()
                break
            elif tableConfirm == "n" or \
                 tableConfirm == "no":
                break
            else:
                console.print("\n[red]ERROR[/red]\nInvalid option entered!\n")

        # handle admission for selected mode
        if mode == "single":
            # get user ID of applicant to be admitted
            uid = input("Enter UID of applicant: ")
            uid = Utils.cleanString(uid)

            self._admit(uid)
        elif mode == "batch":
            uids = input("Enter UIDs of applicants to be admitted (separated by commas): ")
            uids = Utils.cleanString(uids).replace(" ", "").split(',')
            admittedCount = 0

            for uid in uids:
                if self._admit(uid):
                    admittedCount += 1

            if admittedCount > 0:
                console.print(f"\n[green]SUCCESS[/green]\n{admittedCount} "\
                              "applicant(s) have been admitted successfully!\n")
        elif mode == "all":
            admittedCount = 0

            for uid in list(self.admissionApplications.keys()):
                if self._admit(uid):
                    admittedCount += 1

            if admittedCount > 0:
                console.print(f"\n[green]SUCCESS[/green]\n{admittedCount} "\
                              "applicant(s) have been admitted successfully!\n")

    """
    helper function for rejectStudent method
    """
    def _reject(self, applicantId):
        # check if application exists
        if applicantId not in self.admissionApplications.keys():
            console.print("\n[red]ERROR[/red]\nInvalid UID!\n")
        elif applicantId in self.admissionApplications.keys() and \
             self.admissionApplications.get(applicantId)['applicationStatus'] == 'rejected':
            console.print(f"Applicant with UID: [yellow]{applicantId}[/yellow]"\
                          " has already been rejected!")
        else:
            # update admission application status
            self.admissionApplications[applicantId]['applicationStatus'] = "rejected"

            # print success message
            console.print(f"\n[green]SUCCESS[/green]\nApplicant with UID: {applicantId} "\
                          f"has been denied admission!\n")

            # log admin action
            self.adminLog(f"rejected {applicantId}")
            return True

    """
    reject student admission
    """
    def rejectStudent(self):
        modeList = ['single', 'batch', 'all']

        # check if there are current admission applications
        if not self.admissionApplications:
            console.print("\n[yellow]INFO[/yellow]\nThere"\
                          " are no applications currently!\n")
            return

        # print mode of admission
        console.print("\n[yellow]ADMISSION REJECTION MODES[/yellow]\n")
        print(
            "[SINGLE] - Reject a single student\n",
            "[BATCH]  - Reject multiple students\n",
            "[ALL]    - Reject all applied students\n",
            sep=""
        )

        # collect input for admission rejection mode
        while True:
            mode = input("Enter Admission Rejection Mode: ")
            mode = mode.lower()

            if mode not in modeList:
                console.print("\n[red]ERROR[/red]\nInvalid mode selected\n")
            else:
                break

        # prompt to print admission applications 
        while True:
            tableConfirm = input("View applications? [Y | N]:  ").strip().lower()

            if tableConfirm == "y" or \
               tableConfirm == "yes":
                self.viewApplications()
                break
            elif tableConfirm == "n" or \
                 tableConfirm == "no":
                break
            else:
                console.print("\n[red]ERROR[/red]\nInvalid option entered!\n")

        # handle admission rejection for selected mode
        if mode == "single":
            # get user ID of applicant to be rejected
            uid = input("Enter UID of applicant: ")
            uid = Utils.cleanString(uid)

            self._reject(uid)
        elif mode == "batch":
            uids = input("Enter UIDs of applicants to be rejected (separated by commas): ")
            uids = Utils.cleanString(uids).replace(" ", "").split(',')
            rejectedCount = 0

            for uid in uids:
                if self._reject(uid):
                    rejectedCount += 1

            if rejectedCount > 0:
                console.print(f"\n[green]SUCCESS[/green]\n{rejectedCount} "\
                              "applicant(s) have been denied admission!!\n")
        elif mode == "all":
            rejectedCount = 0

            for uid in list(self.admissionApplications.keys()):
                if self._reject(uid):
                    rejectedCount += 1

            if rejectedCount > 0:
                console.print(f"\n[green]SUCCESS[/green]\n{rejectedCount} "\
                              "applicant(s) have been denied admission!\n")

    """
    view admission applications
    """
    def viewApplications(self):
        # check if there are available applications
        if not self.admissionApplications:
            console.print("\n[yellow]There are no "\
                          "available admission applications "\
                          "at the moment!\n[/yellow]")
            return

        # format header
        header = ["SN", "ID", "COURSE", "EMAIL", "UTME SCORE", "APPLICATION DATE"]
        data = []

        # print applications
        for key, value in self.admissionApplications.items():
            # do not fetch application if status is not <pending>
            if value.get('applicationStatus') != 'pending':
                continue

            # get values
            subData = []
            sn = list(self.admissionApplications).index(key) + 1
            subData.append(sn)
            subData.append(value.get('id'))
            subData.append(value.get('courseOfChoice'))
            subData.append(value.get('email'))
            subData.append(value.get('jambScore'))
            subData.append(value.get('applicationDate'))

            # append values to data
            data.append(subData)

        # print table if there are pending applications
        if data:
            print(tabulate(data, headers=header, tablefmt="double_grid"))
        else:
            console.print("\n[yellow]There are no "\
                          "available admission applications "\
                          "at the moment!\n[/yellow]")

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

        # clean the username and password input
        username = Utils.cleanString(username)
        password = Utils.cleanString(password)

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
        message = f"[ADMIN] - ({self.username}@{self.email})"\
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
    view all students
    """
    def viewStudents(self):
        students = self.mainHandleDict.get('students')
        # check if there are students
        if not students:
            console.print("\n[yellow]There are no students admitted yet![/yellow]\n")
            return
        
        table = []
        header = ["SN", "MATRIC NO.", "NAME", "COURSE", "EMAIL"]

        for index, (uid, student) in enumerate(students.items(), 1):
            fullName = f"{student.get('firstName')} {student.get('lastName')}"
            table.append([
                index,
                student.get('matricNo'),
                fullName,
                student.get('department'),
                student.get('email')
            ])

        print(tabulate(table, headers=header, tablefmt="double_grid"))

    def schoolStats(self):
        """
        view school statistics
        """
        students = self.mainHandleDict.get('students', {})

        # check if there are students
        if not students:
            console.print("\n[yellow]No student data available[/yellow]\n")
            return

        totalStudents = len(students)
        per_course = {}
        per_school = {}

        for s in students.values():
            course = s.get('courseOfChoice')
            school = s.get('school')

            if course in per_course:
                per_course[course] += 1
            else:
                per_course[course] = 1

            if school in per_school:
                per_school[school] += 1
            else:
                per_school[school] = 1

        # # loop through students and count course enrollments
        # for s in students.values():
        #     course = s.get('courseOfChoice')
        #     if course in per_course:
        #         per_course[course] += 1

        console.print("\n[green]Student Statistics[/green]\n")
        for course, count in per_course.items():
            print(f"{course}: {count} student(s)")

    """
    log current admin out
    """
    def logout(self):
        Utils.logout(self.mainHandle)
