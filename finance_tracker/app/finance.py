from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Transaction
# from sqlalchemy import func

finance_bp = Blueprint(
    "finance",
    __name__,
    template_folder="templates/finance",
)


@finance_bp.route("/")
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")

    from sqlalchemy import func

    category_summary = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter_by(user_id=current_user.id).group_by(Transaction.category).all()

    categories = [c[0] for c in category_summary]
    totals = [float(c[1]) for c in category_summary]

    return render_template(
        "finance/dashboard.html",
        income=income,
        expense=expense,
        transactions=transactions,
        categories=categories,
        totals=totals,
        category_summary=category_summary
    )




@finance_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        t_type = request.form["type"]
        category = request.form["category"]
        amount = float(request.form["amount"])

        new_tx = Transaction(
            type=t_type,
            category=category,
            amount=amount,
            user_id=current_user.id
        )

        db.session.add(new_tx)
        db.session.commit()

        return redirect(url_for("finance.dashboard"))

    return render_template("finance/add_transaction.html")

@finance_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('finance.dashboard'))

    if request.method == "POST":
        transaction.category = request.form["category"]
        transaction.amount = float(request.form["amount"])
        transaction.type = request.form["type"]
        transaction.description = request.form["description"]

        db.session.commit()
        flash("Transaction updated!", "success")
        return redirect(url_for("finance.dashboard"))

    return render_template("finance/edit_transaction.html", transaction=transaction)


@finance_bp.route("/delete/<int:id>")
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for('finance.dashboard'))

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted!", "success")
    return redirect(url_for("finance.dashboard"))


