"""aqui foi criado um segundo arquivo de py, acho que para dividir melhor o código, já que aqui
está a classe para criar um post no blog"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

"""a classe abaixo serve para registrar novos usuários e vai ser exportada para o main.py. Reparar 
que estamos usando o WTForm ao invés do HTML Forms o que muda a sintaxe"""
##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

"""a classe abaixo é para novo usuários"""

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")

"""a classe abaixo é para criar o formulário de login, usando o Flask-Login"""
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")

"""abaixo um código para criar uma sessão de comentário na rota post.html"""
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
