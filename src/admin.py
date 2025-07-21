# standard library imports
import hashlib, datetime, os, random, csv, \
    platform, subprocess, string, subprocess

# third party imports
from typing import Union
from tabulate import tabulate
from collections import Counter
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, \
    Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# local app imports
from src.user import User
from src.utils import Utils

# constants
CONSOLE = Console()

class Admin(User):
    """
    handle admin commands and \
    functionalities
    """

    def __init__(self, main_handle) -> None:
        self.admin_commands = {
            'login': self.login,
            'logout': self.logout,
            'admit applicants': self.admit_student,
            'add admin': self.add_admin,
            'add school': self.add_school,
            'reject applicants': self.reject_student,
            'view my log': self.view_my_log,
            'view admins': self.view_admins,
            'view students': self.view_students,
            'view admin log': self.view_admin_log,
            'add department': self.add_department,
            'view school stats': self.school_stats,
            'export students': self.export_students,
            'view applications': self.view_applications,
            'view commands': self.view_commands,
            'expel student': self.expel_student,
            'suspend student': self.suspend_student,
            'unsuspend student': self.unsuspend_student,
            'add course': self.add_course,
            'bulk expel': self.bulk_expel_students,
            'bulk suspend': self.bulk_suspend_students,
            'bulk unsuspend': self.bulk_unsuspend_students,
            'remove school': self.remove_school,
            'remove department': self.remove_department,
            'set test': self.set_test,
            'set exam': self.set_exam
        }

        # call constructor of base class
        super().__init__(main_handle)

        # set root admin if db file does not exist
        if not self.main_handle_dict.get('admins'):
            self.main_handle_dict['admins'] = Utils.root_admin()
        
        # check if there is a logged in user and set user data
        if self.main_handle.logged_in:
            self.set_logged_in_data(self.main_handle_dict.get('logged_in_user'))

        # execute given user command
        self.execute_command()

    def execute_command(self) -> None:
        """
        execute user command
        """

        if self.command in self.admin_commands.keys():
            self.admin_commands.get(self.command)()

    def view_commands(self) -> None:
        """
        view list of available commands
        """

        CONSOLE.print("\n[blue]Available Admin Commands:[/blue]\n")

        for cmd in sorted(self.admin_commands.keys(), key=len):
            CONSOLE.print(f"[green]{cmd}[/green]")

        print()

    def get_admin_data(self) -> dict:
        """
        get registration data of new admin
        """

        # get the admin dictionary
        admins = self.main_handle_dict.get('admins')
        admin_emails = []
        admin_usernames = []

        if admins:
            # get all emails
            for key, value in admins.items():
                admin_emails.append(value.get('email'))

            # get all usernames
            for key, value in admins.items():
                admin_usernames.append(value.get('username'))
            
        # get and validate first_name
        while True:
            first_name = input("Enter First_Name: ").lower()
            check = Utils.validate_name(first_name)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
            else:
                break

        # get and validate last name
        while True:
            last_name = input("Enter Last Name: ").lower()
            check = Utils.validate_name(last_name)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
            else:
                break

        # get and validate email
        while True:
            email = input("Enter Email: ")
            email = Utils.clean_string(email).lower()

            if Utils.is_valid_email(email):
                if email in admin_emails:
                    CONSOLE.print(f"Entered email [yellow]`{email}`[/yellow]"
                                  "already exists!")
                    continue

                break
            else:
                CONSOLE.print("[red]Invalid email. Try again![/red]")

        # get and validate username
        while True:
            username = input("Enter Username: ")
            username = Utils.clean_string(username).lower()
            check = Utils.validate_username(username)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
            else:
                if username in admin_usernames:
                    CONSOLE.print(f"Username [yellow]`{username}`[/yellow] is already taken!")
                    continue

                break

        # get and validate password
        while True:
            password = input("Enter Password: ")
            check = Utils.validate_password(password)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
            else:
                break

        # hash password
        password = hashlib.md5(password.encode()).hexdigest()

        # assign collected data to new list
        admin_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
            'password': password
        }

        # return admin data
        return admin_data

    def add_admin(self) -> None:
        """
        add a new admin with priviledges
        """

        # cancel operation if user is not root
        if self.username != "root":
            CONSOLE.print("\n[red]Only the root admin can do this![/red]\n")
            return

        # get info of new admin
        admin_data = self.get_admin_data()

        # new admin dictionary
        admin = {
            'username': admin_data['username'],
            'password': admin_data['password'],
            'email': admin_data['email'],
            'first_name': admin_data['first_name'],
            'last_name':  admin_data['last_name']
        }

        # add new admin to main handle dictionary for admins
        self.main_handle_dict['admins'].update({admin_data['username']: admin})

        # add entry to admin log
        self.admin_log(f"added new admin with username: {admin_data['username']}")

        # print success message
        CONSOLE.print("\n[green]SUCCESS[/green]\n"\
                      f"Admin with username [yellow]{admin_data['username']}[/yellow]"\
                      " was created!\n")

    def view_admins(self) -> None:
        """
        view current admins on the portal
        """

        sn = 1
        table = []
        admins = self.main_handle_dict.get('admins')

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

    def _admit(self, applicant_id: str = None) -> Union[None, True]:
        """
        helper function for the admit_student method
        """

        if applicant_id:
            applicant_id = applicant_id.lower()

        # check if application exists
        if applicant_id not in self.admission_applications.keys():
            CONSOLE.print("\n[red]ERROR[/red]\nInvalid UID!\n")
        elif self.admission_applications.get(applicant_id)['application_status'] != 'pending':
            # return silently if status is not = pending
            return
        else:
            # get applicant info
            applicant_info = self.admission_applications.get(applicant_id)
            matric_tail = applicant_info.get('course_code')[0:2]
            digits = f"{random.randint(0,99999):05}"
            matric = f"{datetime.datetime.now().year}/1/{digits}{matric_tail}"
            admission_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            # set student info
            student = {
                'application_id': applicant_info.get('id'),
                'email': applicant_info.get('email'),
                'first_name': applicant_info.get('first_name'),
                'middle_name': applicant_info.get('middle_name'),
                'last_name': applicant_info.get('last_name'),
                'date_of_birth': applicant_info.get('date_of_birth'),
                'state_of_origin': applicant_info.get('state_of_origin'),
                'state_of_residence': applicant_info.get('state_of_residence'),
                'school': applicant_info.get('school'),
                'department': applicant_info.get('course_of_choice'),
                'course_code': applicant_info.get('course_code'),
                'password': applicant_info.get('password'),
                'matric_no': matric,
                'admission_date': admission_date,
                'level': 100,
                'cgpa': 0.00
            }

            # update admission application status
            self.admission_applications[applicant_id]['application_status'] = "admitted"
            
            # add matric number to application data for easy password change and lookup
            self.admission_applications[applicant_id]['matric_no'] = matric

            # create students attribute of main handle if it does not exist
            if not self.main_handle_dict.get('students'):
                self.main_handle_dict['students'] = {}

            self.main_handle_dict['students'].update({matric: student})
                
            # print success message
            CONSOLE.print(f"\n[green]SUCCESS[/green]\n{applicant_info.get('first_name').title()} "\
                          f"{applicant_info.get('last_name').title()} has been admitted successfully!\n"
                          f"Matric No: {matric.upper()}\n")

            # log admin action
            self.admin_log(f"admitted {applicant_id} "\
                          f"with matric no: {matric}")

            return True

    def admit_student(self) -> None:
        """
        admit student
        """

        check = False
        mode_list = ['single', 'batch', 'all']

        # check if there are current admission applications
        for key, value in self.admission_applications.items():
            if value.get('application_status') == 'pending':
                check = True
                break

        if not check:
            CONSOLE.print("\n[yellow]INFO[/yellow]\nThere are no pending applications!\n")
            return

        # print mode of admission
        CONSOLE.print("\n[yellow]ADMISSION MODES[/yellow]\n")
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

            if mode not in mode_list:
                CONSOLE.print("\n[red]ERROR[/red]\nInvalid mode selected\n")
            else:
                break

        # prompt to print admission applications 
        while True:
            table_confirm = input("View applications? [Y | N]:  ").strip().lower()

            if table_confirm == "y" or \
               table_confirm == "yes":
                self.view_applications()
                break
            elif table_confirm == "n" or \
                 table_confirm == "no":
                break
            else:
                CONSOLE.print("\n[red]ERROR[/red]\nInvalid option entered!\n")

        # handle admission for selected mode
        if mode == "single":
            # get user ID of applicant to be admitted
            uid = input("Enter UID of applicant: ")
            uid = Utils.clean_string(uid)

            self._admit(uid)
        elif mode == "batch":
            uids = input("Enter UIDs of applicants to be admitted (separated by commas): ")
            uids = Utils.clean_string(uids).replace(" ", "").split(',')
            admitted_count = 0

            for uid in uids:
                if self._admit(uid):
                    admitted_count += 1

            if admitted_count > 0:
                CONSOLE.print(f"\n[green]SUCCESS[/green]\n{admitted_count} "\
                              "applicant(s) have been admitted successfully!\n")
        elif mode == "all":
            admitted_count = 0

            for uid in list(self.admission_applications.keys()):
                # check and only attempt to admit students with `pending` status
                if self.admission_applications.get(uid)['application_status'] != 'pending':
                    continue

                if self._admit(uid):
                    admitted_count += 1

            if admitted_count > 0:
                CONSOLE.print(f"\n[green]SUCCESS[/green]\n{admitted_count} "\
                              "applicant(s) have been admitted successfully!\n")

    def _reject(self, applicant_id: str) -> Union[None, True]:
        """
        helper function for reject_student method
        """

        # check if application exists
        if applicant_id not in self.admission_applications.keys():
            CONSOLE.print("\n[red]ERROR[/red]\nInvalid UID!\n")
        elif applicant_id in self.admission_applications.keys() and \
             self.admission_applications.get(applicant_id)['application_status'] == 'rejected':
            CONSOLE.print(f"Applicant with UID: [yellow]{applicant_id}[/yellow]"\
                          " has already been rejected!")
        else:
            # update admission application status
            self.admission_applications[applicant_id]['application_status'] = "rejected"

            # print success message
            CONSOLE.print(f"\n[green]SUCCESS[/green]\nApplicant with UID: {applicant_id} "\
                          f"has been denied admission!\n")

            # log admin action
            self.admin_log(f"rejected {applicant_id}")
            
            Utils.save_data(self.paths.get('db'), self.main_handle_dict)

            return True

    def reject_student(self) -> None:
        """
        reject student admission
        """

        mode_list = ['single', 'batch', 'all']

        # check if there are current admission applications
        if not self.admission_applications:
            CONSOLE.print("\n[yellow]INFO[/yellow]\nThere"\
                          " are no applications currently!\n")
            return

        # print mode of admission
        CONSOLE.print("\n[yellow]ADMISSION REJECTION MODES[/yellow]\n")
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

            if mode not in mode_list:
                CONSOLE.print("\n[red]ERROR[/red]\nInvalid mode selected\n")
            else:
                break

        # prompt to print admission applications 
        while True:
            table_confirm = input("View applications? [Y | N]:  ").strip().lower()

            if table_confirm == "y" or \
               table_confirm == "yes":
                self.view_applications()
                break
            elif table_confirm == "n" or \
                 table_confirm == "no":
                break
            else:
                CONSOLE.print("\n[red]ERROR[/red]\nInvalid option entered!\n")

        # handle admission rejection for selected mode
        if mode == "single":
            # get user ID of applicant to be rejected
            uid = input("Enter UID of applicant: ")
            uid = Utils.clean_string(uid)

            self._reject(uid)
        elif mode == "batch":
            uids = input("Enter UIDs of applicants to be rejected (separated by commas): ")
            uids = Utils.clean_string(uids).replace(" ", "").split(',')
            rejected_count = 0

            for uid in uids:
                if self._reject(uid):
                    rejected_count += 1

            if rejected_count > 0:
                CONSOLE.print(f"\n[green]SUCCESS[/green]\n{rejected_count} "\
                              "applicant(s) have been denied admission!!\n")
        elif mode == "all":
            rejected_count = 0

            for uid in list(self.admission_applications.keys()):
                if self._reject(uid):
                    rejected_count += 1

            if rejected_count > 0:
                CONSOLE.print(f"\n[green]SUCCESS[/green]\n{rejected_count} "\
                              "applicant(s) have been denied admission!\n")

    def view_applications(self) -> None:
        """
        view admission applications
        """

        # check if there are available applications
        if not self.admission_applications:
            CONSOLE.print("\n[yellow]There are no "\
                          "available admission applications "\
                          "at the moment!\n[/yellow]")
            return

        # format header
        sn = 1
        data = []
        header = ["SN", "ID", "COURSE", "EMAIL", "UTME SCORE", "APPLICATION DATE"]

        # print applications
        for key, value in self.admission_applications.items():
            # do not fetch application if status is not <pending>
            if value.get('application_status') != 'pending':
                continue

            # get values
            sub_data = []
            sub_data.append(sn)
            sub_data.append(value.get('id').upper())
            sub_data.append(value.get('course_of_choice').title())
            sub_data.append(value.get('email'))
            sub_data.append(value.get('jamb_score'))
            sub_data.append(value.get('application_date'))

            # append values to data
            data.append(sub_data)
            sn += 1

        # print table if there are pending applications
        if data:
            print(tabulate(data, headers=header, tablefmt="grid"))
        else:
            CONSOLE.print("\n[yellow]There are no "\
                          "available admission applications "\
                          "at the moment!\n[/yellow]")

        # save action to admin log
        self.admin_log("viewed admission applications")

    def login(self) -> None:
        """
        log in as admin
        """

        # get admin dictionary
        admins = self.main_handle_dict.get('admins')

        # get username and password of admin
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        # clean the username and password input
        username = Utils.clean_string(username)
        password = Utils.clean_string(password)

        # hash user password
        password = hashlib.md5(password.encode())
        password = password.hexdigest()

        # check if admin exists and log admin in
        if username in admins.keys():
            if password == admins[username]['password']:
                # call set logged in data method
                self.set_logged_in_data(admins.get(username))

                # print login successful message
                CONSOLE.print(f"\n[green] Welcome {self.username}![/green]")
                CONSOLE.print("[blue]Type 'view commands' to see a list of available commands[/blue]\n")
            else:
                CONSOLE.print("\n[red]Invalid username or password![/red]\n")
        else:
            CONSOLE.print("\n[red]Invalid username or password![/red]\n")

    def set_logged_in_data(self, admin: dict) -> None:
        """
        set login data for current admin
        """

        # set admin attributes for current admin
        self.email = admin.get('email')
        self.username = admin.get('username')
        self.password = admin.get('password')
        self.last_name = admin.get('last_name')
        self.first_name = admin.get('first_name')
        self.middle_name = admin.get('middle_name')

        # set main_handle attributes for login
        self.main_handle.user = 'admin'
        self.main_handle.logged_in = True
        self.main_handle.logged_in_user = admin
        self.main_handle.prompt = f"[red]({self.username}@admin):   [/red]"

    def admin_log(self, action: str = None) -> None:
        """
        write admin action to the log file
        """

        # return if no action specified
        if not action:
            return

        date_object = datetime.datetime.now()
        date = date_object.strftime("%d-%B-%Y")
        time = date_object.strftime("%I:%M %p")
        filepath = self.paths.get('admin_logs')

        # format message to be logged
        message = f"[ADMIN] - ({self.username}@{self.email})"\
            f" - ({action}) on ({date}) at ({time})\n"

        # write to file
        with open(filepath, 'a') as file:
            file.write(message)

    def view_admin_log(self) -> None:
        """
        view admin logs
        """

        # check if log file exists
        filepath = self.paths.get('admin_logs')
        check_file = os.path.exists(filepath)

        if check_file:
            # use the <less> to view admin log
            try:
                subprocess.run(['less', filepath], check=True)
            except:
                CONSOLE.print("[red]\nError loading logs!\n[/red]")
        else:
            CONSOLE.print("[yellow]Oops, no logs have "\
                          "been kept for admins quite yet[/yellow]")

    def view_my_log(self) -> None:
        """
        view logs for current admin
        """

        my_actions = []
        ny_key = f"{self.username}@{self.email}"
        filepath = self.paths.get('admin_logs')
        check_file = os.path.exists(filepath)

        if check_file:
            with open(filepath, 'r') as file:
                content = file.readlines()

            # loop through file list
            for i in content:
                log = i[:-1]
                
                # check if admin performed current action
                if ny_key in log:
                    # append action to current admin actions
                    my_actions.append(log)

            # print current admin actions if any
            if my_actions:
                print()

                for j in my_actions:
                    print(j)

                print()
            else:
                CONSOLE.print("\n[yellow]Oops, you've performed "\
                              "no actions yet[/yellow]\n")
        else:
            CONSOLE.print("\n[yellow]Oops, no logs have "\
                          "been kept for admins quite yet[/yellow]\n")
    
    def view_students(self) -> None:
        """
        view all students
        """

        # check if there are students
        if not self.students:
            CONSOLE.print("\n[yellow]There are no students admitted yet![/yellow]\n")
            return

        sn = 1
        table = []
        header = ["SN", "MATRIC NO.", "NAME", "COURSE", "EMAIL", "STATUS"]

        for uid, student in self.students.items():
            full_name = f"{student.get('first_name')} {student.get('last_name')}"
            status = "Suspended" if student.get('suspended') else "Active"
            table.append([
                sn,
                student.get('matric_no').upper(),
                full_name.title(),
                student.get('department').title(),
                student.get('email'),
                status
            ])
            sn += 1

        print(tabulate(table, headers=header, tablefmt="grid"))

    def school_stats(self) -> None:
        """
        view school statistics
        """

        if not self.students:
            CONSOLE.print("\n[yellow]No student data available[/yellow]\n")
            return

        totalStudents = len(self.students)
        per_course = {}
        per_school = {}

        for s in self.students.values():
            course = s.get('course_of_choice')
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
            course = s.get('course_of_choice')
            if course in per_course:
                per_course[course] += 1

        CONSOLE.print("\n[green]Student Statistics[/green]\n")
        for course, count in per_course.items():
            print(f"Total Students: {count} student(s)")

        CONSOLE.print("\n[green]School Statistics[/green]\n")
        for school, count in per_school.items():
            print(f"{school.upper()}: {count} student(s)\n")

    def open_file(self, filepath: str) -> None:
        """
        put comment here
        """

        try:
            if platform.system() == "Windows": # windows
                os.startfile(filepath)
            elif platform.system() == "Darwin":  # mac
                subprocess.run(["open", filepath])
            else:  # linux
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            CONSOLE.print(f"[red]Couldn't open file automatically: {e}[/red]")

    def export_students(self) -> None:
        """
        put comment here
        """

        if not self.students:
            CONSOLE.print("\n[yellow]No students available to export.[/yellow]\n")
            return

        format_options = ['pdf', 'csv']

        while True:
            file_format = input("Enter export format (pdf/csv): ").strip().lower()
            if file_format in format_options:
                break
            else: 
                CONSOLE.print("[red]Invalid format. Please choose 'csv' or 'pdf'.[/red]")

        downloads_folder = str(Path.home() / "Downloads")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"students_{timestamp}.{file_format}"
        suggested_path = os.path.join(downloads_folder, default_name)

        file_path = input(f"Enter full path to save the file [Default: {suggested_path}]: ").strip()
        if not file_path:
            file_path = suggested_path

        if file_format == 'pdf':
            self.export_students_as_pdf(file_path)
        elif file_format == 'csv':
            self.export_student_as_csv(file_path)

    def export_students_as_pdf(self, filepath: str) -> None:
        """
        put comment here
        """

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
            style_sheet = getSampleStyleSheet()

            # customize the heading style
            header_style = style_sheet['Heading1']
            header_style.leftIndent = 0
            header_style.alignment = 0  # 0 = left, 1 = center, 2 = right

            elements.append(Paragraph("List of admitted students", header_style))
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
                full_name = " ".join([
                    student.get("first_name", ""),
                    student.get("middle_name", ""),
                    student.get("last_name", "")
                ]).strip().title()
                row = ([
                    index,
                    student.get("matric_no").upper(),
                    full_name,
                    student.get("email"),
                    student.get("department").title(),
                    student.get("school").upper(),
                    student.get("admission_date"),
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
            elements.append(Paragraph(f"Total students: {len(self.students)}", style_sheet['Normal']))

            doc.build(elements)

            CONSOLE.print(f"\n[green]SUCCESS[/green] PDF exported to: [blue]{filepath}[/blue]\n")
            self.admin_log(f"exported students list as PDF to {filepath}")
            self.open_file(filepath)

        except Exception as e:
            CONSOLE.print(f"\n[red]ERROR[/red] Failed to export PDF: {e}\n")

    def export_student_as_csv(self, filepath: str) -> None:
        """
        put comment here
        """

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
                        "Matric Number": student.get("matric_no"),
                        "First Name": student.get("first_name"),
                        "Middle Name": student.get("middle_name"),
                        "Last Name": student.get("last_name"),
                        "Email": student.get("email"),
                        "Course of study": student.get("course_of_choice"),
                        "School": student.get("school"),
                        "Admission Date": str(student.get("admission_date", ""))
                    })

                writer.writerow({})
                writer.writerow({"Matric Number": f"Total Students: {len(self.students)}"})

            CONSOLE.print(f"\n[green]SUCCESS[/green] Exported students to [blue]{filepath}[/blue]\n")
            self.admin_log(f"exported students list as CSV to {filepath}")
            self.open_file(filepath)

        except Exception as e:
            CONSOLE.print(f"\n[red]ERROR[/red] Failed to export students: {e}\n")

    def add_school(self) -> None:
        """
        add a new school/faculty to school
        """

        # get full name of school
        while True:
            school_name = input("Enter full name of school/faculty: ")
            school_name = Utils.clean_string(school_name).lower()
            check = False

            # check for valid school name
            for i in school_name:
                if i not in f"{string.ascii_letters}'- ":
                    CONSOLE.print(f"[red]Invalid characters in school name[/red]")
                    check = True
                    break

            if not check:
                break

        # check if school already exists
        if Utils.check_faculty(school_name):
            CONSOLE.print(f"\nSchool [yellow italic]{school_name.title()}[/yellow italic] already exists!\n")
            return

        # get school initials
        while True:
            initials = input("Enter initials for school: ")
            initials = Utils.clean_string(initials).lower()
            check = Utils.validate_name(initials)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
            else:
                break

        # check if school already exists
        if Utils.check_faculty(initials):
            CONSOLE.print(f"\nSchool with initials: [yellow]{initials.upper()}[/yellow] already exists!\n")
            return

        # save school/faculty to dictionary
        Utils.save_school(school_name, initials)

        # save action to admin log
        self.admin_log(f"added new faculty: {school_name}")

    def add_department(self) -> None:
        """
        add a new department under a school/faculty
        """

        # get faculty/school name to add department under
        school_name = input("Enter name of parent Faculty: ")
        school_name = Utils.clean_string(school_name).lower()

        # check if entered school exists
        faculty = Utils.check_faculty(school_name)

        if not faculty:
            CONSOLE.print(f"\nEntered faculty [yellow underline]"\
                          f"{school_name}[/yellow underline] does not exist\n")

            CONSOLE.print("[yellow]OPTIONS[/yellow]\n\n"\
                          "[yellow bold]1[/yellow bold]  View current faculties\n"\
                          "[yellow bold]2[/yellow bold]  Add new faculty/school\n")

            option = input("Enter chosen option: ").strip()

            # view current faculties if user chose `1`
            if option == '1':
                Utils.view_faculties()
            elif option == '2':
                self.add_school()
            else:
                CONSOLE.print("[red]Invalid option![/red]")
                return
        else:
            # get full department name
            while True:
                dept_name = input("Enter full department name: ")
                dept_name = Utils.clean_string(dept_name).lower()
                check = Utils.check_department(dept_name)

                if check:
                    CONSOLE.print(f"[red]{check}[/red]")
                else:
                    break

            # get department/course code
            while True:
                dept_code = input("Enter department/course code: ")
                dept_code = Utils.clean_string(dept_code).lower()
                check = Utils.check_department(dept_code)

                if check:
                    CONSOLE.print(f"[red]{check}[/red]")
                else:
                    break


            # get cut off mark for current department
            while True:
                dept_cut_off = input("Enter cut off mark for department: ")
                dept_cut_off = Utils.validate_number(dept_cut_off)

                if dept_cut_off:
                    # check if cut off is within min and max range
                    if dept_cut_off < 0:
                        CONSOLE.print(f"\n[yellow]Cut off can't be less than 0[/yellow]")
                    elif dept_cut_off > 400:
                        CONSOLE.print(f"\n[red]Cut off can't be greater than 400[/red]")
                    else:
                        break
                else:
                    CONSOLE.print("\n[red]Invalid number entered![/red]\n")

            # add new department with details
            Utils.add_department(faculty, dept_name, dept_code, dept_cut_off)

            # save action to admin log
            self.admin_log(f"added new department [{dept_name}] to faculty [{faculty}]")

    def expel_student(self) -> None:
        """
        expel a student
        """

        if not self.students:
            CONSOLE.print("\n[yellow]No students to expel![/yellow]\n")
            return

        matric_no = input("Enter Matric Number of student to expel: ").strip().lower()

        if matric_no in self.students:
            student = self.students[matric_no]
            full_name = f"{student.get('first_name')} {student.get('last_name')}"\
                f" {student.get('middle_name', '')}"

            CONSOLE.print(f"\n[red bold]WARNING![/red bold] You are about to "\
                          f"[red]EXPEL[/red] {full_name.title()} (Matric No: {matric_no}).")
            confirm = input("Are you sure? Type 'yes' to confirm: ").strip().lower()

            if confirm == 'yes':
                self.students.pop(matric_no)

                CONSOLE.print(f"\n[red]Student {matric_no} has been expelled.[/red]\n")
                self.admin_log(f"expelled student {matric_no} ({full_name})")
            else:
                CONSOLE.print("\n[yellow]Action cancelled. No student was expelled.[/yellow]\n")
        else:
            CONSOLE.print(f"\n[yellow]No student found with Matric No {matric_no}[/yellow]\n")

    def bulk_expel_students(self) -> None:
        """
        bulk expel
        """

        students = self.main_handle_dict.get('students')
        if not students:
            CONSOLE.print("\n[yellow]No students available![/yellow]\n")
            return

        file_path = Utils.prompt_file_selection()
        if not file_path:
            return

        matric_nos = Utils.extract_matric_numbers(file_path)
        if not matric_nos:
            CONSOLE.print("[red]No valid matric numbers found in the file.[/red]")
            return

        expelled, not_found = [], []

        for matric in matric_nos:
            if matric in students:
                student = students.pop(matric)
                expelled.append((matric, f"{student.get('first_name')} {student.get('last_name')}"))
                self.admin_log(f"bulk expelled student {matric} ({student.get('first_name')} {student.get('last_name')})")
            else:
                not_found.append(matric)

        if expelled:
            CONSOLE.print("\n[red bold]Expelled Students:[/red bold]")
            for m, name in expelled:
                CONSOLE.print(f"[red]{m} - {name}[/red]")

        if not_found:
            CONSOLE.print("\n[yellow bold]Matric numbers not found:[/yellow bold]")
            for m in not_found:
                CONSOLE.print(f"[yellow]{m}[/yellow]")

    def suspend_student(self) -> None:
        """
        suspend a student
        """

        if not self.students:
            CONSOLE.print("\n[yellow]No students to suspend![/yellow]\n")
            return

        matric_no = input("Enter Matric Number of student to suspend: ").strip().lower()

        if matric_no in self.students:
            student = self.students[matric_no]
            student['suspended'] = True 
            CONSOLE.print(f"\n[yellow]Student {matric_no.upper()} has been suspended.[/yellow]\n")
            self.admin_log(f"suspended student {matric_no} ({student.get('first_name')} {student.get('last_name')})")
        else:
            CONSOLE.print(f"\n[yellow]No student found with Matric No {matric_no}[/yellow]\n")


    def bulk_suspend_students(self) -> None:
        """
        bulk suspend
        """

        students = self.main_handle_dict.get('students')
        if not students:
            CONSOLE.print("\n[yellow]No students available![/yellow]\n")
            return

        file_path = Utils.prompt_file_selection()
        if not file_path:
            return

        matric_nos = Utils.extract_matric_numbers(file_path)
        if not matric_nos:
            CONSOLE.print("[red]No valid matric numbers found in the file.[/red]")
            return

        suspended, not_found = [], []

        for matric in matric_nos:
            if matric in students:
                students[matric]['suspended'] = True
                suspended.append((matric, f"{students[matric].get('first_name')} {students[matric].get('last_name')}"))
                self.admin_log(f"suspended student {matric} ({students[matric].get('first_name')} {students[matric].get('last_name')})")
            else:
                not_found.append(matric)


        if suspended:
            CONSOLE.print("\n[yellow bold]Suspended Students:[/yellow bold]")
            for m, name in suspended:
                CONSOLE.print(f"[yellow]{m} - {name}[/yellow]")

        if not_found:
            CONSOLE.print("\n[red bold]Matric numbers not found:[/red bold]")
            for m in not_found:
                CONSOLE.print(f"[red]{m}[/red]")

    def unsuspend_student(self) -> None:
        """
        unsuspend a student
        """

        if not self.students:
            CONSOLE.print("\n[yellow]No students available![/yellow]\n")
            return

        matric_no = input("Enter Matric Number of student to unsuspend: ").strip().lower()

        if matric_no in self.students:
            student = self.students[matric_no]

            if student.get('suspended'):
                student['suspended'] = False
                CONSOLE.print(f"\n[green]Student {matric_no.upper()} has been unsuspended.[/green]\n")
                self.admin_log(f"unsuspended student {matric_no} ({student.get('first_name')} {student.get('last_name')})")
            else:
                CONSOLE.print(f"\n[yellow]Student {matric_no.upper()} is not suspended.[/yellow]\n")
        else:
            CONSOLE.print(f"\n[yellow]No student found with Matric No {matric_no.upper()}[/yellow]\n")

    def bulk_unsuspend_students(self) -> None:
        """
        bulk unsusend
        """

        students = self.main_handle_dict.get('students')
        if not students:
            CONSOLE.print("\n[yellow]No students available![/yellow]\n")
            return

        file_path = Utils.prompt_file_selection()
        if not file_path:
            return

        matric_nos = Utils.extract_matric_numbers(file_path)
        if not matric_nos:
            CONSOLE.print("[red]No valid matric numbers found in the file.[/red]")
            return

        unsuspended, not_found, already_active = [], [], []

        for matric in matric_nos:
            if matric in students:
                if students[matric].get('suspended'):
                    students[matric]['suspended'] = False
                    unsuspended.append((matric, f"{students[matric].get('first_name')} {students[matric].get('last_name')}"))
                    self.admin_log(f"unsuspended student {matric} ({students[matric].get('first_name')} {students[matric].get('last_name')})")
                else:
                    already_active.append(matric)
            else:
                not_found.append(matric)

        if unsuspended:
            CONSOLE.print("\n[green bold]Unsuspended Students:[/green bold]")
            for m, name in unsuspended:
                CONSOLE.print(f"[green]{m} - {name}[/green]")

        if already_active:
            CONSOLE.print("\n[yellow bold]These students were not suspended:[/yellow bold]")
            for m in already_active:
                CONSOLE.print(f"[yellow]{m}[/yellow]")

        if not_found:
            CONSOLE.print("\n[red bold]Matric numbers not found:[/red bold]")
            for m in not_found:
                CONSOLE.print(f"[red]{m}[/red]")

    def add_course(self) -> None:
        """
        add a new course to a faculty or department
        """

        department = subtract_units = None

        # print options
        CONSOLE.print(
            "\nOPTIONS:\n\n",
            "[yellow bold]1[yellow bold] Set course for entire faculty\n",
            "[yellow bold]2[yellow bold] Set course for specific department\n"
        )

        # check chosen option
        option = input("Enter option: ").strip()
        if option != '1' and option != '2':
            CONSOLE.print("Invalid option entered!")
            return

        # ask to view available faculties in the school
        if input("View faculties in the school? (Yes | No)  ").strip().lower() == 'yes':
            Utils.view_faculties()

        # get school/faculty name
        while True:
            school = Utils.clean_string(input("Enter school: "))
            check_faculty = Utils.check_faculty(school)
            if check_faculty:
                school = check_faculty.lower()
                break
            CONSOLE.print("[yellow]Invalid faculty entered![/yellow]")

        # end execution if school has no departments
        if Utils.check_not_empty_faculty(school):
            CONSOLE.print("\n[red]There are no current departments in chosen faculty![/red]\n")
            return

        # ask for department if chosen option is 2
        while True and option == '2':
            department = Utils.clean_string(input("Enter department: ")).lower()
            department = Utils.check_department(department, False)
            if department:
                break
            CONSOLE.print("[yellow]Invalid department entered![/yellow]")

        # get level
        while True:
            level = input("Enter level: ").strip()
            if level in self.levels:
                break
            CONSOLE.print("[yellow]Invalid level entered![/yellow]")

        # get semester to set course for
        if level == '400':
            semester = 'first_semester'
            CONSOLE.print("\nSemester: (first)\n")
        else:
            CONSOLE.print("\nSemesters: (first, second)\n")
            while True:
                semester = input("Enter semester: ")
                semester = Utils.clean_string(semester).lower()

                if semester == 'first' or semester == 'second':
                    semester = f"{semester}_semester"
                    break

                if semester == 'first_semester' or semester == 'second_semester':
                    break

                CONSOLE.print("[yellow]Invalid semester entered![/yellow]")

        # get all available courses
        courses = Utils.load_courses()
        CONSOLE.rule(style="dim white", characters="-")

        # get course name
        while True:
            course_name = Utils.clean_string(input("Enter full course name: ")).lower()

            if course_name:
                if department:
                    # check if course exists and prompt to overwrite
                    check_course = courses[school][department][level][semester]['courses']

                    for key, value in check_course.items():
                        if course_name == value.get('name'):
                            CONSOLE.print(f"\n[yellow]Course {course_name.title()} already exists![/yellow]")

                            while True:
                                confirm = input("Continue to overwrite (Yes | No)?  ").lower()

                                if confirm == "no":
                                    CONSOLE.print("[red]Operation Aborted![/red]")
                                    return
                                elif confirm == 'yes':
                                    pop_course_code = courses[school][department][level][semester]['courses'][course_name]['code']
                                    subtract_units = courses[school][department][level][semester]['courses'][course_name]['unit']
                                    break
                                else:
                                    CONSOLE.print("[red]Invalid Input![/red]")
                            break
                else:
                    # loop through departments and check for a duplicate course
                    for key, value in courses[school].items():
                        for key, value in value[level][semester]['courses'].items():
                            if course_name == value.get('name'):
                                CONSOLE.print(f"\n[yellow]Course {course_name.title()} already exists![/yellow]")

                                while True:
                                    confirm = input("Continue to overwrite (Yes | No)?  ").lower()

                                    if confirm == "no":
                                        CONSOLE.print("[red]Operation Aborted![/red]")
                                        return
                                    elif confirm == 'yes':
                                        pop_course_code = value.get('code')
                                        subtract_units = value.get('unit')
                                        break
                                    else:
                                        CONSOLE.print("[red]Invalid Input![/red]")
                                break

                        # break outer loop if subtract_units is set
                        if subtract_units:
                            break
                break
                            
        # get course code
        while True:
            course_code = Utils.clean_string(input("Enter Course code: ")).lower()
            if course_code:
                break

        # get course units
        while True:
            course_unit = Utils.validate_number(input("Enter course units: "))
            if course_unit:
                break

            CONSOLE.print("[yellow]Invalid unit entered![/yellow]")

        # set new course dictionary
        new_course = {
            course_code: {
                'name': course_name,
                'code': course_code,
                'unit': course_unit
            }
        }

        # set course for specific department if department entered
        if department:
            courses[school][department][level][semester]['courses'].update(new_course)

            # update total_units
            if not courses[school][department][level][semester]['total_units']:
                courses[school][department][level][semester]['total_units'] = course_unit
            else:
                courses[school][department][level][semester]['total_units'] += course_unit

            # update total_courses
            if not courses[school][department][level][semester]['total_courses']:
                courses[school][department][level][semester]['total_courses'] = 1
            else:
                courses[school][department][level][semester]['total_courses'] += 1

            # check if course already exists and subtract its units and total
            if subtract_units:
                courses[school][department][level][semester]['total_units'] -= subtract_units
                courses[school][department][level][semester]['total_courses'] -= 1
                courses[school][department][level][semester]['courses'].pop(pop_course_code)

        else:
            for key, value in courses[school].items():
                value[level][semester]['courses'].update(new_course)

                # update total_units
                if not value[level][semester]['total_units']:
                    value[level][semester]['total_units'] = course_unit
                else:
                    value[level][semester]['total_units'] += course_unit

                # update total_courses
                if not value[level][semester]['total_courses']:
                    value[level][semester]['total_courses'] = 1
                else:
                    value[level][semester]['total_courses'] += 1

                # check if course already exists and subtract its units and total
                if subtract_units:
                    value[level][semester]['total_units'] -= subtract_units
                    value[level][semester]['total_courses'] -= 1
                    value[level][semester]['courses'].pop(pop_course_code)

        # save changes to file
        Utils.write_to_file(self.paths.get('courses'), courses)

        # save to admin log
        if department:
            message = f"added Course: {course_code} to "\
                f"Faculty: {school} | Department: {department} | Level: {level}"
            department_info = department
        else:
            message = f"added Course: {course_code} to "\
                f"all departments in School: {school} and Level: {level}"
            department_info = "all"

        self.admin_log(message)
            
        # print success message
        CONSOLE.print(
            f"\n[green bold]SUCCESS[/green bold]\n\n"\
            f"Added new course [yellow]{course_name.title()}[/yellow]\n"\
            f"To school: [yellow]{school.upper()}[/yellow]\n"\
            f"To department: [yellow]{department_info.upper()}[/yellow]\n"\
            f"Level: [yellow]{level}[/yellow]\n"\
            f"Semester: [yellow]{semester.title()}[/yellow]\n"
        )

        # --- update course in tests and exams json file

        # load and update file content
        content = Utils.load_from_file(self.paths.get('tests_and_exams'))
        content[school][level]['tests'][semester].update({course_code: []})
        content[school][level]['exams'][semester].update({course_code: []})

        # write updated content to file
        Utils.write_to_file(self.paths.get('tests_and_exams'), content)
        
        # --- end update of course in tests and exams file

    def remove_school(self) -> None:
        """
        remove a schoo/faculty from school
        """

        school_name = Utils.clean_string(input("Enter School/Faculty Name: ")).lower()

        # check if faculty/school exists
        check_school = Utils.check_faculty(school_name)

        if not check_school:
            CONSOLE.print("\n[red bold]ERROR[/red bold]\n"\
                          f"Entered school {school_name.upper()} doesn't exist!\n")
            return

        # delete school from all records
        school_name = check_school
        Utils.delete_faculty(school_name)

        # write to admin log
        self.admin_log(f"removed faculty: {school_name} from school")

        # print success message
        CONSOLE.print(f"\n[green bold]SUCCESS[/green bold]\nOperations Completed!\n")

    def remove_department(self) -> None:
        """
        remove department
        """

        department = Utils.clean_string(input("Enter Department Name: ")).lower()

        # check if faculty/school exists
        check_department = Utils.check_department(department, False)

        if not check_department:
            CONSOLE.print("\n[red bold]ERROR[/red bold]\n"\
                          f"Entered department {department.upper()} doesn't exist!\n")
            return

        # delete school from all records
        department = check_department
        Utils.delete_department(department)

        # write to admin log
        self.admin_log(f"removed department: {department} from school")

        # print success message
        CONSOLE.print(f"\n[green bold]SUCCESS[/green bold]\nOperations Completed!\n")

    def set_test(self) -> None:
        """
        set tests 
        """

        self.set_questions("tests")

    def set_exam(self) -> None:
        """
        set exams
        """

        self.set_questions("exams")

    def set_questions(self, set_key: str = None) -> None:
        """
        set test or exam questions
        @set_key: used in access to set test or exam
        """

        if not set_key:
            return

        # get faculty/school
        while True:
            school = Utils.clean_string(input("Enter School/Faculty: ")).lower()
            school = Utils.check_faculty(school)

            if not school:
                CONSOLE.print(f"\n[red]ERROR[/red]\nInvalid School/Faculty!\n")
                continue

            break

        # get level
        while True:
            level = Utils.clean_string(input("Enter level: "))

            if level not in self.levels:
                CONSOLE.print(f"\n[red]ERROR[/red]\nInvalid Level!\n")
                continue

            break

        # get semester to set questions for
        while True:
            semester = Utils.clean_string(input("Enter semester: ")).lower()

            if semester == 'first':
                semester = 'first_semester'
                break

            if semester == 'second':
                semester = 'second_semester'
                break

            if semester == 'first_semester' or\
               semester == 'second_semester':
                break

            CONSOLE.print(f"\n[red]ERROR[/red]\nInvalid Semester!\n")

        # get course code
        while True:
            course = Utils.clean_string(input("Enter Course Code: ")).lower()
            course = Utils.check_course(course)

            if not course:
                CONSOLE.print(f"\n[red]ERROR[/red]\nInvalid Course!\n")
                continue

            break

        # get number of questions to be set
        while True:
            number = Utils.validate_number(input("Enter number of questions: "))

            if not number:
                CONSOLE.print(f"\n[red]ERROR[/red]\nInvalid Number!\n")
                continue

            if number < 2 or number > 100:
                CONSOLE.print(f"\n[red]ERROR[/red]\nMin: 2 | Max: 100\n")
                continue

            break

        # get questions
        question_list = []

        for sn in range(1, number + 1):
            # setup panel
            panel = Panel("", title="[bold]Question[/bold]", subtitle=f"[italic]{sn} of {number}[/italic]")
            CONSOLE.print(panel)

            # get question
            options = {}
            question = Utils.clean_string(input("Question: "))

            # get options
            for letter in range(ord('a'), ord('a') + 4):
                if chr(letter) == 'a':
                    CONSOLE.print("\n[bold]Options:[/bold]\n")

                while True:
                    option = Utils.clean_string(input(f"Option {chr(letter)}: "))

                    # check if option value already exists
                    if option.lower() in [x.lower() for x in options.values()]:
                        CONSOLE.print(f"\n[red]ERROR[/red]\nDuplicate option!\n")
                        continue

                    # check for empty return
                    if not option:
                        CONSOLE.print(f"\n[red]ERROR[/red]\nType in an option!\n")
                        continue

                    break

                # update options dictionary for current question
                options.update({chr(letter): option})

            # get correct answer to question
            while True:
                correct_option = input("\nEnter correct option (a-d): ").strip().lower()

                # ensure string length is exactly 1
                if len(correct_option) != 1:
                    CONSOLE.print(f"\n[red]ERROR[/red]\nInvalid option!\n")
                    continue                    

                # check if entered option is within range
                if ord(correct_option) not in range(ord('a'), ord('a') + 4):
                    CONSOLE.print(f"\n[red]ERROR[/red]\nInvalid option!\n")
                    continue

                break

            # update the questions list
            question_list.append({
                'question': question,
                'options': options,
                'correct option': correct_option
            })

        # set question in tests and exams dictionary
        try:
            content = Utils.load_from_file(self.paths.get('tests_and_exams'))
            content[school][level][set_key][semester].update({course: question_list})

            Utils.write_to_file(self.paths.get('tests_and_exams'), content)

            # print success message
            CONSOLE.print(f"\n[green bold]SUCCESS[/green bold]\nSuccessfuly set {set_key[:-1]} questions!\n")

            # add to admin log
            self.admin_log(f"set {set_key[:-1]} questions for course: {course} and level: {level}")
        except:
            CONSOLE.print("\n[red]ERROR[/red]\nAn Error occured! \nYou cannot perform this operation!\n")
