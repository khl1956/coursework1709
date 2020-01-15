from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms import validators


class HashtagForm(Form):
    hashtag_name = StringField("Name: ", [
        validators.DataRequired("Please enter name."),
        validators.Length(2, 100, "Name should be from 2 to 100 symbols")
    ])

    submit = SubmitField("Save")
