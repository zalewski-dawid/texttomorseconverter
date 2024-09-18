from flask_wtf import FlaskForm
from wtforms import SubmitField,TextAreaField
from wtforms.validators import DataRequired, Regexp


class TextForm(FlaskForm):
    text = TextAreaField('TEXT', validators=[DataRequired(),
                                             Regexp(
                                                 r'^[a-zA-Z0-9,.?/\-() ]+$',
                                                 message="Only allowed characters: a-z, A-Z, 0-9, , . ? / - ( ) and spaces."
                                             )

                                             ])
    submit=SubmitField('Convert')

