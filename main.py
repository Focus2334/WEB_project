from flask import Flask, render_template, redirect
from data import db_session
from data.exhibits import Exhibit
from data.comments import Comment
from forms.user import RegisterForm
from data.users import User
from flask_login import LoginManager
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login_form import LoginForm
from forms.comment_form import CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/exhibits.db")
login_manager = LoginManager()
login_manager.init_app(app)
db_sess = db_session.create_session()
# news = Exhibit(title="Ваза", content="описание", image="vaza.jpg")
# db_sess.add(news)
# db_sess.commit()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    @app.route("/")
    def index():
        db_sess = db_session.create_session()
        ex = db_sess.query(Exhibit)
        return render_template("index.html", exhibits=ex)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/exhibit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def exhibit(id):
        form = CommentForm()
        db_sess = db_session.create_session()
        ex = db_sess.query(Exhibit).filter(Exhibit.id == id)
        comments = db_sess.query(Comment).filter(Comment.exhibit_id == id)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            comnt = Comment()
            comnt.content = form.text.data
            comnt.exhibit_id = id
            current_user.comments.append(comnt)
            db_sess.merge(current_user)
            db_sess.commit()
        print(current_user.name)
        return render_template("exhibit.html", exhibit=ex, form=form, comments=comments)

    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
