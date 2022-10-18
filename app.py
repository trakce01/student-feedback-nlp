from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user
from flask_login.utils import logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
import secrets

# initialization

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])


# db config

db.init_app(app)

# flask-login
login_manager.init_app(app)
login_manager.login_view = "auth"

# flask-migrate
migrate = Migrate()
migrate.init_app(app, db)

from models import Faculty, Feedback, Student, User
from forms import (
    FacultyForm,
    FeedbackForm,
    LoginForm,
    RegisterForm,
    SelectionForm,
    StudentForm,
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Custom Flask-CLI Commands


@app.cli.command("add-admin")
def add_admin():
    try:
        admin = User(
            role=0,
            email="admin@studentfeedback.in",
            private_id="admin",
            password="studentFeedback",
        )
        db.session.add(admin)
        db.session.commit()
        print("admin created")
    except:
        print("admin already created!")


# auth pages
@app.route("/auth")
def auth():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    return render_template("auth.html")


@app.route("/auth/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    user = User.query.filter_by(email=form.email.data).first()

    if request.method == "POST" and form.validate():
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("login unsuccessful!", category="danger")
    return render_template("login.html", title="login", form=form)


@app.route("/auth/create", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        domain = form.email.data.split("@")[1]
        role = int()

        if domain == "student.mes.ac.in":
            role = 2
        elif domain == "mes.ac.in":
            role = 1

        user = User(
            email=form.email.data,
            private_id=secrets.token_hex(4),
            password=secrets.token_hex(5),
            role=role,
        )

        db.session.add(user)
        db.session.commit()

        new_user = User.query.filter_by(email=form.email.data).first()
        flash(
            f"almost done! please fill in the following details.",
            category="success",
        )

        if role == 1 or role == 2:
            return redirect(url_for("additional", id=new_user.id))
        else:
            return redirect(url_for("login"))
    return render_template("create.html", form=form, title="register")


@app.route("/auth/additional/<id>", methods=["GET", "POST"])
def additional(id):
    user = User.query.filter_by(id=id).first()

    faculty_form = FacultyForm()
    student_form = StudentForm()
    if user.role == 1:
        if faculty_form.validate_on_submit():
            faculty = Faculty(
                name=faculty_form.name.data,
                subject=faculty_form.subject.data,
                semester=faculty_form.semester.data,
                branch=faculty_form.branch.data,
                user=user,
            )
            db.session.add(faculty)
            db.session.commit()
            return redirect(url_for("login"))
    elif user.role == 2:
        if student_form.validate_on_submit():
            student = Student(
                branch=student_form.branch.data,
                user=user,
            )
            db.session.add(student)
            db.session.commit()
            return redirect(url_for("login"))
    else:
        return "route is not available"

    return render_template(
        "additional.html",
        faculty_form=faculty_form,
        student_form=student_form,
        user=user,
        title="additional data",
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth"))


# Dashboard Pages
@app.route("/", methods=["POST", "GET"])
@login_required
def dashboard():

    if current_user.role == 0:
        student_count = len(Student.query.all())
        feedback_count = len(Feedback.query.all())
        faculty_overall_sentiment = float()
        faculties = list()
        users = User.query.filter_by(role=1).all()
        for user in users:
            faculty = Faculty.query.filter_by(user_id=user.id).first()
            faculties.append(faculty)
        feeds = Feedback.query.all()
        pos = 0
        neg = 0
        neutral = 0

        for f in feeds:
            if f.sentiment > 0:
                pos += 1
            elif f.sentiment < 0:
                neg += 1
            elif f.sentiment == 0:
                neutral += 1

        # pos = (pos / feedback_count) * 100
        # neg = (neg / feedback_count) * 100
        # neutral = (neutral / feedback_count) * 100

        faculty_sentiment = 0
        for feed in feeds:
            faculty_sentiment += feed.sentiment
        if len(faculties) > 0:
            faculty_overall_sentiment = faculty_sentiment / feedback_count
        print(faculty_overall_sentiment)
        return render_template(
            "dashboard.html",
            current_user=current_user,
            faculties=faculties,
            student_count=student_count,
            feedback_count=feedback_count,
            faculty_overall_sentiment=faculty_overall_sentiment,
            pos=pos,
            neg=neg,
            neutral=neutral,
        )
    elif current_user.role == 1:
        faculty = Faculty.query.filter_by(user_id=current_user.id).first()

        faculty_overall_sentiment = 0
        if faculty.sentiment is None:
            faculty_overall_sentiment = 0
        else:
            faculty_overall_sentiment = faculty.sentiment

        faculty_feedbacks = Feedback.query.filter_by(faculty_id=faculty.id).all()
        faculty_feedbacks_count = len(faculty_feedbacks)

        pos = 0
        neg = 0
        neutral = 0

        for f in faculty_feedbacks:
            if f.sentiment > 0:
                pos += 1
            elif f.sentiment < 0:
                neg += 1
            elif f.sentiment == 0:
                neutral += 1

        #         faculty_overall_sentiment = float()
        #         faculty_sentiment = 0
        #         for feedback in faculty_feedbacks:
        #             faculty_sentiment += feedback.sentiment

        #         if faculty_feedbacks_count == 0:
        #             faculty_overall_sentiment = 0
        #         else:
        #             faculty_overall_sentiment = (
        #                 faculty_sentiment) / (faculty_feedbacks_count)
        #         print(faculty_overall_sentiment)
        return render_template(
            "dashboard.html",
            current_user=current_user,
            faculty_feedbacks=faculty_feedbacks,
            faculty_feedbacks_count=faculty_feedbacks_count,
            faculty_overall_sentiment=faculty_overall_sentiment,
            pos=pos,
            neg=neg,
            neutral=neutral,
        )
    elif current_user.role == 2:
        selectform = SelectionForm()
        if selectform.validate_on_submit():
            sem = selectform.semester.data
            return redirect(url_for("feedback", sem=sem))
        return render_template(
            "dashboard.html",
            current_user=current_user,
            sform=selectform,
        )


@app.route("/feedback/<sem>", methods=["POST", "GET"])
@login_required
def feedback(sem):

    form = SelectionForm()

    if form.validate_on_submit():
        semester = form.semester.data
        return redirect(url_for("feedback", sem=semester))
    else:
        form.semester.data = sem

    student = Student.query.filter_by(user_id=current_user.id).first()
    faculties = Faculty.query.filter_by(semester=sem, branch=student.branch)
    feedback = Feedback.query.filter_by(user_id=current_user.id)
    
    return render_template("Feedbackpg.html", faculties=faculties,feedback=feedback, form=form)


@app.route("/feedback/add/<faculty_id>", methods=["GET", "POST"])
@login_required
def form(faculty_id):
    feedbackforms = FeedbackForm()
    # teacher = request.args.get("teacher")
    # subject = request.args.get("subject")
    faculty = Faculty.query.filter_by(id=faculty_id).first()
    if feedbackforms.validate_on_submit():
        sentiment = feedbackforms.sentiment_analysis(
            [
                feedbackforms.punctuality.data,
                feedbackforms.teaching_style.data,
                feedbackforms.portion_completion.data,
                feedbackforms.doubt_solving.data,
                feedbackforms.teacher_preparedness.data,
                feedbackforms.additional_comments.data,
            ]
        )
        feeds = Feedback(
            faculty=faculty,
            user=current_user,
            punctuality=feedbackforms.punctuality.data,
            teaching_style=feedbackforms.teaching_style.data,
            portion_completion=feedbackforms.portion_completion.data,
            doubt_solving=feedbackforms.doubt_solving.data,
            teacher_preparedness=feedbackforms.teacher_preparedness.data,
            additional_comments=feedbackforms.additional_comments.data,
            sentiment=sentiment,
        )

        db.session.add(feeds)
        db.session.commit()
        if faculty.sentiment == None:
            faculty.sentiment = sentiment
        else:
            faculty.sentiment = (faculty.sentiment + sentiment) / 2
        db.session.commit()
        flash("your feedback has been recorded!", category="success")
        return redirect(url_for("dashboard"))
    return render_template("form.html", form=feedbackforms)


if __name__ == "__main__":
    app.debug = True
    app.run()
