class CustomerModel:
    # instance attribute
    def __init__(self, customerID, customerName="", address1="", address2 ="", city="", state="", pincode="", contactNbr="", emailID="", aadharNbr=""):
        self.customerID = customerID
        self.customerName = customerName
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.pincode = pincode

        self.contactNbr = contactNbr
        self.emailID = emailID
        self.aadharNbr = aadharNbr

