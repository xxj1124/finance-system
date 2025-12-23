#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预算管理模块视图
"""

from flask import render_template, request, redirect, url_for, flash, session
from app.models import db, Budget
from app.views import main_bp
from app.utils.auth import login_required, admin_required
from datetime import datetime

# 预算列表
@main_bp.route('/budget/list')
@login_required
def budget_list():
    """预算列表"""
    budgets = Budget.query.filter_by(is_deleted=False).order_by(Budget.year.desc(), Budget.department).all()
    return render_template('budget/list.html', budgets=budgets)

# 添加预算
@main_bp.route('/budget/add', methods=['GET', 'POST'])
@login_required
def budget_add():
    """添加预算"""
    if request.method == 'POST':
        try:
            department = request.form['department']
            budget_amount = float(request.form['budget_amount'])
            year = int(request.form['year'])
            
            # 检查是否已存在相同部门和年份的预算
            existing_budget = Budget.query.filter_by(
                department=department, 
                year=year, 
                is_deleted=False
            ).first()
            
            if existing_budget:
                flash(f'{department}部门{year}年的预算已存在！', 'danger')
                return redirect(url_for('main.budget_add'))
            
            # 创建新预算
            new_budget = Budget(
                department=department,
                budget_amount=budget_amount,
                year=year,
                status='draft'
            )
            
            db.session.add(new_budget)
            db.session.commit()
            
            flash('预算添加成功！', 'success')
            return redirect(url_for('main.budget_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'预算添加失败: {str(e)}', 'danger')
    
    # 默认使用当前年份
    current_year = datetime.now().year
    return render_template('budget/add.html', current_year=current_year)

# 编辑预算
@main_bp.route('/budget/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def budget_edit(id):
    """编辑预算"""
    budget = Budget.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # 只有草稿状态的预算可以编辑
            if budget.status != 'draft':
                flash('只有草稿状态的预算可以编辑！', 'danger')
                return redirect(url_for('main.budget_edit', id=id))
            
            budget.department = request.form['department']
            budget.budget_amount = float(request.form['budget_amount'])
            budget.year = int(request.form['year'])
            
            db.session.commit()
            
            flash('预算编辑成功！', 'success')
            return redirect(url_for('main.budget_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'预算编辑失败: {str(e)}', 'danger')
    
    return render_template('budget/edit.html', budget=budget)

# 查看预算详情
@main_bp.route('/budget/view/<int:id>')
@login_required
def budget_view(id):
    """查看预算详情"""
    budget = Budget.query.get_or_404(id)
    
    # 计算预算使用比例
    if budget.budget_amount > 0:
        usage_ratio = (budget.used_amount / budget.budget_amount) * 100
    else:
        usage_ratio = 0
    
    return render_template('budget/view.html', budget=budget, usage_ratio=usage_ratio)

# 审批预算
@main_bp.route('/budget/approve/<int:id>')
@login_required
@admin_required  # 仅管理员可审批预算
def budget_approve(id):
    """审批预算"""
    try:
        budget = Budget.query.get_or_404(id)
        
        # 只有草稿状态的预算可以审批
        if budget.status != 'draft':
            flash('只有草稿状态的预算可以审批！', 'danger')
            return redirect(url_for('main.budget_list'))
        
        budget.status = 'approved'
        db.session.commit()
        
        flash('预算审批成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'预算审批失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.budget_list'))

# 激活预算
@main_bp.route('/budget/activate/<int:id>')
@login_required
@admin_required  # 仅管理员可激活预算
def budget_activate(id):
    """激活预算"""
    try:
        budget = Budget.query.get_or_404(id)
        
        # 只有审批通过的预算可以激活
        if budget.status != 'approved':
            flash('只有审批通过的预算可以激活！', 'danger')
            return redirect(url_for('main.budget_list'))
        
        budget.status = 'active'
        db.session.commit()
        
        flash('预算激活成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'预算激活失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.budget_list'))

# 删除预算
@main_bp.route('/budget/delete/<int:id>')
@login_required
@admin_required  # 仅管理员可删除预算
def budget_delete(id):
    """删除预算"""
    try:
        budget = Budget.query.get_or_404(id)
        
        # 只有草稿状态的预算可以删除
        if budget.status not in ['draft']:
            flash('只有草稿状态的预算可以删除！', 'danger')
            return redirect(url_for('main.budget_list'))
        
        budget.is_deleted = True
        db.session.commit()
        
        flash('预算删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'预算删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.budget_list'))

# 预算分析
@main_bp.route('/budget/analysis')
@login_required
def budget_analysis():
    """预算分析"""
    current_year = datetime.now().year
    
    # 获取当前年份的所有激活预算
    budgets = Budget.query.filter_by(
        year=current_year, 
        status='active', 
        is_deleted=False
    ).order_by(Budget.department).all()
    
    # 计算总体预算使用情况
    total_budget = sum(budget.budget_amount for budget in budgets)
    total_used = sum(budget.used_amount for budget in budgets)
    
    if total_budget > 0:
        overall_ratio = (total_used / total_budget) * 100
    else:
        overall_ratio = 0
    
    return render_template(
        'budget/analysis.html',
        budgets=budgets,
        current_year=current_year,
        total_budget=total_budget,
        total_used=total_used,
        overall_ratio=overall_ratio
    )
