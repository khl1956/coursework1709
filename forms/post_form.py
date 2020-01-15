from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, TextAreaField
from wtforms import validators


class PostForm(Form):
    post_id = HiddenField()

    post_title = StringField("Title: ", [
        validators.DataRequired("Please enter your title."),
        validators.Length(2, 100, "title should be from 2 to 100 symbols")
    ])

    post_text = TextAreaField("Text: ", [
        validators.DataRequired("Please enter your text."),
        validators.Length(10, 1000, "Text should be from 10 to 1000 symbols")
    ])

    submit = SubmitField("Save")
