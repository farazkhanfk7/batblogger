import os
from flask import Blueprint
from flask import render_template, flash,redirect,url_for, request,current_app
from flask_login import login_user,current_user,logout_user,login_required
from blog.models import User
from blog import db,bcrypt,mail
from blog.auth.utils import save_picture,send_reset_email
from blog.auth.forms import LoginForm,RegistrationForm,UpdateAccountForm,RequestResetForm,ResetPasswordForm

auth = Blueprint('auth',__name__)

@auth.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You are able to Login.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            # login_user takes user and remember as arg
            login_user(user,remember=form.remember.data)
            flash('You have been logged in.','success')
            next_page = request.args.get('next')
            return redirect(url_for('auth.account')) if next_page else redirect(url_for('main.blog'))
        else:
            flash('Login Unsucessful. Please check email and password','danger')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@auth.route("/account",methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            '''
            The code below checks if the current user pic is available and it's not the default pic
            If yes, then it's deletes the previous image to save space
            '''
            if current_user.image_file and current_user.image_file != 'default.jpg':
                current_picture_path = os.path.join(current_app.root_path,'static/profilepics',current_user.image_file)
                os.remove(current_picture_path)
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        '''
        Assigning values to sqlalchemy database
        '''
        flash('Your account has been updated.','success')
        return redirect(url_for('auth.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    # image_file = url_for('static',filename='profilepics/'+current_user.image_file) in case you want, tho did this already in template
    return render_template('account.html',form=form)


@auth.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password','info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html',form=form)

@auth.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Invalid token",'danger')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been changed ! You can Login now.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html',form=form)