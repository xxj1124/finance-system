#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税务处理模块视图
"""

from flask import render_template, request, redirect, url_for, flash, session
from app.models import db, Tax
from app.views import main_bp
from app.utils.auth import login_required, admin_required
from datetime import datetime

# 税务列表
@main_bp.route('/tax/list')
@login_required
def tax_list():
    """税务列表"""
    taxes = Tax.query.filter_by(is_deleted=False).order_by(Tax.tax_period.desc(), Tax.tax_type).all()
    return render_template('tax/list.html', taxes=taxes)

# 添加税务申报
@main_bp.route('/tax/add', methods=['GET', 'POST'])
@login_required
def tax_add():
    """添加税务申报"""
    if request.method == 'POST':
        try:
            tax_type = request.form['tax_type']
            tax_period = request.form['tax_period']
            amount = float(request.form['amount'])
            
            # 创建新税务申报
            new_tax = Tax(
                tax_type=tax_type,
                tax_period=tax_period,
                amount=amount,
                status='pending'
            )
            
            db.session.add(new_tax)
            db.session.commit()
            
            flash('税务申报添加成功！', 'success')
            return redirect(url_for('main.tax_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'税务申报添加失败: {str(e)}', 'danger')
    
    # 默认使用当前年份和月份作为申报期
    current_period = datetime.now().strftime('%Y%m')
    return render_template('tax/add.html', current_period=current_period)

# 编辑税务申报
@main_bp.route('/tax/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def tax_edit(id):
    """编辑税务申报"""
    tax = Tax.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # 只有待提交状态的税务申报可以编辑
            if tax.status != 'pending':
                flash('只有待提交状态的税务申报可以编辑！', 'danger')
                return redirect(url_for('main.tax_edit', id=id))
            
            tax.tax_type = request.form['tax_type']
            tax.tax_period = request.form['tax_period']
            tax.amount = float(request.form['amount'])
            
            db.session.commit()
            
            flash('税务申报编辑成功！', 'success')
            return redirect(url_for('main.tax_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'税务申报编辑失败: {str(e)}', 'danger')
    
    return render_template('tax/edit.html', tax=tax)

# 查看税务申报详情
@main_bp.route('/tax/view/<int:id>')
@login_required
def tax_view(id):
    """查看税务申报详情"""
    tax = Tax.query.get_or_404(id)
    return render_template('tax/view.html', tax=tax)

# 提交税务申报
@main_bp.route('/tax/submit/<int:id>')
@login_required
def tax_submit(id):
    """提交税务申报"""
    try:
        tax = Tax.query.get_or_404(id)
        
        # 只有待提交状态的税务申报可以提交
        if tax.status != 'pending':
            flash('只有待提交状态的税务申报可以提交！', 'danger')
            return redirect(url_for('main.tax_list'))
        
        tax.status = 'submitted'
        tax.submit_time = datetime.now()
        db.session.commit()
        
        flash('税务申报提交成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'税务申报提交失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.tax_list'))

# 审批税务申报
@main_bp.route('/tax/approve/<int:id>')
@login_required
@admin_required  # 仅管理员可审批税务申报
def tax_approve(id):
    """审批税务申报"""
    try:
        tax = Tax.query.get_or_404(id)
        
        # 只有已提交状态的税务申报可以审批
        if tax.status != 'submitted':
            flash('只有已提交状态的税务申报可以审批！', 'danger')
            return redirect(url_for('main.tax_list'))
        
        tax.status = 'approved'
        tax.approval_time = datetime.now()
        db.session.commit()
        
        flash('税务申报审批成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'税务申报审批失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.tax_list'))

# 删除税务申报
@main_bp.route('/tax/delete/<int:id>')
@login_required
@admin_required  # 仅管理员可删除税务申报
def tax_delete(id):
    """删除税务申报"""
    try:
        tax = Tax.query.get_or_404(id)
        
        # 只有待提交状态的税务申报可以删除
        if tax.status not in ['pending']:
            flash('只有待提交状态的税务申报可以删除！', 'danger')
            return redirect(url_for('main.tax_list'))
        
        tax.is_deleted = True
        db.session.commit()
        
        flash('税务申报删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'税务申报删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.tax_list'))