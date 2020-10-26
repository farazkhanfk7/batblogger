from flask import render_template, flash,redirect,url_for, request
from blog import app,db,bcrypt
from blog.forms import RegistrationForm,LoginForm
from blog.models import User,Post
from flask_login import login_user,current_user,logout_user,login_required


posts = [
    {
        'author':'Faraz Khan',
        'title': 'Blog Post one',
        'content': 'First post Content',
        'date_posted':'April 20,2020'
    },
    {
        'author':'Abdullah Tahir',
        'title': 'Blog Post two ',
        'content': 'Second post Content',
        'date_posted':'May 10,2020'
    }
]

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/blog')
def blog():
    return render_template('home.html',posts=posts)

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You are able to Login.','success')
        return redirect(url_for('login'))
    return render_template('auth/register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            flash('You have been logged in.','success')
            next_page = request.args.get('next')
            return redirect(url_for('account')) if next_page else redirect(url_for('blog'))
        else:
            flash('Login Unsucessful. Please check email and password','danger')
    return render_template('auth/login.html',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html')
