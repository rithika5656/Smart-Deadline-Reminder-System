from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for storing student information"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    deadlines = db.relationship('Deadline', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'


class Deadline(db.Model):
    """Deadline model for storing exam/assignment deadlines"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    deadline_type = db.Column(db.String(50), nullable=False)  # exam, assignment, project, quiz
    reminder_sent = db.Column(db.Boolean, default=False)
    reminder_hours = db.Column(db.Integer, default=24)  # hours before deadline to send reminder
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Deadline {self.title}>'
    
    @property
    def is_overdue(self):
        return datetime.utcnow() > self.due_date
    
    @property
    def time_remaining(self):
        delta = self.due_date - datetime.utcnow()
        if delta.days < 0:
            return "Overdue"
        elif delta.days == 0:
            hours = delta.seconds // 3600
            if hours == 0:
                minutes = delta.seconds // 60
                return f"{minutes} minutes"
            return f"{hours} hours"
        elif delta.days == 1:
            return "1 day"
        else:
            return f"{delta.days} days"
