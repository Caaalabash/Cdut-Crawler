from wtforms import Form, StringField,validators

class SubscriptionForm(Form):
    user = StringField('Username', [ validators.DataRequired(),validators.Length(min=10, max=12)])
    email = StringField('Email', [ validators.DataRequired(),validators.Email()])
    pwd = StringField('Password', [ validators.DataRequired(),validators.Length(min=6, max=30)])
    check =StringField('Check', [ validators.DataRequired(),validators.Length(min=4, max=4)])

class UnsubscriptionForm(Form):
  user = StringField('Username', [validators.DataRequired(), validators.Length(min=10, max=12)])


class ChangeEmailForm(Form):
  user = StringField('Username', [validators.DataRequired(), validators.Length(min=10, max=12)])
  email = StringField('Email', [validators.DataRequired(), validators.Email()])
