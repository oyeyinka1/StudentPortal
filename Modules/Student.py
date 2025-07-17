from Modules.User import User
from Modules.Utils import Utils
import hashlib
from rich.console import Console
from rich.table import Table
from tabulate import tabulate

console = Console()

"""
student class
"""
class Student(User):
    """
    constructor function
    """
    def __init__(self, mainHandle):
        self.studentCommands = {
            'login': self.login,
            'logout': self.logout,
            'view courses': self.viewCourses
        }

        # call constructor of base class
        super().__init__(mainHandle)

        # set login data if user is logged in
        self.studentInfo = None
        if self.mainHandleDict.get('loggedInUser'):
            self.studentInfo = self.mainHandleDict.get('loggedInUser')

        # execute given command
        self.executeCommand()

    """
    execute user command
    """
    def executeCommand(self):
        if self.command in self.studentCommands.keys():
            self.studentCommands.get(self.command)()

    """
    log the student into the portal
    """
    def login(self):
        matric = input("Enter your matriculation number: ")
        matric = Utils.cleanString(matric).lower()

        password = input("Enter your password: ")
        password = Utils.cleanString(password)
        hashedPassword = hashlib.md5(password.encode()).hexdigest()

        if matric in self.students.keys():
            self.studentInfo = self.students.get(matric)

            # check if user is still in admission applications and has not setup student account
            if self.studentInfo.get('applicationId') in self.admissionApplications.keys():
                console.print("\n[red]ERROR[/red]\nYou must FIRST setup your student account!\n")
                return

            if hashedPassword == self.studentInfo['password']:
                # Set login data in main handle
                self.mainHandleDict['loggedIn'] = True
                self.mainHandleDict['user'] = 'student'
                self.mainHandle.prompt = f"[purple]({matric.upper()})   [/purple]"

                console.print(f"[green]\n<< Welcome back, {self.studentInfo['firstName']}! >>\n[/green]")

                # set login data for student
                self.mainHandleDict['loggedInUser'] = self.studentInfo

                # delete studentSetup key/value of student dictionary
                if self.studentInfo.get("studentSetup"):
                    del self.studentInfo["studentSetup"]
            else:
                console.print("[red]\nInvalid Matriculation Number or Password[/red]\n")
        else:
            console.print("[red]\nInvalid Matriculation Number or Password[/red]\n")

    """
    view first and second semester courses for current level
    """
    def viewCourses(self):
        courseLookup = {}

        courseLookup.update({'level': self.studentInfo.get('level')})
        courseLookup.update({'school': self.studentInfo.get('school')})
        courseLookup.update({'courseCode': self.studentInfo.get('courseCode')})

        courses = Utils.loadCourses(courseLookup)

        coursesSem1 = []
        coursesSem2 = []

        table = Table(title=f"Your {self.studentInfo.get('level')} Level Courses")

        # print dictionary info
        for key, value in courses.items():
            table.add_column(key.title())

        # get total units for both semesters
        table.add_row(f"Total Units: {courses.get('first semester').get('total units')}", \
                      f"Total Units: {courses.get('second semester').get('total units')}")

        # get total courses for both semesters
        table.add_row(f"Total Courses: {courses.get('first semester').get('total courses')}", \
                      f"Total Courses: {courses.get('second semester').get('total courses')}")

        # get the courses for both semesters
        sem1 = courses.get('first semester').get('courses')
        sem2 = courses.get('second semester').get('courses')

        # parse all sem 1 courses
        for key, value in sem1.items():
            coursesSem1.append(f"{value.get('code').upper()} | [purple]{value.get('unit')} Units[/purple]")

        # parse all sem 2 courses
        for key, value in sem2.items():
            coursesSem2.append(f"{value.get('code').upper()} | [purple]{value.get('unit')} Units[/purple]")

        # make table length equal for both courses
        if len(coursesSem1) < len(coursesSem2):
            while len(coursesSem1) < len(coursesSem2):
                coursesSem1.append("")
        elif len(coursesSem2) < len(coursesSem1):
            while len(coursesSem2) < len(coursesSem1):
                coursesSem2.append("")

        # add whiteline separator before adding courses
        table.add_row("\n", "\n")

        # add course data to table rows
        for sem1Course, sem2Course in zip(coursesSem1, coursesSem2):
            table.add_row(sem1Course, sem2Course)

        # print table
        console.print("\n", table, "\n")
