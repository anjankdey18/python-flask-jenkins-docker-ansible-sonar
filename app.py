from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,IntegerField,SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
#from .forms import MCQForm
from flask_session import Session
import mysql.connector
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
Session(app)
# MySQL Configuration
#load_dotenv(".env")
load_dotenv("db.env")
mysql = MySQL(app)

app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
#app.config['MYSQL_DB'] = 'mcqdb'
app.secret_key = 'Y/OjkVknLkxn9rkQnla/aaazRZ9i4iys3DrHxEotIS0='

class RegisterForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self,field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where email=%s",(field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")

class MCQForm(FlaskForm):
    question = StringField('Question')
    option1 = StringField('Option 1')
    option2 = StringField('Option 2')
    option3 = StringField('Option 3')
    option4 = StringField('Option 4')
    correct_option = IntegerField('Correct Option (1-4)')
    submit = SubmitField('Add Question')

# # Function to check if user is logged in
# def is_logged_in():
#     return 'username' in session


# Function to check if user is admin
def is_admin():
    if 'is_admin' in session:
        return session['is_admin']
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

        # store data into database 
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html',form=form)

# Function to check if user is logged in
def is_logged_in():
    return 'username' in session

# @app.route('/user_result')
# def user_result():
#     if is_logged_in():
#         # Calculate the exam score (assuming the score is stored in the session)
#         exam_score = session.get('exam_score', None)
#         # Render the template, passing the exam score
#         return render_template('user_result.html', exam_score=exam_score)
#     # return redirect(url_for('user_login'))
#     return redirect(url_for('login'))

@app.route('/user_result')
def user_result():
    if is_logged_in():
        # Calculate the exam score (assuming the score is stored in the session)
        # exam_score = session.get('exam_score', None)
        # # Render the template, passing the exam score
        # return render_template('user_result.html', exam_score=exam_score)
        # Log session contents for debugging
        app.logger.debug("Session contents: %s", session)
        score = session.get('score', None)
         # Log exam score for debugging
        app.logger.debug("Exam score: %s", score)
        # Render the template, passing the exam score
        return render_template('user_result.html', score=score)
    # return redirect(url_for('user_login'))
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            return redirect(url_for('dashboard'))
            #return redirect(url_for('user_result'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html',form=form)

@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html',form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where id=%s",(user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashboard.html',user=user)
            
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where id=%s",(user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('admin_dashboard.html',user=user)
            
    return redirect(url_for('admin_login'))

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    form = MCQForm()
    if form.validate_on_submit():
        # Insert question into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO MCQs (question, option1, option2, option3, option4, correct_option) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (form.question.data, form.option1.data, form.option2.data, form.option3.data, form.option4.data, form.correct_option.data))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('add_question'))
    return render_template('add_question.html', form=form)

@app.route('/questions')
def display_questions():
    # Fetch questions from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM MCQs")
    questions = cursor.fetchall()
    return render_template('questions.html', questions=questions)

# @app.route('/take_exam', methods=['GET', 'POST'])
# def take_exam():
#     if request.method == 'POST':
#         # Handle form submission if needed (e.g., to grade the exam)
#         pass
#     # Fetch questions from the database
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT * FROM MCQs")
#     questions = cursor.fetchall()
#     return render_template('take_exam.html', questions=questions)

@app.route('/take_exam', methods=['GET', 'POST'])
def take_exam():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        # Handle form submission
        total_questions = 0
        correct_answers = 0

        # Fetch questions and correct answers from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, correct_option FROM MCQs")
        # cursor.execute("SELECT id, correct_option FROM questions")
        questions = cursor.fetchall()

        # Loop through each question to check the submitted answer
        for question in questions:
            total_questions += 1
            question_id = question[0]
            correct_option = question[1]
            submitted_answer = int(request.form.get(f'answer{question_id}'))

            # Check if the submitted answer is correct
            if submitted_answer == correct_option:
                correct_answers += 1
        
        # Calculate the score
        score = (correct_answers / total_questions) * 100

        # Render the result template with the score
        return render_template('exam_result.html', score=score)
        # return render_template('user_result.html', score=score)

    # If it's a GET request, display the exam form
    cursor.execute("SELECT * FROM MCQs")
    questions = cursor.fetchall()
    return render_template('take_exam.html', questions=questions)

# # Function to check if user is logged in
# def is_logged_in():
#     return 'email' in session

# @app.route('/user_result')
# def user_result():
#     if is_logged_in():
#         return render_template('user_result.html')
#     return redirect(url_for('login'))

# @app.route('/submit_exam', methods=['POST'])
# def submit_exam():
#     score = 0
#     total_questions = 0
#     for question_id, answer in request.form.items():
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT correct_option FROM MCQs WHERE id = %s", (question_id,))
#         correct_option = cursor.fetchone()[0]
#         total_questions += 1
#         if int(answer) == correct_option:
#             score += 1

#     flash(f'Your score: {score}/{total_questions}')
#     return redirect(url_for('display_questions'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

# Function to read questions from a file
def read_questions_from_file(file_path):
    questions = []
    with open(file_path, 'r') as file:
        for line in file:
            # Parse the line and extract question data (e.g., question, options, answer)
            question_data = line.strip().split(',')
            questions.append(question_data)
    return questions

# # Function to connect to MySQL database and insert questions
# def insert_questions_into_database(questions):
#     #Connect to MySQL database
#     db_connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Poonam_dey9228,
#         database="mydatabase"
#     )
#     # app.config['MYSQL_HOST'] = 'localhost'
#     # app.config['MYSQL_USER'] = 'root'
#     # app.config['MYSQL_PASSWORD'] = 'Poonam_dey9228'
#     # app.config['MYSQL_DB'] = 'mydatabase'

#     cursor = mysql.connection.cursor()
#     # Insert questions into the database
#     for question_data in questions:
#         # Assuming the questions table has columns: id, question_text, option1, option2, option3, option4, correct_option
#         query = "INSERT INTO questions (question_text, option1, option2, option3, option4, correct_option) VALUES (%s, %s, %s, %s, %s, %s)"
#         cursor.execute(query, question_data)
    
#     # Commit changes and close connection
#     mysql.connection.commit()
#     cursor.close()
#     mysql.connection.close()

# # if __name__ == "__main__":
# #     # File path containing questions
# #     file_path = "questions.csv"
    
# #     # Read questions from the file
# #     questions = read_questions_from_file(file_path)
    
# #     # Insert questions into the database
# #     insert_questions_into_database(questions)


# if __name__ == '__main__':
#     app.run(debug=True)

#     # File path containing questions
#     file_path = "~/myApps/flask-auth-db-mcq-updated/questions.csv"
    
#     # Read questions from the file
#     questions = read_questions_from_file(file_path)
    
#     # Insert questions into the database
#     insert_questions_into_database(questions)
@app.route('/insert_questions_into_database', methods=['GET', 'POST'])
def insert_questions_into_database(questions):
    try:
        # Connect to MySQL database
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Poonam_dey9228",
            database="mydatabase"
        )
        # cursor = db_connection.cursor()
        cursor = mysql.connection.cursor()

        # Insert questions into the database
        for question_data in questions:
            query = "INSERT INTO questions (question_text, option1, option2, option3, option4, correct_option) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, question_data)

        # Commit changes
        mysql.connection.commit()
        print("Questions inserted successfully.")
        cursor.close()

    except mysql.connector.Error as error:
        print("Error inserting questions:", error)

    finally:
        # Close cursor and database connection
        if 'cursor' in locals():
            cursor.close()
        if 'db_connection' in locals() and db_connection.is_connected():
            db_connection.close()

# if __name__ == '__main__':
#     app.run(debug=True)
    # File path containing questions
    #file_path = "~/myApps/flask-auth-db-mcq-updated/questions.csv"
    file_path = "~/myApps/flask-auth-db-mcq-updated/questions.txt"
    
    # Read questions from the file
    questions = read_questions_from_file(file_path)
    
    # Insert questions into the database
    insert_questions_into_database(questions)

#########################
# Function to insert questions into MySQL table
def insert_questions_into_database(questions):
    cursor = mysql.connection.cursor()

    # Insert questions into the database
    # for question_data in questions:
    #     query = "INSERT INTO questions (question_text, option1, option2, option3, option4, correct_option) VALUES (%s, %s, %s, %s, %s, %s)"
    #     cursor.execute(query, question_data)

    for question, options, correct_option in questions:
        options_str = ', '.join(options)
        sql = "INSERT INTO questions (question, options, correct_option) VALUES (%s, %s, %s)"
        cursor.execute(sql, (question, options_str, correct_option))
    
    # Commit changes and close connection
    # Commit changes
    mysql.connection.commit()
    print("Questions inserted successfully in the sqldb.")
    cursor.close()
    #db_connection.close()
    #mysql.connection.close()


#############
#@app.route('/insert_questions_into_database', methods=['GET', 'POST'])
# def insert_questions_into_database(questions):
#     try:
#         # Connect to MySQL database
#         db_connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="Poonam_dey9228",
#             database="mydatabase"
#         )
#             # Check if connection is established
#         if db_connection:
#             print("Connected to MySQL database")
#         # cursor = db_connection.cursor()
#         cursor = mysql.connection.cursor()

#         # Insert questions into the database
#         for question_data in questions:
#             query = "INSERT INTO questions (question_text, option1, option2, option3, option4, correct_option) VALUES (%s, %s, %s, %s, %s, %s)"
#             cursor.execute(query, question_data)

#         # Commit changes
#         mysql.connection.commit()
#         print("Questions inserted successfully.")
#         #cursor.close()
#         #db_connection.close()

#     except mysql.connector.Error as error:
#         print("Error inserting questions:", error)

#     finally:
#         # Close cursor and database connection
#         if 'cursor' in locals():
#             cursor.close()
#         if 'db_connection' in locals() and db_connection.is_connected():
#             db_connection.close()

# MySQL Configuration
# MYSQL_HOST = 'localhost'
# MYSQL_USER = 'root'
# MYSQL_PASSWORD = 'Poonam_dey9228'
# MYSQL_DB = 'mcqdb'
# cursor = mysql.connection.cursor()
# def connect_to_database():
#     cursor = mysql.connection.cursor()
#     return cursor.connect(host=MYSQL_HOST,
#                            user=MYSQL_USER,
#                            password=MYSQL_PASSWORD,
#                            database=MYSQL_DB,
#                            cursorclass=cursor.cursors.DictCursor)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    #cursor = mysql.connection.cursor()
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('upload.html', error='No file part')

        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return render_template('upload.html', error='No file selected')
        
        # Check file extension
        if not file.filename.endswith('.txt'):
            return render_template('upload.html', error='Only .txt files are allowed')

        # Read and parse the file contents ///file upload but not showing on db
        # questions = []
        # for line_bytes in file:
        #     line = line_bytes.decode('utf-8').strip()
        #     if line.startswith('Question:'):
        #         question_text = line[len('Question:'):].strip()
        #     elif line.startswith('Options:'):
        #         options = [opt.strip() for opt in line_bytes.decode('utf-8').strip().split('.')]
        #     elif line.startswith('Correct Answer:'):
        #         correct_option = line[len('Correct Answer:'):].strip()
        #         questions.append((question_text,) + tuple(options) + (correct_option,))
        table_name = "MCQs"
        #table_name = "questions"
        questions = []
        with open('questions.txt', 'r') as file:
            for line in file:
                parts = line.split('|')
                if len(parts) == 3:
                    question, options, correct_option = parts
                    option1, option2, option3, option4 = options.split(',')
                    # Process the question, options, and correct option here
                    # Insert data into the questions table
                    cursor = mysql.connection.cursor()
                    sql = "INSERT INTO {} (question, option1, option2, option3, option4, correct_option) VALUES (%s, %s, %s, %s, %s, %s)".format(table_name)
                    #sql = "INSERT INTO questions (question, option1, option2, option3, option4, correct_option) VALUES (%s, %s, %s, %s, %s, %s)"
                    values = (question, option1.strip(), option2.strip(), option3.strip(), option4.strip(), int(correct_option))
                    cursor.execute(sql, values)
                    mysql.connection.commit()
                    print("Questions inserted successfully in the sqldb.")
                    cursor.close()

                else:
                    print("Invalid format in line:", line)

        # Insert questions into the database
        #insert_questions_into_database(questions)

        return render_template('upload.html', success='Questions uploaded successfully')

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

