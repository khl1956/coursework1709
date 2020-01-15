from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField
from wtforms import validators


class PersonForm(Form):
    id = HiddenField()

    username = StringField("Login: ", [
        validators.DataRequired("Please enter your login."),
        validators.Length(3, 20, "Login should be from 3 to 20 symbols")
    ])

    password = PasswordField("Password: ", [
        validators.DataRequired("Please enter your password."),
        validators.Length(8, 20, "Password should be from 8 to 20 symbols")
    ])

    name = StringField("Name: ", [
        validators.DataRequired("Please enter your name."),
        validators.Length(3, 20, "Name should be from 3 to 20 symbols")
    ])

    surname = StringField("Surname: ", [
        validators.DataRequired("Please enter your surname."),
        validators.Length(3, 20, "Surname should be from 3 to 20 symbols")
    ])

    email = StringField("Email: ", [
        validators.DataRequired("Please enter your email."),
        validators.Email("Wrong email format")
    ])

    submit = SubmitField("Save")
