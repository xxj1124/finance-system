#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
销售管理模块视图
"""

from flask import render_template, request, redirect, url_for, flash, session
from app.models import db, Customer, SalesOrder, SalesOrderItem, Voucher, VoucherEntry
from app.views import main_bp
from app.utils.auth import login_required, admin_required
from datetime import datetime
import uuid

# 客户管理

@main_bp.route('/sales/customer/list')
@login_required
def customer_list():
    """客户列表"""
    customers = Customer.query.filter_by(is_deleted=False).all()
    return render_template('sales/customer_list.html', customers=customers)

@main_bp.route('/sales/customer/add', methods=['GET', 'POST'])
@login_required
def customer_add():
    """添加客户"""
    if request.method == 'POST':
        try:
            customer = Customer(
                name=request.form['name'],
                contact=request.form['contact'],
                phone=request.form['phone'],
                email=request.form.get('email'),
                address=request.form.get('address'),
                tax_number=request.form.get('tax_number'),
                credit_limit=float(request.form.get('credit_limit', 0))
            )
            db.session.add(customer)
            db.session.commit()
            flash('客户添加成功！', 'success')
            return redirect(url_for('main.customer_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'客户添加失败: {str(e)}', 'danger')
    return render_template('sales/customer_add.html')

@main_bp.route('/sales/customer/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def customer_edit(id):
    """编辑客户"""
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.contact = request.form['contact']
            customer.phone = request.form['phone']
            customer.email = request.form.get('email')
            customer.address = request.form.get('address')
            customer.tax_number = request.form.get('tax_number')
            customer.credit_limit = float(request.form.get('credit_limit', 0))
            db.session.commit()
            flash('客户编辑成功！', 'success')
            return redirect(url_for('main.customer_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'客户编辑失败: {str(e)}', 'danger')
    return render_template('sales/customer_edit.html', customer=customer)

@main_bp.route('/sales/customer/delete/<int:id>')
@login_required
@admin_required
def customer_delete(id):
    """删除客户"""
    try:
        customer = Customer.query.get_or_404(id)
        customer.is_deleted = True
        db.session.commit()
        flash('客户删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'客户删除失败: {str(e)}', 'danger')
    return redirect(url_for('main.customer_list'))

# 销售订单管理

@main_bp.route('/sales/order/list')
@login_required
def sales_order_list():
    """销售订单列表"""
    orders = SalesOrder.query.filter_by(is_deleted=False).all()
    return render_template('sales/order_list.html', orders=orders)

@main_bp.route('/sales/order/add', methods=['GET', 'POST'])
@login_required
def sales_order_add():
    """添加销售订单"""
    if request.method == 'POST':
        try:
            customer_id = request.form['customer_id']
            tax_rate = float(request.form['tax_rate'])
            payment_method = request.form['payment_method']
            order_number = f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            # 获取订单项目
            item_names = request.form.getlist('item_name[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            
            total_amount = 0
            items = []
            for item_name, quantity, unit_price in zip(item_names, quantities, unit_prices):
                if item_name and quantity and unit_price:
                    quantity = float(quantity)
                    unit_price = float(unit_price)
                    amount = quantity * unit_price
                    total_amount += amount
                    item = SalesOrderItem(
                        item_name=item_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        amount=amount
                    )
                    items.append(item)
            
            # 计算税额
            tax_amount = total_amount * tax_rate
            
            # 创建订单
            order = SalesOrder(
                order_number=order_number,
                customer_id=customer_id,
                total_amount=total_amount,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                payment_method=payment_method,
                status='pending',
                user_id=1  # 假设当前用户ID为1
            )
            
            # 添加订单项
            for item in items:
                order.items.append(item)
            
            db.session.add(order)
            db.session.commit()
            flash('销售订单添加成功！', 'success')
            return redirect(url_for('main.sales_order_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'销售订单添加失败: {str(e)}', 'danger')
    
    customers = Customer.query.filter_by(is_deleted=False).all()
    return render_template('sales/order_add.html', customers=customers)

@main_bp.route('/sales/order/view/<int:id>')
@login_required
def sales_order_view(id):
    """查看销售订单详情"""
    order = SalesOrder.query.get_or_404(id)
    return render_template('sales/order_view.html', order=order)

@main_bp.route('/sales/order/approve/<int:id>')
@login_required
@admin_required  # 只有管理员才能审批销售订单
def sales_order_approve(id):
    """审批销售订单"""
    try:
        order = SalesOrder.query.get_or_404(id)
        order.status = 'approved'
        order.approval_id = session['user_id']  # 使用当前登录用户ID
        order.approval_time = datetime.now()
        db.session.commit()
        flash('销售订单审批成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'销售订单审批失败: {str(e)}', 'danger')
    return redirect(url_for('main.sales_order_list'))

@main_bp.route('/sales/order/complete/<int:id>')
@login_required
def sales_order_complete(id):
    """完成销售订单"""
    try:
        order = SalesOrder.query.get_or_404(id)
        order.status = 'completed'
        order.payment_time = datetime.now()
        db.session.commit()
        flash('销售订单已完成！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'销售订单完成失败: {str(e)}', 'danger')
    return redirect(url_for('main.sales_order_list'))

@main_bp.route('/sales/order/cancel/<int:id>')
@login_required
def sales_order_cancel(id):
    """取消销售订单"""
    try:
        order = SalesOrder.query.get_or_404(id)
        order.status = 'cancelled'
        db.session.commit()
        flash('销售订单已取消！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'销售订单取消失败: {str(e)}', 'danger')
    return redirect(url_for('main.sales_order_list'))
