#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会计核算模块视图
"""

from flask import render_template, request, redirect, url_for, flash, session
from app.models import db, Account, Voucher, VoucherEntry, PurchaseOrder, SalesOrder, Expense
from app.views import main_bp
from app.utils.auth import login_required, admin_required
from datetime import datetime
import uuid

# 会计科目管理

@main_bp.route('/account/list')
@login_required
def account_list():
    """会计科目列表"""
    accounts = Account.query.filter_by(is_deleted=False).all()
    return render_template('account/list.html', accounts=accounts)

@main_bp.route('/account/add', methods=['GET', 'POST'])
@login_required
def account_add():
    """添加会计科目"""
    if request.method == 'POST':
        try:
            account = Account(
                code=request.form['code'],
                name=request.form['name'],
                type=request.form['type'],
                parent_code=request.form.get('parent_code'),
                description=request.form.get('description'),
                balance=float(request.form.get('balance', 0))
            )
            db.session.add(account)
            db.session.commit()
            flash('会计科目添加成功！', 'success')
            return redirect(url_for('main.account_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'会计科目添加失败: {str(e)}', 'danger')
    # 获取所有科目作为父科目选项
    parent_accounts = Account.query.filter_by(is_deleted=False).all()
    return render_template('account/add.html', parent_accounts=parent_accounts)

@main_bp.route('/account/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def account_edit(id):
    """编辑会计科目"""
    account = Account.query.get_or_404(id)
    if request.method == 'POST':
        try:
            account.name = request.form['name']
            account.type = request.form['type']
            account.parent_code = request.form.get('parent_code')
            account.description = request.form.get('description')
            # 不允许直接修改余额，余额应该通过凭证自动更新
            db.session.commit()
            flash('会计科目编辑成功！', 'success')
            return redirect(url_for('main.account_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'会计科目编辑失败: {str(e)}', 'danger')
    parent_accounts = Account.query.filter(Account.is_deleted == False, Account.id != id).all()
    return render_template('account/edit.html', account=account, parent_accounts=parent_accounts)

@main_bp.route('/account/delete/<int:id>')
@login_required
@admin_required
def account_delete(id):
    """删除会计科目"""
    try:
        account = Account.query.get_or_404(id)
        # 检查是否有子科目
        has_children = Account.query.filter_by(parent_code=account.code, is_deleted=False).first()
        if has_children:
            flash('该科目存在子科目，不能删除！', 'danger')
            return redirect(url_for('main.account_list'))
        # 检查是否有凭证分录使用该科目
        has_entries = VoucherEntry.query.filter_by(account_code=account.code, is_deleted=False).first()
        if has_entries:
            flash('该科目已被凭证分录使用，不能删除！', 'danger')
            return redirect(url_for('main.account_list'))
        account.is_deleted = True
        db.session.commit()
        flash('会计科目删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'会计科目删除失败: {str(e)}', 'danger')
    return redirect(url_for('main.account_list'))

@main_bp.route('/account/view/<int:id>')
@login_required
def account_view(id):
    """查看会计科目详情"""
    account = Account.query.get_or_404(id)
    return render_template('account/view.html', account=account)

# 仪表盘

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """仪表盘"""
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    # 获取当前月份
    today = datetime.today()
    current_month_start = today.replace(day=1)
    current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # 计算本月收入、支出、利润
    # 1. 获取本月的凭证
    vouchers = Voucher.query.filter(
        Voucher.date >= current_month_start.date(),
        Voucher.date <= current_month_end.date(),
        Voucher.status == 'posted',
        Voucher.is_deleted == False
    ).all()
    
    # 2. 初始化本月收支变量
    total_income = Decimal('0.0')
    total_expense = Decimal('0.0')
    
    # 遍历凭证计算本月收支
    for voucher in vouchers:
        for entry in voucher.entries:
            if entry.account and entry.account.type == 'income':
                total_income += entry.credit  # 收入类账户增加记在贷方
            elif entry.account and entry.account.type in ['expense', 'cost']:
                total_expense += entry.debit
    
    total_profit = total_income - total_expense
    
    # 获取待处理事项数量
    pending_orders = PurchaseOrder.query.filter_by(status='pending', is_deleted=False).count() + SalesOrder.query.filter_by(status='pending', is_deleted=False).count()
    pending_expenses = Expense.query.filter_by(status='pending', is_deleted=False).count()
    pending_vouchers = Voucher.query.filter_by(status='draft', is_deleted=False).count()
    total_pending = pending_orders + pending_expenses + pending_vouchers
    
    # 获取最近交易记录
    recent_transactions = []
    
    # 获取最近的凭证
    recent_vouchers = Voucher.query.filter_by(is_deleted=False).order_by(Voucher.create_time.desc()).limit(5).all()
    for voucher in recent_vouchers:
        recent_transactions.append({
            'date': voucher.date.strftime('%Y-%m-%d'),
            'type': '凭证',
            'description': voucher.summary,
            'amount': sum(entry.debit for entry in voucher.entries),
            'status': voucher.status
        })
    
    # 获取最近的费用报销
    recent_expenses = Expense.query.filter_by(is_deleted=False).order_by(Expense.create_time.desc()).limit(5).all()
    for expense in recent_expenses:
        recent_transactions.append({
            'date': expense.create_time.strftime('%Y-%m-%d'),
            'type': '费用报销',
            'description': expense.description,
            'amount': expense.amount,
            'status': expense.status
        })
    
    # 按日期排序
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:10]  # 只显示最近10条
    
    return render_template('dashboard.html', 
                         total_income=total_income,
                         total_expense=total_expense,
                         total_profit=total_profit,
                         total_pending=total_pending,
                         recent_transactions=recent_transactions)

# 凭证管理

@main_bp.route('/voucher/list')
@login_required
def voucher_list():
    """凭证列表"""
    vouchers = Voucher.query.filter_by(is_deleted=False).all()
    return render_template('voucher/list.html', vouchers=vouchers)

@main_bp.route('/voucher/add', methods=['GET', 'POST'])
@login_required
def voucher_add():
    """添加凭证"""
    if request.method == 'POST':
        try:
            # 生成凭证编号
            voucher_number = f"VOU{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            # 创建凭证，使用当前登录用户ID
            voucher = Voucher(
                voucher_number=voucher_number,
                date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
                summary=request.form['summary'],
                user_id=session['user_id']  # 使用当前登录用户ID
            )
            
            # 处理凭证分录
            entry_count = int(request.form['entry_count'])
            total_debit = 0
            total_credit = 0
            
            for i in range(entry_count):
                account_code = request.form[f'account_code_{i}']
                debit = float(request.form[f'debit_{i}'] or 0)
                credit = float(request.form[f'credit_{i}'] or 0)
                description = request.form.get(f'description_{i}', '')
                
                # 验证科目存在
                account = Account.query.filter_by(code=account_code, is_deleted=False).first()
                if not account:
                    flash(f'第{i+1}行分录的科目不存在！', 'danger')
                    return redirect(url_for('main.voucher_add'))
                
                # 创建分录
                entry = VoucherEntry(
                    account_code=account_code,
                    debit=debit,
                    credit=credit,
                    description=description
                )
                voucher.entries.append(entry)
                
                # 累计借贷方
                total_debit += debit
                total_credit += credit
            
            # 检查借贷平衡
            if abs(total_debit - total_credit) > 0.01:
                flash('凭证借贷不平衡！', 'danger')
                return redirect(url_for('main.voucher_add'))
            
            db.session.add(voucher)
            db.session.commit()
            flash('凭证添加成功！', 'success')
            return redirect(url_for('main.voucher_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'凭证添加失败: {str(e)}', 'danger')
    
    # 获取所有科目
    accounts = Account.query.filter_by(is_deleted=False).all()
    return render_template('voucher/add.html', accounts=accounts)

@main_bp.route('/voucher/view/<int:id>')
@login_required
def voucher_view(id):
    """查看凭证详情"""
    voucher = Voucher.query.get_or_404(id)
    return render_template('voucher/view.html', voucher=voucher)

@main_bp.route('/voucher/approve/<int:id>')
@login_required
@admin_required  # 只有管理员才能审核凭证
def voucher_approve(id):
    """审核凭证"""
    try:
        voucher = Voucher.query.get_or_404(id)
        if voucher.status != 'draft':
            flash('只有草稿状态的凭证可以审核！', 'danger')
            return redirect(url_for('main.voucher_list'))
        
        voucher.status = 'approved'
        voucher.approval_id = session['user_id']  # 使用当前登录用户ID作为审核人
        voucher.approval_time = datetime.now()
        
        db.session.commit()
        flash('凭证审核成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'凭证审核失败: {str(e)}', 'danger')
    return redirect(url_for('main.voucher_list'))

@main_bp.route('/voucher/post/<int:id>')
@login_required
@admin_required  # 只有管理员才能过账凭证
def voucher_post(id):
    """过账凭证"""
    try:
        voucher = Voucher.query.get_or_404(id)
        if voucher.status != 'approved':
            flash('只有审核通过的凭证可以过账！', 'danger')
            return redirect(url_for('main.voucher_list'))
        
        # 更新科目余额
        for entry in voucher.entries:
            account = Account.query.filter_by(code=entry.account_code).first()
            if account:
                # 根据科目类型更新余额
                if account.type in ['asset', 'expense', 'cost']:
                    account.balance += entry.debit - entry.credit
                else:  # liability, equity, income
                    account.balance += entry.credit - entry.debit
        
        voucher.status = 'posted'
        voucher.post_time = datetime.now()
        
        db.session.commit()
        flash('凭证过账成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'凭证过账失败: {str(e)}', 'danger')
    return redirect(url_for('main.voucher_list'))

@main_bp.route('/voucher/delete/<int:id>')
@login_required
@admin_required  # 只有管理员才能删除凭证
def voucher_delete(id):
    """删除凭证"""
    try:
        voucher = Voucher.query.get_or_404(id)
        if voucher.status == 'posted':
            flash('已过账的凭证不能删除！', 'danger')
            return redirect(url_for('main.voucher_list'))
        
        voucher.is_deleted = True
        db.session.commit()
        flash('凭证删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'凭证删除失败: {str(e)}', 'danger')
    return redirect(url_for('main.voucher_list'))
