
from cgitb import text
import re
from flask import Flask, request, session, redirect, render_template, url_for, flash
from werkzeug.utils import secure_filename
import os
import base64
from flask_mysqldb import MySQL
from face_det import detectFace, check_and_add, check_and_pass
from console import get_list

PATH_NEW = "static/unknown/"

app = Flask(__name__)
app.config['SECRET_KEY'] = "FACE_RECO1234"
app.config['UPLOAD_FOLDER'] = 'static/unknown'
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024*1024
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '4026970Zee'
app.config['MYSQL_DB'] = "data"

mysql = MySQL(app)
fol_path = f""

def get_user_info(nome):

    cur = mysql.connection.cursor()
    cur.execute(f"SELECT namee,email from utenti WHERE user = '{nome}'")
    res = cur.fetchone()
    return res

#setting up the main page
@app.route('/', methods=['GET', 'POST'])
def main_page():
    global fol_path
    if(request.method == 'POST'):
        #check everything if it's correct

        nome = request.form['user']
        surname = request.form['name'] 
        mail = request.form['email']
        profile_img = request.files['filo']
        img_data=request.form['file']

        #check if the user already exists
        cursor = mysql.connection.cursor()
        cursor.execute(f'''
            SELECT user FROM utenti WHERE user = '{nome}'
        ''')
        
        res = cursor.fetchone()
        
        if(res is None):
            
            #add the snapshot
            
            img_data = img_data[23:]
            img_data = img_data.encode("ascii")
            with open(f"static/unknown/{nome}.jpg", "wb") as fh:
                fh.write(base64.decodebytes(img_data))

            #check if the face is detectable or not
            if detectFace(f"static/unknown/{nome}.jpg"):

                #check if the face encodings are different

                if not check_and_add(nome, f"static/unknown/{nome}.jpg"):

                    
                    #ADD TO THE DATABASE
                    cursor.execute(f"INSERT INTO utenti (user,namee,email) VALUES('{nome}','{surname}','{mail}')")
                    cursor.connection.commit()
                    cursor.close()

                    #  add the files

                    profile_img.save(os.path.join('static/profile_images', secure_filename(nome+".jpg")))
                    os.remove(PATH_NEW+nome+".jpg")

                    #create the folder name 

                    os.mkdir(f'static/{nome}')

                    #when the last check has been done craete session

                    #session created
                    session['user'] = nome
                    fol_path = f"static/{session.get('user')}"


                else:
                    os.remove(PATH_NEW+nome+".jpg")
                    flash('The face is already registered')
                    return redirect(url_for('sign_in'))
            else:
                os.remove(PATH_NEW+nome+".jpg")
                flash('the face is not detectable, or there are multiple faces in the photo')
                return redirect(url_for('sign_in'))
        else:
            flash('The username already exists')
            return redirect(url_for('sign_in'))

        return render_template('index.html', details=get_user_info(session['user']), dati=get_list(fol_path), path=fol_path)
        
    elif(session.get('user') is not None):
        return render_template('index.html', details=get_user_info(session['user']), dati=get_list(fol_path), path=fol_path)
    else:
        return redirect(url_for('sign_in'))

    

@app.route('/sign-in')
def sign_in():
    if(session.get('user') is not None):
        return redirect(url_for('main_page'))
    return render_template('sign-in.html')

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        name = request.files['file']
        path = request.form['paths']

        name.save(os.path.join(path, secure_filename(name.filename)))
        return redirect(url_for('main_page'))




@app.route("/files", methods=['GET', 'POST'])
def file_manage():
    global fol_path
    if(request.method == 'POST'):
        texts = request.form['percorso']
        fol_path = texts

    return redirect(url_for('main_page'))

@app.route('/create', methods=['GET','POST'])
def create_dir():
    if(request.method == 'POST'):
        name = request.form['name']
        pat = request.form['paths']
        pat += f'/{name}'

        os.mkdir(pat)
        return redirect(url_for('main_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global fol_path

    if(session.get("user") is not None):
        return redirect(url_for('main_page'))

    if(request.method == 'POST'):
        name2 = request.form['user']
        img = request.form['link']
        img = img[23:]

        #convert it into bytes

        img = img.encode('ascii')
        with open(PATH_NEW+name2+".jpg", "wb") as fh:
            fh.write(base64.decodebytes(img))

        #check if the face is detectable or not

        if detectFace(PATH_NEW+name2+".jpg"):


            #check if the face and name are together
            if check_and_pass(name2, PATH_NEW+name2+".jpg"):
                session['user'] = name2;
                fol_path = f"static/{session.get('user')}"
                os.remove(PATH_NEW+name2+".jpg")
                return redirect(url_for('main_page'))
            else:
                os.remove(PATH_NEW+name2+".jpg")
                flash("Username doesn't match with the face")
                return redirect(url_for('login'))

        else:
            os.remove(PATH_NEW+name2+".jpg")
            flash("face not detectable, or multiple faces in the photo")
            return redirect(url_for('login'))

    return render_template('login.html')



if(__name__ == "__main__"):
    app.run(host='0.0.0.0', port=80,debug=True)