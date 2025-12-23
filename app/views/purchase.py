#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
采购管理视图
"""

from flask import render_template, redirect, url_for, flash, request, session
from app.models import db, Supplier, PurchaseOrder, PurchaseOrderItem
from app.views import main_bp
from app.utils.auth import login_required, admin_required
from datetime import datetime
import uuid

# 供应商管理

@main_bp.route('/supplier/list')
@login_required
def supplier_list():
    """
    供应商列表
    """
    suppliers = Supplier.query.filter_by(is_deleted=False).all()
    return render_template('purchase/supplier_list.html', suppliers=suppliers)

@main_bp.route('/supplier/add', methods=['GET', 'POST'])
@login_required
def supplier_add():
    """
    添加供应商
    """
    if request.method == 'POST':
        try:
            # 获取表单数据
            name = request.form['name']
            contact = request.form['contact']
            phone = request.form['phone']
            email = request.form['email']
            address = request.form['address']
            tax_number = request.form['tax_number']
            bank_account = request.form['bank_account']
            
            # 创建供应商
            supplier = Supplier(
                name=name,
                contact=contact,
                phone=phone,
                email=email,
                address=address,
                tax_number=tax_number,
                bank_account=bank_account
            )
            
            # 保存数据
            db.session.add(supplier)
            db.session.commit()
            
            flash('供应商添加成功！', 'success')
            return redirect(url_for('main.supplier_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'供应商添加失败: {str(e)}', 'danger')
    
    return render_template('purchase/supplier_add.html')

@main_bp.route('/supplier/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def supplier_edit(supplier_id):
    """
    编辑供应商
    """
    supplier = Supplier.query.filter_by(id=supplier_id, is_deleted=False).first()
    if not supplier:
        flash('供应商不存在或已删除', 'danger')
        return redirect(url_for('main.supplier_list'))
    
    if request.method == 'POST':
        try:
            # 更新供应商信息
            supplier.name = request.form['name']
            supplier.contact = request.form['contact']
            supplier.phone = request.form['phone']
            supplier.email = request.form['email']
            supplier.address = request.form['address']
            supplier.tax_number = request.form['tax_number']
            supplier.bank_account = request.form['bank_account']
            
            # 保存数据
            db.session.commit()
            
            flash('供应商更新成功！', 'success')
            return redirect(url_for('main.supplier_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'供应商更新失败: {str(e)}', 'danger')
    
    return render_template('purchase/supplier_edit.html', supplier=supplier)

@main_bp.route('/supplier/delete/<int:supplier_id>')
@login_required
@admin_required
def supplier_delete(supplier_id):
    """
    删除供应商
    """
    supplier = Supplier.query.filter_by(id=supplier_id, is_deleted=False).first()
    if not supplier:
        flash('供应商不存在或已删除', 'danger')
        return redirect(url_for('main.supplier_list'))
    
    try:
        # 软删除供应商
        supplier.is_deleted = True
        db.session.commit()
        
        flash('供应商删除成功！', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'供应商删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.supplier_list'))

# 采购订单管理

@main_bp.route('/purchase/order/list')
@login_required
def purchase_order_list():
    """
    采购订单列表
    """
    orders = PurchaseOrder.query.filter_by(is_deleted=False).all()
    return render_template('purchase/order_list.html', orders=orders)

@main_bp.route('/purchase/order/add', methods=['GET', 'POST'])
@login_required
def purchase_order_add():
    """
    添加采购订单
    """
    if request.method == 'POST':
        try:
            # 获取表单数据
            supplier_id = request.form['supplier_id']
            tax_rate = float(request.form['tax_rate'])
            payment_method = request.form['payment_method']
            
            # 创建订单编号
            order_number = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            # 获取订单明细
            item_names = request.form.getlist('item_name[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            
            # 计算订单总金额
            total_amount = 0
            items = []
            
            for item_name, quantity, unit_price in zip(item_names, quantities, unit_prices):
                if item_name and quantity and unit_price:
                    quantity = float(quantity)
                    unit_price = float(unit_price)
                    amount = quantity * unit_price
                    total_amount += amount
                    
                    item = PurchaseOrderItem(
                        item_name=item_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        amount=amount
                    )
                    items.append(item)
            
            # 计算税额
            tax_amount = total_amount * tax_rate
            
            # 创建采购订单
            order = PurchaseOrder(
                order_number=order_number,
                supplier_id=supplier_id,
                total_amount=total_amount,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                payment_method=payment_method,
                status='pending',
                user_id=1  # 假设当前用户ID为1
            )
            
            # 添加订单明细
            for item in items:
                order.items.append(item)
            
            # 保存数据
            db.session.add(order)
            db.session.commit()
            
            flash('采购订单添加成功！', 'success')
            return redirect(url_for('main.purchase_order_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'采购订单添加失败: {str(e)}', 'danger')
    
    # 获取供应商列表
    suppliers = Supplier.query.filter_by(is_deleted=False).all()
    return render_template('purchase/order_add.html', suppliers=suppliers)

@main_bp.route('/purchase/order/view/<int:order_id>')
@login_required
def purchase_order_view(order_id):
    """
    查看采购订单详情
    """
    order = PurchaseOrder.query.filter_by(id=order_id, is_deleted=False).first()
    if not order:
        flash('采购订单不存在或已删除', 'danger')
        return redirect(url_for('main.purchase_order_list'))
    
    return render_template('purchase/order_view.html', order=order)

@main_bp.route('/purchase/order/approve/<int:order_id>')
@login_required
@admin_required  # 只有管理员才能审批采购订单
def purchase_order_approve(order_id):
    """
    审批采购订单
    """
    order = PurchaseOrder.query.filter_by(id=order_id, is_deleted=False).first()
    if not order:
        flash('采购订单不存在或已删除', 'danger')
        return redirect(url_for('main.purchase_order_list'))
    
    try:
        # 更新订单状态
        order.status = 'approved'
        order.approval_id = session['user_id']  # 使用当前登录用户ID
        order.approval_time = datetime.now()
        
        db.session.commit()
        flash('采购订单审批成功！', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'采购订单审批失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.purchase_order_list'))

@main_bp.route('/purchase/order/cancel/<int:order_id>')
@login_required
@admin_required
def purchase_order_cancel(order_id):
    """
    取消采购订单
    """
    order = PurchaseOrder.query.filter_by(id=order_id, is_deleted=False).first()
    if not order:
        flash('采购订单不存在或已删除', 'danger')
        return redirect(url_for('main.purchase_order_list'))
    
    try:
        # 更新订单状态
        order.status = 'cancelled'
        
        db.session.commit()
        flash('采购订单取消成功！', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'采购订单取消失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.purchase_order_list'))

@main_bp.route('/purchase/order/complete/<int:order_id>')
@login_required
@admin_required
def purchase_order_complete(order_id):
    """
    完成采购订单
    """
    order = PurchaseOrder.query.filter_by(id=order_id, is_deleted=False).first()
    if not order:
        flash('采购订单不存在或已删除', 'danger')
        return redirect(url_for('main.purchase_order_list'))
    
    try:
        # 更新订单状态
        order.status = 'completed'
        
        db.session.commit()
        flash('采购订单完成成功！', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'采购订单完成失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.purchase_order_list'))