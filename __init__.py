from flask import Flask, render_template, redirect, request, session, jsonify
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# librarys import

app = Flask(__name__)

# flask start

# mysql config
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_DB'] = 'banking'

mysql = MySQL()
mysql.init_app(app) #mysql engine start
# mysql config end

app.config['SECRET_KEY'] = 'banking'  #secret key for login system

@app.route('/')
def home():
    try:
        if session.get('admin'):
            heading = 'dashboard'
            pid = session.get('admin')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('select id,name,number,email,role,balance from users where id=%s', pid)
            profile = cursor.fetchall()

            cursor.execute(
                'select concat("Balance:     ",amount,",            ",ttype,",  Date:              ",date) from accounts where uid=%s limit 5', pid)
            recenttrasition = cursor.fetchall()
            conn.close()
            return render_template('dashboard.html', heading=heading,profile=profile,recenttrasition=recenttrasition)
        else:
            return redirect('/login')
    except Exception as e:
        return str(e)

# user management tab
@app.route('/settings', methods=['GET','POST'])
def settings():
    try:
        if session.get('admin') and (session.get('role')== 'Admin'):
            if request.method == 'POST':
                action = request.args.get('action')
                if action == 'add':
                    name = request.form['name']
                    email = request.form['email']
                    number = request.form['number']
                    password = request.form['password']
                    cpassword = request.form['cpassword']
                    role = request.form['role']
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute('select id from users where email=%s', email)

                    data = cursor.fetchall()

                    if data:
                        conn.close()
                        session['response'] = 'Email already registered!'
                        return redirect('/settings')
                    if password == cpassword:
                        password = generate_password_hash(password)
                        conn = mysql.connect()
                        cursor = conn.cursor()
                        cursor.execute('insert into users (name,email,number,password,role) values(%s,%s,%s,%s,%s)',
                                       (name, email, number, password, role))
                        conn.commit()
                        conn.close()
                        session['response'] = 'User ' + name + ' Add Successfully..'
                        return redirect('/settings')
                    else:
                        session['response'] = 'Password not matched.'
                        return redirect('/settings')
                elif action == 'edit':
                    id = request.args.get('id')
                    name = request.form['name']
                    email = request.form['email']
                    number = request.form['number']
                    role = request.form['role']

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute('update users set name=%s,email=%s,number=%s,role=%s where id=%s',
                                   (name, email, number, role, id))
                    conn.commit()
                    conn.close()
                    session['response'] = 'User ' + name + ' edit Successfully.'
                    return redirect('/settings')
                elif action == 'delete':
                    id = request.args.get('id')
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute('delete from users  where id=%s', id)
                    conn.commit()
                    conn.close()
                    session['response'] = 'User delete Successfully.'
                    return redirect('/settings')
                elif action == 'reset':
                    name = request.form['user']
                    temp = name.split(',')[0]
                    name = name.split(',')[1]
                    name = name.split(':')[1]
                    id = temp.split(':')[1]
                    password = request.form['password']
                    cpassword = request.form['cpassword']
                    if password == cpassword:
                        password = generate_password_hash(password)
                        conn = mysql.connect()
                        cursor = conn.cursor()
                        cursor.execute('update users set password=%s where id=%s', (password, id))
                        conn.commit()
                        conn.close()
                        session['response'] = 'User ' + name + ' password reset successfully.'
                        return redirect('/settings')
                    else:
                        session['response'] = 'Password not matched'
                        return redirect('/settings')
                else:
                    return redirect('/settings')

            else:
                heading = 'settings'
                response = None
                if session.get('response'):
                    response = session.get('response')
                    session.pop('response', None)
                view = request.args.get('view')
                if view == 'ajax':
                    id = request.args.get('id')
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute('select id,name,email,number,role from users where id=%s', id)
                    data = cursor.fetchall()
                    conn.close()
                    return jsonify(data)
                else:
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute('select id,name,email,number,role from users')
                    users = cursor.fetchall()
                    conn.close()
                    return render_template('settings.html', response=response, heading=heading, users=users)
        else:
            return redirect('/')
    except Exception as e:
        session['error'] = 'Error'
        session['error_response'] = str(e)
        return redirect('/error')
        # return str(e)


@app.route('/profile',methods=['GET','POST'])
def profile():
    try:
        if session.get('admin'):
            if request.method == 'POST':
                action = request.args.get('action')
                userid =  session.get('admin')
                if action == 'edit':
                    name = request.form['name']
                    phone =  request.form['number']
                    email =  request.form['email']

                    conn =  mysql.connect()
                    cursor =  conn.cursor()

                    cursor.execute('update users set name=%s,number=%s,email=%s where id=%s',(name,phone,email,userid))
                    conn.commit()
                    conn.close()
                    session['response'] = 'User '+ name +' updated successfully .! '
                    return redirect('/profile')
                else:
                    return redirect('/profile')

            else:
                heading = 'profile'
                pid =  session.get('admin')
                conn = mysql.connect()
                cursor =  conn.cursor()
                cursor.execute('select id,name,number,email,role,balance from users where id=%s',pid)
                profile =  cursor.fetchall()

                cursor.execute('select concat("Balance:     ",amount,",            ",ttype,",  Date:              ",date) from accounts where uid=%s limit 5', pid)
                recenttrasition = cursor.fetchall()
                cursor.execute('select id,type,ttype,amount,date,description from accounts where uid=%s',pid)
                trasitions = cursor.fetchall()

                conn.close()
                return render_template('profile.html',heading=heading,profile=profile,recenttrasition=recenttrasition,trasitions=trasitions)
        else:
            return redirect('/login')
    except Exception as e:
        session['error'] = 'Error'
        session['error_response'] = str(e)
        return redirect('/error')

@app.route('/transitions',methods=['GET','POST'])
def transitions():
    try:
        if session.get('admin'):
            if request.method == 'POST':
                return redirect('/transitions')
            else:
                heading = 'transitions'
                pid =  session.get('admin')
                conn = mysql.connect()
                cursor =  conn.cursor()
                if session.get('role') == 'Admin':
                    cursor.execute('select id,type,ttype,amount,date,description from accounts')
                else:
                    cursor.execute('select id,type,ttype,amount,date,description from accounts where uid=%s',pid)
                trasitions = cursor.fetchall()
                conn.close()
                return render_template('transition.html',heading=heading,trasitions=trasitions)
        else:
            return redirect('/login')
    except Exception as e:
        session['error'] = 'Error'
        session['error_response'] = str(e)
        return redirect('/error')


@app.route('/deposit',methods=['GET','POST'])
def deposit():
    try:
        if session.get('admin'):
            userid = session.get('admin')
            if request.method == 'POST':
                action = request.args.get('action')
                if action == 'add':

                    amount =  request.form['amount']
                    type = request.form['type']
                    rid = 0
                    # date = request.form['date']
                    description =  request.form['description']

                    conn =  mysql.connect()
                    cursor = conn.cursor()

                    cursor.execute('insert into accounts (uid,amount,type,rid,date,description,ttype) values (%s,%s,%s,%s,now(),%s,%s)',(userid,amount,type,rid,description,'Deposit'))
                    conn.commit()

                    cursor.execute('update users set balance =  balance + %s where id=%s',(amount,userid))
                    conn.commit()
                    conn.close()
                    session['response'] = 'You are credited ' + str(amount) + ' successfully .!'
                    return redirect('/deposit')
                else:
                    return redirect('/deposit')

            else:
                heading = 'deposit'
                response =  None
                if session.get('response'):
                    response =  session.get('response')
                    session.pop('response')
                conn =  mysql.connect()
                cursor =  conn.cursor()
                cursor.execute('select id,type,amount,date,description from accounts where uid=%s and ttype="Deposit"',userid)
                deposit =  cursor.fetchall()
                conn.close()
                return render_template('deposit.html',heading=heading,response=response,deposit=deposit)
        else:
            return redirect('/')
    except Exception as e:
        session['error'] = 'Error'
        session['error_response'] = str(e)
        return redirect('/error')

@app.route('/withdraw',methods=['GET','POST'])
def withdraw():
    try:
        if session.get('admin'):
            userid = session.get('admin')
            if request.method == 'POST':
                action = request.args.get('action')
                if action == 'add':

                    amount =  request.form['amount']
                    type  = request.form['type']
                    rid = 0
                    # date = request.form['date']
                    description =  request.form['description']

                    conn =  mysql.connect()
                    cursor = conn.cursor()

                    cursor.execute('select id,balance from users where id=%s',userid)
                    data =  cursor.fetchall()

                    if (( int(data[0][1]) - int(amount) ) >=  0):

                        cursor.execute('insert into accounts (uid,amount,type,rid,date,description,ttype) values (%s,%s,%s,%s,now(),%s,%s)',(userid,amount,type,rid,description,'Withdraw'))
                        conn.commit()

                        cursor.execute('update users set balance =  balance - %s where id=%s',(amount,userid))
                        conn.commit()
                        conn.close()
                        session['response'] = 'You are debited ' + str(amount) + ' successfully .!'
                        return redirect('/withdraw')
                    else:
                        conn.close()
                        session['response'] = 'Insufficient funding .!'
                        return redirect('/withdraw')

                else:
                    return redirect('/withdraw')

            else:
                heading = 'withdraw'
                response =  None
                if session.get('response'):
                    response =  session.get('response')
                    session.pop('response')
                conn =  mysql.connect()
                cursor =  conn.cursor()
                cursor.execute('select id,type,amount,date,description from accounts where uid=%s and ttype="Withdraw"',userid)
                withdraw =  cursor.fetchall()
                conn.close()
                return render_template('withdraw.html',heading=heading,response=response,withdraw=withdraw)
        else:
            return redirect('/')
    except Exception as e:
        session['error'] = 'Error'
        session['error_response'] = str(e)
        return redirect('/error')


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if session.get('admin'):
            return redirect('/')
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            number = request.form['number']
            password = request.form['password']
            cpassword = request.form['cpassword']
            role = 'User'
            balance =  0
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('select id from users where email=%s', email)

            data = cursor.fetchall()

            if data:
                conn.close()
                session['response'] = 'Email already registered!'
                return redirect('/register')
            if password == cpassword:
                password = generate_password_hash(password)
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute('insert into users (name,email,number,password,role,balance) values(%s,%s,%s,%s,%s,%s)',
                               (name, email, number, password, role,balance))
                conn.commit()
                conn.close()
                session['response'] = 'User ' + name + ' Add Successfully..'
                return redirect('/')
            else:
                session['response'] = 'Password not matched.'
                return redirect('/register')


        else:
            response =  None
            if session.get('response'):
                response =  session.get('response')
                session.pop('response')
            return render_template('register.html',response=response)

    except Exception as e:
        return render_template('register.html', response=str(e))


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session.get('admin'):
            return redirect('/')
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('select id,name,email,password,role from users where email=%s', email)
            data = cursor.fetchall()
            conn.close()
            if data:
                if check_password_hash(data[0][3], password):
                    session['admin'] = data[0][0]
                    session['name'] = data[0][1]
                    session['role'] = data[0][4]
                    return redirect('/')
                else:
                    return render_template('login.html', response='Invalid password.')
            else:
                return render_template('login.html', response='Account is not registerated.')
        else:
            response = None
            if session.get('response'):
                response =  session.get('response')
                session.pop('response',None)
            return render_template('login.html',response=response)
    except Exception as e:
        return render_template('login.html', response=str(e))


@app.route('/logout')
def logout():
    if session.get('admin'):
        session.pop('admin', None)
    if session.get('name'):
        session.pop('name', None)
    if session.get('role'):
        session.pop('role', None)

    return redirect('/')

@app.route('/error')
def error():
    error = None
    error_response = None
    if session.get('error'):
        error = session.get('error')
        session.pop('error', None)
    if session.get('error_response'):
        error_response = session.get('error_response')
        session.pop('error_response', None)
    if error == None and error_response == None:
        return redirect('/admin')
    return render_template('error.html', error_response=error_response, error=error)


if __name__ == '__main__':
    app.run(debug=True)
