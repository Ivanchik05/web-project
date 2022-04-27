from flask import Flask, render_template, redirect, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.questions import Questions
from data.answers import Answers
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.questions import QuestionsForm
from forms.answers import AnswersForm
import sqlite3

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/date.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


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
    answers = db_sess.query(Answers)
    con = sqlite3.connect('db/date.db')
    cur = con.cursor()
    lst = cur.execute('''SELECT question_id FROM answers''').fetchall()
    question_id = list(map(lambda x: x[0], lst))
    return render_template("questions.html", questions=questions, question_id=question_id, answers=answers,
                           title='Вопросы')


@app.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = QuestionsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        question = Questions()
        question.theme = form.theme.data
        question.content = form.content.data
        current_user.questions.append(question)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/all_questions')
    return render_template('add_question.html', title='Добавление вопроса',
                           form=form)


@app.route('/delete_question/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_question(id):
    db_sess = db_session.create_session()
    question = db_sess.query(Questions).filter(Questions.id == id).first()
    answer = db_sess.query(Answers).filter(Answers.question_id == id).first()
    if question and answer:
        db_sess.delete(question)
        db_sess.delete(answer)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/all_questions')


@app.route('/answer/<int:id>', methods=['GET', 'POST'])
@login_required
def answer(id):
    form = AnswersForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        answers = Answers()
        answers.question_id = id
        answers.content = form.content.data
        current_user.answers.append(answers)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/all_questions')
    con = sqlite3.connect('db/date.db')
    cur = con.cursor()
    lst = cur.execute('''SELECT theme FROM questions WHERE id = ?''', (id,)).fetchall()
    question = list(map(lambda x: x[0], lst))[0]
    return render_template('answer.html', title='Ответ',
                           form=form, question=question)


@app.route('/')
@app.route('/Главная.html')
def index():
    return render_template('Главная.html', title='Главная')


@app.route('/Контакты.html')
def contacts():
    return render_template('Контакты.html', title='Контакты')


@app.route('/novo_kazan')
def novo_kazan():
    return render_template('articles/novo_kazan.html', title='Ново-Казанский собор')


@app.route('/museum')
def museum():
    return render_template('articles/museum.html', title='Лебедянский краеведческий музей')


@app.route('/zamyatin_house')
def zamyatin_house():
    return render_template('articles/zamyatin_house.html', title='Дом-музей Е.И.Замятина')


@app.route('/monastery')
def monastery():
    return render_template('articles/monastery.html', title='Свято-Троицкий монастырь')


@app.route('/igumnov_house')
def river_mecha():
    return render_template('articles/igumnov_house.html', title='Дом Игумновых')


@app.route('/county_school')
def county_school():
    return render_template('articles/county_school.html', title='Уездное училище')


@app.route('/bridge')
def bridge():
    return render_template('articles/bridge.html', title='Казённый мост')


@app.route('/tyapkina_mountain')
def tyapkina_mountain():
    return render_template('articles/tyapkina_mountain.html', title='Тяпкина гора')


if __name__ == '__main__':
    main()
