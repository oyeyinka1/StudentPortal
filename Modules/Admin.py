from tabulate import tabulate
from collections import Counter
from Modules.User import User
from Modules.Utils import Utils
from rich.console import Console
from rich.panel import Panel
import hashlib, datetime, os, random, csv, platform, subprocess, string, subprocess
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


# get instance of Console
console = Console()

"""
class to handle admin commands and \
functionalities
"""
class Admin(User):
    """
    contructor function of class
    """
    def __init__(self, mainHandle):
        self.adminCommands = {
            'login': self.login,
            'logout': self.logout,
            'admit applicants': self.admitStudent,
            'add admin': self.addAdmin,
            'add school': self.addSchool,
            'reject applicants': self.rejectStudent,
            'view my log': self.viewMyLog,
            'view admins': self.viewAdmins,
            'view students': self.viewStudents,
            'view admin log': self.viewAdminLog,
            'add department': self.addDepartment,
            'view school stats': self.schoolStats,
            'export students': self.exportStudents,
            'view applications': self.viewApplications,
            'view commands': self.viewCommands,
            'expel student': self.expelStudent,
            'suspend student': self.suspendStudent,
            'unsuspend student': self.unsuspendStudent,
            'add course': self.addCourse,
            'bulk expel': self.bulkExpelStudents,
            'bulk suspend': self.bulkSuspendStudents,
            'bulk unsuspend': self.bulkUnsuspendStudents,
            'remove school': self.removeSchool,
            'remove department': self.removeDepartment,
            'set test': self.setTest,
            'set exam': self.setExam
        }

        # call constructor of base class
        super().__init__(mainHandle)

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
    view list of available commands
    """
    def viewCommands(self):
        console.print("\n[blue]Available Admin Commands:[/blue]\n")
        for cmd in sorted(self.adminCommands.keys(), key=len):
            console.print(f"[green]{cmd}[/green]")
        print()

    """
    get registration data of new admin
    """
    def getAdminData(self):
        # get the admin dictionary
        admins = self.mainHandleDict.get('admins')
        adminEmails = []
        adminUsernames = []

        if admins:
            # get all emails
            for key, value in admins.items():
                adminEmails.append(value.get('email'))

            # get all usernames
            for key, value in admins.items():
                adminUsernames.append(value.get('username'))
            
        # get and validate first name
        while True:
            firstname = input("Enter First Name: ").lower()
            check = Utils.validateName(firstname)

            if check:
                console.print(f"[red]{check}[/red]")
            else:
                break

        # get and validate last name
        while True:
            lastname = input("Enter Last Name: ").lower()
            check = Utils.validateName(lastname)

            if check:
                console.print(f"[red]{check}[/red]")
            else:
                break

        # get and validate email
        while True:
            email = input("Enter Email: ")
            email = Utils.cleanString(email).lower()

            if Utils.isValidEmail(email):
                if email in adminEmails:
                    console.print(f"Entered email [yellow]`{email}`[/yellow]"
                                  "already exists!")
                    continue

                break
            else:
                console.print("[red]Invalid email. Try again![/red]")

        # get and validate username
        while True:
            username = input("Enter Username: ")
            username = Utils.cleanString(username).lower()
            check = Utils.validateUsername(username)

            if check:
                console.print(f"[red]{check}[/red]")
            else:
                if username in adminUsernames:
                    console.print(f"Username [yellow]`{username}`[/yellow] is already taken!")
                    continue

                break

        # get and validate password
        while True:
            password = input("Enter Password: ")
            check = Utils.validatePassword(password)

            if check:
                console.print(f"[red]{check}[/red]")
            else:
                break

        # hash password
        password = hashlib.md5(password.encode()).hexdigest()

        # assign collected data to new list
        adminData = {
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'username': username,
            'password': password
        }

        # return admin data
        return adminData

    """
    add a new admin with priviledges
    """
    def addAdmin(self):
        # cancel operation if user is not root
        if self.username != "root":
            console.print("\n[red]Only the root admin can do this![/red]\n")
            return

        # get info of new admin
        adminData = self.getAdminData()

        # new admin dictionary
        admin = {
            'username': adminData['username'],
            'password': adminData['password'],
            'email': adminData['email'],
            'firstName': adminData['firstname'],
            'lastName':  adminData['lastname']
        }

        # add new admin to main handle dictionary for admins
        self.mainHandleDict['admins'].update({adminData['username']: admin})

        # add entry to admin log
        self.adminLog(f"added new admin with username: {adminData['username']}")

        # print success message
        console.print("\n[green]SUCCESS[/green]\n"\
                      f"Admin with username [yellow]{adminData['username']}[/yellow]"\
                      " was created!\n")

    """
    view current admins in the portal
    """
    def viewAdmins(self):
        sn = 1
        table = []
        admins = self.mainHandleDict.get('admins')

        # end execution if no admins
        if not admins:
            return

        for key, value in admins.items():
            email = value.get('email')
            username = value.get('username')

            row = [sn, username, email]
            table.append(row)
            sn += 1

        print(tabulate(table, headers=["SN", "USERNAME", "EMAIL"], tablefmt='outline'))

    """
    helper function for the admitStudent method
    """
    def _admit(self, applicantId):
        # check if application exists
        if applicantId not in self.admissionApplications.keys():
            console.print("\n[red]ERROR[/red]\nInvalid UID!\n")
        elif self.admissionApplications.get(applicantId)['applicationStatus'] != 'pending':
            # return silently if status is not = pending
            return
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
                'school': applicantInfo.get('school'),
                'department': applicantInfo.get('courseOfChoice'),
                'courseCode': applicantInfo.get('courseCode'),
                'password': applicantInfo.get('password'),
                'matricNo': matric,
                'admissionDate': admissionDate,
                'level': 100,
                'cgpa': 0.00
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
            console.print(f"\n[green]SUCCESS[/green]\n{applicantInfo.get('firstName').title()} "\
                          f"{applicantInfo.get('lastName').title()} has been admitted successfully!\n"
                          f"Matric No: {matric.upper()}\n")

            # log admin action
            self.adminLog(f"admitted {applicantId} "\
                          f"with matric no: {matric}")

            return True

    """
    admit student
    """
    def admitStudent(self):
        check = False
        modeList = ['single', 'batch', 'all']

        # check if there are current admission applications
        for key, value in self.admissionApplications.items():
            if value.get('applicationStatus') == 'pending':
                check = True
                break

        if not check:
            console.print("\n[yellow]INFO[/yellow]\nThere are no pending applications!\n")
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
                # check and only attempt to admit students with `pending` status
                if self.admissionApplications.get(uid)['applicationStatus'] != 'pending':
                    continue

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
            
            Utils.saveData(self.paths.get('db'), self.mainHandleDict)

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
        sn = 1
        data = []
        header = ["SN", "ID", "COURSE", "EMAIL", "UTME SCORE", "APPLICATION DATE"]

        # print applications
        for key, value in self.admissionApplications.items():
            # do not fetch application if status is not <pending>
            if value.get('applicationStatus') != 'pending':
                continue

            # get values
            subData = []
            subData.append(sn)
            subData.append(value.get('id'))
            subData.append(value.get('courseOfChoice'))
            subData.append(value.get('email'))
            subData.append(value.get('jambScore'))
            subData.append(value.get('applicationDate'))

            # append values to data
            data.append(subData)
            sn += 1

        # print table if there are pending applications
        if data:
            print(tabulate(data, headers=header, tablefmt="grid"))
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
                console.print(f"\n[green] Welcome {self.username}![/green]")
                console.print("[blue]Type 'view commands' to see a list of available commands[/blue]\n")
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
        filepath = self.paths.get('admin_logs')

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
        filepath = self.paths.get('admin_logs')
        checkFile = os.path.exists(filepath)

        if checkFile:
            # use the <less> to view admin log
            try:
                subprocess.run(['less', filepath], check=True)
            except:
                console.print("[red]\nError loading logs!\n[/red]")
        else:
            console.print("[yellow]Oops, no logs have "\
                          "been kept for admins quite yet[/yellow]")

    """
    view logs for current admin
    """
    def viewMyLog(self):
        myActions = []
        myKey = f"{self.username}@{self.email}"
        filepath = self.paths.get('admin_logs')
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
        # check if there are students
        if not self.students:
            console.print("\n[yellow]There are no students admitted yet![/yellow]\n")
            return

        sn = 1
        table = []
        header = ["SN", "MATRIC NO.", "NAME", "COURSE", "EMAIL", "STATUS"]

        for uid, student in self.students.items():
            fullName = f"{student.get('firstName')} {student.get('lastName')}"
            status = "Suspended" if student.get('suspended') else "Active"
            table.append([
                sn,
                student.get('matricNo').upper(),
                fullName.title(),
                student.get('department').title(),
                student.get('email'),
                status
            ])
            sn += 1

        print(tabulate(table, headers=header, tablefmt="grid"))

    """
    view school statistics
    """
    def schoolStats(self):
        if not self.students:
            console.print("\n[yellow]No student data available[/yellow]\n")
            return

        totalStudents = len(self.students)
        per_course = {}
        per_school = {}

        for s in self.students.values():
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

        # loop through students and count course enrollments
        for s in self.students.values():
            course = s.get('courseOfChoice')
            if course in per_course:
                per_course[course] += 1

        console.print("\n[green]Student Statistics[/green]\n")
        for course, count in per_course.items():
            print(f"Total Students: {count} student(s)")

        console.print("\n[green]School Statistics[/green]\n")
        for school, count in per_school.items():
            print(f"{school.upper()}: {count} student(s)\n")

    """
    put comment here
    """
    def openFile(self, filepath):
        try:
            if platform.system() == "Windows": # windows
                os.startfile(filepath)
            elif platform.system() == "Darwin":  # mac
                subprocess.run(["open", filepath])
            else:  # linux
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            console.print(f"[red]Couldn't open file automatically: {e}[/red]")

    """
    put comment here
    """
    def exportStudents(self):
        if not self.students:
            console.print("\n[yellow]No students available to export.[/yellow]\n")
            return

        formatOptions = ['pdf', 'csv']
        while True:
            fileFormat = input("Enter export format (pdf/csv): ").strip().lower()
            if fileFormat in formatOptions:
                break
            else: 
                console.print("[red]Invalid format. Please choose 'csv' or 'pdf'.[/red]")

        downloads_folder = str(Path.home() / "Downloads")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"students_{timestamp}.{fileFormat}"
        suggested_path = os.path.join(downloads_folder, default_name)

        file_path = input(f"Enter full path to save the file [Default: {suggested_path}]: ").strip()
        if not file_path:
            file_path = suggested_path

        if fileFormat == 'pdf':
            self.exportStudentsAsPDF(file_path)
        elif fileFormat == 'csv':
            self.exportStudentsAsCSV(file_path)

    """
    put comment here
    """
    def exportStudentsAsPDF(self, filepath):
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                leftMargin=36,  # reduce left margin
                rightMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            elements = []
            styleSheet = getSampleStyleSheet()

            # customize the heading style
            headerStyle = styleSheet['Heading1']
            headerStyle.leftIndent = 0
            headerStyle.alignment = 0  # 0 = left, 1 = center, 2 = right

            elements.append(Paragraph("List of admitted students", headerStyle))
            elements.append(Spacer(1, 12))

            data = [[
                "SN", 
                "Matric No", 
                "Full Name", 
                "Email", 
                "Course of study", 
                "School",
                "Admission Date"
            ]]

            for index, student in enumerate(self.students.values(), 1):
                fullName = " ".join([
                    student.get("firstName", ""),
                    student.get("middleName", ""),
                    student.get("lastName", "")
                ]).strip().title()
                row = ([
                    index,
                    student.get("matricNo").upper(),
                    fullName,
                    student.get("email"),
                    student.get("department").title(),
                    student.get("school").upper(),
                    student.get("admissionDate"),
                ])
                data.append(row)

            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))

            elements.append(table)
            elements.append(Spacer(1,12))
            elements.append(Paragraph(f"Total students: {len(self.students)}", styleSheet['Normal']))

            doc.build(elements)

            console.print(f"\n[green]SUCCESS[/green] PDF exported to: [blue]{filepath}[/blue]\n")
            self.adminLog(f"exported students list as PDF to {filepath}")
            self.openFile(filepath)

        except Exception as e:
            console.print(f"\n[red]ERROR[/red] Failed to export PDF: {e}\n")

    """
    put comment here
    """
    def exportStudentsAsCSV(self, filepath):
        headers = [
            "Matric Number", 
            "First Name", 
            "Middle Name", 
            "Last Name",
            "Email", 
            "Course of study",
            "School",
            "Admission Date"
        ]

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()

                for student in self.students.values():
                    writer.writerow({
                        "Matric Number": student.get("matricNo"),
                        "First Name": student.get("firstName"),
                        "Middle Name": student.get("middleName"),
                        "Last Name": student.get("lastName"),
                        "Email": student.get("email"),
                        "Course of study": student.get("courseOfChoice"),
                        "School": student.get("school"),
                        "Admission Date": str(student.get("admissionDate", ""))
                    })

                writer.writerow({})
                writer.writerow({"Matric Number": f"Total Students: {len(self.students)}"})

            console.print(f"\n[green]SUCCESS[/green] Exported students to [blue]{filepath}[/blue]\n")
            self.adminLog(f"exported students list as CSV to {filepath}")
            self.openFile(filepath)

        except Exception as e:
            console.print(f"\n[red]ERROR[/red] Failed to export students: {e}\n")

    """
    add a new school/faculty to school
    """
    def addSchool(self):
        # get full name of school
        while True:
            schoolName = input("Enter full name of school/faculty: ")
            schoolName = Utils.cleanString(schoolName).lower()
            check = False

            # check for valid school name
            for i in schoolName:
                if i not in f"{string.ascii_letters}'- ":
                    console.print(f"[red]Invalid characters in school name[/red]")
                    check = True
                    break

            if not check:
                break

        # check if school already exists
        if Utils.checkFaculty(schoolName):
            console.print(f"\nSchool [yellow italic]{schoolName.title()}[/yellow italic] already exists!\n")
            return

        # get school initials
        while True:
            initials = input("Enter initials for school: ")
            initials = Utils.cleanString(initials).lower()
            check = Utils.validateName(initials)

            if check:
                console.print(f"[red]{check}[/red]")
            else:
                break

        # check if school already exists
        if Utils.checkFaculty(initials):
            console.print(f"\nSchool with initials: [yellow]{initials.upper()}[/yellow] already exists!\n")
            return

        # save school/faculty to dictionary
        Utils.saveSchool(schoolName, initials)

        # save action to admin log
        self.adminLog(f"added new faculty: {schoolName}")

    """
    add a new department under a school/faculty
    """
    def addDepartment(self):
        # get faculty/school name to add department under
        schoolName = input("Enter name of parent Faculty: ")
        schoolName = Utils.cleanString(schoolName).lower()

        # check if entered school exists
        faculty = Utils.checkFaculty(schoolName)

        if not faculty:
            console.print(f"\nEntered faculty [yellow underline]"\
                          f"{schoolName}[/yellow underline] does not exist\n")

            console.print("[yellow]OPTIONS[/yellow]\n\n"\
                          "[yellow bold]1[/yellow bold]  View current faculties\n"\
                          "[yellow bold]2[/yellow bold]  Add new faculty/school\n")

            option = input("Enter chosen option: ").strip()

            # view current faculties if user chose `1`
            if option == '1':
                Utils.viewFaculties()
            elif option == '2':
                self.addSchool()
            else:
                console.print("[red]Invalid option![/red]")
                return
        else:
            # get full department name
            while True:
                deptName = input("Enter full department name: ")
                deptName = Utils.cleanString(deptName).lower()
                check = Utils.checkDepartment(deptName)

                if check:
                    console.print(f"[red]{check}[/red]")
                else:
                    break

            # get department/course code
            while True:
                deptCode = input("Enter department/course code: ")
                deptCode = Utils.cleanString(deptCode).lower()
                check = Utils.checkDepartment(deptCode)

                if check:
                    console.print(f"[red]{check}[/red]")
                else:
                    break


            # get cut off mark for current department
            while True:
                deptCutOff = input("Enter cut off mark for department: ")
                deptCutOff = Utils.validateNumber(deptCutOff)

                if deptCutOff:
                    # check if cut off is within min and max range
                    if deptCutOff < 0:
                        console.print(f"\n[yellow]Cut off can't be less than 0[/yellow]")
                    elif deptCutOff > 400:
                        console.print(f"\n[red]Cut off can't be greater than 400[/red]")
                    else:
                        break
                else:
                    console.print("\n[red]Invalid number entered![/red]\n")

            # add new department with details
            Utils.addDepartment(faculty, deptName, deptCode, deptCutOff)

            # save action to admin log
            self.adminLog(f"added new department [{deptName}] to faculty [{faculty}]")

    """
    expel a student
    """
    def expelStudent(self):
        if not self.students:
            console.print("\n[yellow]No students to expel![/yellow]\n")
            return

        matricNo = input("Enter Matric Number of student to expel: ").strip()

        if matricNo in self.students:
            student = self.students[matricNo]
            fullName = f"{student.get('firstName')} {student.get('lastName')}"

            console.print(f"\n[red bold]WARNING![/red bold] You are about to [red]EXPEL[/red] {fullName} (Matric No: {matricNo}).")
            confirm = input("Are you sure? Type 'yes' to confirm: ").strip().lower()

            if confirm == 'yes':
                self.students.pop(matricNo)

                console.print(f"\n[red]Student {matricNo} has been expelled.[/red]\n")
                self.adminLog(f"expelled student {matricNo} ({fullName})")
            else:
                console.print("\n[yellow]Action cancelled. No student was expelled.[/yellow]\n")
        else:
            console.print(f"\n[yellow]No student found with Matric No {matricNo}[/yellow]\n")

    """
    bulk expel
    """
    def bulkExpelStudents(self):
        students = self.mainHandleDict.get('students')
        if not students:
            console.print("\n[yellow]No students available![/yellow]\n")
            return

        file_path = Utils.promptFileSelection()
        if not file_path:
            return

        matric_nos = Utils.extractMatricNumbers(file_path)
        if not matric_nos:
            console.print("[red]No valid matric numbers found in the file.[/red]")
            return

        expelled, not_found = [], []

        for matric in matric_nos:
            if matric in students:
                student = students.pop(matric)
                expelled.append((matric, f"{student.get('firstName')} {student.get('lastName')}"))
                self.adminLog(f"bulk expelled student {matric} ({student.get('firstName')} {student.get('lastName')})")
            else:
                not_found.append(matric)


        if expelled:
            console.print("\n[red bold]Expelled Students:[/red bold]")
            for m, name in expelled:
                console.print(f"[red]{m} - {name}[/red]")

        if not_found:
            console.print("\n[yellow bold]Matric numbers not found:[/yellow bold]")
            for m in not_found:
                console.print(f"[yellow]{m}[/yellow]")


    """
    suspend a student
    """
    def suspendStudent(self):
        if not self.students:
            console.print("\n[yellow]No students to suspend![/yellow]\n")
            return

        matricNo = input("Enter Matric Number of student to suspend: ").strip().lower()

        if matricNo in self.students:
            student = self.students[matricNo]
            student['suspended'] = True 
            console.print(f"\n[yellow]Student {matricNo.upper()} has been suspended.[/yellow]\n")
            self.adminLog(f"suspended student {matricNo} ({student.get('firstName')} {student.get('lastName')})")
        else:
            console.print(f"\n[yellow]No student found with Matric No {matricNo}[/yellow]\n")


    """
    bulk suspend
    """
    def bulkSuspendStudents(self):
        students = self.mainHandleDict.get('students')
        if not students:
            console.print("\n[yellow]No students available![/yellow]\n")
            return

        file_path = Utils.promptFileSelection()
        if not file_path:
            return

        matric_nos = Utils.extractMatricNumbers(file_path)
        if not matric_nos:
            console.print("[red]No valid matric numbers found in the file.[/red]")
            return

        suspended, not_found = [], []

        for matric in matric_nos:
            if matric in students:
                students[matric]['suspended'] = True
                suspended.append((matric, f"{students[matric].get('firstName')} {students[matric].get('lastName')}"))
                self.adminLog(f"suspended student {matric} ({students[matric].get('firstName')} {students[matric].get('lastName')})")
            else:
                not_found.append(matric)


        if suspended:
            console.print("\n[yellow bold]Suspended Students:[/yellow bold]")
            for m, name in suspended:
                console.print(f"[yellow]{m} - {name}[/yellow]")

        if not_found:
            console.print("\n[red bold]Matric numbers not found:[/red bold]")
            for m in not_found:
                console.print(f"[red]{m}[/red]")


    """
    unsuspend a student
    """
    def unsuspendStudent(self):
        if not self.students:
            console.print("\n[yellow]No students available![/yellow]\n")
            return

        matricNo = input("Enter Matric Number of student to unsuspend: ").strip().lower()

        if matricNo in self.students:
            student = self.students[matricNo]

            if student.get('suspended'):
                student['suspended'] = False
                console.print(f"\n[green]Student {matricNo.upper()} has been unsuspended.[/green]\n")
                self.adminLog(f"unsuspended student {matricNo} ({student.get('firstName')} {student.get('lastName')})")
            else:
                console.print(f"\n[yellow]Student {matricNo.upper()} is not suspended.[/yellow]\n")
        else:
            console.print(f"\n[yellow]No student found with Matric No {matricNo.upper()}[/yellow]\n")


    """
    bulk unsusend
    """
    def bulkUnsuspendStudents(self):
        students = self.mainHandleDict.get('students')
        if not students:
            console.print("\n[yellow]No students available![/yellow]\n")
            return

        file_path = Utils.promptFileSelection()
        if not file_path:
            return

        matric_nos = Utils.extractMatricNumbers(file_path)
        if not matric_nos:
            console.print("[red]No valid matric numbers found in the file.[/red]")
            return

        unsuspended, not_found, already_active = [], [], []

        for matric in matric_nos:
            if matric in students:
                if students[matric].get('suspended'):
                    students[matric]['suspended'] = False
                    unsuspended.append((matric, f"{students[matric].get('firstName')} {students[matric].get('lastName')}"))
                    self.adminLog(f"unsuspended student {matric} ({students[matric].get('firstName')} {students[matric].get('lastName')})")
                else:
                    already_active.append(matric)
            else:
                not_found.append(matric)


        if unsuspended:
            console.print("\n[green bold]Unsuspended Students:[/green bold]")
            for m, name in unsuspended:
                console.print(f"[green]{m} - {name}[/green]")

        if already_active:
            console.print("\n[yellow bold]These students were not suspended:[/yellow bold]")
            for m in already_active:
                console.print(f"[yellow]{m}[/yellow]")

        if not_found:
            console.print("\n[red bold]Matric numbers not found:[/red bold]")
            for m in not_found:
                console.print(f"[red]{m}[/red]")


    """
    add a new course to a faculty or department
    """
    def addCourse(self):
        department = subtractUnits = None

        # print options
        console.print(
            "\nOPTIONS:\n\n",
            "[yellow bold]1[yellow bold] Set course for entire faculty\n",
            "[yellow bold]2[yellow bold] Set course for specific department\n"
        )

        # check chosen option
        option = input("Enter option: ").strip()
        if option != '1' and option != '2':
            console.print("Invalid option entered!")
            return

        # ask to view available faculties in the school
        if input("View faculties in the school? (Yes | No)  ").strip().lower() == 'yes':
            Utils.viewFaculties()

        # get school/faculty name
        while True:
            school = Utils.cleanString(input("Enter school: "))
            checkFaculty = Utils.checkFaculty(school)
            if checkFaculty:
                school = checkFaculty.lower()
                break
            console.print("[yellow]Invalid faculty entered![/yellow]")

        # end execution if school has no departments
        if Utils.checkNotEmptyFaculty(school):
            console.print("\n[red]There are no current departments in chosen faculty![/red]\n")
            return

        # ask for department if chosen option is 2
        while True and option == '2':
            department = Utils.cleanString(input("Enter department: ")).lower()
            if Utils.checkDepartment(department):
                break
            console.print("[yellow]Invalid department entered![/yellow]")

        # get level
        while True:
            level = input("Enter level: ").strip()
            if level in self.levels:
                break
            console.print("[yellow]Invalid level entered![/yellow]")

        # get semester to set course for
        if level == '400':
            semester = 'first semester'
            console.print("\nSemester: (first)\n")
        else:
            console.print("\nSemesters: (first, second)\n")
            while True:
                semester = input("Enter semester: ")
                semester = Utils.cleanString(semester).lower()

                if semester == 'first' or semester == 'second':
                    semester = f"{semester} semester"
                    break

                if semester == 'first semester' or semester == 'second semester':
                    break

                console.print("[yellow]Invalid semester entered![/yellow]")

        # get all available courses
        courses = Utils.loadCourses()
        console.rule(style="dim white", characters="-")

        # get course name
        while True:
            courseName = Utils.cleanString(input("Enter full course name: ")).lower()

            if courseName:
                if department:
                    # check if course exists and prompt to overwrite
                    checkCourse = courses[school][department][level][semester]['courses']

                    for key, value in checkCourse.items():
                        if courseName == value.get('name'):
                            console.print(f"\n[yellow]Course {courseName.title()} already exists![/yellow]")

                            while True:
                                confirm = input("Continue to overwrite (Yes | No)?  ").lower()

                                if confirm == "no":
                                    console.print("[red]Operation Aborted![/red]")
                                    return
                                elif confirm == 'yes':
                                    popCourseCode = courses[school][department][level][semester]['courses'][courseName]['code']
                                    subtractUnits = courses[school][department][level][semester]['courses'][courseName]['unit']
                                    break
                                else:
                                    console.print("[red]Invalid Input![/red]")
                            break
                else:
                    # loop through departments and check for a duplicate course
                    for key, value in courses[school].items():
                        for key, value in value[level][semester]['courses'].items():
                            if courseName == value.get('name'):
                                console.print(f"\n[yellow]Course {courseName.title()} already exists![/yellow]")

                                while True:
                                    confirm = input("Continue to overwrite (Yes | No)?  ").lower()

                                    if confirm == "no":
                                        console.print("[red]Operation Aborted![/red]")
                                        return
                                    elif confirm == 'yes':
                                        popCourseCode = value.get('code')
                                        subtractUnits = value.get('unit')
                                        break
                                    else:
                                        console.print("[red]Invalid Input![/red]")
                                break

                        # break outer loop if subtractUnits is set
                        if subtractUnits:
                            break
                break
                            
        # get course code
        while True:
            courseCode = Utils.cleanString(input("Enter Course code: ")).lower()
            if courseCode:
                break

        # get course units
        while True:
            courseUnit = Utils.validateNumber(input("Enter course units: "))
            if courseUnit:
                break

            console.print("[yellow]Invalid unit entered![/yellow]")

        # set new course dictionary
        newCourse = {
            courseCode: {
                'name': courseName,
                'code': courseCode,
                'unit': courseUnit
            }
        }

        # set course for specific department if department entered
        if department:
            courses[school][department][level][semester]['courses'].update(newCourse)

            # update total units
            if not courses[school][department][level][semester]['total units']:
                courses[school][department][level][semester]['total units'] = courseUnit
            else:
                courses[school][department][level][semester]['total units'] += courseUnit

            # update total courses
            if not courses[school][department][level][semester]['total courses']:
                courses[school][department][level][semester]['total courses'] = 1
            else:
                courses[school][department][level][semester]['total courses'] += 1

            # check if course already exists and subtract its units and total
            if subtractUnits:
                courses[school][department][level][semester]['total units'] -= subtractUnits
                courses[school][department][level][semester]['total courses'] -= 1
                courses[school][department][level][semester]['courses'].pop(popCourseCode)

        else:
            for key, value in courses[school].items():
                value[level][semester]['courses'].update(newCourse)

                # update total units
                if not value[level][semester]['total units']:
                    value[level][semester]['total units'] = courseUnit
                else:
                    value[level][semester]['total units'] += courseUnit

                # update total courses
                if not value[level][semester]['total courses']:
                    value[level][semester]['total courses'] = 1
                else:
                    value[level][semester]['total courses'] += 1

                # check if course already exists and subtract its units and total
                if subtractUnits:
                    value[level][semester]['total units'] -= subtractUnits
                    value[level][semester]['total courses'] -= 1
                    value[level][semester]['courses'].pop(popCourseCode)

        # save changes to file
        Utils.writeToFile(self.paths.get('courses'), courses)

        # save to admin log
        if department:
            message = f"added Course: {courseCode} to "\
                f"Faculty: {school} | Department: {department} | Level: {level}"
            departmentInfo = department
        else:
            message = f"added Course: {courseCode} to "\
                f"all departments in School: {school} and Level: {level}"
            departmentInfo = "all"

        self.adminLog(message)
            

        # print success message
        console.print(
            f"\n[green bold]SUCCESS[/green bold]\n\n"\
            f"Added new course [yellow]{courseName.title()}[/yellow]\n"\
            f"To school: [yellow]{school.upper()}[/yellow]\n"\
            f"To department: [yellow]{departmentInfo.upper()}[/yellow]\n"\
            f"Level: [yellow]{level}[/yellow]\n"\
            f"Semester: [yellow]{semester.title()}[/yellow]\n"
        )

        # --- update course in tests and exams json file

        # load and update file content
        content = Utils.loadFromFile(self.paths.get('tests_and_exams'))
        content[school][level]['tests'][semester].update({courseCode: []})
        content[school][level]['exams'][semester].update({courseCode: []})

        # write updated content to file
        Utils.writeToFile(self.paths.get('tests_and_exams'), content)
        
        # --- end update of course in tests and exams file
    """
    remove a schoo/faculty from school
    """
    def removeSchool(self):
        schoolName = Utils.cleanString(input("Enter School/Faculty Name: ")).lower()

        # check if faculty/school exists
        checkSchool = Utils.checkFaculty(schoolName)

        if not checkSchool:
            console.print("\n[red bold]ERROR[/red bold]\n"\
                          f"Entered school {schoolName.upper()} doesn't exist!\n")
            return

        # delete school from all records
        schoolName = checkSchool
        Utils.deleteFaculty(schoolName)

        # write to admin log
        self.adminLog(f"removed faculty: {schoolName} from school")

        # print success message
        console.print(f"\n[green bold]SUCCESS[/green bold]\nOperations Completed!\n")

    """
    remove department
    """
    def removeDepartment(self):
        department = Utils.cleanString(input("Enter Department Name: ")).lower()

        # check if faculty/school exists
        checkDepartment = Utils.checkDepartment(department, False)

        if not checkDepartment:
            console.print("\n[red bold]ERROR[/red bold]\n"\
                          f"Entered department {department.upper()} doesn't exist!\n")
            return

        # delete school from all records
        department = checkDepartment
        Utils.deleteDepartment(department)

        # write to admin log
        self.adminLog(f"removed department: {department} from school")

        # print success message
        console.print(f"\n[green bold]SUCCESS[/green bold]\nOperations Completed!\n")

    """
    set tests 
    """
    def setTest(self):
        self.setQuestions("tests")

    """
    set exams
    """
    def setExam(self):
        self.setQuestions("exams")

    """
    set test or exam questions
    @setKey: used in access to set test or exam
    """
    def setQuestions(self, setKey=None):
        if not setKey:
            return

        # get faculty/school
        while True:
            school = Utils.cleanString(input("Enter School/Faculty: ")).lower()
            if not Utils.checkFaculty(school):
                console.print(f"\n[red]ERROR[/red]\nInvalid School/Faculty!\n")
                continue

            break

        # get level
        while True:
            level = Utils.cleanString(input("Enter level: "))
            if level not in self.levels:
                console.print(f"\n[red]ERROR[/red]\nInvalid Level!\n")
                continue

            break

        # get semester to set questions for
        while True:
            semester = Utils.cleanString(input("Enter semester: ")).lower()

            if semester == "first":
                semester = "first semester"
                break

            if semester == "second":
                semester = "second semester"
                break

            if semester == "first semester" or\
               semester == "second semester":
                break

            console.print(f"\n[red]ERROR[/red]\nInvalid Semester!\n")

        # get course code
        while True:
            course = Utils.cleanString(input("Enter Course Code: ")).lower()
            course = Utils.checkCourse(course)

            if not course:
                console.print(f"\n[red]ERROR[/red]\nInvalid Course!\n")
                continue

            break

        # get number of questions to be set
        while True:
            number = Utils.validateNumber(input("Enter number of questions: "))

            if not number:
                console.print(f"\n[red]ERROR[/red]\nInvalid Number!\n")
                continue

            if number < 5 or number > 100:
                console.print(f"\n[red]ERROR[/red]\nMin: 5 | Max: 100\n")
                continue

            break

        # get questions
        questionList = []

        for sn in range(1, number + 1):
            # setup panel
            panel = Panel("", title="[bold]Question[/bold]", subtitle=f"[italic]{sn} of {number}[/italic]")
            console.print(panel)

            # get question
            options = {}
            question = Utils.cleanString(input("Question: ")).lower()

            # get options
            for letter in range(ord('a'), ord('a') + 4):
                if chr(letter) == 'a':
                    console.print("\n[bold]Options:[/bold]\n")

                while True:
                    option = Utils.cleanString(input(f"Option {chr(letter)}: ")).lower()

                    if not option:
                        console.print(f"\n[red]ERROR[/red]\nType in an option!\n")
                        continue

                    break

                # update options dictionary for current question
                options.update({chr(letter): option})

            # get correct answer to question
            while True:
                correctOption = input("\nEnter correct option (a-d): ").strip().lower()

                # ensure string length is exactly 1
                if len(correctOption) != 1:
                    console.print(f"\n[red]ERROR[/red]\nInvalid option!\n")
                    continue                    

                # check if entered option is within range
                if ord(correctOption) not in range(ord('a'), ord('a') + 4):
                    console.print(f"\n[red]ERROR[/red]\nInvalid option!\n")
                    continue

                break

            # setup the question dict
            questionList.append({
                'question': question,
                'options': options,
                'correct option': correctOption
            })

        # --- set question in tests and exams dictionary
        try:
            content = Utils.loadFromFile(self.paths.get('tests_and_exams'))
            content[school][level][setKey][semester].update({course: questionList})

            Utils.writeToFile(self.paths.get('tests_and_exams'), content)

            # print success message
            console.print(f"\n[green bold]SUCCESS[/green bold]\nSuccessfuly set {setKey[:-1]} questions!\n")

            # add to admin log
            self.adminLog(f"set {setKey[:-1]} questions for course: {course} and level: {level}")
        except:
            console.print("\n[red]ERROR[/red]\nAn Error occured! \nYou cannot perform this operation!\n")
