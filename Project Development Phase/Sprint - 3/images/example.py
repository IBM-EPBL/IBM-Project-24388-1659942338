from flask import *
import ibm_db
from sendgridmail import sendmail
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

dsn_hostname = (os.getenv('DNS_HOST'))
dsn_uid = (os.getenv('DNS_UID'))
dsn_pwd = (os.getenv('DNS_PWD'))
dsn_driver = (os.getenv('DNS_DRIVER'))
dsn_database = (os.getenv('DNS_DB'))
dsn_port = (os.getenv('DNS_PORT'))
dsn_security = (os.getenv('DNS_SEC') )
dsn = ("DRIVER={0};"
"DATABASE={1};"
"HOSTNAME={2};"
"PORT={3};"
"UID={4};"
"PWD={5};"
"SECURITY={6};").format(dsn_driver,dsn_database,dsn_hostname,dsn_port,dsn_uid,dsn_pwd,dsn_security)
print(dsn)
try:
  conn = ibm_db.pconnect(dsn,"","")
  print("success")
except:
  print(ibm_db.conn_errormsg())

# conn = ibm_db.connect(os.getenv('DB_KEY'),'','')


app.app_context().push()
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SECRET_KEY'] = 'AJDJRJS24$($(#$$33--'

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/")
def login():
    return render_template("login.html")

# Login
@app.route("/loginmethod", methods = ['GET'])
def loginmethod():
    global userid
    msg = ''

    if request.method == 'GET':
        uname = request.args.get("uname")
        psw = request.args.get("psw")

        sql = "SELECT * FROM accounts WHERE uname =? AND psw=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, uname)
        ibm_db.bind_param(stmt, 2, psw)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if account:
            session['loggedin'] = True
            session['id'] = account['UNAME']
            userid = account['UNAME']
            session['username'] = account['UNAME']
            return redirect(url_for("about"))
        else:
            msg = 'Incorrect Username and Password'
            flash(msg)
            return redirect(url_for("login"))

# Signup
@app.route("/signupmethod", methods = ['POST'])
def signupmethod():
    msg = ''
    if request.method == 'POST':
        uname = request.form['uname']
        email = request.form['email']
        name = request.form['name']
        dob = request.form['dob']
        psw = request.form['psw']
        con_psw = request.form['con_psw']

        sql = "SELECT * FROM accounts WHERE uname =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, uname)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if account:
            msg = 'Account already exists !'
            flash(msg)
            return redirect(url_for("signup"))
        elif psw != con_psw:
            msg = "Password and Confirm Password do not match."
            flash(msg)
            return redirect(url_for("signup"))
        else:
            insert_sql = "INSERT INTO accounts VALUES (?, ?, ?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, dob)
            ibm_db.bind_param(prep_stmt, 4, uname)
            ibm_db.bind_param(prep_stmt, 5, psw)
            ibm_db.execute(prep_stmt)

            insert_donor = "INSERT INTO donor(Name,Username,Email,DOB,Availability) VALUES (?, ?, ?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_donor)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, uname)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, dob)
            ibm_db.bind_param(prep_stmt, 5, "Not Available")
            ibm_db.execute(prep_stmt)

            sendmail(email, 'Plasma donor App login',name, 'You are successfully Registered!')

            return redirect(url_for("login"))

    elif request.method == 'POST':
        msg = 'Please fill out the form !'
        flash(msg)
        return redirect(url_for("signup"))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/requester')
def requester():
    if session['loggedin'] == True:
        return render_template('home.html')
    else:
        msg = 'Please login!'
        return render_template('login.html', msg = msg)

@app.route('/dash')
def dash():
    if session['loggedin'] == True:
        sql = "SELECT COUNT(*), (SELECT COUNT(*) FROM DEONOR WHERE BloodType= 'O Positive'), (SELECT COUNT(*) FROM DEONOR WHERE BloodType='A Positive'), (SELECT COUNT(*) FROM DEONOR WHERE BloodType='B Positive'), (SELECT COUNT(*) FROM DEONOR WHERE BloodType='AB Positive'), (SELECT COUNT(*) FROM DEONOR WHERE BloodType='O Negative'), (SELECT COUNT(*) FROM DEONOR WHERE BloodType='A Negative'), (SELECT COUNT(*) FROM DEONOR WHERE BloodType='B Negative'), (SELECT COUNT(*) FROM DEONOR WHERE BloodType='AB Negative') FROM dEonor"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        return render_template('dashboard.html',b=account)
    else:
        msg = 'Please login!'
        return render_template('login.html', msg = msg)

@app.route('/requested',methods=['POST'])
def requested():
    bloodgrp = request.form['bloodgrp']
    address = request.form['address']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    insert_sql = "INSERT INTO requested VALUES (?, ?, ?, ?, ?, ?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, session["username"])
    ibm_db.bind_param(prep_stmt, 2, bloodgrp)
    ibm_db.bind_param(prep_stmt, 3, address)
    ibm_db.bind_param(prep_stmt, 4, name)
    ibm_db.bind_param(prep_stmt, 5, email)
    ibm_db.bind_param(prep_stmt, 6, phone)
    ibm_db.execute(prep_stmt)
    sendmail(email,'Plasma donor App plasma request', name ,'Your request for plasma is received.')

    # send_sql = "SELECT EMAIL FROM donor where BloodTypeTYPE = ?"
    # prep_stmt = ibm_db.prepare(conn, send_sql)
    # ibm_db.bind_param(prep_stmt, 1, bloodgrp)
    # ibm_db.execute(prep_stmt)
    # send = ibm_db.fetch_assoc(prep_stmt)
    # print(send)
    # for i in send:
    #     sendmail(i.strip(), 'Plasma donor App plasma request', name, 'A Donee has requested for Blood.')

    return render_template('home.html', pred="Your request is sent to the concerned people.")

@app.route('/about')
def about():
    print(session["username"], session['id'])

    display_sql = "SELECT * FROM donor WHERE username = ?"
    prep_stmt = ibm_db.prepare(conn, display_sql)
    ibm_db.bind_param(prep_stmt, 1, session['id'])
    ibm_db.execute(prep_stmt)
    account = ibm_db.fetch_assoc(prep_stmt)
    print(account)
    donors = {}
    for values in account:
        if type(account[values]) == str:
            donors[values] = account[values].strip()
        else:
            donors[values] = account[values]

    print(donors)
    return render_template("about.html", account = donors)

@app.route('/details', methods = ['POST'])
def details():
    if request.method == 'POST':
        uname = request.form['uname']
        email = request.form['email']
        name = request.form['name']
        dob = request.form['dob']
        age = request.form['age']
        phone = request.form['phone']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        bloodtype = request.form['bloodtype']
        description = request.form['description']
        avail = request.form['avail']

        sql = "SELECT * FROM donor WHERE Username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, uname)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            update_sql = "UPDATE donor set Name=?, Username=?, Email=?, DOB=?, Age=?, Phone=?, City=?, State=?, Country=?, BloodType=?,Description=?,Availability=? where Username = ?"
            prep_stmt = ibm_db.prepare(conn, update_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, uname)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, dob)
            ibm_db.bind_param(prep_stmt, 5, age)
            ibm_db.bind_param(prep_stmt, 6, phone)
            ibm_db.bind_param(prep_stmt, 7, city)
            ibm_db.bind_param(prep_stmt, 8, state)
            ibm_db.bind_param(prep_stmt, 9, country)
            ibm_db.bind_param(prep_stmt, 10, bloodtype)
            ibm_db.bind_param(prep_stmt, 11, description)
            ibm_db.bind_param(prep_stmt, 12, avail)
            ibm_db.bind_param(prep_stmt, 13, uname)
            ibm_db.execute(prep_stmt)
            print("Update Success")
            return redirect(url_for("about")) 
            # return render_template('about.html', pred="Your details updated")

        else:
            insert_sql = "INSERT INTO donor VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, uname)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, dob)
            ibm_db.bind_param(prep_stmt, 5, age)
            ibm_db.bind_param(prep_stmt, 6, phone)
            ibm_db.bind_param(prep_stmt, 7, city)
            ibm_db.bind_param(prep_stmt, 8, state)
            ibm_db.bind_param(prep_stmt, 9, country)
            ibm_db.bind_param(prep_stmt, 10, bloodtype)
            ibm_db.bind_param(prep_stmt, 11, description)
            ibm_db.bind_param(prep_stmt, 12, avail)
            ibm_db.bind_param(prep_stmt, 13, (str(False)))

            ibm_db.execute(prep_stmt)
            print("Sucess")
            return redirect(url_for("about"))

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('login.html')
    
if __name__ == '__main__':
   app.run(host='0.0.0.0',debug='TRUE')