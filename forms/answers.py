from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField


class AnswersForm(FlaskForm):
    content = TextAreaField("Содержание")
    submit = SubmitField('Ответить')
