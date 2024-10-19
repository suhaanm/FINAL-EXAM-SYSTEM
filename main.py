from flask import Flask, render_template, request, url_for
from replit import db
from flask import redirect, make_response, session
from requests import get
from flask_mail import * 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import sqlite3
import os
import random as rand
from datetime import datetime, timedelta
import re
import statistics
from flask import jsonify
from markupsafe import Markup
from flask_socketio import SocketIO, send, emit
#from flask_socketio import SocketIO


app = Flask(__name__)


app.config['SECRET_KEY'] = "snsjdknkzmxniensskdnjkfnieujnsdsjkfdsnjksndkjnfxkncndfyjekrnmsddsfbhjefkdsnfxmcndakd"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 7)


socketio = SocketIO(app, cors_allowed_origins='*')
#socketio = SocketIO(app)

@app.route('/hbd/<name>')
def hbdrickroll(name):
  return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

@app.route('/stock-market/<nombre>')
def stockmarket(nombre):
  if "su" in nombre.lower():
    dell = "9.347834785469"
  else:
    dell = "0.232342347284"
  return f"Stock market says sara likes {nombre} a rating of {dell}/10. (HIGHER MEANS BETTER)"

@app.route('/bestie-sign/<name>',methods=["GET","POST"])
def bestierickroll(name):
  if request.method == "GET":
    return "<form method=\"post\" action=\"/bestie-sign/abc\">Are you my bestie?<input type=\"text\" placeholder=\"yes/no\"></input><button type=\"submit\">Submit</button></form>"
  if request.method == "POST":
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

def sort_list(X, Y):
  return [x for _, x in sorted(zip(Y, X), key=lambda pair: pair[0])]

def checkKeyDuplicate(k):
  exams = []
  for i in db.keys():
    tests = db[i][2]
    for j in tests:
      exams.append(j)
  if k in exams:
    return True
  else:
    return False

def createKey():
  k = ""
  r = ["A", "B", "C", "D", "E", "F", "G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9","0"]
  for i in range(0,10):
    j = rand.randint(0,len(r)-1)
    k += r[j]
  if checkKeyDuplicate(k):
    createKey()
  else:
    return k



@app.route('/teacher/register', methods = ['GET', 'POST'])
def signup():
  if request.method == 'POST':
    req = request.form
    username = req.get('username')
    password = req.get('password')
    email = req.get("email")
    if username not in db.keys():
      db[username] = [password, email,[]]
      session["user"] = username
      return redirect('/teacher/dashboard')
    else:
      return render_template('teacherregister.html', msg="The username is already taken")
  elif request.method == 'GET':
    return render_template('teacherregister.html')



@app.route('/teacher/login', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    req = request.form
    username = req.get('username')
    password = req.get('password')
    if username in db.keys():
      if password == db[username][0]:
        session["user"] = username
        return redirect('/teacher/dashboard')
      else:
        return render_template('teacherlogin.html', msg="The password is incorrect")
    else:
      return render_template('teacherlogin.html', msg="The username doesn't exist")
  elif request.method == 'GET':
    return render_template('teacherlogin.html')


@app.route('/teacher')
def teacher():
  try:
    username = session["user"]
    return redirect('/teacher/dashboard')
  except Exception as e:
    return render_template('teacher.html')




@app.route('/teacher/dashboard', methods = ['GET', 'POST'])
def dashboard():
  username = session["user"]
  nameList = []
  numList = []
  accessList = []
  showresponselist = []
  connection = sqlite3.connect('db/examsetup.db')
  cursor = connection.cursor()
  for k in db[username][2]:
    cursor.execute(f"SELECT examname,num,access FROM {k}")
    result = cursor.fetchall()
    for j in result:
        examname = j[0]
        numquestions = j[1]
        nameList.append(examname)
        numList.append(numquestions)
        accessdes = j[2]
        accessList.append(accessdes)
  connection.commit()
  connection.close()

  for exam_key in db[username][2]:
    try:
        tn = 0
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name FROM {exam_key}")
        result = cursor.fetchall()
        for q in result:
          tn += 1
        connection.commit()
        connection.close()
        if tn >= 1:
          showresponse = True
          showresponselist.append(showresponse)
        else:
          showresponse = False
          showresponselist.append(showresponse)
    except Exception as e:
        showresponse = False
        showresponselist.append(showresponse)
  """nameList.reverse()
  numList.reverse()
  accessList.reverse()
  showresponselist.reverse()
  createdTests = db[username][2]
  createdTests.reverse()"""
  createdTests = db[username][2]
  if request.method == "GET":
    return render_template("teacherdashboard.html", username=username, email=db[username][1], createdTests=createdTests, nameList=nameList,numList=numList,showresponselist=showresponselist,accessList=accessList)

@app.route('/student/exam', methods = ['GET', 'POST'])
def studentexam():
  if request.method == "GET":
    return render_template('studentexam.html')
  if request.method == "POST":
    req = request.form
    examkey = req.get("examkey")
    name = req.get("name")
    email = req.get("email")
    

    
    openexams = []
    for i in db.keys():
      tests = db[i][2]
      for j in tests:
        openexams.append(j)

    if examkey in openexams:
      
      if examkey in session:
        return render_template('studentexam.html', ek=examkey, nm=name,msg="You've already submitted the test!",em=email)
      qList = []
      aList = []
      pList = []
      examname = ""
      numquestions = 0
      mintime = 0
      message = ""
      teacher = ""
      access = ""

      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT question,answer,points FROM {examkey}")
      result = cursor.fetchall()
      for i in result:
        qList.append(i[0].replace("<[0]>","\""))
        aList.append(i[1].replace("<[0]>","\""))
        pList.append(i[2])
      connection.commit()
      connection.close()

      connection = sqlite3.connect('db/examsetup.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT examname,num,time,message,teacher,access FROM {examkey}")
      result2 = cursor.fetchall()
      for j in result2:
        examname = j[0]
        numquestions = j[1]
        mintime = j[2]
        message = j[3].replace("<[=0-0=]>","\"")
        teacher = j[4]
        access = j[5]
      connection.commit()
      connection.close()


      nameList = []
      emailList = []
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,email FROM {examkey}")
        result2 = cursor.fetchall()
        for itm in result2:
          nameList.append(itm[0])
          emailList.append(itm[1])
      except Exception as e:
        nameList.append("")


      if name in nameList:
        return render_template('studentexam.html', ek=examkey, nm=name,msg="The name has been used before",em=email)

      if email in emailList:
        return render_template('studentexam.html', ek=examkey, nm=name,msg="The email has been used before",em=email)

      timelimit = datetime.now() + timedelta(minutes=mintime)
      duetime = timelimit.strftime("%Y-%m-%dT%H:%M:%SZ")

      rn = datetime.now()
      starttime = rn.strftime("%Y-%m-%d %H:%M:%S")

      if mintime == 0:
        des = False
      else:
        des = True

      if access != "True":
        return render_template('studentexam.html', ek=examkey, nm=name,msg="The exam hasn't been opened at the moment",em=email)

      if "E"+examkey in session:
        checks = session["E"+examkey]
        #checksstr = datetime.strptime(checks,"%Y-%m-%d %H:%M:%S")
        duetime = checks

      session["E"+examkey] = duetime
      return render_template('exam.html', examkey = examkey, name=name, examname=examname, numquestions=numquestions,duetime=duetime,starttime=starttime,message=message,teacher=teacher,qList=qList,pList=pList,des=des, email=email)
    else:
      return render_template('studentexam.html', ek=examkey, nm=name,msg="The exam key does not exist")



@app.route('/student/exam/custom/<css_file>/<exam_key>', methods = ['GET', 'POST'])
def studentexamcustomwithkey(css_file, exam_key):
  css_file = css_file.replace("-=-","/")
  if request.method == "GET":
    return render_template('custom/studentexam.html',css=css_file,des="false",examkey=exam_key,ek=exam_key)
  if request.method == "POST":
    req = request.form
    examkey = req.get("examkey")
    name = req.get("name")
    email = req.get("email")
    

    
    openexams = []
    for i in db.keys():
      tests = db[i][2]
      for j in tests:
        openexams.append(j)

    if examkey in openexams:
      
      if examkey in session:
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="You've already submitted the test!",em=email,css=css_file, des="false",examkey=exam_key)
      qList = []
      aList = []
      pList = []
      examname = ""
      numquestions = 0
      mintime = 0
      message = ""
      teacher = ""
      access = ""

      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT question,answer,points FROM {examkey}")
      result = cursor.fetchall()
      for i in result:
        qList.append(i[0].replace("<[0]>","\""))
        aList.append(i[1].replace("<[0]>","\""))
        pList.append(i[2])
      connection.commit()
      connection.close()

      connection = sqlite3.connect('db/examsetup.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT examname,num,time,message,teacher,access FROM {examkey}")
      result2 = cursor.fetchall()
      for j in result2:
        examname = j[0]
        numquestions = j[1]
        mintime = j[2]
        message = j[3]
        teacher = j[4]
        access = j[5]
      connection.commit()
      connection.close()


      nameList = []
      emailList = []
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,email FROM {examkey}")
        result2 = cursor.fetchall()
        for itm in result2:
          nameList.append(itm[0])
          emailList.append(itm[1])
      except Exception as e:
        nameList.append("")


      if name in nameList:
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The name has been used before",em=email,css=css_file, des="false",examkey=exam_key)

      if email in emailList:
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The email has been used before",em=email,css=css_file, des="false",examkey=exam_key)

      timelimit = datetime.now() + timedelta(minutes=mintime)
      duetime = timelimit.strftime("%Y-%m-%dT%H:%M:%SZ")

      rn = datetime.now()
      starttime = rn.strftime("%Y-%m-%d %H:%M:%S")

      if mintime == 0:
        des = False
      else:
        des = True

      if access != "True":
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The exam hasn't been opened at the moment",em=email,css=css_file, des="false",examkey=exam_key)

      if "E"+examkey in session:
        checks = session["E"+examkey]
        #checksstr = datetime.strptime(checks,"%Y-%m-%d %H:%M:%S")
        duetime = checks

      session["E"+examkey] = duetime
      return render_template('custom/exam.html', examkey = examkey, name=name, examname=examname, numquestions=numquestions,duetime=duetime,starttime=starttime,message=message,teacher=teacher,qList=qList,pList=pList,des=des, email=email,css=css_file)
    else:
      return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The exam key does not exist",css=css_file, des="false",examkey=exam_key)




@app.route('/student/exam/custom/<css_file>', methods = ['GET', 'POST'])
def studentexamcustom(css_file):
  css_file = css_file.replace("-=-","/")
  if request.method == "GET":
    return render_template('custom/studentexam.html',css=css_file)
  if request.method == "POST":
    req = request.form
    examkey = req.get("examkey")
    name = req.get("name")
    email = req.get("email")
    

    
    openexams = []
    for i in db.keys():
      tests = db[i][2]
      for j in tests:
        openexams.append(j)

    if examkey in openexams:
      
      if examkey in session:
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="You've already submitted the test!",em=email,css=css_file)
      qList = []
      aList = []
      pList = []
      examname = ""
      numquestions = 0
      mintime = 0
      message = ""
      teacher = ""
      access = ""

      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT question,answer,points FROM {examkey}")
      result = cursor.fetchall()
      for i in result:
        qList.append(i[0].replace("<[0]>","\""))
        aList.append(i[1].replace("<[0]>","\""))
        pList.append(i[2])
      connection.commit()
      connection.close()

      connection = sqlite3.connect('db/examsetup.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT examname,num,time,message,teacher,access FROM {examkey}")
      result2 = cursor.fetchall()
      for j in result2:
        examname = j[0]
        numquestions = j[1]
        mintime = j[2]
        message = j[3]
        teacher = j[4]
        access = j[5]
      connection.commit()
      connection.close()


      nameList = []
      emailList = []
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,email FROM {examkey}")
        result2 = cursor.fetchall()
        for itm in result2:
          nameList.append(itm[0])
          emailList.append(itm[1])
      except Exception as e:
        nameList.append("")


      if name in nameList:
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The name has been used before",em=email,css=css_file)

      if email in emailList:
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The email has been used before",em=email,css=css_file)

      timelimit = datetime.now() + timedelta(minutes=mintime)
      duetime = timelimit.strftime("%Y-%m-%dT%H:%M:%SZ")

      rn = datetime.now()
      starttime = rn.strftime("%Y-%m-%d %H:%M:%S")

      if mintime == 0:
        des = False
      else:
        des = True

      if access != "True":
        return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The exam hasn't been opened at the moment",em=email,css=css_file)

      if "E"+examkey in session:
        checks = session["E"+examkey]
        #checksstr = datetime.strptime(checks,"%Y-%m-%d %H:%M:%S")
        duetime = checks

      session["E"+examkey] = duetime
      return render_template('custom/exam.html', examkey = examkey, name=name, examname=examname, numquestions=numquestions,duetime=duetime,starttime=starttime,message=message,teacher=teacher,qList=qList,pList=pList,des=des, email=email,css=css_file)
    else:
      return render_template('custom/studentexam.html', ek=examkey, nm=name,msg="The exam key does not exist",css=css_file)

@app.route('/guide')
def guide():
  return render_template('guide.html')

@app.route('/teacher/dashboard/generate/custom',methods=['POST','GET'])
def generatecustom():
  if request.method == "GET":
    return render_template('custom/generate.html')
  elif request.method == "POST":
    req = request.form
    cssurl = req.get('cssurl')
    code = f"""<iframe style="border:none; position:fixed; top:0; left:0; bottom:0; right:0; width:100%; height:100%; border:none; margin:0; padding:0; overflow:hidden; z-index:999999;" src="https://exam.wizdeveloper.com/student/exam/custom/{cssurl.replace("/","-=-")}" width="100%" height="100%"></iframe>"""
    if cssurl.replace(" ","") == "":
      code = f"""<iframe style="border:none; position:fixed; top:0; left:0; bottom:0; right:0; width:100%; height:100%; border:none; margin:0; padding:0; overflow:hidden; z-index:999999;" src="https://exam.wizdeveloper.com/student/exam" width="100%" height="100%"></iframe>"""
    return render_template('custom/generated.html',code=code)

@app.route('/teacher/dashboard/responses/combine/<first_key>/<second_key>/<third_key>', methods=["GET","POST"])
def combinethreescores(first_key,second_key,third_key):
  username = session["user"]
  if first_key in db[username][2] and second_key in db[username][2] and third_key in db[username][2]:
    if request.method == "GET":
      fpList = []
      faList = []
      fm = 0
      fscores = []
      fnames = []
      femails = []
      fstarttimes = []
      fendtimes = []
      frawresponses = []
      fresponses = []
      fdistributions = []
      ffocuses = []


      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {first_key}")
      result = cursor.fetchall()
      for i in result:
        faList.append(i[0])
        fpList.append(i[1])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {first_key}")
        result = cursor.fetchall()
        for q in result:
          fnames.append(q[0])
          fstarttimes.append(q[1])
          fendtimes.append(q[2])
          femails.append(q[3].lower().replace(" ",""))
          frawresponses.append(q[4])
          ffocuses.append(q[5])
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for w in frawresponses:
        
        fresponses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for y in fpList:
        fm += y

      for r in fresponses:
        distribution = ""
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == faList[t].replace(" ","").lower():
            distribution += "✅"
            score += fpList[t]
          else:
            distribution += "❌"
        fdistributions.append(distribution)
        fscores.append(score)




      spList = []
      saList = []
      sm = 0
      sscores = []
      snames = []
      semails = []
      sstarttimes = []
      sendtimes = []
      srawresponses = []
      sresponses = []
      sdistributions = []
      sfocuses = []


      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {second_key}")
      result = cursor.fetchall()
      for i in result:
        saList.append(i[0])
        spList.append(i[1])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {second_key}")
        result = cursor.fetchall()
        for q in result:
          snames.append(q[0])
          sstarttimes.append(q[1])
          sendtimes.append(q[2])
          semails.append(q[3].lower().replace(" ",""))
          srawresponses.append(q[4])
          sfocuses.append(q[5])
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for w in srawresponses:
        
        sresponses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for y in spList:
        sm += y

      for r in sresponses:
        distribution = ""
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == saList[t].replace(" ","").lower():
            distribution += "✅"
            score += spList[t]
          else:
            distribution += "❌"
        sdistributions.append(distribution)
        sscores.append(score)



      tpList = []
      taList = []
      tm = 0
      tscores = []
      tnames = []
      temails = []
      tstarttimes = []
      tendtimes = []
      trawresponses = []
      tresponses = []
      tdistributions = []
      tfocuses = []


      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {third_key}")
      result = cursor.fetchall()
      for i in result:
        taList.append(i[0])
        tpList.append(i[1])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {third_key}")
        result = cursor.fetchall()
        for q in result:
          tnames.append(q[0])
          tstarttimes.append(q[1])
          tendtimes.append(q[2])
          temails.append(q[3].lower().replace(" ",""))
          trawresponses.append(q[4])
          tfocuses.append(q[5])
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for w in trawresponses:
        
        tresponses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for y in tpList:
        tm += y

      for r in tresponses:
        distribution = ""
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == taList[t].replace(" ","").lower():
            distribution += "✅"
            score += tpList[t]
          else:
            distribution += "❌"
        tdistributions.append(distribution)
        tscores.append(score)





      cm = sm + fm + tm
      ctotals = []
      cscores = []
      cnames = []
      cemails = []
      cstarttimes = []
      cendtimes = []
      cresponses = []
      cdistributions = []
      cfocuses = []
      testsTaken = []

      visitedEmails = []
      for em in femails + semails + temails:
        if em not in visitedEmails:
          if em in femails:
            if em in semails:
              if em in temails:
                testsTaken.append([0,1,2])
                findex = femails.index(em)
                sindex = semails.index(em)
                tindex = temails.index(em)

                cnames.append([fnames[findex],snames[sindex],tnames[tindex]])
                cemails.append(em)
                cstarttimes.append([fstarttimes[findex],sstarttimes[sindex],tstarttimes[tindex]])
                cendtimes.append([fendtimes[findex],sendtimes[sindex],tendtimes[tindex]])
                cresponses.append([fresponses[findex],sresponses[sindex],tresponses[tindex]])
                cdistributions.append([fdistributions[findex],sdistributions[sindex],tdistributions[tindex]])
                cfocuses.append([ffocuses[findex],sfocuses[sindex],tfocuses[tindex]])
                cscores.append([[fscores[findex],fm],[sscores[sindex],sm],[tscores[tindex],tm]])
                ctotals.append(fscores[findex]+sscores[sindex]+tscores[tindex])



              else:
                testsTaken.append([0,1])
                findex = femails.index(em)
                sindex = semails.index(em)

                cnames.append([fnames[findex],snames[sindex]])
                cemails.append(em)
                cstarttimes.append([fstarttimes[findex],sstarttimes[sindex]])
                cendtimes.append([fendtimes[findex],sendtimes[sindex]])
                cresponses.append([fresponses[findex],sresponses[sindex]])
                cdistributions.append([fdistributions[findex],sdistributions[sindex]])
                cfocuses.append([ffocuses[findex],sfocuses[sindex]])
                cscores.append([[fscores[findex],fm],[sscores[sindex],sm]])
                ctotals.append(fscores[findex]+sscores[sindex])
            else:
              if em in temails:
                testsTaken.append([0,2])
                findex = femails.index(em)
                tindex = temails.index(em)

                cnames.append([fnames[findex],tnames[tindex]])
                cemails.append(em)
                cstarttimes.append([fstarttimes[findex],tstarttimes[tindex]])
                cendtimes.append([fendtimes[findex],tendtimes[tindex]])
                cresponses.append([fresponses[findex],tresponses[tindex]])
                cdistributions.append([fdistributions[findex],tdistributions[tindex]])
                cfocuses.append([ffocuses[findex],tfocuses[tindex]])
                cscores.append([[fscores[findex],fm],[tscores[tindex],tm]])
                ctotals.append(fscores[findex]+tscores[tindex])                

              else:
                testsTaken.append([0])
                findex = femails.index(em)

                cnames.append([fnames[findex]])
                cemails.append(em)
                cstarttimes.append([fstarttimes[findex]])
                cendtimes.append([fendtimes[findex]])
                cresponses.append([fresponses[findex]])
                cdistributions.append([fdistributions[findex]])
                cfocuses.append([ffocuses[findex]])
                cscores.append([[fscores[findex],fm]])
                ctotals.append(fscores[findex])
          else:
            if em in semails:
              if em in temails:

                testsTaken.append([1,2])
                sindex = semails.index(em)
                tindex = temails.index(em)

                cnames.append([snames[sindex],tnames[tindex]])
                cemails.append(em)
                cstarttimes.append([sstarttimes[sindex],tstarttimes[tindex]])
                cendtimes.append([sendtimes[sindex],tendtimes[tindex]])
                cresponses.append([sresponses[sindex],tresponses[tindex]])
                cdistributions.append([sdistributions[sindex],tdistributions[tindex]])
                cfocuses.append([sfocuses[sindex],tfocuses[tindex]])
                cscores.append([[sscores[sindex],sm],[tscores[tindex],tm]])
                ctotals.append(sscores[sindex]+tscores[tindex])




              else:
                testsTaken.append([1])
                sindex = semails.index(em)

                cnames.append([snames[sindex]])
                cemails.append(em)
                cstarttimes.append([sstarttimes[sindex]])
                cendtimes.append([sendtimes[sindex]])
                cresponses.append([sresponses[sindex]])
                cdistributions.append([sdistributions[sindex]])
                cfocuses.append([sfocuses[sindex]])
                cscores.append([[sscores[sindex],sm]])
                ctotals.append(sscores[sindex])
            else:
              if em in temails:
                testsTaken.append([2])
                tindex = temails.index(em)

                cnames.append([tnames[tindex]])
                cemails.append(em)
                cstarttimes.append([tstarttimes[tindex]])
                cendtimes.append([tendtimes[tindex]])
                cresponses.append([tresponses[tindex]])
                cdistributions.append([tdistributions[tindex]])
                cfocuses.append([tfocuses[tindex]])
                cscores.append([[tscores[tindex],tm]])
                ctotals.append(tscores[tindex])


              else:
                print("error")
          visitedEmails.append(em)






      sortedNames= sort_list(cnames, ctotals)
      sortedEmails = sort_list(cemails,ctotals)
      sortedStarttimes = sort_list(cstarttimes, ctotals)
      sortedEndtimes = sort_list(cendtimes,ctotals)
      sortedDistributions = sort_list(cdistributions,ctotals)
      sortedFocuses = sort_list(cfocuses,ctotals)
      sortedResponses = sort_list(cresponses,ctotals)
      sortedScores = sort_list(cscores,ctotals)

      ctotals.sort()



      return render_template('teacherresponsescombined.html',examkey=first_key + "  "+second_key + "  " + third_key,names=sortedNames,responses=sortedResponses,emails=sortedEmails,starttimes=sortedStarttimes,endtimes=sortedEndtimes,distributions=sortedDistributions,scores=sortedScores,totals=ctotals,m=cm,highest=max(ctotals),lowest=min(ctotals),focusList=sortedFocuses,res=len(ctotals),avg=sum(ctotals)/len(ctotals),median=statistics.median(ctotals))



@app.route('/teacher/dashboard/responses/combine/<first_key>/<second_key>', methods=["GET","POST"])
def combinescores(first_key,second_key):
  username = session["user"]
  if first_key in db[username][2] and second_key in db[username][2]:
    if request.method == "GET":
      fpList = []
      faList = []
      fm = 0
      fscores = []
      fnames = []
      femails = []
      fstarttimes = []
      fendtimes = []
      frawresponses = []
      fresponses = []
      fdistributions = []
      ffocuses = []


      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {first_key}")
      result = cursor.fetchall()
      for i in result:
        faList.append(i[0])
        fpList.append(i[1])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {first_key}")
        result = cursor.fetchall()
        for q in result:
          fnames.append(q[0])
          fstarttimes.append(q[1])
          fendtimes.append(q[2])
          femails.append(q[3].lower().replace(" ",""))
          frawresponses.append(q[4])
          ffocuses.append(q[5])
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for w in frawresponses:
        
        fresponses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for y in fpList:
        fm += y

      for r in fresponses:
        distribution = ""
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == faList[t].replace(" ","").lower():
            distribution += "✅"
            score += fpList[t]
          else:
            distribution += "❌"
        fdistributions.append(distribution)
        fscores.append(score)








      spList = []
      saList = []
      sm = 0
      sscores = []
      snames = []
      semails = []
      sstarttimes = []
      sendtimes = []
      srawresponses = []
      sresponses = []
      sdistributions = []
      sfocuses = []


      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {second_key}")
      result = cursor.fetchall()
      for i in result:
        saList.append(i[0])
        spList.append(i[1])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {second_key}")
        result = cursor.fetchall()
        for q in result:
          snames.append(q[0])
          sstarttimes.append(q[1])
          sendtimes.append(q[2])
          semails.append(q[3].lower().replace(" ",""))
          srawresponses.append(q[4])
          sfocuses.append(q[5])
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for w in srawresponses:
        
        sresponses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for y in spList:
        sm += y

      for r in sresponses:
        distribution = ""
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == saList[t].replace(" ","").lower():
            distribution += "✅"
            score += spList[t]
          else:
            distribution += "❌"
        sdistributions.append(distribution)
        sscores.append(score)








      cm = sm + fm
      ctotals = []
      cscores = []
      cnames = []
      cemails = []
      cstarttimes = []
      cendtimes = []
      cresponses = []
      cdistributions = []
      cfocuses = []
      testsTaken = []

      visitedEmails = []
      for em in femails + semails:
        if em not in visitedEmails:
          if em in femails:
            if em in semails:
              testsTaken.append([0,1])
              findex = femails.index(em)
              sindex = semails.index(em)

              cnames.append([fnames[findex],snames[sindex]])
              cemails.append(em)
              cstarttimes.append([fstarttimes[findex],sstarttimes[sindex]])
              cendtimes.append([fendtimes[findex],sendtimes[sindex]])
              cresponses.append([fresponses[findex],sresponses[sindex]])
              cdistributions.append([fdistributions[findex],sdistributions[sindex]])
              cfocuses.append([ffocuses[findex],sfocuses[sindex]])
              cscores.append([[fscores[findex],fm],[sscores[sindex],sm]])
              ctotals.append(fscores[findex]+sscores[sindex])
            else:
              testsTaken.append([0])
              findex = femails.index(em)

              cnames.append([fnames[findex]])
              cemails.append(em)
              cstarttimes.append([fstarttimes[findex]])
              cendtimes.append([fendtimes[findex]])
              cresponses.append([fresponses[findex]])
              cdistributions.append([fdistributions[findex]])
              cfocuses.append([ffocuses[findex]])
              cscores.append([[fscores[findex],fm]])
              ctotals.append(fscores[findex])
          else:
            if em in semails:
              testsTaken.append([1])
              sindex = semails.index(em)

              cnames.append([snames[sindex]])
              cemails.append(em)
              cstarttimes.append([sstarttimes[sindex]])
              cendtimes.append([sendtimes[sindex]])
              cresponses.append([sresponses[sindex]])
              cdistributions.append([sdistributions[sindex]])
              cfocuses.append([sfocuses[sindex]])
              cscores.append([[sscores[sindex],sm]])
              ctotals.append(sscores[sindex])
            else:
              print("error")
          visitedEmails.append(em)






      sortedNames= sort_list(cnames, ctotals)
      sortedEmails = sort_list(cemails,ctotals)
      sortedStarttimes = sort_list(cstarttimes, ctotals)
      sortedEndtimes = sort_list(cendtimes,ctotals)
      sortedDistributions = sort_list(cdistributions,ctotals)
      sortedFocuses = sort_list(cfocuses,ctotals)
      sortedResponses = sort_list(cresponses,ctotals)
      sortedScores = sort_list(cscores,ctotals)

      ctotals.sort()



      return render_template('teacherresponsescombined.html',examkey=first_key + "  "+second_key,names=sortedNames,responses=sortedResponses,emails=sortedEmails,starttimes=sortedStarttimes,endtimes=sortedEndtimes,distributions=sortedDistributions,scores=sortedScores,totals=ctotals,m=cm,highest=max(ctotals),lowest=min(ctotals),focusList=sortedFocuses,res=len(ctotals),avg=sum(ctotals)/len(ctotals),median=statistics.median(ctotals))


  else:
    return 'You don\'t have access to do this!'





@app.route("/teacher/dashboard/statistics/<exam_key>", methods=["GET","POST"])
def statisticschart(exam_key):
  username = session["user"]
  if exam_key in db[username][2]:
    if request.method == "GET":
      aList = []
      pList = []
      scores = []
      names = []
      emails = []
      starttimes = []
      endtimes = []
      rawresponses = []
      responses = []
      distributions = []
      focuses = []
      numSolves = []
      allqs = []
      m=0

      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {exam_key}")
      result = cursor.fetchall()
      for i in result:
        aList.append(i[0])
        pList.append(i[1])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {exam_key}")
        result = cursor.fetchall()
        for q in result:
          names.append(q[0])
          starttimes.append(q[1])
          endtimes.append(q[2])
          emails.append(q[3])
          rawresponses.append(q[4])
          allqs.append(re.split('<=0=>',q[4].replace("<[0]>","\"").replace(" ","")))
          focuses.append(q[5])
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for w in rawresponses:
        
        responses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for el in pList:
        m += el

      for i in aList:
        numSolves.append(0)

      for r in responses:
        distribution = ""
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == aList[t].replace(" ","").lower():
            distribution += "✅"
            numSolves[t] += 1
            score += pList[t]
          else:
            distribution += "❌"
        distributions.append(distribution)
        scores.append(score)


      sortedNames= sort_list(names, scores)
      sortedEmails = sort_list(emails,scores)
      sortedStarttimes = sort_list(starttimes, scores)
      sortedEndtimes = sort_list(endtimes,scores)
      sortedDistributions = sort_list(distributions,scores)
      sortedFocuses = sort_list(focuses,scores)
      sortedResponses = sort_list(responses,scores)

      scores.sort()




      legend1 = 'Number of Solves'
      legend2 = "Number of People"
      labels1 = []
      labels2 = []
      values1 = []
      values2 = []

      for sc in range(0,m+1):
        labels2.append(f"{sc}")
        values2.append(scores.count(sc))
      
      for nm in range(0,len(aList)):
        labels1.append(f"Question {nm+1}")
        values1.append(numSolves[nm])
        
      fallqs = []
      dallqs = []
      mallqs = []

      for j in range(0,len(aList)):
        temp = []
        for i in allqs:
          temp.append(i[j])
        dallqs.append(temp)

      
      for i in dallqs:
        temp = []
        temp2 = []
        for j in i:
          if j not in temp2:
            temp.append(j)
          temp2.append(j)
        fallqs.append(temp)
      
      for k in dallqs:
        temp = []
        for j in k:
          temp.append(k.count(j))
        mallqs.append(temp)


      return render_template('statistics.html', values1=values1, labels1=labels1, legend1=legend1,legend2=legend2,values2=values2, labels2=labels2,examkey=exam_key,fallqs=fallqs,dallqs=dallqs,mallqs=mallqs,totalres = len(allqs))
  else:
    return 'You don\'t have access to this page'

@app.route('/teacher/dashboard/responses/mail/draft/<exam_key>', methods = ["GET","POST"])
def emaildraft(exam_key):
  username = session["user"]
  if exam_key in db[username][2]:
    if request.method == "GET":
        finaldraft = ""
        finaltitle = ""
        connection = sqlite3.connect('db/emaildrafts.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT title, draft FROM {exam_key}")
        result = cursor.fetchall()
        for q in result:
          finaltitle += q[0].replace("<0=0=0=0>","\"")
          finaldraft += q[1].replace("<0=0=0=0>","\"")
        connection.commit()
        connection.close()
        return render_template('emaildraft.html',examkey=exam_key,finaldraft=finaldraft,finaltitle=finaltitle)
    elif request.method == "POST":
      req = request.form
      draft = req.get("draftdraft")
      title = req.get("titledraft")
      finaldraft = draft.replace("\"","<0=0=0=0>").replace("\'","<0=0=0=0>")
      finaltitle = title.replace("\"","<0=0=0=0>").replace("\'","<0=0=0=0>")

      conne = sqlite3.connect('db/emaildrafts.db')
      cu = conne.cursor()
      cu.execute(f"""
      UPDATE {exam_key}
      SET title = "{finaltitle}",
      draft = "{finaldraft}";
      """)
      conne.commit()
      conne.close()
      return redirect('/teacher/dashboard')





@app.route('/teacher/dashboard/responses/<exam_key>/mail/<email>/<int:row_num>', methods=["GET","POST"])
def sendscoremail(exam_key,email,row_num):
  username = session["user"]
  if exam_key in db[username][2]:
    if request.method == "GET":
      aList = []
      pList = []
      scores = []
      emails = []
      rawresponses = []
      responses = []
      ind = 0
      indlist = []
      finalemail = []
      finalind = 0
      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {exam_key}")
      result = cursor.fetchall()
      for i in result:
        aList.append(i[0])
        pList.append(i[1])
      connection.commit()
      connection.close()
      names = []
      starttimes = []
      endtimes = []
      focuses = []
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {exam_key}")
        result = cursor.fetchall()
        for q in result:
          names.append(q[0])
          starttimes.append(q[1])
          endtimes.append(q[2])
          emails.append(q[3])
          rawresponses.append(q[4])
          focuses.append(q[5])
          indlist.append(ind)
          print(q[3],ind)
          ind += 1
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for i in range(0,len(emails)):
        if emails[i].replace(" ","") == email:
          finalemail.append(i)

      for i in range(0,len(indlist)):
        if indlist[i] == row_num:
          finalind == i

      for w in rawresponses:
        
        responses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for r in responses:
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == aList[t].replace(" ","").lower():
            score += pList[t]
          else:
            print("")
        scores.append(score)

      sortedindlist = sort_list(indlist,scores)
      sortedEmails = sort_list(emails,scores)

      scores.sort()

      if sortedEmails[row_num].replace(" ","") == email.replace(" ",""):
        femail = 0
        for i in range(0,len(emails)):
          if emails[i].replace(" ","") == email.replace(" ",""):
            if sortedEmails.index(emails[i]) == row_num:
              femail = i
        
        unsortedind = femail

        firstlist = ["[score]","[name]","[email]","[rank]","[distribution]","[average]","[median]","[responses]","[focuslost]","[starttime]","[endtime]","[timetaken]","[max]","[min]","[total]"]
        repllist = [scores[unsortedind],names[unsortedind],emails[unsortedind],row_num,"needtoinsertdistribution",avg,median,responses[unsortedind],focuses[unsortedind],starttimes[unsortedind],endtimes[unsortedind],"inserttimetaken",max(scores),min(scores),"inserttotal"]

        for repl in range(0,len(firstlist)):
          draft.replace(firstlist[repl],repllist[repl])


        #SEND THE MESSAGE
        # ADD SMTP

        return redirect(f'/teacher/dashboard/responses/{exam_key}')
      else:
        print(emails[row_num],row_num)







@app.route('/teacher/dashboard/responses/<exam_key>/delete/<email>/<int:row_num>', methods=["GET","POST"])
def teacherresponsesdelete(exam_key,email,row_num):
  username = session["user"]
  if exam_key in db[username][2]:
    if request.method == "GET":
      aList = []
      pList = []
      scores = []
      emails = []
      rawresponses = []
      responses = []
      ind = 0
      indlist = []
      finalemail = []
      finalind = 0
      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT answer,points FROM {exam_key}")
      result = cursor.fetchall()
      for i in result:
        aList.append(i[0])
        pList.append(i[1])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {exam_key}")
        result = cursor.fetchall()
        for q in result:
          emails.append(q[3])
          rawresponses.append(q[4])
          indlist.append(ind)
          print(q[3],ind)
          ind += 1
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for i in range(0,len(emails)):
        if emails[i].replace(" ","") == email:
          finalemail.append(i)

      for i in range(0,len(indlist)):
        if indlist[i] == row_num:
          finalind == i

      for w in rawresponses:
        
        responses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for r in responses:
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == aList[t].replace(" ","").lower():
            score += pList[t]
          else:
            print("")
        scores.append(score)

      sortedindlist = sort_list(indlist,scores)
      sortedEmails = sort_list(emails,scores)

      scores.sort()
      #print(emails[row_num],row_num)
      if sortedEmails[row_num].replace(" ","") == email.replace(" ",""):
        femail = 0
        for i in range(0,len(emails)):
          if emails[i].replace(" ","") == email.replace(" ",""):
            if sortedEmails.index(emails[i]) == row_num:
              femail = i


        unsortedind = femail
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()

        cursor.execute(f"""
          delete from {exam_key} where rowid = (select rowid from {exam_key} limit 1 offset {unsortedind});
          """)
        connection.commit()
        connection.close()

        return redirect(f'/teacher/dashboard/responses/{exam_key}')
      else:
        print(emails[row_num],row_num)

@app.route('/teacher/dashboard/responses/<exam_key>', methods=["GET","POST"])
def teacherresponses(exam_key):
  username = session["user"]
  if exam_key in db[username][2]:
    if request.method == "GET":
      qList = []
      aList = []
      pList = []
      m = 0
      scores = []
      names = []
      emails = []
      starttimes = []
      endtimes = []
      rawresponses = []
      indexno = []
      responses = []
      distributions = []
      focuses = []
      tempin = 0
      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT question,answer,points FROM {exam_key}")
      result = cursor.fetchall()
      for i in result:
        qList.append(i[0])
        aList.append(i[1])
        pList.append(i[2])
      connection.commit()
      connection.close()
      try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name,starttime,endtime,email, responses,focus FROM {exam_key}")
        result = cursor.fetchall()
        for q in result:
          names.append(q[0])
          starttimes.append(q[1])
          endtimes.append(q[2])
          emails.append(q[3])
          rawresponses.append(q[4])
          focuses.append(q[5])
          indexno.append(tempin)
          tempin += 1
        connection.commit()
        connection.close()
      except Exception as e:
        return 'This form hasnt recieved any responses yet'

      for w in rawresponses:
        
        responses.append(re.split('<=0=>',w.replace("<[0]>","\"")))

      for y in pList:
        m += y

      for r in responses:
        distribution = ""
        score = 0
        for t in range(0,len(r)):
          if r[t].replace(" ","").lower() == aList[t].replace(" ","").lower():
            distribution += "✅"
            score += pList[t]
          else:
            distribution += "❌"
        distributions.append(distribution)
        scores.append(score)


      sortedNames= sort_list(names, scores)
      sortedEmails = sort_list(emails,scores)
      sortedStarttimes = sort_list(starttimes, scores)
      sortedEndtimes = sort_list(endtimes,scores)
      sortedDistributions = sort_list(distributions,scores)
      sortedFocuses = sort_list(focuses,scores)
      sortedResponses = sort_list(responses,scores)
      sortedindexno = sort_list(indexno,scores)
      """sortedNames= sorted(names, key = scores.index)
      sortedEmails = sorted(emails, key = scores.index) 
      sortedStarttimes = sorted(starttimes, key = scores.index)
      sortedEndtimes = sorted(endtimes, key = scores.index)
      sortedDistributions = sorted(distributions, key = scores.index)
      sortedFocuses = sorted(focuses, key = scores.index)
      sortedResponses = sorted(responses, key = scores.index)
      sortedindexno = sorted(indexno, key = scores.index)"""


      scores.sort()


      return render_template('teacherdashboardresponses.html',examkey=exam_key,names=sortedNames,responses=sortedResponses,emails=sortedEmails,starttimes=sortedStarttimes,endtimes=sortedEndtimes,distributions=sortedDistributions,scores=scores,m=m,highest=max(scores),lowest=min(scores),res=len(scores),avg=sum(scores)/len(scores),median=statistics.median(scores),focusList=sortedFocuses,indexno=sortedindexno)

    #elif request.method == "POST":

  else:
    return 'You dont have access to this page'

@app.route('/student/exam/<exam_key>', methods=['POST'])
def studentexamfinal(exam_key):
  if request.method == "POST":
    req  = request.form
    netstatus = req.get("netstatus")
    nameList = []
    email = req.get("email")
    name = req.get("name")


    session[exam_key] = "True"
    rn = datetime.now()
    supposedtime = datetime.now()+timedelta()
    try:
      supposedendtime = session["E"+exam_key]
      supposedtime = datetime.strptime(supposedendtime,"%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
      print(e)
    try:
        connection = sqlite3.connect('db/responses.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name FROM {exam_key}")
        result2 = cursor.fetchall()
        for itm in result2:
          nameList.append(itm[0])
        if name in nameList:
          #return "The test has already been submitted!"
          return redirect('/success')
    except Exception as e:
        nameList.append("")


    times = req.get("focuscheck")
    starttime = req.get("starttime")
    num=0
    ttime = 0
    examaccess = ""
    listOfResponses = ""
    connection = sqlite3.connect('db/examsetup.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT examname,num,access,time FROM {exam_key}")
    result2 = cursor.fetchall()
    for j in result2:
        num = j[1]
        examaccess = j[2]
        ttime = j[3]
    connection.commit()
    connection.close()

    if rn >= supposedtime  + timedelta(minutes=1) and ttime != 0:
      name += " [Internet Delay] "
    endtime = rn.strftime("%Y-%m-%d %H:%M:%S")
    

    for i in range(1,num+1):
      a = req.get(f"q{i}").replace("\"","<[0]>").replace("\"","<[0]>")
      if i != num:
        listOfResponses += a
        listOfResponses += "<=0=>"
      else:
        listOfResponses += a

    if examaccess == "False":
      name += " [Closed Submission] "

    connection = sqlite3.connect('db/responses.db')
    cursor = connection.cursor()
    SQL_STATEMENT = f"""CREATE TABLE IF NOT EXISTS {exam_key} (
	  name TEXT,
	  starttime TEXT,
	  endtime TEXT,
    email TEXT,
    responses TEXT,
    focus INTEGER
    );"""
    cursor.execute(SQL_STATEMENT)
    cursor.execute(f"""
    INSERT INTO {exam_key} 
    ('name','starttime','endtime','email', 'responses','focus')
    VALUES (
      "{name}", "{starttime}", "{endtime}", "{email}", "{listOfResponses}",{times}
      );
    """)
    connection.commit()
    connection.close()

    return redirect('/success')

@app.route('/success')
def success():
  return render_template('submitted.html')

@app.route('/', methods = ["GET","POST"])
def ind():
  #ip = get('https://api.ipify.org').text
  #print(ip)
  return render_template('index.html')



@app.route('/teacher/dashboard/clone/<exam_key>', methods=['GET','POST'])
def clone(exam_key):
  username = session["user"]
  if exam_key in db[username][2]:
    k = createKey()
    

    qList = []
    aList = []
    pList = []
    examname = ""
    numquestions = 0
    mintime = 0
    message = ""
    teacher = ""

    connection = sqlite3.connect('db/data.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT question,answer,points FROM {exam_key}")
    result = cursor.fetchall()
    for i in result:
      qList.append(i[0])
      aList.append(i[1])
      pList.append(i[2])
    connection.commit()
    connection.close()
    access = ""
    connection = sqlite3.connect('db/examsetup.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT examname,num,time,message,teacher,access FROM {exam_key}")
    result2 = cursor.fetchall()
    for j in result2:
      examname = j[0]
      numquestions = j[1]
      mintime = j[2]
      message = j[3]
      teacher = j[4]
      access = j[5]
    connection.commit()
    connection.close()




    ##ADD DATA

    connection = sqlite3.connect('db/examsetup.db')
    cursor = connection.cursor()
    SQL_STATEMENT = f"""CREATE TABLE {k} (
	  examname TEXT,
	  num INTEGER,
	  time INTEGER,
    message TEXT,
    teacher TEXT,
    access TEXT
    );"""
    cursor.execute(SQL_STATEMENT)

    cursor.execute(f"""
    INSERT INTO {k} 
    ('examname','num','time','message','teacher','access')
    VALUES (
      "{examname} (Clone)", {numquestions}, {mintime}, "{message}", "{teacher}","{access}"
      );
    """)
    connection.commit()
    connection.close()

    conn = sqlite3.connect('db/data.db')
    c = conn.cursor()
    SQL_STAT = f"""CREATE TABLE {k} (
	  ind INTEGER,
	  question TEXT,
	  answer TEXT,
    points INTEGER
    );"""
    
    c.execute(SQL_STAT)

    for n in range(1,numquestions+1):
      c.execute(f"""
        INSERT INTO {k} 
        ('ind','question','answer','points')
        VALUES (
          {n}, "{qList[n-1]}", "{aList[n-1]}", {pList[n-1]}
        );
      """)
    conn.commit()
    conn.close()

    l = db[username][2]
    l1= l
    l1.append(k)
    info = [db[username][0],db[username][1],l1]
    db[username] = info

    return redirect('/teacher/dashboard')


@app.route('/teacher/dashboard/new', methods = ["GET", "POST"])
def new():
  username = session["user"]
  if request.method == "GET":
    return render_template('teacherdashboardnew.html')
  elif request.method == "POST":
    req = request.form
    examname = req.get("examname")
    num = int(req.get("num"))
    k = createKey()

    ##ADD EXAM INFO TO THE DATA
    connection = sqlite3.connect('db/examsetup.db')
    cursor = connection.cursor()
    SQL_STATEMENT = f"""CREATE TABLE {k} (
	  examname TEXT,
	  num INTEGER,
	  time INTEGER,
    message TEXT,
    teacher TEXT,
    access TEXT
    );"""
    cursor.execute(SQL_STATEMENT)
    

    cursor.execute(f"""
    INSERT INTO {k} 
    ('examname','num','time','message','teacher','access')
    VALUES (
      "{examname}", {num}, 0, "", "{username}","False"
      );
    """)
    connection.commit()
    connection.close()

    conn = sqlite3.connect('db/data.db')
    c = conn.cursor()
    SQL_STAT = f"""CREATE TABLE {k} (
	  ind INTEGER,
	  question TEXT,
	  answer TEXT,
    points INTEGER
    );"""
    
    c.execute(SQL_STAT)

    for n in range(1,num+1):
      c.execute(f"""
        INSERT INTO {k} 
        ('ind','question','answer','points')
        VALUES (
          {n}, "", "", 0
        );
      """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect('db/emaildrafts.db')
    c = conn.cursor()
    SQL_STAT2 = f"""CREATE TABLE {k} (
    title TEXT,
	  draft TEXT
    );"""
    c.execute(SQL_STAT2)
    c.execute(f"""
    INSERT INTO {k} 
    ('title','draft')
    VALUES (
      "", ""
      );
    """)
    conn.commit()
    conn.close()

    l = db[username][2]
    l1 = l
    l1.insert(0,k)
    info = [db[username][0],db[username][1],l1]
    db[username] = info

    return redirect(f'/teacher/dashboard/edit/{k}')

@app.route('/teacher/dashboard/edit/<exam_key>', methods = ["GET", "POST"])
def edit(exam_key):
  username = session["user"]
  if exam_key in db[username][2]:
    if request.method == "GET":
      qList = []
      aList = []
      pList = []
      examname = ""
      numquestions = 0
      mintime = 0
      message = ""
      teacher = ""
      des = False

      connection = sqlite3.connect('db/data.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT question,answer,points FROM {exam_key}")
      result = cursor.fetchall()
      for i in result:
        qList.append(i[0].replace("<[0]>","\""))
        aList.append(i[1].replace("<[0]>","\""))
        pList.append(i[2])
      connection.commit()
      connection.close()
      access = ""
      connection = sqlite3.connect('db/examsetup.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT examname,num,time,message,teacher,access FROM {exam_key}")
      result2 = cursor.fetchall()
      for j in result2:
        examname = j[0]
        numquestions = j[1]
        mintime = j[2]
        message = j[3].replace('<[=0-0=]>',"\"")
        teacher = j[4]
        access = j[5]
      connection.commit()
      connection.close()

      if access == "True":
        des = True
      else:
        des = False

      return render_template('teacherdashboardedit.html', examkey = exam_key,qList=qList,aList=aList,pList=pList, examname=examname, numquestions=numquestions,mintime=mintime,message=message,teacher=teacher,des=des)

    if request.method == "POST":
      req = request.form
      numquestions = 0
      qList = []
      aList = []
      pList = []
      examname = req.get("examname")
      mintime = req.get("mintime")
      teacher = req.get("teacher")
      message = req.get("message").replace("\"","<[=0-0=]>").replace("\'","<[=0-0=]>")
      accdes = ""
      if 'access' in req:
        accdes = "True"
      else:
        accdes = "False"

      connection = sqlite3.connect('db/examsetup.db')
      cursor = connection.cursor()
      cursor.execute(f"SELECT examname,num FROM {exam_key}")
      result2 = cursor.fetchall()
      for j in result2:
        numquestions = j[1]
      connection.commit()
      connection.close()

      for i in range(1,numquestions+1):
        qList.append(req.get(f"q{i}").replace("\"","<[0]>").replace("\'","<[0]>"))
        aList.append(req.get(f"a{i}").replace("\"","<[0]>").replace("\'","<[0]>"))
        pList.append(req.get(f"p{i}"))
      
      conn = sqlite3.connect('db/data.db')
      c = conn.cursor()
      for i in range(0,len(qList)):
        SQL_STAT1 = f"""UPDATE {exam_key} 
	      SET question = "{qList[i]}"
        WHERE ind = {i+1};
        """
        c.execute(SQL_STAT1)
        SQL_STAT2 = f"""UPDATE {exam_key} 
	      SET answer = "{aList[i]}"
        WHERE ind = {i+1};
        """
        c.execute(SQL_STAT2)
        SQL_STAT3 = f"""UPDATE {exam_key} 
	      SET points = "{pList[i]}"
        WHERE ind = {i+1};
        """
        c.execute(SQL_STAT3)
      conn.commit()
      conn.close()


      conne = sqlite3.connect('db/examsetup.db')
      cu = conne.cursor()

      cu.execute(f"""
      UPDATE {exam_key}
      SET examname = "{examname}",
      num = {numquestions},
      time = {mintime},
      message = "{message}",
      teacher = "{teacher}",
      access = "{accdes}";
      """)

      conne.commit()
      conne.close()


      return redirect('/teacher/dashboard')
  else:
    return 'You dont have access to this page'


@app.route('/teacher/dashboard/delete/<exam_key>', methods = ["GET", "POST"])
def deleteexamkey(exam_key):
  username = session["user"]
  if exam_key in db[username][2]:
    

    connection = sqlite3.connect('db/data.db')
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE {exam_key}")
    connection.commit()
    connection.close()

    try:
      connection = sqlite3.connect('db/responses.db')
      cursor = connection.cursor()
      cursor.execute(f"DROP TABLE {exam_key}")
      connection.commit()
      connection.close()
    except Exception as e:
      print(e)

    connection = sqlite3.connect('db/examsetup.db')
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE {exam_key}")
    connection.commit()
    connection.close()

    try:
      connection = sqlite3.connect('db/emaildrafts.db')
      cursor = connection.cursor()
      cursor.execute(f"DROP TABLE {exam_key}")
      connection.commit()
      connection.close()
    except Exception as e:
      print(e)

    l = db[username][2]
    l.remove(exam_key)
    info = [db[username][0],db[username][1], l]
    db[username] = info

    return redirect('/teacher/dashboard')
  else: 
    return 'You dont have permission to do this!'






@app.route("/logout", methods = ["GET", "POST"])
def logout():
  session.pop('user', None)
  return redirect('/')



@socketio.on('join')
def socketconnect(json):
  ####socketio.emit('response', {'name': json['name'], 'key': json['key']}, broadcast=True)
  #print(str(json))
  emit('join', json, broadcast=True)

@socketio.on('unjoin')
def socketdisconnect(json):
  emit('unjoin',json,broadcast=True)


#app.run(host='0.0.0.0', port=8080)
#socketio.run(app, host='0.0.0.0', port=8080)

socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT",5000)), allow_unsafe_werkzeug=True)