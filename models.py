from sqlalchemy.orm import backref
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    private_id = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Integer, nullable=False)
    faculty = db.relationship("Faculty", backref="user", uselist=False)
    student = db.relationship("Student", backref="user", uselist=False)
    feedbacks = db.relationship("Feedback", backref="user")


class Student(db.Model):

    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Faculty(db.Model):

    __tablename__ = "faculty"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sentiment = db.Column(db.Float, nullable=True)
    feedbacks = db.relationship("Feedback", backref="faculty")
    semester = db.Column(db.String(255), nullable=False)
    branch = db.Column(db.String(255), nullable=False)


class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    punctuality = db.Column(db.Text)
    teaching_style = db.Column(db.Text)
    portion_completion = db.Column(db.Text)
    doubt_solving = db.Column(db.Text)
    teacher_preparedness = db.Column(db.Text)
    additional_comments = db.Column(db.Text)
    sentiment = db.Column(db.Float)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"id:{self.id} \n sentiment:{self.faculty_id}, \n subject:{self.user_id}"
