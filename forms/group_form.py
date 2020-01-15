from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField
from wtforms import validators


class GroupForm(Form):
    group_id = HiddenField()

    group_name = StringField("Name: ", [
        validators.DataRequired("Please enter your name."),
        validators.Length(5, 200, "Name should be from 5 to 20 symbols")
    ])

    group_description = StringField("Description: ", [
        validators.DataRequired("Please enter your description."),
        validators.Length(10, 500, "Description should be from 10 to 20 symbols")
    ])

    submit = SubmitField("Save")
