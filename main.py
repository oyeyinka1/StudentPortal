# standard library imports
import random, string, hashlib

# third party imports
from rich.console import Console

# local app imports
from src.utils import Utils
from src.guest import Guest
from src.admin import Admin
from src.student import Student
from src.file_storage import Storage


# get console instance
console = Console()

class Shell:
    """
    receives user commands, formats, parses and calls
    corresponding methods/classes to handle user-given
    command
    """

    def __init__(self):
        # attributes that should rely solely on file Storage
        self.admission_applications = {}

        # load data from file storage
        self.load_storage()

        # instantiate class attributes
        self.shell = True
        self.user_input = ""
        self.prompt = f"[blue](pyShell):   [/blue]"
        self.default_prompt = f"[blue](pyShell):   [/blue]"

        # class attributes to handle login
        self.user = None
        self.logged_in = None
        self.logged_in_user = None
        
        """
        self.run_shell: run the shell of the program
        self.setshellEssentialss: instantiates essential \
                                  class attributes
        """
        self.set_shell_essentials()
        self.run_shell()

    def run_shell(self) -> None:
        """
        start up the python shell for input
        """

        try:
            while self.shell:
                self.user_input = str(console.input(self.prompt))

                # call method to handle user input
                self.parse_input()
        except KeyboardInterrupt:
            # catch keyboard interrupt before exiting shell
            console.print("\n[red]Exiting shell...[/red]")
            self.shell = False
            
    def parse_input(self) -> None:
        """
        route user command to appropriate handler function/class
        """

        # trim excess whitespace from user input
        self.command = Utils.clean_string(self.user_input)

        # return if input string is empty
        if not self.command:
            return

        user_commands = []
        users = ['guest', 'admin', 'student']
        shell_commands = self.shell_native_commands.keys()

        # get all user commands
        for i in users:
            command = self.user_permissions[i].keys()
            for j in command:
                user_commands.append(j)

        # check if command is shell native and run
        if self.command in shell_commands:
            self.shell_native_commands.get(self.command)()
            return

        # check if command is non existent at all
        if self.command not in shell_commands and \
           self.command not in user_commands:
            console.print("\n[red]ERROR[/red]\nInvalid command entered!\n")
            return

        # check if command exists but user is not logged in
        if self.command in user_commands and not self.logged_in:
            console.print("\n[red]ERROR[/red]\nYou do not have "\
                  "permissions to run this command!\n")
            return

        """
        run command if it is not shell native \
        but exists and user is logged in
        """
        if self.command in user_commands and self.logged_in:
            if self.command not in self.user_permissions[self.user].keys():
                console.print("\n[red]ERROR[/red]\nYou do not have "\
                      "permissions to run this command!\n")
                return
            else:
                self.user_handle.get(self.user)(self)
                return

    def exit(self) -> None:
        """
        exit the shell
        """
        
        self.shell = False

    def info(self) -> None:
        """
        print all available shell native commands
        """

        # print all available shell native commands
        console.print("[blue]\nShell Commands[/blue]")
        for command in sorted(list(self.shell_native_commands.keys()), key=len):
            console.print(f"[green]{command}[/green]")

        # print available user commands if logged in
        if self.__dict__.get('user'):
            console.print(f"\n[blue]{self.user.title()} Commands[/blue]")
            for command in sorted(list(self.user_permissions[self.user].keys()), key=len):
                console.print(f"[green]{command}[/green]")

        # print new line
        print()

    def login(self) -> None:
        """
        log the user in
        """

        # check if there is a logged in user
        if self.logged_in:
            console.print("[yellow]\nOops!\nAlready "\
                          "logged in\n[/yellow]")
            return

        users = ['guest', 'admin', 'student']

        console.print("\nUSER MODES")
        console.print("[yellow]GUEST[/yellow]\t"\
                      "[red]ADMIN[/red]\t"\
                      "[purple]STUDENT[/purple]\n")

        while True:
            user_mode = input("Enter user mode: ").lower().strip()

            # allow user to abort login
            if user_mode == 'cancel':
                return

            if user_mode not in users:
                console.print("\n[red]ERROR[/red]\n"\
                              "Invalid user mode!\n"\
                              "[yellow]Type `cancel` to "\
                              "abort login\n[/yellow]")
            else:
                break

        # call appropriate user class to handle login
        self.user_handle.get(user_mode)(self)

    def view_programmes(self) -> None:
        """
        view available programmes
        """

        # call view programmes method of utils
        Utils.view_programmes()

    def apply(self) -> None:
        """
        apply for admission
        """
        
        # call guest class to handle admission application
        Guest(self)

    def set_shell_essentials(self) -> None:
        """
        sets shell essential attributes
        """

        # set shell native commands to be handled by this class
        self.shell_native_commands = {
            'exit': self.exit,
            'info': self.info,
            'login': self.login,
            'apply': self.apply,
            'view programmes': self.view_programmes
        }

        # set user native commands to be handled by user classes
        self.user_handle = {
            'guest': Guest,
            'admin': Admin,
            'student': Student
        }

        # set permissions for hierarchy of users
        self.user_permissions = {
            'guest': {
                'logout': True,
                'check status': True,
                'cancel application': True,
            },
            'admin': {
                'admit applicants': True,
                'reject applicants': True,
                'logout': True,
                'view my log': True,
                'view admin log': True,
                'view applications': True,
                'view students': True,    
                'view school stats': True,
                'export students': True,
                'add admin': True,
                'view admins': True,
                'add school': True,
                'add department': True,
                'view commands': True,
                'expel student': True,
                'suspend student': True,
                'unsuspend student': True,
                'add course': True,
                'bulk expel': True,
                'bulk suspend': True,
                'bulk unsuspend': True,
                'remove school': True,
                'remove department': True,
                'set exam': True,
                'set test': True
            },
            'student': {
                'logout': True,
                'view courses': True
            }
        }

    def load_storage(self) -> None:
        """
        load data from file Storage
        """

        load = Storage.load()

        if load:    
            self.__dict__.update(load)

    def save_storage(self) -> None:
        """
        strip unwanted values in <self> and save to Storage
        """

        # save to file Storage
        Storage.save(self)

    def __del__(self) -> None:
        """
        save to file Storage upon exit of program
        """

        self.save_storage()

# initialize class 
Shell()
