#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并修复系统初始化问题
"""

import os
import sys
import datetime
from sqlalchemy.sql.expression import func

# 添加项目路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入应用
from app import create_app
from app.models import db, Account, Company, Voucher, VoucherEntry

# 创建应用实例
app = create_app()

with app.app_context():
    print("=== 修复系统初始化问题 ===")
    
    # 1. 检查公司信息
    print("\n1. 检查公司信息...")
    company = Company.query.filter_by(is_deleted=False).first()
    if company:
        print(f"   公司名称: {company.name}")
        print(f"   注册资本: {company.registered_capital}")
    else:
        print("   未找到公司信息")
    
    # 2. 检查实收资本
    print("\n2. 检查实收资本...")
    paid_in_capital = Account.query.filter_by(code='4001', is_deleted=False).first()
    if paid_in_capital:
        print(f"   当前实收资本: {paid_in_capital.balance}")
        
        # 如果存在公司信息，将实收资本设置为注册资本
        if company:
            print(f"   设置实收资本为注册资本: {company.registered_capital}")
            paid_in_capital.balance = company.registered_capital
            db.session.commit()
            print(f"   实收资本已修复为: {paid_in_capital.balance}")
        else:
            # 如果没有公司信息，设置一个合理的实收资本值
            print(f"   未找到公司信息，将实收资本设置为合理值")
            paid_in_capital.balance = 100000.00  # 设置为10万
            db.session.commit()
            print(f"   实收资本已修复为: {paid_in_capital.balance}")
    
    # 3. 重新检查资产负债表平衡
    print("\n3. 重新检查资产负债表平衡...")
    accounts = Account.query.filter_by(is_deleted=False).all()
    
    assets = sum(float(a.balance) for a in accounts if a.type == 'asset')
    liabilities = sum(float(a.balance) for a in accounts if a.type == 'liability')
    equity = sum(float(a.balance) for a in accounts if a.type == 'equity')
    
    total_assets = assets
    total_liab_equity = liabilities + equity
    
    print(f"   资产总计: {total_assets}")
    print(f"   负债总计: {liabilities}")
    print(f"   所有者权益总计: {equity}")
    print(f"   负债及所有者权益总计: {total_liab_equity}")
    
    if abs(total_assets - total_liab_equity) < 0.01:
        print("   ✅ 资产负债表平衡！")
    else:
        print(f"   ❌ 资产负债表仍然不平衡，差额: {total_assets - total_liab_equity}")
        print("   需要进一步检查科目的余额计算逻辑")
    
    print("\n=== 修复完成 ===")