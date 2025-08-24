from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from . import db
from .models import Task, Category
from .forms import TaskForm, CategoryForm, EmptyForm


main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.tasks"))
    return redirect(url_for("auth.login"))


# ---------- Категории ----------
@main_bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        cat = Category(name=name, user_id=current_user.id)
        db.session.add(cat)
        try:
            db.session.commit()
            flash("Категория добавлена", "success")
            return redirect(url_for("main.categories"))
        except IntegrityError:
            db.session.rollback()
            flash("Такая категория уже существует", "warning")
    cats = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    empty_form = EmptyForm()
    return render_template("categories/index.html", form=form, categories=cats, empty_form=empty_form)


@main_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    cat = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    Task.query.filter_by(user_id=current_user.id, category_id=cat.id).update({Task.category_id: None})
    db.session.delete(cat)
    db.session.commit()
    flash("Категория удалена", "info")
    return redirect(url_for("main.categories"))


# ---------- Задачи ----------
@main_bp.route("/tasks", methods=["GET"])
@login_required
def tasks():
    form = TaskForm()
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()

    form.category_id.choices = [(0, "Без категории")] + [(c.id, c.name) for c in categories]

    show = request.args.get("show", "all")  
    q = Task.query.filter_by(user_id=current_user.id)
    if show == "open":
        q = q.filter_by(is_done=False)
    elif show == "done":
        q = q.filter_by(is_done=True)

    q = q.order_by(Task.is_done.asc(), Task.priority.desc(), Task.deadline.asc().nulls_last())
    items = q.all()

    empty_form = EmptyForm()
    return render_template("tasks/index.html", form=form, tasks=items, categories=categories, show=show, empty_form=empty_form)


@main_bp.route("/tasks/create", methods=["POST"])
@login_required
def create_task():
    form = TaskForm()
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    form.category_id.choices = [(0, "Без категории")] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        task = Task(
            title=form.title.data.strip(),
            description=form.description.data or None,
            deadline=form.deadline.data,
            priority=int(form.priority.data),
            user_id=current_user.id,
            category_id=None if form.category_id.data == 0 else form.category_id.data,
            is_done=form.is_done.data or False,
        )
        db.session.add(task)
        db.session.commit()
        flash("Задача создана", "success")
        return redirect(url_for("main.tasks"))

    items = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("tasks/index.html", form=form, tasks=items, categories=categories, show="all" )


@main_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    
    form = TaskForm(obj=task)
    form.category_id.choices = [(0, "Без категории")] + [(c.id, c.name) for c in categories]

    # НЕ устанавливаем form.category_id.data здесь при POST! 
    # Только если GET (форма открывается первый раз)
    if request.method == "GET":
        form.category_id.data = task.category_id or 0
        form.priority.data = str(task.priority)

    if form.validate_on_submit():
        task.title = form.title.data.strip()
        task.description = form.description.data or None
        task.deadline = form.deadline.data
        task.priority = int(form.priority.data)
        task.category_id = None if form.category_id.data == 0 else int(form.category_id.data)
        task.is_done = bool(form.is_done.data)
        db.session.commit()
        flash("Задача обновлена", "success")
        return redirect(url_for("main.tasks"))

    return render_template("tasks/edit.html", form=form, task=task)



@main_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.is_done = not task.is_done
    db.session.commit()
    flash("Статус задачи изменён", "info")
    return redirect(request.referrer or url_for("main.tasks"))


@main_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash("Задача удалена", "info")
    return redirect(url_for("main.tasks"))

@main_bp.route("/stats")
@login_required
def stats():
    total = Task.query.filter_by(user_id=current_user.id).count()
    done = Task.query.filter_by(user_id=current_user.id, is_done=True).count()
    open_tasks = total - done

    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # последние 7 дней

    daily_counts = []
    for day in days:
        count = Task.query.filter(
            Task.user_id == current_user.id,
            Task.is_done == True,
            Task.deadline != None,
            Task.deadline <= day
        ).count()
        daily_counts.append(count)

    return render_template(
        "stats/index.html",
        total=total,
        done=done,
        open_tasks=open_tasks,
        days=[d.strftime("%d.%m") for d in days],
        daily_counts=daily_counts,
    )
