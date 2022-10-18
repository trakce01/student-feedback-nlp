from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError
from models import User
from textblob import TextBlob


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("login")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("create")

    def validate_email(self, email):
        read_email = email.data
        email_domain = str()
        try:
            email_domain = read_email.split("@")[1]
        except Exception as e:
            print(str(e))
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("a user with that email already exists!")

        if email_domain == "student.mes.ac.in":
            pass
        elif email_domain == "mes.ac.in":
            pass
        else:
            raise ValidationError("invalid email domain")


class FacultyForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    subject = StringField("subject", validators=[DataRequired()])
    semester = SelectField(
        "Choose Semester",
        choices=[
            ("SEM I", "SEM 1"),
            ("SEM II", "SEM 2"),
            ("SEM III", "SEM 3"),
            ("SEM IV", "SEM 4"),
            ("SEM V", "SEM 5"),
            ("SEM VI", "SEM 6"),
            ("SEM VII", "SEM 7"),
            ("SEM VIII", "SEM 8"),
        ],
        validators=[DataRequired()],
    )
    branch = SelectField(
        "Choose Branch",
        choices=[
            ("Comps", "COMPS"),
            ("Mech", "MECH"),
            ("It", "IT"),
            ("Auto", "AUTO"),
            ("extc", "EXTC"),
        ],
    )
    submit = SubmitField("get started")


class StudentForm(FlaskForm):
    branch = SelectField(
        "Choose Branch",
        choices=[
            ("Comps", "COMPS"),
            ("Mech", "MECH"),
            ("It", "IT"),
            ("Auto", "AUTO"),
            ("extc", "EXTC"),
        ],
    )
    submit = SubmitField("get started")


class FeedbackForm(FlaskForm):
    punctuality = TextAreaField(validators=[DataRequired()])
    teaching_style = TextAreaField(validators=[DataRequired()])
    portion_completion = TextAreaField(validators=[DataRequired()])
    doubt_solving = TextAreaField(validators=[DataRequired()])
    teacher_preparedness = TextAreaField(validators=[DataRequired()])
    additional_comments = TextAreaField(validators=[DataRequired()])
    submit = SubmitField("Submit")

    def sentiment_analysis(self, data):
        sentiment = []
        for i in data:
            blob = TextBlob(i)
            for sent in blob.sentences:
                sentiment.append(sent.sentiment.polarity)
            return sum(sentiment) / len(sentiment)


class SelectionForm(FlaskForm):
    semester = SelectField(
        "Choose Semester",
        choices=[
            ("SEM I", "SEM 1"),
            ("SEM II", "SEM 2"),
            ("SEM III", "SEM 3"),
            ("SEM IV", "SEM 4"),
            ("SEM V", "SEM 5"),
            ("SEM VI", "SEM 6"),
            ("SEM VII", "SEM 7"),
            ("SEM VIII", "SEM 8"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")
