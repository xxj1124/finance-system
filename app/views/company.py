#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业初始化视图
"""

from flask import render_template, redirect, url_for, flash, request
from app.models import db, Company, Account, User
from app.views import main_bp
from werkzeug.security import generate_password_hash
from app.utils.auth import login_required, admin_required
import json

@main_bp.route('/')
def index():
    """
    首页
    """
    # 检查企业是否已初始化
    company = Company.query.filter_by(is_deleted=False).first()
    
    if not company:
        # 企业未初始化，重定向到初始化页面
        return redirect(url_for('main.company_init'))
    else:
        # 企业已初始化，检查是否已登录
        from flask import session
        if 'user_id' in session:
            # 已登录，重定向到dashboard
            return redirect(url_for('main.dashboard'))
        else:
            # 未登录，重定向到登录页面
            return redirect(url_for('main.login'))

@main_bp.route('/company/init', methods=['GET', 'POST'])
def company_init():
    """
    企业初始化
    """
    # 检查是否已经初始化过企业信息
    company = Company.query.filter_by(is_deleted=False).first()
    if company:
        flash('企业信息已初始化，如需修改请进入企业设置', 'info')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            name = request.form['name']
            registered_capital = request.form['registered_capital']
            industry = request.form['industry']
            accounting_period = request.form['accounting_period']
            currency = request.form['currency']
            
            # 处理启用模块
            enabled_modules = request.form.getlist('modules')
            enabled_modules_str = json.dumps(enabled_modules)
            
            # 创建企业信息
            new_company = Company(
                name=name,
                registered_capital=registered_capital,
                industry=industry,
                accounting_period=accounting_period,
                currency=currency,
                enabled_modules=enabled_modules_str
            )
            
            # 自动生成标准会计科目表
            generate_default_accounts()
            
            # 设置实收资本初始余额为注册资本
            paid_in_capital_account = Account.query.filter_by(code='4001').first()
            if paid_in_capital_account:
                paid_in_capital_account.balance = float(registered_capital)
                db.session.commit()
            
            # 创建默认管理员用户
            default_admin = User(
                username='admin',
                password=generate_password_hash('123456'),
                real_name='系统管理员',
                role='admin'
            )
            
            # 保存数据
            db.session.add(new_company)
            db.session.add(default_admin)
            db.session.commit()
            
            flash('企业初始化成功！默认管理员账号：admin，密码：123456', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'初始化失败: {str(e)}', 'danger')
    
    return render_template('company/init.html')



# 生成默认会计科目
def generate_default_accounts():
    """
    生成默认会计科目表
    """
    default_accounts = [
        # 资产类
        {'code': '1001', 'name': '库存现金', 'type': 'asset', 'parent_code': None},
        {'code': '1002', 'name': '银行存款', 'type': 'asset', 'parent_code': None},
        {'code': '100201', 'name': '工商银行', 'type': 'asset', 'parent_code': '1002'},
        {'code': '100202', 'name': '建设银行', 'type': 'asset', 'parent_code': '1002'},
        {'code': '1122', 'name': '应收账款', 'type': 'asset', 'parent_code': None},
        {'code': '1221', 'name': '其他应收款', 'type': 'asset', 'parent_code': None},
        {'code': '1403', 'name': '原材料', 'type': 'asset', 'parent_code': None},
        {'code': '1405', 'name': '库存商品', 'type': 'asset', 'parent_code': None},
        {'code': '1601', 'name': '固定资产', 'type': 'asset', 'parent_code': None},
        {'code': '1602', 'name': '累计折旧', 'type': 'asset', 'parent_code': None},
        {'code': '1801', 'name': '长期待摊费用', 'type': 'asset', 'parent_code': None},
        
        # 负债类
        {'code': '2001', 'name': '短期借款', 'type': 'liability', 'parent_code': None},
        {'code': '2202', 'name': '应付账款', 'type': 'liability', 'parent_code': None},
        {'code': '2203', 'name': '预收账款', 'type': 'liability', 'parent_code': None},
        {'code': '2211', 'name': '应付职工薪酬', 'type': 'liability', 'parent_code': None},
        {'code': '2221', 'name': '应交税费', 'type': 'liability', 'parent_code': None},
        {'code': '2241', 'name': '其他应付款', 'type': 'liability', 'parent_code': None},
        
        # 所有者权益类
        {'code': '4001', 'name': '实收资本', 'type': 'equity', 'parent_code': None},
        {'code': '4002', 'name': '资本公积', 'type': 'equity', 'parent_code': None},
        {'code': '4101', 'name': '盈余公积', 'type': 'equity', 'parent_code': None},
        {'code': '4103', 'name': '本年利润', 'type': 'equity', 'parent_code': None},
        {'code': '4104', 'name': '利润分配', 'type': 'equity', 'parent_code': None},
        
        # 成本类
        {'code': '5001', 'name': '生产成本', 'type': 'cost', 'parent_code': None},
        {'code': '5101', 'name': '制造费用', 'type': 'cost', 'parent_code': None},
        
        # 损益类
        {'code': '6001', 'name': '主营业务收入', 'type': 'income', 'parent_code': None},
        {'code': '6051', 'name': '其他业务收入', 'type': 'income', 'parent_code': None},
        {'code': '6301', 'name': '营业外收入', 'type': 'income', 'parent_code': None},
        {'code': '6401', 'name': '主营业务成本', 'type': 'expense', 'parent_code': None},
        {'code': '6402', 'name': '其他业务成本', 'type': 'expense', 'parent_code': None},
        {'code': '6403', 'name': '税金及附加', 'type': 'expense', 'parent_code': None},
        {'code': '6601', 'name': '销售费用', 'type': 'expense', 'parent_code': None},
        {'code': '6602', 'name': '管理费用', 'type': 'expense', 'parent_code': None},
        {'code': '6603', 'name': '财务费用', 'type': 'expense', 'parent_code': None},
        {'code': '6711', 'name': '营业外支出', 'type': 'expense', 'parent_code': None},
        {'code': '6801', 'name': '所得税费用', 'type': 'expense', 'parent_code': None}
    ]
    
    # 保存默认会计科目
    for account_data in default_accounts:
        account = Account(
            code=account_data['code'],
            name=account_data['name'],
            type=account_data['type'],
            parent_code=account_data['parent_code']
        )
        db.session.add(account)
    
    db.session.commit()