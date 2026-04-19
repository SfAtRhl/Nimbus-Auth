from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import get_user_by_email
from utils import validate_password_policy

class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )
    submit = SubmitField("Create Account")

    def validate_email(self, field):
        if get_user_by_email(field.data.lower()):
            raise ValidationError("An account with this email already exists")

    def validate_password(self, field):
        errors = validate_password_policy(field.data)
        if errors:
            raise ValidationError(" ".join(errors))

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")

class ForgotPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )
    submit = SubmitField("Reset Password")

    def validate_password(self, field):
        errors = validate_password_policy(field.data)
        if errors:
            raise ValidationError(" ".join(errors))
