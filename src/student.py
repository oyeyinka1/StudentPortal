# standard library imports
import hashlib

# third party imports
from rich.table import Table
from tabulate import tabulate
from rich.console import Console

# local app imports
from src.user import User
from src.utils import Utils

# constants
CONSOLE = Console()

class Student(User):
    """
    handle student operations
    """

    def __init__(self, main_handle):
        self.student_commands = {
            'login': self.login,
            'logout': self.logout,
            'view courses': self.view_courses
        }

        # call constructor of base class
        super().__init__(main_handle)

        # set login data if user is logged in
        self.student_info = None
        if self.main_handle_dict.get('logged_in_user'):
            self.student_info = self.main_handle_dict.get('logged_in_user')

        # execute given command
        self.execute_command()

    def execute_command(self) -> None:
        """
        execute user command
        """

        if self.command in self.student_commands.keys():
            self.student_commands.get(self.command)()

    def login(self) -> None:
        """
        log the student into the portal
        """

        matric = input("Enter your matriculation number: ")
        matric = Utils.clean_string(matric).lower()

        password = input("Enter your password: ")
        password = Utils.clean_string(password)
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        if matric in self.students.keys():
            self.student_info = self.students.get(matric)

            # check if user is still in admission applications and has not setup student account
            if self.student_info.get('applicationId') in self.admission_applications.keys():
                CONSOLE.print("\n[red]ERROR[/red]\nYou must FIRST setup your student account!\n")
                return

            if hashed_password == self.student_info['password']:
                # Set login data in main handle
                self.main_handle_dict['logged_in'] = True
                self.main_handle_dict['user'] = 'student'
                self.main_handle.prompt = f"[purple]({matric.upper()})   [/purple]"

                CONSOLE.print(f"[green]\n<< Welcome back, {self.student_info['first_name']}! >>\n[/green]")

                # set login data for student
                self.main_handle_dict['logged_in_user'] = self.student_info

                # delete student_setup key/value of student dictionary
                if self.student_info.get("student_setup"):
                    del self.student_info["student_setup"]
            else:
                CONSOLE.print("[red]\nInvalid Matriculation Number or Password[/red]\n")
        else:
            CONSOLE.print("[red]\nInvalid Matriculation Number or Password[/red]\n")

    def view_courses(self) -> None:
        """
        view first and second semester courses for current level
        """

        course_lookup = {}

        course_lookup.update({'level': self.student_info.get('level')})
        course_lookup.update({'school': self.student_info.get('school')})
        course_lookup.update({'course_code': self.student_info.get('course_code')})

        courses = Utils.load_courses(course_lookup)

        courses_sem1 = []
        courses_sem2 = []

        table = Table(title=f"Your {self.student_info.get('level')} Level Courses")

        # print dictionary info
        for key, value in courses.items():
            table.add_column(key.title())

        # get total_units for both semesters
        table.add_row(f"Total Units: {courses.get('first_semester').get('total_units')}", \
                      f"Total Units: {courses.get('second_semester').get('total_units')}")

        # get total_courses for both semesters
        table.add_row(f"Total Courses: {courses.get('first_semester').get('total_courses')}", \
                      f"Total Courses: {courses.get('second_semester').get('total_courses')}")

        # get the courses for both semesters
        sem1 = courses.get('first_semester').get('courses')
        sem2 = courses.get('second_semester').get('courses')

        # parse all sem 1 courses
        for key, value in sem1.items():
            courses_sem1.append(f"{value.get('code').upper()} | [purple]{value.get('unit')} Units[/purple]")

        # parse all sem 2 courses
        for key, value in sem2.items():
            courses_sem2.append(f"{value.get('code').upper()} | [purple]{value.get('unit')} Units[/purple]")

        # make table length equal for both courses
        if len(courses_sem1) < len(courses_sem2):
            while len(courses_sem1) < len(courses_sem2):
                courses_sem1.append("")
        elif len(courses_sem2) < len(courses_sem1):
            while len(courses_sem2) < len(courses_sem1):
                courses_sem2.append("")

        # add whiteline separator before adding courses
        table.add_row("\n", "\n")

        # add course data to table rows
        for sem1_course, sem2_course in zip(courses_sem1, courses_sem2):
            table.add_row(sem1_course, sem2_course)

        # print table
        CONSOLE.print("\n", table, "\n")
