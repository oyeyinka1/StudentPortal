from Modules.Utils import Utils
import hashlib
from rich.console import Console
from tabulate import tabulate

console = Console()

"""
student class
"""
class Student:
    """
    constructor function
    """
    def __init__(self, mainHandle):
        self.studentCommands = {
            'login': self.login,
            'logout': self.logout,
            'view courses': self.viewCourses
        }

        self.mainHandle = mainHandle
        self.mainHandleDict = self.mainHandle.__dict__
        self.command = self.mainHandleDict.get('command')
        self.students = self.mainHandleDict.get('students')

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
        matric = Utils.cleanString(matric)

        password = input("Enter your password: ")
        password = Utils.cleanString(password)
        hashedPassword = hashlib.md5(password.encode()).hexdigest()

        if matric in self.students.keys():
            self.studentInfo = self.students.get(matric)

            if hashedPassword == self.studentInfo['password']:
                # Set login data in main handle
                self.mainHandleDict['loggedIn'] = True
                self.mainHandleDict['user'] = 'student'
                self.mainHandle.prompt = f"[purple]({matric})   [/purple]"

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
    log the current user out of the portal
    """
    def logout(self):
        Utils.logout(self.mainHandle)

    """
    view first and second semester courses for current level
    """
    def viewCourses(self):
        courseLookup = {}

        courseLookup.update({'level': self.studentInfo.get('level')})
        courseLookup.update({'school': self.studentInfo.get('school')})
        courseLookup.update({'courseCode': self.studentInfo.get('courseCode')})

        courses = Utils.loadCourses(courseLookup)

        header = []
        tableRows = []

        # get table data
        for key, value in courses.items():
            row = []
            header.append(key.upper())

            row.append(f"Total Courses: {value.get('total courses')}")
            row.append(f"Total Credit Units: {value.get('total units')}")

            for course, units in value.get('courses').items():
                row.append(f"{course.upper()} - {units}")

            tableRows.append(row)

        print(header, tableRows)
        print(tabulate(tableRows, headers=header, tablefmt='rounded_outline'))
