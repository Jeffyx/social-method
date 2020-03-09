from flask import render_template, url_for, request, flash, redirect
from forms import ContactForm, LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_mail import Message, Mail
from app import app, db, Userdreams, engine, User, Observation
import pandas as pd 
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    #User.query.filter_by(username=username)
    #posts = current_user.posts.order_by(Observation.timestamp.desc()).paginate(page, 3, False)
    posts = Observation.query.filter_by(user_id=current_user.id).order_by(Observation.timestamp.desc()).paginate(page, 3, False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('posts'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            message = 'Invalid username or password'
            flash(message)
            return render_template('login.html', title='Sign In', form=form, message=message)
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
        message = 'Congratulations, you are now a registered user!'
        flash(message)
        #return redirect(url_for('login'))
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

@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    observation = db.session.query(Observation).all()
    form = PostForm()
    if form.validate_on_submit():
        post = Observation(body=form.post.data, user_id=current_user.id, timestamp=datetime.utcnow())
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('posts'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, 3, False)
    next_url = url_for('posts', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('posts', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('posts.html', title='Home', observation=observation, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Observation.query.order_by(Observation.timestamp.desc()).paginate(page, 3, False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('posts.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)

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

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect('/edit_profile')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('posts'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('posts'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=False)
    app.run()