from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, URLField
from wtforms.validators import DataRequired, Email, Length, URL, Optional


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email(message="Must be email format abc@website.com")])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL', validators=[Optional(), URL(message="Use proper URL https://www.blahblah.com/heyo")])
    header_image_url = StringField("(Optional) Header Image URL", validators=[Optional(), URL(message="User proper URL http://www.abc.com/hellno")])
class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Must be email format abc@website.com")])
    image_url = URLField('Image URL', validators=[Optional(), URL(message="Use proper URL https://www.blahblah.com/heyo")])
    header_image_url = URLField('Header Image URL', validators=[Optional(), URL(message="Use proper URL https://www.blahblah.com/heyo")])
    bio = StringField('Bio', validators=[DataRequired(), Length(min=10, message="Add more than 10 characters to your bio")])
    


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
