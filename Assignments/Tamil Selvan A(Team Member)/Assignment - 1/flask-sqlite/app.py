from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'vairamuthu'

def is_logged_in(email):
   con = sql.connect("student_database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from students where email = ?", (email,))
   student = cur.fetchone()
   return student

@app.route('/login',methods = ['POST','GET'])
def login():
   if request.method == "POST":
      con = sql.connect("student_database.db")
      con.row_factory = sql.Row
      cur = con.cursor()
      cur.execute("select * from students where email = ?", (request.form['email'],))
      student = cur.fetchone()
      if student is None:
         return render_template('login.html', msg="user not found!")
      else:
         return render_template('result.html', msg="logged in successfully..",userData = student)
   else:
      return render_template('login.html')

@app.route('/signup',methods = ['POST','GET'])
def signup():
   msg=''
   if request.method == 'POST':
      try:
         name = request.form['name']
         email = request.form['email']
         password = request.form['password']
         if is_logged_in(email) is None:
            with sql.connect("student_database.db") as con:
               cur = con.cursor()
               cur.execute("INSERT INTO students (name,email,password) VALUES (?,?,?)", (name, email, password))
               con.commit()
            return render_template("login.html")
         else:
            return render_template("signup.html",msg="User already present!")
      except:
         con.rollback()
         return render_template("signup.html",msg="error in insert operation")
   else:
      return render_template('signup.html')

@app.route('/about', methods = ['GET'])
def about():
   return render_template('about.html')

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/list')
def list():
   con = sql.connect("student_database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from students")
   students = cur.fetchall();
   return render_template("list.html", students = students)

if __name__ == '__main__':
   app.run(debug = True)