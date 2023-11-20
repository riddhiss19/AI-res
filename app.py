from fileinput import filename
import os
import string
import pymysql
from flask import Flask, render_template, request, redirect, flash, send_file, session
from passlib.hash import sha256_crypt
import gc
from werkzeug.utils import secure_filename
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from colorama import Fore
import pafy
import plotly.express as px
import io,random
from werkzeug.utils import secure_filename
import pandas
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.naive_bayes import MultinomialNB
from cluster import findJobTitle

from test_utils import *

UPLOAD_FOLDER = 'D:/3 year VIT/AI/CP/AI-res/Resumes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

app = Flask(__name__)
app.debug = True
app.secret_key = 'resumeai'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='ai_pro',
    port=3306,
    use_unicode=True,
    charset="utf8"
)


@app.route("/")
def home():
    return render_template("/home.html")


@app.route("/cvreport.html")
def cvreport():
    cursor = connection.cursor()
    save_image_path = os.path.join(app.config['UPLOAD_FOLDER'], session['cv'])
    resume_data = ResumeParser(save_image_path).get_extracted_data()
    if resume_data:
        resume_text = pdf_reader(save_image_path)
        insert_data(resume_data['name'], resume_data['email'],resume_data['no_of_pages'], str(resume_data['skills']), session['id'])
    command = "select Name, Email_ID, Page_No, Actual_skills from user_data where stud_id =%s"
    cursor.execute(command, session['id'])
    res = cursor.fetchall()

    ### Resume writing recommendation
    resume_text = pdf_reader(save_image_path)
    resume_score = 0
    
    if 'Objective' or 'Summary' in resume_text:
        a=''
        if 'Objective' in resume_text:
            resume_score = resume_score+10
            a = '[+] Awesome! You have added Objective'
        elif 'Summary' in resume_text:
            resume_score = resume_score+10
            a = '[+] Awesome! You have added Summary'
        else:
            a = '[-] According to our recommendation please add your career objective or summary, it will give your career intension to the Recruiters.'
        

    if 'Declaration' or 'Career Statement'  in resume_text:
        resume_score = resume_score + 10
        b = '[+] Awesome! You have added Declaration'
    else:
        b ='[-] According to our recommendation please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you'

    if 'Hobbies' or 'Interests' in resume_text:
        resume_score = resume_score + 10
        c = '[+] Awesome! You have added your Hobbies'
    else:
        c = '[-] According to our recommendation please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.'

    if 'Achievements' or 'Milestones' in resume_text:
        resume_score = resume_score + 10
        d = '[+] Awesome! You have added your Achievements'
    else:
        d = '[+] According to our recommendation please add Achievements. It will show that you are capable for the required position.'

    if 'Projects' or 'Project' in resume_text:
        resume_score = resume_score + 25
        e = '[+] Awesome! You have added your Projects'
    else:
        e = '[-] According to our recommendation please add Projects. It will show that you have done work related the required position or not.'

    if 'Internships' or 'Work Experience' or 'Position of responsibility' or 'Career History' in resume_text:
        g=''
        if 'Internships' in resume_text:
            resume_score += 25
            g = '[+] Awesome! You have added your Internships'
        elif 'Work Experience' in resume_text:
            resume_score += 25
            g = '[+] Awesome! You have added your Work Experience'
        elif 'Position of responsibility' in resume_text:
            resume_score += 25
            g = '[+] Awesome! You have added your Position of responsibility'
        elif 'Career History' in resume_text:
            resume_score += 25
            g = '[+] Awesome! You have added your Career History'
        else:
            g = '[-] Highly recommanded for adding any Experience. It is valued by recruiters.' 

    if 'Linkedin' or 'Github' or 'Portfolio' or 'Leetcode' in resume_text:
        resume_score += 10
        k = '[+] Awesome! You have added Social Profile links'
    else:
        k = '[-] Consider adding links to your professional Social Profiles like LinkedIn.'

    score = 0
    for percent_complete in range(resume_score):
            score +=1
            
    m = 'Your Resume Writing Score:' + str(score)
    # print(" Your Resume Writing Score: ", str(score))
    connection.commit()
    cursor.close()
    return render_template("/cvreport.html", data = res, value1=a, value2 =b, value3 = c, value4 =d, value5 =e, value6= g, value7 =k, value9=m)
    
   

@app.route("/reportgeneration")
def reportgeneration():
    cursor = connection.cursor()
    command = "select stud_first_name, stud_last_name, stud_class, science, humanities, commerce, aptitude, total from student_profile where stud_id =%s "
    cursor.execute(command, session['id'])
    res = cursor.fetchall()
    cursor.close()
    return render_template("/reportgeneration.html", data=res)


  
@app.route("/resCompare")
def resCompare():
    uid = session['username']
    cursor = connection.cursor()
    save_image_path = os.path.join(app.config['UPLOAD_FOLDER'], session['cv'])
    resume_data = ResumeParser(save_image_path).get_extracted_data()
    if resume_data:
        resume_text = pdf_reader(save_image_path)
        insert_data(resume_data['name'], resume_data['email'],resume_data['no_of_pages'], str(resume_data['skills']), session['id'])
    command = "select Name, Email_ID, Page_No, Actual_skills from user_data where stud_id =%s"
    cursor.execute(command, session['id'])
    connection.commit()

    print(resume_data["skills"])
    predicted_job = findJobTitle(resume_data["skills"])
    # print(predicted_job)
    command = "select * from company_info where job_title = %s"
    cursor.execute(command, predicted_job)
    res = cursor.fetchall()

    #give code to sort res according ascendingly to decimal value of salary
    sorted_dict = sorted(res, key=lambda x: x[4], reverse=True)

    # print(res)
    score_dict = []
    for i in sorted_dict:
        ret_skills = i[5].split(",")
        # print(ret_skills)
        counter = 0
        for data in resume_data["skills"]:
            
            if data not in ret_skills:
                counter+=1
                # print(Fore.GREEN)
                # print(data)
                # print(Fore.WHITE)
        i = list(i)
        i.append(counter)
        score_dict.append(i)
    
    # print(score_dict)

    sorted_dict1 = sorted(score_dict, key=lambda x: x[-1], reverse=False)
    # print(sorted_dict1)
    
    # print(sorted_dict)
    ### Resume writing recommendation

    cursor = connection.cursor()
    command = "select * from company_info"
    cursor.execute(command)
    res = cursor.fetchall()
    cursor.close()
    return render_template("/resCompare.html",value1=predicted_job, data=sorted_dict1) 


@app.route("/home.html")
def intro():
    return render_template("/home.html")


@app.route("/login.html")
def login():
    return render_template("/login.html")


@app.route('/check_user', methods=['POST']) 
def check_user():
    if request.method == 'POST':
        email = request.form['email']
        user_password = request.form['password']
        cursor = connection.cursor()
        com = "select * from login where u_email='" + email + "'"
        result = cursor.execute(com)
        cursor.close()
        if not result:
            flash("Invalid Login")
            return render_template("/login.html")
        else:
            cursor = connection.cursor()
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            data = cursor.fetchone()[2]
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            utype = cursor.fetchone()[3]
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            uid = cursor.fetchone()[0]
            cursor.close()
            if utype == "Applicant":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "Applicant"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/reportgeneration.html")
                else:
                    flash("Invalid Login")
                gc.collect()
                return redirect("/login.html")
            elif utype == "admin":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "admin"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/adminhome.html")
                else:
                    flash("Invalid Login")
                    gc.collect()
                    return redirect("/login.html")
            elif utype == "b":
                if data == user_password:
                    session['logged_in'] = True
                    session['type'] = "personnel"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/instructorhome.html")
                else:
                    flash("Invalid Login")
                    gc.collect()
                    return redirect('/login.html')

            flash("Error Occured")
            gc.collect()
            return redirect('/login.html')


@app.route('/add_company', methods=['POST'])
def add_company():
    cursor = connection.cursor()
    cmp_name = request.form['frst_name']
    job_title = request.form['job_title']
    job_dsc = request.form['job_dsc']
    salary = request.form['salary']
    skills=request.form['skills']
    cmd = "insert into company_info(company_name, job_title, job_desc, job_salary,job_skills) VALUES (%s, %s, %s, %s,%s) "
    cursor.execute(cmd, (cmp_name, job_title, job_dsc, salary,skills))
    connection.commit()
    return redirect('/instructorhome.html')
    

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template("/login.html")


@app.route('/logoutprofile', methods=['POST'])  # if not registered
def logoutprofile():
    id = session['username']
    cursor = connection.cursor()
    cmd = "delete from login where u_email = '" + id + "' "
    cursor.execute(cmd)
    connection.commit()
    session.pop('user', None)
    cursor.close()
    flash("Sorry registration unsuccessful")
    return render_template("/signup.html")


@app.route("/signup.html")
def index():
    return render_template("/signup.html")


@app.route("/instructorhome.html")
def instructorhome():
    return render_template("/instructorhome.html")


@app.route('/post_user', methods=['POST'])  # sign up function
def post_user():
    if request.method == 'POST':
        cursor = connection.cursor()
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])
        utype = "Applicant"
        x = cursor.execute("select * from login where u_email='" + email + "'")
        if int(x) > 0:
            flash("That username is already taken, please choose another")
            return redirect("/signup.html")
        else:
            if request.form['password'] == request.form['con_password']:
                sql = """ALTER TABLE login AUTO_INCREMENT = 100"""
                cursor.execute(sql)
                com = """insert into login (u_email,password,user_type) values (%s, %s, %s)"""
                cursor.execute(com, (email, password, utype))
                query = "select * from login where u_email='" + email + "'"
                cursor.execute(query)
                data = cursor.fetchone()[0]
                connection.commit()
                session['logged_in'] = True
                session['username'] = email
                session['id'] = data
                cursor.close()
                return render_template("/profile.html")
            else:
                flash("Password not same")
                return redirect("/signup.html")


@app.route("/profile.html")
def profile():
    return render_template('/profile.html')


@app.route('/post_profile', methods=['POST'])  # profile completion function
def post_profile():
    id = session['id']
    if request.method == 'POST':
        cursor = connection.cursor()
        firstnme = request.form['frst_name']
        lst_nme = request.form['lst_name']
        dob = request.form['dob']
        gender = request.form['optradio']
        cntno = request.form['phn_no']
        email = session['username']
        institute = request.form['inst']
        clas = request.form['clasnme']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pin = request.form['pin_code'] 
        cv = request.files['cv']
        
        if cv and allowed_file(cv.filename):
            filename = secure_filename(cv.filename)
            cv.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['cv'] = secure_filename(cv.filename)
            
            com = "insert into student_profile (stud_id,stud_first_name,stud_last_name,stud_dob,stud_gender,cnt_number,stud_email,stud_inst,stud_class,stud_house,stud_city,stud_country, pin_code, cv_path)	values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(com,
                        (session['id'], firstnme, lst_nme, dob, gender, cntno, email, institute, clas, house, city, country, pin, session['cv']))
            connection.commit()
        flash("Registration successful!!")
        return redirect("/viewprofile")
    connection.close()
    

@app.route("/studeditprofile/<id>")  # student profile edit
def studeditprofile(id):
    cursor = connection.cursor()
    command = "select * from student_profile where stud_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/studeditprofile.html", data=res)



@app.route("/viewprofile")  # student profile view
def view_user():
    uid = session['username']
    cursor = connection.cursor()
    command = "select * from student_profile where stud_email= '" + uid + "'"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/viewprofile.html", data=res)


@app.route("/instructorprofileview")  # instructor profile view
def instructorprofileview():
    uid = session['username']
    cursor = connection.cursor()
    command = "select * from instructor_details"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/instructorprofileview.html", data=res)



@app.route("/instmanagestudent")  # instructor student profile view
def instmanagestudent():
    uid = session['username']
    cursor = connection.cursor()
    command = "select * from student_profile"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/instmanagestudent.html", data=res)



def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def insert_data(name,email,no_of_pages,skills, stud_id):
    cursor = connection.cursor()
    DB_table_name = 'user_data'
    insert_sql = "REPLACE INTO " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, no_of_pages, skills,stud_id)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


@app.route("/update_profile", methods=['post'])  # student profile update
def update_user():
    if request.method == 'POST':
        uid = session['username']
        frst_name = request.form['frst_name']
        lst_name = request.form['lst_name']
        phone_no = request.form['phn_no']
        institute = request.form['inst']
        clasnme = request.form['clasnme']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pincode = request.form['pin_code']
        cv = request.files['cv']
        if cv and allowed_file(cv.filename):
            filename = secure_filename(cv.filename)
            cv.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['cv'] = secure_filename(cv.filename)
        qry = "update student_profile set stud_first_name='" + frst_name + "',stud_last_name='" + lst_name + "',cnt_number='" + phone_no + "', stud_inst='" + institute + "', stud_class='" + clasnme + "',stud_house='" + house + "',stud_city='" + city + "',stud_country='" + country + "', pin_code='" + pincode + "', cv_path='" + session['cv'] + "' where stud_email='" + uid + "'"
        cursor = connection.cursor()
        cursor.execute(qry)
        connection.commit()
        flash("update successful")
        return render_template("/viewprofile.html")
    else:
        return render_template("/viewprofile.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def filfunction(file, fname):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        oldext = os.path.splitext(filename)[1]
        os.rename(UPLOAD_FOLDER + filename, UPLOAD_FOLDER + fname + oldext)
        return oldext


def learning_user():
    data = open('data/corpus').read()
    labels, texts = [], []
    for i, line in enumerate(data.split("\n")):
        content = line.split()
        labels.append(content[0])
        texts.append(" ".join(content[1:]))

    # create a dataframe using texts and lables
    trainDF = pandas.DataFrame()
    trainDF['text'] = texts
    trainDF['label'] = labels
    # split the dataset into training and validation datasets
    train_x, valid_x, train_y, valid_y = train_test_split(trainDF['text'], trainDF['label'])

    # label encode the target variable
    encoder = sklearn.preprocessing.LabelEncoder()
    train_y = encoder.fit_transform(train_y)
    valid_y = encoder.fit_transform(valid_y)

    # create a count vectorizer object
    count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}')
    count_vect.fit(trainDF['text'])

    # transform the training and validation data using count vectorizer object
    xtrain_count = count_vect.transform(train_x)
    xvalid_count = count_vect.transform(valid_x)
    nb = MultinomialNB()
    nb.fit(xtrain_count, train_y)
    y_pred = nb.predict(xvalid_count)
    accuracy = (accuracy_score(valid_y, y_pred))
    print ("accuracy =", accuracy)
    print(classification_report(valid_y, y_pred))

    trainDF['char_count'] = trainDF['text'].apply(len)
    addfile(trainDF['char_count'].head())
    trainDF['word_count'] = trainDF['text'].apply(lambda x: len(x.split()))
    addfile(trainDF['word_count'].head())
    trainDF['word_density'] = trainDF['char_count'] / (trainDF['word_count'] + 1)
    addfile(trainDF['word_density'].head())
    trainDF['punctuation_count'] = trainDF['text'].apply(
        lambda x: len("".join(_ for _ in x if _ in string.punctuation)))
    addfile(trainDF['punctuation_count'].head())
    trainDF['title_word_count'] = trainDF['text'].apply(lambda x: len([wrd for wrd in x.split() if wrd.istitle()]))
    addfile(trainDF['title_word_count'].head())
    trainDF['upper_case_word_count'] = trainDF['text'].apply(lambda x: len([wrd for wrd in x.split() if wrd.isupper()]))
    addfile(trainDF['upper_case_word_count'].head())

    return 0


def addfile(x):
    f = open('outcome.txt', 'a')
    f.write(str(x) + '\n')
    f.close()

if __name__ == "__main__":
    app.run()
