"""A intenção do código é aprimorar o site do blog para que possa ter usuários. O site já veio funcionando,
detalhe que quando ele já vem um número de host, não funciona, o código app.run abaixo que deixa o flask gerar
o endereço é o que funciona. Como o blog é basicamente uma continuação do que foi feito nas aulas anteriores,
vou comentar apenas as novidades.
abaixo, as bibliotecas, flask, para lidar com internet no Python, com o render template para lidar com o html,
redirect e url for para redirecionar a rota, flash para mostrar mensagens, bootstrap e ck editor para templates
prontas, datetime para lidar com data e hora, werkzeug.security para lidar com password e seu hashing,
alchemy pra lidar com banco de dados no formato sql, o relationship é para lidar com a relação chave valor
no banco de dados,flask-login para lidar com o login do usuário, o forms
é a outra aba de código python e estão sendo importadas duas classes lá criadas, o gravatar é usado
 para imagens de avatar para comentários de blogs, o wraps é a função para usar o Python
decorator, porque ele vai embrulhar (wraps) outra função, já o abort é um método para mostrar uma página com uma
mensagem de erro de acordo com o código de erro http."""

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm
from flask_gravatar import Gravatar
from functools import wraps
from flask import abort


"""o código de inicialização de cada biblioteca, inclusive o login_manager, para lidar com os critérios
de login dos usuários"""
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)


"""You will need to provide a user_loader callback. This callback is used to reload the user object from 
the user ID stored in the session. It should take the str ID of a user, and return the corresponding user
object. Traduzindo, aqui o sistema carrega o ID do usuário da sessão que está fazendo o login...aparentemente"""
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

"""abaixo, o código para a criação da tabela de usuário no db. A novidade aqui é a criação do relationship, conceito
do SQL Alchemy para estabelecer a relação de uma chave com vários valores ou o contrário. Nesse caso, o back_populates
faz com que a lista de postagens seja relacionada com a propriedade author no DB"""
# Create the User Table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")

    # *******Add parent relationship*******#
    # "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")

"""abaixo, a criação da tabela de cada post para o DB. A novidade é a criação da Foreign Key para que outras
pessoas possam usar o site e seja relacionado a elas os próprios posts"""
##CONFIGURE TABLES

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # ***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="parent_post")

"""aqui o código para criar o espaço para comentários no DB, também usando o conceito de relationship
para relacionar o comentário ao author"""


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    # ***************Child Relationship*************#
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


db.create_all()

"""abaixo foi criada a função decorator para que somente o administrador tenha acesso a páginas através do hard coding
ou seja, caso ele digite o endereço http, o usuário só pode acessar essas páginas através dos cliques nos botões.
A função abort é uma função do flask e serve para trazer uma página em branco com uma mensagem de erro"""
#Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

#Everytime you call render_template(), you pass the current_user over to the template.
#current_user.is_authenticated will be True if they are logged in/authenticated after registering.
#You can check for this is header.html. Portanto, foi passado o current user para todas as rotas,
#para quando o ele estiver logado o header.html lide com o código JINJA lá passado

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user)

"""abaixo o código para registrar novos usuários, é estabelecida uma função que será acionada quando for
clicado o botão register na home page, quando o formulário for preenchido (submit), primeiro, será checado
 se o usuário já existe, se existir, ele é redirecionado para a página de login, se não, o método hash
  será acionado para transformar a senha e um novo usuário, da classe User será adicionado e o caminha será redirecionado
a home. As duas linhas do login-user voltam o usuário para a home page quando o usuário estiver devidamente logado
com o Flask-Login"""


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)
"""abaixo, a rota para o login do usuário. 
Reparar na sintaxe, primeiro determinou que o user é o primeiro a ser encontrado por filtragem através do e-mail.
Assim, se não for usuário aparece uma mensagem (flash) e é redirecionado para a mesma rota de login, a mesma coisa 
se a senha não bater, e, por fim, se tudo bater, retorna para a home"""


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form, current_user=current_user)

"""aqui é a rota para o logout com a função lougout_user, própria do Flask-login"""
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

"""aqui é rota para ler os posts e há uma sessão de comentários, mas o código garante que somente
  usuários autenticados poderão deixar comentários"""
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template("post.html", post=requested_post, form=form, current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)

"""aqui a rota para lidar com novos posts, marcada com um decorator para que só o administrador tenha acesso, pois
 mesmo sem ver o botão, um usuário que não fosse o administrador, poderia acessá-lo digitando o endereço, a mesma
 coisa para as outras rotas que o usaram o decorator @admin_only"""
@app.route("/new-post", methods=["GET", "POST"])
#Mark with decorator
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)



@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == '__main__':
    app.run(debug=True)
