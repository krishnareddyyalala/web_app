from flask import *
import sqlite3
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import io
import base64

app=Flask(__name__)

app.secret_key = "your_very_secret_key"

@app.route('/')
def home():
    return redirect(url_for('basic'))

@app.route('/basic', methods=['GET','POST'])

def basic():
    if request.method=='POST':
       username=request.form['username']
       password=request.form['password']
       
       conn=get_db_connection()
       cursor=conn.cursor()
       cursor.execute("select id, password from users where username=?",(username,))
       user=cursor.fetchone()
       conn.close()

       if user is None:
          return 'invalid password'
       if password==user[1]:
          session['username']=username
          session['user_id'] = user[0]

          return redirect(url_for('dashboard'))
       
    return render_template('basic.html')

@app.route('/dashboard')
def dashboard():
   if 'username' not in session:
      return redirect(url_for('basic'))
   return render_template('dashboard.html',username=session['username'])

@app.route('/deposit', methods=['GET','POST'])
def deposit():
  if request.method=='POST':
    date=request.form['date']
    day=request.form['day']
    purpose=request.form['deposit']
    type='deposit'
    amount=float(request.form['amount'])
    

    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("SELECT balance FROM user_transactions ORDER BY id DESC LIMIT 1")
    prev_balance = cursor.fetchone()
    if prev_balance:
        prev_balance = prev_balance[0]
    else:
        prev_balance = 0

    balance = prev_balance + float(amount)


    cursor.execute(
     "Insert into user_transactions(date,day,purpose,type,amount,balance, user_id) values(?,?,?,?,?,?,?)",(date,day,purpose,type,amount,balance,session['user_id'])
    )
    conn.commit()
    conn.close()
    return 'deposited successfully'

  return render_template('deposit.html')

@app.route('/checkb')
def checkb():
   conn=get_db_connection()
   cursor=conn.cursor()

   cursor.execute(
    "select balance from user_transactions where user_id=(?) order by id desc limit 1",
    (session['user_id'],)
   )
   
   cbalance = cursor.fetchone()
   conn.close()

    # If no transactions yet
   if cbalance:
        balance = cbalance[0]
   else:
        balance = 0.0

   return render_template('checkb.html',balance=balance)

@app.route('/ta',methods=['GET','POST'])
def ta(): 
 conn=get_db_connection()
 cursor=conn.cursor()

 query = """
    SELECT date, day, purpose, amount
    FROM user_transactions
    WHERE user_id = ? AND type = 'expense'
  """
 params = [session['user_id']]

 
 if request.method == 'POST':
     date_range = request.form.get('date_range')
     amount_range = request.form.get('amount_range')

     today = datetime.today()
     end_date = today.strftime('%Y-%m-%d')

     if date_range == "this month":
        start_date = date(today.year, today.month, 1).strftime('%Y-%m-%d')

     elif date_range == "last 30 days":
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')

     elif date_range == "last 90 days":
        start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
     else:
        start_date=None
     
     if start_date:
        query+="and date between ? and ?"
        params.extend([start_date,end_date])

     if amount_range == "above 200":
       query += " AND amount > 200"
     elif amount_range == "1000-5000":
       query += " AND amount BETWEEN 1000 AND 5000"
     elif amount_range == "above 5000":
       query += " AND amount > 5000"


 cursor.execute(query,params)
 rows = cursor.fetchall()

 conn.close()

 return render_template('ta.html', transactions=rows)
   

@app.route('/adde',methods=['GET','POST'])
def adde():
  if request.method=='POST':
    date=request.form['date']
    day=request.form['day']
    purpose=request.form['purpose']
    type='expense'
    amount=float(request.form['amount'])

    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("SELECT balance FROM user_transactions ORDER BY id DESC LIMIT 1")
    prev_balance = cursor.fetchone()
    if prev_balance:
        prev_balance = prev_balance[0]
        if prev_balance>=amount:
          balance = prev_balance - float(amount)
        else:
          return 'insufficient balance'
    else:
        prev_balance = 0
        return 'insufficient balance'

    cursor.execute(
     "Insert into user_transactions(date,day,purpose,type,amount,balance, user_id) values(?,?,?,?,?,?,?)",(date,day,purpose,type,amount,balance,session['user_id'])
    )
    conn.commit()
    conn.close()
    return 'added successfully'
  
  return render_template('adde.html')

@app.route('/chart')
def chart():
   conn=get_db_connection()
   cursor=conn.cursor()

   cursor.execute(
    "SELECT purpose, SUM(amount) FROM user_transactions " \
    "WHERE user_id = ? AND type = 'expense' GROUP BY purpose",
    (session['user_id'],)
   )

   rows=cursor.fetchall()
   conn.close()
    
   labels = [row[0] for row in rows]
   values = [row[1] for row in rows]


   plt.pie(values, labels=labels, autopct='%1.1f%%')
   plt.title('Expense by Purpose')


   img = io.BytesIO()
   plt.savefig(img, format='png')
   img.seek(0)
   plt.close()   

   chart_url = base64.b64encode(img.getvalue()).decode()

   return render_template('chart.html', chart_url=chart_url)


def get_db_connection():
    conn=sqlite3.connect('database.db')
    return conn

@app.route('/signup',methods=['GET','POST'])
def signup():
  if request.method == 'POST':

    username=request.form['username']
    password=request.form['password']
    password1=request.form['password1']
    
    if password != password1:
        return 'password mismatch'
    
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute(
        "INSERT INTO users(username, password) VALUES(?,?)",(username,password)
    )
    conn.commit()
    conn.close()
    return 'created successfully'

  return render_template('signup.html')

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


