from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint, Index, event
from . import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    categories = db.relationship("Category", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    tasks = db.relationship("Task", backref="category", lazy="dynamic")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_category_user_name"),
        Index("ix_category_user", "user_id"),
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)

    # приоритет: 1=low, 2=medium, 3=high
    priority = db.Column(db.Integer, default=2, nullable=False)

    is_done = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_task_user_done", "user_id", "is_done"),
        Index("ix_task_deadline", "deadline"),
    )

    def __repr__(self):
        return f"<Task {self.title} done={self.is_done}>"

# Авто-установка completed_at при пометке выполненной
@event.listens_for(Task.is_done, "set")
def set_completed_at(target, value, oldvalue, initiator):
    if value is True and oldvalue is not True:
        target.completed_at = datetime.utcnow()
    elif value is False and oldvalue is not False:
        target.completed_at = None
