from flask import render_template, url_for, request, flash
from forms import ContactForm
from flask_mail import Message, Mail
from app import app, db, Userdreams

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

#http://127.0.0.1:55072/browser/ for postgres admin manager gui
@app.route('/db_form', methods=['GET', 'POST'])
def db_form():
    if request.method == 'POST':
        user_name = request.form['user_name']
        dream = request.form['dream']
        if user_name == '' or dream == '':
            return render_template('db_form.html', message='Make sure you fill out everything on the Database Form!')
        print(user_name, dream)
        if db.session.query(Userdreams).filter(Userdreams.user_name == user_name).count() == 0:
            data = Userdreams(user_name, dream)
            db.session.add(data)
            db.session.commit()
        else:
            return render_template('db_form.html', message='Only one dream per person!')
    return render_template('db_form.html', title='Database Form')

@app.route('/ssm', methods=['GET', 'POST'])
def ssm():
    return render_template('ssm.html', title='Socail Method')

@app.route('/')
@app.route('/posts')
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