from flask import Blueprint
from flask import render_template,redirect,url_for, request
from blog.models import User,Post

main = Blueprint('main',__name__)

@main.route('/')
def home():
    return render_template('welcome.html')

@main.route('/blog')
def blog():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=4)
    return render_template('home.html',posts=posts)

@main.route('/about')
def about():
    return "<h3>Contact : farazkhan138@gmail.com<h3>"

@main.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    return render_template('user_profile.html',user=user,posts=posts)