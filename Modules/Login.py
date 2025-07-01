"""
class to handle user login
"""
class Login:
    """
    """
    def __init__(self, mainHandle):
        self.mainHandle = mainHandle
        self.mainHandleDict = mainHandle.__dict__

        self.user = self.mainHandleDict.get("user")
        

    """
    """
    def loginGuest(self):
        pass

    """
    """
    def loginAdmin(self):
        pass

    """
    """
    def loginStudent(self):
        pass
