from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, StringField, PasswordField, BooleanField, SubmitField, validators

class ConfigForm(FlaskForm):
    cpu_grow = IntegerField('cpu_grow', [validators.NumberRange(min=0, max=10, message="Integer with 3 digits")], render_kw={'readonly': ''})
    cpu_shrink = IntegerField('cpu_shrink', [validators.NumberRange(min=0, max=10, message="Integer with 3 digits")], render_kw={'readonly': ''})
    ratio_expand = FloatField('ratio_expand', [validators.NumberRange(min=0, max=10, message="Float with 3 digits")], render_kw={'readonly': ''})
    ratio_shrink = FloatField('ratio_shrink', [validators.NumberRange(min=0, max=10, message="Float with 3 digits")], render_kw={'readonly': ''})
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')