from flask import Blueprint
from flask import render_template, flash,redirect,url_for, request,abort
from blog.models import Post
from flask_login import current_user,login_required
from blog import db
from blog.posts.forms import BlogForm

posts = Blueprint('posts',__name__)

@posts.route('/blog/new',methods=['GET','POST'])
@login_required
def new_post():
    form = BlogForm()
    if form.validate_on_submit():
        # using author here (check backref in models.py)
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created !','success')
        return redirect(url_for('main.blog'))
    return render_template('create_post.html',form=form)


@posts.route("/blog/<int:id>")
def post(id):
    # post = Post.query.get(id) or
    post = Post.query.get_or_404(id)
    return render_template('readblog.html',post=post)

@posts.route("/blog/<int:id>/update",methods=['GET','POST'])
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
        return redirect(url_for('posts.post',id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('update_post.html',form=form) 


@posts.route("/blog/<int:id>/delete",methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your blog has been deleted",'success')
    return redirect(url_for('main.blog'))