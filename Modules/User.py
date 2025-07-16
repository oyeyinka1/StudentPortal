from Modules.Utils import Utils

"""
base/parent class for our distinct user classes
"""
class User:
    """
    constructor function \
    instantiates common attributes for \
    inheriting classes \
    """
    def __init__(self, mainHandle):

        self.levels = ['100', '200', '300', '400', '500']

        self.paths = {
            "db": "./Modules/Storage/db.json",
            "courses": "./Modules/Storage/courses.json",
            "faculties": "./Modules/Storage/faculties.json",
            "programmes": "./Modules/Storage/programmes.json",
            "admin_logs": "./Modules/Storage/admin_logs.json",
            "tests_and_exams": "./Modules/Storage/tests_and_exams.json",
            "states_and_cities": "./Modules/Misc/states_and_cities.json"
        }

        self.mainHandle = mainHandle
        self.mainHandleDict = mainHandle.__dict__

        self.command = self.mainHandleDict.get('command')
        self.students = self.mainHandleDict.get('students', {})
        self.loginCheck = self.mainHandleDict.get('loggedIn')
        self.admissionApplications = self.mainHandleDict.get('admissionApplications')

    """
    log the current user out of the portal
    """
    def logout(self):
        Utils.logout(self.mainHandle)
