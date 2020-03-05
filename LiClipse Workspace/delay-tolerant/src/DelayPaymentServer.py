from flask import Flask, request, render_template, redirect, url_for, session
import os
import pypyodbc
import zipfile
import numpy as np
import cv2
from os.path import isfile, join

from RoleModel import RoleModel
from UserModel import UserModel
from Constants import connString


app = Flask(__name__)
app.secret_key = "MySecret"
ctx = app.app_context()
ctx.push()

with ctx:
    pass

userName = ""
roleObject = None
message = ""
msgType = ""

def initialize():
    global message, msgType
    message = ""
    msgType=""

def processRole(optionID):
    
    if optionID == 10 :
        if roleObject.canRole == False :
            return False
    if optionID == 20 :
        if roleObject.canUser == False :
            return False
    if optionID == 30 :
        if roleObject.CL111 == False :
            return False
    if optionID == 40 :
        if roleObject.CL222 == False :
            return False
    if optionID == 50 :
        if roleObject.CL333 == False :
            return False
    return True

@app.route('/')
def index():
    global userID, userName
    return render_template('Login.html')  # when the home page is called Index.hrml will be triggered.

@app.route('/processLogin', methods=['POST'])
def processLogin():
    global userID, userName, roleObject
    userName= request.form['userName']
    password= request.form['password']
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM UserTable WHERE userName = '"+userName+"' AND password = '"+password+"' AND isActive = 1"; 
    
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    
    cur1.commit()
    if not row:
        return render_template('Login.html', processResult="Invalid Credentials")
    userID = row[0]
    userName = row[3]
    
    cur2 = conn1.cursor()
    sqlcmd2 = "SELECT * FROM Role WHERE RoleID = '"+str(row[6])+"'"; 
    cur2.execute(sqlcmd2)
    row2 = cur2.fetchone()
   
    if not row2:
        return render_template('Login.html', processResult="Invalid Role")
    
    roleObject = RoleModel(row2[0], row2[1],row2[2],row2[3],row2[4],row2[5])

    return render_template('Dashboard.html')

@app.route("/ChangePassword")
def changePassword():
    global userID, userName
    return render_template('ChangePassword.html')

@app.route("/ProcessChangePassword", methods=['POST'])
def processChangePassword():
    global userID, userName
    oldPassword= request.form['oldPassword']
    newPassword= request.form['newPassword']
    confirmPassword= request.form['confirmPassword']
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM UserTable WHERE userName = '"+userName+"' AND password = '"+oldPassword+"'"; 
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template('ChangePassword.html', msg="Invalid Old Password")
    
    if newPassword.strip() != confirmPassword.strip() :
       return render_template('ChangePassword.html', msg="New Password and Confirm Password are NOT same")
    
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cur2 = conn2.cursor()
    sqlcmd2 = "UPDATE UserTable SET password = '"+newPassword+"' WHERE userName = '"+userName+"'"; 
    cur1.execute(sqlcmd2)
    cur2.commit()
    return render_template('ChangePassword.html', msg="Password Changed Successfully")


@app.route("/Dashboard")
def Dashboard():
    global userID, userName
    return render_template('Dashboard.html')


@app.route("/Information")
def Information():
    global message, msgType
    return render_template('Information.html', msgType=msgType, message = message)




@app.route("/UserListing")

def UserListing():
    global userID, userName
    
    global message, msgType, roleObject
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access User"
        msgType="Error"
        return redirect(url_for('Information'))
    
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM UserTable ORDER BY userName"
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        temp = str(dbrow[6])
        sqlcmd3 = "SELECT * FROM Role WHERE RoleID = '"+temp+"'"
        cursor3.execute(sqlcmd3)
        rolerow = cursor3.fetchone()
        roleModel = RoleModel(0)
        if rolerow:
           roleModel = RoleModel(rolerow[0],rolerow[1])
        else:
           print("Role Row is Not Available")
        
        row = UserModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], dbrow[6], roleModel=roleModel)
        records.append(row)
    return render_template('UserListing.html', records=records)


@app.route("/UserOperation")
def UserOperation():
    
    global userID, userName
    
    global message, msgType, roleObject
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access User"
        msgType="Error"
        return redirect(url_for('Information'))
    
    operation = request.args.get('operation')
    unqid = ""
    
    
    
    rolesDDList = []
    
    conn4 = pypyodbc.connect(connString, autocommit=True)
    cursor4 = conn4.cursor()
    sqlcmd4 = "SELECT * FROM Role"
    cursor4.execute(sqlcmd4)
    print("sqlcmd4???????????????????????????????????????????????????????/", sqlcmd4)
    while True:
        roleDDrow = cursor4.fetchone()
        if not roleDDrow:
            break
        print("roleDDrow[1]>>>>>>>>>>>>>>>>>>>>>>>>>", roleDDrow[1])
        roleDDObj = RoleModel(roleDDrow[0], roleDDrow[1])
        rolesDDList.append(roleDDObj)
        
        
    row = UserModel(0)

    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM UserTable WHERE UserID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:
            
            conn3 = pypyodbc.connect(connString, autocommit=True)
            cursor3 = conn3.cursor()
            temp = str(dbrow[6])
            sqlcmd3 = "SELECT * FROM Role WHERE RoleID = '"+temp+"'"
            cursor3.execute(sqlcmd3)
            rolerow = cursor3.fetchone()
            roleModel = RoleModel(0)
            if rolerow:
               roleModel = RoleModel(rolerow[0],rolerow[1])
            else:
               print("Role Row is Not Available")
            row = UserModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], dbrow[6], roleModel=roleModel)
        
    return render_template('UserOperation.html', row = row, operation=operation, rolesDDList=rolesDDList )




@app.route("/ProcessUserOperation",methods = ['POST'])
def processUserOperation():
    global userName, userID
    operation = request.form['operation']
    unqid = request.form['unqid'].strip()
    userName= request.form['userName']
    emailid= request.form['emailid']
    password=request.form['password']
    contactNo= request.form['contactNo']
    isActive = 0
    if request.form.get("isActive") != None :
        isActive = 1
    roleID= request.form['roleID']
    
    
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    
    
    if operation == "Create" :
        sqlcmd = "INSERT INTO UserTable( userName,emailid, password,contactNo, isActive, roleID) VALUES('"+userName+"','"+emailid+"', '"+contactNo+"', '"+password+"' ,'"+str(isActive)+"', '"+str(roleID)+"')"
    if operation == "Edit" :
        sqlcmd = "UPDATE UserTable SET userName = '"+userName+"', emailid = '"+emailid+"', password = '"+password+"',contactNo='"+contactNo+"',  isActive = '"+str(isActive)+"', roleID = '"+str(roleID)+"' WHERE UserID = '"+unqid+"'"  
    if operation == "Delete" :

        sqlcmd = "DELETE FROM UserTable WHERE UserID = '"+unqid+"'" 

    if sqlcmd == "" :
        return redirect(url_for('Information')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    return redirect(url_for("UserListing"))







'''
    Role Operation Start
'''

@app.route("/RoleListing")
def RoleListing():
    
    global message, msgType
    print("roleObject>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", roleObject)
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(20)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))
    
    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM Role WHERE roleName LIKE '"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6])
        
        records.append(row)
    
    return render_template('RoleListing.html', records=records, searchData=searchData)

@app.route("/RoleOperation")
def RoleOperation():
    
    global message, msgType
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('/'))
    canRole = processRole(120)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))
    
    operation = request.args.get('operation')
    unqid = ""
    row = RoleModel(0, "",0,0,0,0)
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        
        
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Role WHERE RoleID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6])
        
    return render_template('RoleOperation.html', row = row, operation=operation )


@app.route("/ProcessRoleOperation", methods=['POST'])
def ProcessRoleOperation():
    global message, msgType
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('/'))
    canRole = processRole(120)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))
    
    
    print("ProcessRole")
    
    operation = request.form['operation']
    if operation != "Delete" :
        roleName = request.form['roleName']
        canRole = 0
        canUser = 0
        CL111 = 0
        CL222 = 0
        CL333 = 0
        
        
        
        if request.form.get("canRole") != None :
            canRole = 1
        if request.form.get("canUser") != None :
            canUser = 1
        if request.form.get("CL111") != None :
            CL111 = 1
        if request.form.get("CL222") != None :
            CL222 = 1
        if request.form.get("CL333") != None :
            CL333 = 1
        
        
    
    print(1)
    unqid = request.form['unqid'].strip()
    print(operation)
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()
    
    
    sqlcmd = ""
    if operation == "Create" :
        sqlcmd = "INSERT INTO Role (roleName, canRole, canUser, CL111, CL222, CL333) VALUES ('"+roleName+"', '"+str(canRole)+"', '"+str(canUser)+"', '"+str(CL111)+"', '"+str(CL222)+"', '"+str(CL333)+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Role SET roleName = '"+roleName+"', canRole = '"+str(canRole)+"', canUser = '"+str(canUser)+"', CL111 = '"+str(CL111)+"', CL222 = '"+str(CL222)+"', CL333 = '"+str(CL333)+"' WHERE RoleID = '"+unqid+"'" 
    if operation == "Delete" :
        conn4 = pypyodbc.connect(connString, autocommit=True)
        cur4 = conn4.cursor()
        sqlcmd4 = "SELECT roleID FROM UserTable WHERE roleID = '"+unqid+"'" 
        cur4.execute(sqlcmd4)
        dbrow4 = cur4.fetchone()
        if dbrow4:
            message = "You can't Delete this Role Since it Available in Users Table"
            msgType="Error"
            return redirect(url_for('Information')) 
        
        sqlcmd = "DELETE FROM Role WHERE RoleID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Information')) 
    cur3.execute(sqlcmd)
    cur3.commit()
    
    return redirect(url_for('RoleListing')) 
    
'''
    Role Operation End
'''


@app.route("/CustomerListing")
def CustomerListing():
    global msgText, msgType
    print("CustomerListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(
        connString,
        autocommit=True)
    print(connString)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT customerID, customerName, address1, address2, city, state, pincode, contactnbr, emailID, aadharNbr FROM Customer WHERE customerName like '" + searchData + "%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = CustomerModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3])
        records.append(row)
    return render_template('CustomerListing.html', records=records, searchData=searchData)

from CustomerModel import CustomerModel
@app.route("/CustomerOperation")
def CustomerOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = CustomerModel(0, "", "", "")
    row = None
    if operation != "Create":
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(
            connString,
            autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Customers WHERE customerID = '" + unqid + "'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = CustomerModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], dbrow[6], dbrow[7], dbrow[8])

    return render_template('CustomerOperation.html', row=row, operation=operation)


'''
This route will be called when the processUploadImage will be clicked (ie the inner page) is called from the browser.
This means that when the processUploadImage url is triggered (means clicking the submit button) processUploadData method is called.

'''


@app.route("/ProcessCustomerOperation", methods=['POST'])
def ProcessCustomerOperation():
    global msgText, msgType
    operation = request.form['operation']
    if operation != "Delete":
        customerName = request.form['customerName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        contactNbr = request.form['contactNbr']
        emailID = request.form['emailID']
        aadharNbr = request.form['aadharNbr']

    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect(
        connString,
        autocommit=True)
    cur1 = conn1.cursor()

    if operation == "Create":
        sqlcmd = "INSERT INTO Customer (customerName, address1, address2,  city, state, pincode, contactNbr,  emailID, aadharNbr) " \
                 "VALUES('" + customerName + "', '" + address1 + "', '" + address2 + "','" + city + "','" + state + "','" + pincode + "'," \
                "'" + contactNbr + "', '" + emailID + "', '" + aadharNbr + "')"
    if operation == "Edit":
        print("edit inside")
        sqlcmd = "UPDATE Customer SET customerName = '" + customerName + "', address1 = '" + address1 + "', address2 = '" + address2 + "', contactNbr = '" + contactNbr + "', city = '" + city + "', state = '" + state + "', pincode = '" + pincode + "', emailID = '" + emailID + "', aadharNbr = '" + aadharNbr + "' " \
                "WHERE customerID = '" + unqid + "'"
    if operation == "Delete":
        sqlcmd = "DELETE FROM Customer WHERE customerID = '" + unqid + "'"
    print(operation, sqlcmd)
    if sqlcmd == "":
        return redirect(url_for('Error'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    # return render_template('CustomerListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("CustomerListing"))



@app.route("/EmployeeListing")
def EmployeeListing():
    global msgText, msgType
    print("EmployeeListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(
        connString,
        autocommit=True)
    print(connString)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT EmployeeID, EmployeeName, address1, address2, city, state, pincode, contactnbr, emailID, aadharNbr FROM Employee WHERE EmployeeName like '" + searchData + "%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = EmployeeModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3])
        records.append(row)
    return render_template('EmployeeListing.html', records=records, searchData=searchData)

from EmployeeModel import EmployeeModel
@app.route("/EmployeeOperation")
def EmployeeOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = EmployeeModel(0, "", "", "")
    row = None
    if operation != "Create":
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(
            connString,
            autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Employees WHERE EmployeeID = '" + unqid + "'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = EmployeeModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], dbrow[6], dbrow[7], dbrow[8])

    return render_template('EmployeeOperation.html', row=row, operation=operation)


'''
This route will be called when the processUploadImage will be clicked (ie the inner page) is called from the browser.
This means that when the processUploadImage url is triggered (means clicking the submit button) processUploadData method is called.

'''


@app.route("/ProcessEmployeeOperation", methods=['POST'])
def ProcessEmployeeOperation():
    global msgText, msgType
    operation = request.form['operation']

    if operation != "Delete":
        employeeName = request.form['employeeName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        contactNbr = request.form['contactNbr']
        emailID = request.form['emailID']
        aadharNbr = request.form['aadharNbr']

    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect(
        connString,
        autocommit=True)
    cur1 = conn1.cursor()

    if operation == "Create":
        sqlcmd = "INSERT INTO Employee (EmployeeName, address1, address2,  city, state, pincode, contactNbr,  emailID, aadharNbr) " \
                 "VALUES('" + employeeName + "', '" + address1 + "', '" + address2 + "','" + city + "','" + state + "','" + pincode + "'," \
                "'" + contactNbr + "', '" + emailID + "', '" + aadharNbr + "')"
    if operation == "Edit":
        print("edit inside")
        sqlcmd = "UPDATE Employee SET EmployeeName = '" + employeeName + "', address1 = '" + address1 + "', address2 = '" + address2 + "', contactNbr = '" + contactNbr + "', city = '" + city + "', state = '" + state + "', pincode = '" + pincode + "', emailID = '" + emailID + "', aadharNbr = '" + aadharNbr + "' " \
                "WHERE EmployeeID = '" + unqid + "'"
    if operation == "Delete":
        sqlcmd = "DELETE FROM Employee WHERE EmployeeID = '" + unqid + "'"
    print(operation, sqlcmd)
    if sqlcmd == "":
        return redirect(url_for('Error'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    # return render_template('EmployeeListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("EmployeeListing"))


@app.route("/LoanProductListing")
def LoanProductListing():
    global msgText, msgType
    print("LoanProductListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(
        connString,
        autocommit=True)
    print(connString)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT LoanProductID, LoanProductName FROM LoanProduct WHERE LoanProductName like '" + searchData + "%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = LoanProductModel(dbrow[0], dbrow[1])
        records.append(row)
    return render_template('LoanProductListing.html', records=records, searchData=searchData)


from LoanProductModel import LoanProductModel


@app.route("/LoanProductOperation")
def LoanProductOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = LoanProductModel(0, "")
    row = None
    if operation != "Create":
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(
            connString,
            autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM LoanProduct WHERE LoanProductID = '" + unqid + "'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = LoanProductModel(dbrow[0], dbrow[1])

    return render_template('LoanProductOperation.html', row=row, operation=operation)


@app.route("/ProcessLoanProductOperation", methods=['POST'])
def ProcessLoanProductOperation():
    global msgText, msgType
    operation = request.form['operation']
    if operation != "Delete":
        loanProductName = request.form['loanProductName']

    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect(
        connString,
        autocommit=True)
    cur1 = conn1.cursor()

    if operation == "Create":
        sqlcmd = "INSERT INTO LoanProduct (LoanProductName) " \
                 "VALUES('" + loanProductName + "')"
    if operation == "Edit":
        print("edit inside")
        sqlcmd = "UPDATE LoanProduct SET LoanProductName = '" + loanProductName + "' WHERE LoanProductID = '" + unqid + "'"
    if operation == "Delete":
        sqlcmd = "DELETE FROM LoanProduct WHERE LoanProductID = '" + unqid + "'"
    print(operation, sqlcmd)
    if sqlcmd == "":
        return redirect(url_for('Error'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    # return render_template('LoanProductListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("LoanProductListing"))


@app.route("/DepositProductListing")
def DepositProductListing():
    global msgText, msgType
    print("DepositProductListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(
        connString,
        autocommit=True)
    print(connString)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT DepositProductID, DepositProductName FROM DepositProduct WHERE DepositProductName like '" + searchData + "%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = DepositProductModel(dbrow[0], dbrow[1])
        records.append(row)
    return render_template('DepositProductListing.html', records=records, searchData=searchData)


from DepositProductModel import DepositProductModel


@app.route("/DepositProductOperation")
def DepositProductOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = DepositProductModel(0, "")
    row = None
    if operation != "Create":
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(
            connString,
            autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM DepositProduct WHERE DepositProductID = '" + unqid + "'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = DepositProductModel(dbrow[0], dbrow[1])

    return render_template('DepositProductOperation.html', row=row, operation=operation)


@app.route("/ProcessDepositProductOperation", methods=['POST'])
def ProcessDepositProductOperation():
    global msgText, msgType
    operation = request.form['operation']
    if operation != "Delete":
        depositProductName = request.form['depositProductName']

    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect(
        connString,
        autocommit=True)
    cur1 = conn1.cursor()

    if operation == "Create":
        sqlcmd = "INSERT INTO DepositProduct (DepositProductName) " \
                 "VALUES('" + depositProductName + "')"
    if operation == "Edit":
        print("edit inside")
        sqlcmd = "UPDATE DepositProduct SET DepositProductName = '" + depositProductName + "' WHERE DepositProductID = '" + unqid + "'"
    if operation == "Delete":
        sqlcmd = "DELETE FROM DepositProduct WHERE DepositProductID = '" + unqid + "'"
    print(operation, sqlcmd)
    if sqlcmd == "":
        return redirect(url_for('Error'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    # return render_template('DepositProductListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("DepositProductListing"))


from AccountModel import AccountModel
@app.route("/AccountListing")
def AccountListing():
    global userID, userName



    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM AccountTable ORDER BY accountID"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break

        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        temp = str(dbrow[2])
        sqlcmd3 = "SELECT * FROM Customer WHERE CustomerID = '" + temp + "'"
        cursor3.execute(sqlcmd3)
        custrow = cursor3.fetchone()
        custModel = CustomerModel(0)
        if custrow:
            custModel = CustomerModel(custrow[0], custrow[1])
        else:
            print("Customer Row is Not Available")

        row = AccountModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], customerModel=custModel)
        records.append(row)
    return render_template('AccountListing.html', records=records)


@app.route("/AccountOperation")
def AccountOperation():
    global userID, userName



    operation = request.args.get('operation')
    unqid = ""

    selectionList = []

    conn4 = pypyodbc.connect(connString, autocommit=True)
    cursor4 = conn4.cursor()
    sqlcmd4 = "SELECT * FROM Customer order by CustomerName"
    cursor4.execute(sqlcmd4)
    print("sqlcmd4???????????????????????????????????????????????????????/", sqlcmd4)
    while True:
        custrow = cursor4.fetchone()
        if not custrow:
            break
        print("custrow[1]>>>>>>>>>>>>>>>>>>>>>>>>>", custrow[1])
        custObj = CustomerModel(custrow[0], custrow[1])
        selectionList.append(custObj)

    row = AccountModel(0)

    if operation != "Create":
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM AccountTable WHERE uniqueID = '" + unqid + "'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:

            conn3 = pypyodbc.connect(connString, autocommit=True)
            cursor3 = conn3.cursor()
            temp = str(dbrow[2])
            sqlcmd3 = "SELECT * FROM Customer WHERE customerID = '" + temp + "'"
            cursor3.execute(sqlcmd3)
            custrow = cursor3.fetchone()
            custModel = CustomerModel(0)
            if custrow:
                custModel = CustomerModel(custrow[0], custrow[1])
            else:
                print("Customer Row is Not Available")
            print(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4])
            row = AccountModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], customerModel=custModel)

    return render_template('AccountOperation.html', row=row, operation=operation, selectionList=selectionList)


@app.route("/ProcessAccountOperation", methods=['POST'])
def processAccountOperation():
    global userName, userID
    operation = request.form['operation']
    unqid = request.form['unqid'].strip()
    if operation == "Create":
        accountID = request.form['accountID']
        customerID = request.form['customerID']
        accountType = request.form['accountType']
    isActive = 0
    if request.form.get("isActive") != None:
        isActive = 1


    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()

    if operation == "Create":
        sqlcmd = "INSERT INTO AccountTable( accountID,customerID,  accountType, isActive) VALUES('" + accountID + "','" + customerID + "', '" + accountType + "', '" + str(isActive) + "')"
    if operation == "Edit":
        sqlcmd = "UPDATE AccountTable SET  isActive = '" + str(isActive) + "' WHERE uniqueID = '" + unqid + "'"
    if operation == "Delete":
        sqlcmd = "DELETE FROM AccountTable WHERE uniqueID = '" + unqid + "'"

    if sqlcmd == "":
        return redirect(url_for('Information'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    return redirect(url_for("AccountListing"))



from TransactionModel import TransactionModel
@app.route("/TransactionListing")
def TransactionListing():
    global userID, userName



    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM TransactionTable ORDER BY effDate DESC"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break

        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        temp = str(dbrow[2])
        sqlcmd3 = "SELECT * FROM AccountTable WHERE uniqueID = '" + temp + "'"
        cursor3.execute(sqlcmd3)
        accrow = cursor3.fetchone()
        fromAccountModel = AccountModel(0)
        if accrow:
            fromAccountModel = AccountModel(accrow[0], accrow[1])
        else:
            print("Account Row is Not Available")

        temp = str(dbrow[3])
        sqlcmd3 = "SELECT * FROM AccountTable WHERE uniqueID = '" + temp + "'"
        cursor3.execute(sqlcmd3)
        accrow = cursor3.fetchone()
        toAccountModel = AccountModel(0)
        if accrow:
            toAccountModel = AccountModel(accrow[0], accrow[1])
        else:
            print("Account Row is Not Available")




        row = TransactionModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], fromAccountModel=fromAccountModel, toAccountModel=toAccountModel)
        records.append(row)
    return render_template('TransactionListing.html', records=records)


@app.route("/TransactionOperation")
def TransactionOperation():
    global userID, userName



    operation = request.args.get('operation')
    unqid = ""

    selectionList = []
    selectionList1 = []

    conn4 = pypyodbc.connect(connString, autocommit=True)
    cursor4 = conn4.cursor()
    sqlcmd4 = "SELECT * FROM AccountTable order by accountID"
    cursor4.execute(sqlcmd4)
    print("sqlcmd4???????????????????????????????????????????????????????/", sqlcmd4)
    while True:
        trrow = cursor4.fetchone()
        if not trrow:
            break
        print("trrow[1]>>>>>>>>>>>>>>>>>>>>>>>>>", trrow[1])
        trObj = AccountModel(trrow[0], trrow[1])
        print(trrow[0], trrow[1])
        selectionList.append(trObj)
        selectionList1.append(trObj)

    row = TransactionModel(0)



    return render_template('TransactionOperation.html', row=row, operation=operation, selectionList=selectionList, selectionList1=selectionList1)

from datetime import datetime
@app.route("/ProcessTransactionOperation", methods=['POST'])
def processTransactionOperation():
    global userName, userID
    operation = request.form['operation']
    unqid = request.form['unqid'].strip()
    if operation == "Create":

        fromAccountID = request.form['fromAccountID']
        toAccountID = request.form['toAccountID']
        amount = request.form['amount']

    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    print("INSERT INTO TransactionTable( effDate,fromAccountID,  toAccountID, amount) VALUES('" + dt_string + "','" + fromAccountID + "', '" + toAccountID + "', '" + str(
            amount) + "')")
    if operation == "Create":
        sqlcmd = "INSERT INTO TransactionTable( effDate,fromAccountID,  toAccountID, amount) VALUES('" + dt_string + "','" + fromAccountID + "', '" + toAccountID + "', '" + str(
            amount) + "')"

    if sqlcmd == "":
        return redirect(url_for('Information'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    return redirect(url_for("TransactionListing"))

#BLOCKCHAIN Implementation
import os
import hashlib    #
import json

@app.route("/BlockChainGeneration")
def BlockChainGeneration():
    
    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM TransactionTable WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    sqlcmd = "SELECT COUNT(*) FROM TransactionTable WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksNotCreated = dbrow[0]
    return render_template('BlockChainGeneration.html', blocksCreated=blocksCreated, blocksNotCreated=blocksNotCreated)


@app.route("/ProcessBlockchainGeneration", methods=['POST'])
def ProcessBlockchainGeneration():
    
    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM TransactionTable WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    blocksCreated = 0
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    prevHash = ""
    print("blocksCreated", blocksCreated)
    if blocksCreated != 0:
        connx = pypyodbc.connect(connString, autocommit=True)
        cursorx = connx.cursor()
        sqlcmdx = "SELECT * FROM TransactionTable WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY uniqueID"
        cursorx.execute(sqlcmdx)
        dbrowx = cursorx.fetchone()
        print(2)
        if dbrowx:
            uniqueID = dbrowx[0]
            conny = pypyodbc.connect(connString, autocommit=True)
            cursory = conny.cursor()
            sqlcmdy = "SELECT hash FROM TransactionTable WHERE uniqueID < '" + str(uniqueID) + "' ORDER BY uniqueID DESC"
            cursory.execute(sqlcmdy)
            dbrowy = cursory.fetchone()
            if dbrowy:
                print(3)
                prevHash = dbrowy[0]
            cursory.close()
            conny.close()
        cursorx.close()
        connx.close()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT * FROM TransactionTable WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY uniqueID"
    cursor.execute(sqlcmd)

    while True:
        sqlcmd1 = ""
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        unqid = str(dbrow[0])
        '''
        bdata = str(dbrow[1])+str(dbrow[2])+str(dbrow[3])+str(dbrow[4])+str(dbrow[5])+str(dbrow[6])+str(dbrow[7])+str(dbrow[8])+str(dbrow[9])\
                +str(dbrow[10])+str(dbrow[11])+str(dbrow[12])+str(dbrow[13])+str(dbrow[14])+str(dbrow[15])+str(dbrow[18])+str(dbrow[19])+str(dbrow[20])
        '''
        bdata = str(dbrow[1]) + str(dbrow[2]) + str(dbrow[3]) + str(dbrow[4])
        block_serialized = json.dumps(bdata, sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_serialized).hexdigest()

        conn1 = pypyodbc.connect(connString, autocommit=True)
        cursor1 = conn1.cursor()
        sqlcmd1 = "UPDATE TransactionTable SET isBlockChainGenerated = 1, hash = '" + block_hash + "', prevHash = '" + prevHash + "' WHERE uniqueID = '" + unqid + "'"
        cursor1.execute(sqlcmd1)
        cursor1.close()
        conn1.close()
        prevHash = block_hash
    return render_template('BlockchainGenerationResult.html')


@app.route("/BlockChainReport")
def BlockChainReport():

    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()

    sqlcmd1 = "SELECT * FROM TransactionTable WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd1)
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM TransactionTable ORDER BY effDate DESC"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break

        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        temp = str(dbrow[2])
        sqlcmd3 = "SELECT * FROM AccountTable WHERE uniqueID = '" + temp + "'"
        cursor3.execute(sqlcmd3)
        accrow = cursor3.fetchone()
        fromAccountModel = AccountModel(0)
        if accrow:
            fromAccountModel = AccountModel(accrow[0], accrow[1])
        else:
            print("Account Row is Not Available")

        temp = str(dbrow[3])
        sqlcmd3 = "SELECT * FROM AccountTable WHERE uniqueID = '" + temp + "'"
        cursor3.execute(sqlcmd3)
        accrow = cursor3.fetchone()
        toAccountModel = AccountModel(0)
        if accrow:
            toAccountModel = AccountModel(accrow[0], accrow[1])
        else:
            print("Account Row is Not Available")

        row = TransactionModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4],  dbrow[5], dbrow[6], dbrow[7], fromAccountModel=fromAccountModel,
                               toAccountModel=toAccountModel)
        records.append(row)

    return render_template('BlockChainReport.html', records=records)

if __name__ == "__main__":
    app.run()

