#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
费用报销模块视图
"""

from flask import render_template, request, redirect, url_for, flash, session
from app.models import db, Expense, User, Voucher, VoucherEntry, Account
from app.views import main_bp
from app.utils.auth import login_required, admin_required
from datetime import datetime
import uuid

# 费用管理

@main_bp.route('/expense/list')
@login_required
def expense_list():
    """费用记录列表"""
    expenses = Expense.query.filter_by(is_deleted=False).all()
    return render_template('expense/list.html', expenses=expenses)

@main_bp.route('/expense/add', methods=['GET', 'POST'])
@login_required
def expense_add():
    """添加费用记录"""
    if request.method == 'POST':
        try:
            expense_number = f"EXP{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            expense = Expense(
                expense_number=expense_number,
                user_id=session['user_id'],  # 使用当前登录用户ID
                amount=float(request.form['amount']),
                expense_type=request.form['expense_type'],
                description=request.form.get('description'),
                status='pending'
            )
            db.session.add(expense)
            db.session.commit()
            flash('费用记录添加成功！', 'success')
            return redirect(url_for('main.expense_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'费用记录添加失败: {str(e)}', 'danger')
    return render_template('expense/add.html')

@main_bp.route('/expense/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def expense_edit(id):
    """编辑费用记录"""
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        try:
            expense.amount = float(request.form['amount'])
            expense.expense_type = request.form['expense_type']
            expense.description = request.form.get('description')
            db.session.commit()
            flash('费用记录编辑成功！', 'success')
            return redirect(url_for('main.expense_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'费用记录编辑失败: {str(e)}', 'danger')
    return render_template('expense/edit.html', expense=expense)

@main_bp.route('/expense/view/<int:id>')
@login_required
def expense_view(id):
    """查看费用记录详情"""
    expense = Expense.query.get_or_404(id)
    return render_template('expense/view.html', expense=expense)

@main_bp.route('/expense/delete/<int:id>')
@login_required
@admin_required  # 只有管理员才能删除费用记录
def expense_delete(id):
    """删除费用记录"""
    try:
        expense = Expense.query.get_or_404(id)
        expense.is_deleted = True
        db.session.commit()
        flash('费用记录删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'费用记录删除失败: {str(e)}', 'danger')
    return redirect(url_for('main.expense_list'))

@main_bp.route('/expense/approve/<int:id>')
@login_required
@admin_required  # 只有管理员才能审批费用记录
def expense_approve(id):
    """审批费用记录"""
    try:
        expense = Expense.query.get_or_404(id)
        expense.status = 'approved'
        expense.approval_id = session['user_id']  # 使用当前登录用户ID
        expense.approval_time = datetime.now()
        db.session.commit()
        flash('费用记录审批成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'费用记录审批失败: {str(e)}', 'danger')
    return redirect(url_for('main.expense_list'))

@main_bp.route('/expense/reject/<int:id>')
@login_required
@admin_required  # 只有管理员才能拒绝费用记录
def expense_reject(id):
    """拒绝费用记录"""
    try:
        expense = Expense.query.get_or_404(id)
        expense.status = 'rejected'
        expense.approval_id = session['user_id']  # 使用当前登录用户ID
        expense.approval_time = datetime.now()
        db.session.commit()
        flash('费用记录已拒绝！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'费用记录拒绝失败: {str(e)}', 'danger')
    return redirect(url_for('main.expense_list'))

@main_bp.route('/expense/pay/<int:id>')
@login_required
@admin_required  # 只有管理员才能支付费用记录
def expense_pay(id):
    """支付费用记录"""
    try:
        expense = Expense.query.get_or_404(id)
        
        # 1. 更新费用状态
        expense.status = 'paid'
        expense.payment_time = datetime.now()
        
        # 2. 生成凭证
        voucher_number = f"VOU{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
        voucher = Voucher(
            voucher_number=voucher_number,
            date=datetime.now().date(),
            summary=f"支付费用报销: {expense.description or expense.expense_type}",
            status='posted',
            user_id=session['user_id']  # 使用当前登录用户ID
        )
        db.session.add(voucher)
        db.session.flush()  # 获取voucher.id
        
        # 3. 生成凭证分录
        # 借方：费用科目
        expense_account = Account.query.filter_by(type='expense').first()
        if not expense_account:
            # 如果没有费用科目，创建一个默认的
            expense_account = Account(
                code='6602',
                name='管理费用',
                type='expense',
                balance=0.0
            )
            db.session.add(expense_account)
            db.session.flush()
        
        # 贷方：银行存款/现金科目
        cash_account = Account.query.filter_by(code='1001').first()
        if not cash_account:
            # 如果没有现金科目，创建一个默认的
            cash_account = Account(
                code='1001',
                name='库存现金',
                type='asset',
                balance=0.0
            )
            db.session.add(cash_account)
            db.session.flush()
        
        # 借方分录
        debit_entry = VoucherEntry(
            voucher_id=voucher.id,
            account_code=expense_account.code,
            debit=expense.amount,
            credit=0.0,
            description=expense.description or expense.expense_type
        )
        db.session.add(debit_entry)
        
        # 贷方分录
        credit_entry = VoucherEntry(
            voucher_id=voucher.id,
            account_code=cash_account.code,
            debit=0.0,
            credit=expense.amount,
            description=expense.description or expense.expense_type
        )
        db.session.add(credit_entry)
        
        # 4. 更新会计科目余额
        expense_account.balance += expense.amount  # 费用科目余额增加（借方）
        cash_account.balance -= expense.amount  # 现金科目余额减少（贷方）
        
        # 提交所有变更
        db.session.commit()
        flash('费用记录已支付并生成凭证！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'费用记录支付失败: {str(e)}', 'danger')
    return redirect(url_for('main.expense_list'))
