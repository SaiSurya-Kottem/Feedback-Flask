from flask import *
import mysql.connector
from werkzeug.utils import secure_filename
import os
import csv

app=Flask(__name__)
app.secret_key="dnt tell" 

myconn = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="feedback1"
)

@app.route("/")
@app.route("/login",methods=['GET','POST'])
def login():
	if request.method=="POST":
		uname=request.form['uname']
		pwd=request.form['pwd']
		cur=myconn.cursor()
		cur.execute("""select * from adminpanel1 where 
			username=%s and password=%s""",(uname,pwd))
		data=cur.fetchall()
		if data:
			session['loggedin']=True
			flash("Login Successfully")
			return render_template("index.html")
		else:
			flash("Incorrect Username or Password")
	return render_template("login.html")

@app.route("/newevent",methods=['GET','POST'])
def newevent():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method=="POST":
		event_name=request.form['event_name']
		course=request.form.getlist('course')
		course=','.join(course)
		mycur=myconn.cursor()
		mycur.execute("""insert into event2(event_name,course)values(%s,%s)""",(event_name,course))
		myconn.commit()
		flash("Event Created Successfully")
		return redirect(url_for('newevent'))
       
	else:
	    return render_template("index.html")

@app.route("/justcreated",methods=['GET','POST'])
def justcreated():
	if not session.get('loggedin'):
		return render_template("login.html")
	cur=myconn.cursor()
	cur.execute("select * from event2 where status=1")
	data=cur.fetchall()
	return render_template("view.html",data=data)

@app.route("/delete",methods=['GET','POST'])
def delete():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['delete']
		cur=myconn.cursor()
		cur.execute("delete from event2 where sno=%s"%(id))
		myconn.commit()
		flash("Deleted Successfully")
		return redirect(url_for('justcreated'))

@app.route("/regopened",methods=['GET','POST'])
def regopened():
	if request.method == "POST":
		id=request.form['regopened']
		cur=myconn.cursor()
		cur.execute("update event2 set status=2 where sno=%s"%(id))
		myconn.commit()
		flash("Registration Opened Successfully")
		return redirect(url_for('regopened'))
	if not session.get('loggedin'):
		return render_template("login.html")
	cur=myconn.cursor()
	cur.execute("select * from event2 where status=2")
	data=cur.fetchall()
	print(data)
	return render_template("status2.html",data=data)
@app.route("/regclosed",methods=['GET','POST'])
def regclosed():
	if request.method == "POST":
		id=request.form['regclosed']
		cur=myconn.cursor()
		cur.execute("update event2 set status=3 where sno=%s"%(id))
		myconn.commit()
		flash("Registration Closed")
		return redirect(url_for('regclosed'))
	if not session.get('loggedin'):
		return render_template("login.html")
	cur=myconn.cursor()
	cur.execute("select * from event2 where status=3")
	data=cur.fetchall()
	print(data)
	return render_template("status3.html",data=data)	
@app.route("/register",methods=['GET','POST'])
def register():
	if request.method == "POST":
		rollno=request.form['rollno']
		name=request.form['name']
		email=request.form['email']
		phno=request.form['phno']
		college=request.form['college']
		branch=request.form['branch']
		section=request.form['section']
		gen=request.form['gender']
		event_name=request.form['event_name']
		course=request.form['course']
		mycur=myconn.cursor()
		mycur.execute("select * from students1 where rollno=(%s)"%(rollno))
		data=mycur.fetchall()
		
		if len(data)==0:
			mycur.execute("""insert into students1(rollno,name,
				college,branch,section,email,phno,gender,event_name,course)
				values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
				(rollno,name,college,branch,section,email,phno,gen,event_name,course))
			myconn.commit()
			flash("Registered Successfully")

		else:
			flash("Already Registered")
		return redirect(url_for('register'))

	else:
		cur=myconn.cursor()
		cur.execute("SELECT DISTINCT event_name FROM `event2` where status=2")
		data=cur.fetchall()
		return render_template("reg.html",data=data)
		
@app.route("/edit",methods=['GET','POST'])
def edit():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['edit']
		cur=myconn.cursor()
		cur.execute("select * from event2 where sno=%s"%(id))
		data=cur.fetchall()
		course=data[0][2].split(',')
		return render_template("edit.html",data=data,course=course)

@app.route("/update",methods=['GET','POST'])
def update():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['id']
		event_name=request.form['event_name']
		course=request.form.getlist('course')
		course=','.join(course)
		mycur=myconn.cursor()
		mycur.execute("""update event2 set event_name=%s,course=%s where sno=%s""",(event_name,course,id))
		
		myconn.commit()
		return redirect(url_for('view'))
@app.route("/view",methods=['GET','POST'])
def view():
	if not session.get('loggedin'):
		return render_template("login.html")
	cur=myconn.cursor()
	cur.execute("select * from event2")
	data=cur.fetchall()
	return render_template("view.html",data=data)
@app.route("/process",methods=['GET','POST'])
def process():
	course=request.form['event']
	cur=myconn.cursor()
	cur.execute("select course from event2 where event_name=%s",(course,))
	data=cur.fetchall()
	data=data[0][0]
	data=data.split(',')
	print(data)
	return jsonify({'course':data})

@app.route("/eventclosed",methods=['GET','POST'])
def eventclosed():
    if request.method == "POST":
       event_name=request.form['event_name']
       course=request.form['course']
       cur=myconn.cursor()
       cur.execute("select * from students1 where event_name=%s and course=%s",(event_name,course))
       records=cur.fetchall()
       cur.execute("SELECT DISTINCT event_name FROM `event2` where status=3")
       data=cur.fetchall()
       flash("Submitted successfully")
       return render_template("ucs.html",records=records,data=data)
    else:
        cur=myconn.cursor()
        cur.execute("SELECT DISTINCT event_name FROM `event2` where status=3")
        data=cur.fetchall()
        return render_template("ucs.html",data=data)
@app.route("/logout")
def logout():
    session['loggedin']=False
    return render_template("login.html")
@app.route("/details",methods=['GET','POST'])
def details():
    if request.method=='POST':
        ids=request.form.getlist('ids')
        cur=myconn.cursor()
        for id in ids:
            cur.execute("update students1 set status=1 where sno=%s",(id,))
            myconn.commit()
        return redirect(url_for('eventclosed')) 
@app.route("/feedback",methods=['GET','POST'])
def feedback():
	if request.method == "POST":
		rollno=request.form['rollno']
		event_name=request.form['event_name']
		course=request.form['course']
		cur=myconn.cursor()
		cur.execute("select * from students1 where rollno=%s and event_name=%s and course=%s",(rollno,event_name,course))
		records=cur.fetchall()
		if records:
			cur.execute("select * from feedback_table where rollno=%s and event=%s and course=%s",(rollno,event_name,course))
			data=cur.fetchall()
		else:
			flash("You are not eligible to give feedback")
			return redirect(url_for('feedback'))
		if len(data)==0:

			flash("Feedback submitted successfully")
			return render_template("fbform.html",rollno=rollno,event_name=event_name,course=course)
		else:
			flash("You are already given the feedback")
		return redirect(url_for('feedback'))
	else:
		cur=myconn.cursor()
		cur.execute("SELECT DISTINCT event_name FROM `students1` where status=1")
		data=cur.fetchall()
		return render_template("feedback.html",data=data)
@app.route("/feedbackpage",methods=['GET','POST'])
def feedbackpage():
	if request.method=='POST':
		rollno=request.form['rollno']
		event_name=request.form['event_name']
		course=request.form['course']
		secq=request.form['secq']
		thirdq=request.form['thirdq']
		fourthq=request.form['fourthq']
		comment=request.form['comment']
		cur=myconn.cursor()
		cur.execute("""insert into feedback_table(rollno,event,course,Q1,Q2,Q3,comment)
		values(%s,%s,%s,%s,%s,%s,%s)""",(rollno,event_name,course,secq,thirdq,fourthq,comment))
		myconn.commit()
		return redirect(url_for('feedback'))

@app.route("/viewfeedback",methods=['GET','POST'])
def viewfeedback():
	if request.method=='POST':
		course=request.form['course']
		cur=myconn.cursor()
		cur.execute("SELECT ceil((avg(Q1+Q2+Q3)*100)/15) FROM `feedback_table` where course=%s",(course,))
		percentage=cur.fetchall()
		percentage=int(percentage[0][0])
		cur.execute("SELECT DISTINCT course FROM `feedback_table` where status=1")
		data=cur.fetchall()
		return render_template("viewfeedback.html",data=data,percentage=percentage,course=course)
	else:
		cur=myconn.cursor()
		cur.execute("SELECT DISTINCT course FROM `feedback_table` where status=1")
		data=cur.fetchall()
		return render_template("viewfeedback.html",data=data)



if __name__ =="__main__":
	app.run(debug=True)	
