#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复实收资本和资产负债表不平衡问题
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
    
    # 1. 检查并修复实收资本
    print("\n1. 检查实收资本...")
    paid_in_capital = Account.query.filter_by(code='4001', is_deleted=False).first()
    company = Company.query.filter_by(is_deleted=False).first()
    
    if paid_in_capital and company:
        print(f"   当前实收资本: {paid_in_capital.balance}")
        print(f"   公司注册资本: {company.registered_capital}")
        
        # 如果实收资本与注册资本不匹配，进行修复
        if abs(float(paid_in_capital.balance) - float(company.registered_capital)) > 0.01:
            print("   修复实收资本...")
            paid_in_capital.balance = company.registered_capital
            db.session.commit()
            print(f"   实收资本已修复为: {paid_in_capital.balance}")
        else:
            print("   实收资本金额正确，无需修复")
    
    # 2. 检查损益结转凭证
    print("\n2. 检查损益结转凭证...")
    closure_vouchers = Voucher.query.filter(
        Voucher.voucher_number.like('CLOS%'),
        Voucher.is_deleted == False
    ).all()
    
    for voucher in closure_vouchers:
        # 检查凭证借贷平衡
        total_debit = sum(float(entry.debit) for entry in voucher.entries)
        total_credit = sum(float(entry.credit) for entry in voucher.entries)
        
        if abs(total_debit - total_credit) > 0.01:
            print(f"   发现不平衡的损益结转凭证: {voucher.voucher_number}")
            print(f"   借方合计: {total_debit}, 贷方合计: {total_credit}")
            
            # 简单修复：删除不平衡的损益结转凭证
            print(f"   删除不平衡的损益结转凭证...")
            db.session.delete(voucher)
            db.session.commit()
            print(f"   凭证 {voucher.voucher_number} 已删除")
    
    # 3. 重新检查平衡
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
    
    print("\n=== 修复完成 ===")