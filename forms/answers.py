from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField
from wtforms import SubmitField


class AnswersForm(FlaskForm):
    question_id = IntegerField("Номер вопроса")
    content = TextAreaField("Содержание")
    submit = SubmitField('Ответить')
