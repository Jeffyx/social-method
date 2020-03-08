from flask import render_template, url_for, request, flash, redirect
from forms import ContactForm, LoginForm, RegistrationForm
from flask_mail import Message, Mail
from app import app, db, Userdreams, engine, User
import pandas as pd 
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

mail = Mail()
app.secret_key = 'development key'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465 #or port 587
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'waronbaddrivers@gmail.com'
app.config["MAIL_PASSWORD"] = 'war!1234'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_ASCII_ATTACHMENTS'] = True

mail.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('posts'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('posts')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('posts'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('posts'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password_hash=form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#http://127.0.0.1:55072/browser/ for postgres admin manager gui
@app.route('/db_form', methods=['GET', 'POST'])
def db_form():
    userdreams = db.session.query(Userdreams).all()
    print(userdreams)
    if request.method == 'POST':
        user_name = request.form['user_name']
        dream = request.form['dream']
        if user_name == '' or dream == '':
            return render_template('db_form.html', message='Make sure you fill out everything on the Database Form!', userdreams=userdreams)
        print(user_name, dream)
        if db.session.query(Userdreams).filter(Userdreams.user_name == user_name).count() == 0:
            data = Userdreams(user_name, dream)
            db.session.add(data)
            db.session.commit()
        else:
            return render_template('db_form.html', message='Only one dream per person!', userdreams=userdreams)
    return render_template('db_form.html', title='Database Form', userdreams=userdreams)

@app.route('/')
@app.route('/ssm', methods=['GET', 'POST'])
def ssm():
    #userdreams = db.session.query(Userdreams.user_name).all()
    #print(userdreams)

    df = pd.read_sql("SELECT * FROM public.userdreams;", engine)
    userdreams = df['user_name'].tolist()
    user_len = len(userdreams)
    #dreams_list = []
    #for u in userdreams:
    #    dreams_list.append(u)

    return render_template('ssm.html', title='Socail Method', userdreams=userdreams, user_len=user_len)

@app.route('/posts')
@login_required
def posts():
    return render_template('posts.html', title='Home')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()

  #if form.validate_on_submit():
  #    filename = secure_filename(form.file_.file.filename)
  #    file_path = os.path.join(app.config['static'], filename)
  #    form.fileName.file.save(file_path)

  if request.method == 'POST':
      if form.validate() == False:
          flash("All fields are required.")
          return render_template('contact.html', form=form)
      else:
          msg = Message(form.subject.data, sender='waronbaddrivers@gmail.com', recipients=['your_email@example.com'])
          msg.body = """
          From: %s <%s>
          %s
          """ % (form.name.data, form.email.data, form.message.data)
          #with app.open_resource(filename) as fp:
          msg.attach(
            form.file_.data.filename,
            'application/octect-stream',
            form.file_.data.read())
          #msg.attach(
          #  form.file_.file.filename,
          #  "image/png",
          #  fp.read())
          mail.send(msg)
          return render_template('contact.html', success=True)
 
  elif request.method == 'GET':
    return render_template('contact.html', form=form)

@app.route('/article_1')
def article_1():
    return render_template('article_1.html', title='Home')

if __name__ == '__main__':
    app.run(debug=False)
    app.run()