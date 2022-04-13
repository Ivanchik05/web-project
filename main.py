from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.questions import Questions
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.questions import QuestionsForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/date.db")
    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/all_questions")
def forum():
    db_sess = db_session.create_session()
    questions = db_sess.query(Questions)
    return render_template("questions.html", questions=questions)


@app.route('/questions', methods=['GET', 'POST'])
@login_required
def add_news():
    form = QuestionsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        question = Questions()
        question.theme = form.theme.data
        question.content = form.content.data
        current_user.questions.append(question)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_question.html', title='Добавление вопроса',
                           form=form)


@app.route('/')
@app.route('/Главная.html')
def index():
    db_sess = db_session.create_session()
    return render_template('Главная.html', title='Главная')


@app.route('/Контакты.html')
def contacts():
    return render_template('Контакты.html', title='Контакты')


if __name__ == '__main__':
    main()
