from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class QuestionsForm(FlaskForm):
    theme = StringField('Тема', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    submit = SubmitField('Добавить')
