import os
import secrets
from PIL import Image
from blog import mail
from flask import url_for,current_app
from flask_mail import Message


#function to save picture
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    # giving a random filename to every image
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path,'static/profilepics',picture_fn)
    output_size = (200,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender='noreply@demo.com',recipients=[user.email])
    msg.body = f'''To reset your password visit following link: 
{url_for('auth.reset_token',token=token,_external=True)}
If you have not made any request simply ignore this email.
'''
    mail.send(msg)