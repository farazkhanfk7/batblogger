import os
import secrets
from PIL import Image
from flask import render_template, flash,redirect,url_for, request,abort
from blog import app,db,bcrypt,mail
from blog.forms import RegistrationForm,LoginForm,UpdateAccountForm, BlogForm, RequestResetForm, ResetPasswordForm
from blog.models import User,Post
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/blog')
def blog():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=4)
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
            # login_user takes user and remember as arg
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



#function to save picture
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    # giving a random filename to every image
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profilepics',picture_fn)
    output_size = (200,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account",methods=['GET','POST'])
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
                current_picture_path = os.path.join(app.root_path,'static/profilepics',current_user.image_file)
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    # image_file = url_for('static',filename='profilepics/'+current_user.image_file) in case you want, tho did this already in template
    return render_template('account.html',form=form)


@app.route('/blog/new',methods=['GET','POST'])
@login_required
def new_post():
    form = BlogForm()
    if form.validate_on_submit():
        # using author here (check backref in models.py)
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created !','success')
        return redirect(url_for('blog'))
    return render_template('create_post.html',form=form)


@app.route("/blog/<int:id>")
def post(id):
    # post = Post.query.get(id) or
    post = Post.query.get_or_404(id)
    return render_template('readblog.html',post=post)

@app.route("/blog/<int:id>/update",methods=['GET','POST'])
@login_required
def update_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)

    form = BlogForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your blog has been updated",'success')
        return redirect(url_for('post',id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('update_post.html',form=form) 


@app.route("/blog/<int:id>/delete",methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your blog has been deleted",'success')
    return redirect(url_for('blog'))

@app.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    return render_template('user_profile.html',user=user,posts=posts)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender='noreply@demo.com',recipients=[user.email])
    msg.body = f'''To reset your password visit following link: 
{url_for('reset_token',token=token,_external=True)}
If you have not made any request simply ignore this email.
'''
    mail.send(msg)

@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('auth/reset_request.html',form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Invalid token",'danger')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been changed ! You can Login now.','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',form=form)

