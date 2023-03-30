from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, CreateNewUser, Login
from flask_gravatar import Gravatar


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

##CONFIGURE TABLES

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class NewUser(UserMixin, db.Model):
    __tablename__ = "new_users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return NewUser.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
@login_required
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = CreateNewUser()
    registering_email = form.email.data
    if form.validate_on_submit():
        if NewUser.query.filter_by(email=registering_email).first():
            flash("You have already signed up with that Email.")
            return redirect(url_for("register"))
        else:
            new_user = NewUser(
                email=form.email.data,      #type:ignore
                username=form.name.data, #type:ignore
                password=generate_password_hash(form.password.data) #type: ignore
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))



@app.route('/login', methods=["GET", "POST"])
def login():
    form = Login()
    login_user_email = form.email.data
    login_user_password = form.password.data
    if form.validate_on_submit():
        user = NewUser.query.filter_by(email=login_user_email).first()
        if user and check_password_hash(user.password, login_user_password):
            login_user(user, force=True)
            return redirect(url_for("contact"))
        else:
            flash("Your Email or Password is Wrong!!!\nPlease Try Again")
            return redirect(url_for("login"))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post, current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact")
@login_required
def contact():
    return render_template("contact.html", current_user=current_user)


@app.route("/new-post")
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data, #type: ignore
            subtitle=form.subtitle.data,    #type: ignore
            body=form.body.data,            #type: ignore
            img_url=form.img_url.data,      #type: ignore
            author=current_user,            #type: ignore
            date=date.today().strftime("%B %d, %Y")     #type: ignore
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, current_user=current_user)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
