class AccountModel:
    def __init__(self, uniqueID=0, accountID="", customerID=0, accountType="",isActive=0, customerModel=None):
        self.uniqueID = uniqueID
        self.accountID = accountID
        self.customerID = customerID
        self.accountType = accountType
        self.isActive = isActive
        self.customerModel = customerModel
       
