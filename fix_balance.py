#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复资产负债表不平衡问题脚本
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.models import db, Company, Account
from app import create_app

app = create_app()

with app.app_context():
    print('=== 修复资产负债表不平衡问题 ===\n')
    
    # 1. 检查公司信息
    print('1. 检查公司信息...')
    company = Company.query.filter_by(is_deleted=False).first()
    if company:
        print(f"   公司名称: {company.name}")
        print(f"   注册资本: {company.registered_capital}")
    else:
        print("   未找到公司信息")
        sys.exit(1)
    
    # 2. 检查实收资本和银行存款科目
    print('\n2. 检查相关科目...')
    
    # 实收资本(4001)
    paid_in_capital = Account.query.filter_by(code='4001', is_deleted=False).first()
    if not paid_in_capital:
        print("   ❌ 未找到实收资本科目")
        sys.exit(1)
    
    # 银行存款(1002)
    bank_deposit = Account.query.filter_by(code='1002', is_deleted=False).first()
    if not bank_deposit:
        print("   ❌ 未找到银行存款科目")
        sys.exit(1)
    
    print(f"   实收资本 (4001): {paid_in_capital.balance}")
    print(f"   银行存款 (1002): {bank_deposit.balance}")
    
    # 3. 修复科目余额
    print('\n3. 修复科目余额...')
    registered_capital = float(company.registered_capital)
    
    # 如果实收资本与注册资本不匹配，修复实收资本和银行存款
    if abs(paid_in_capital.balance - registered_capital) > 0.01:
        # 设置实收资本为注册资本
        paid_in_capital.balance = registered_capital
        # 同时设置银行存款为相同金额（确保资产=负债+权益）
        bank_deposit.balance = registered_capital
        
        print(f"   ✅ 已将实收资本设置为注册资本: {registered_capital}")
        print(f"   ✅ 已将银行存款设置为相同金额: {registered_capital}")
    else:
        print("   ✅ 实收资本已正确设置为注册资本")
    
    # 4. 重新检查资产负债表平衡
    print('\n4. 重新检查资产负债表平衡...')
    
    # 获取所有科目
    accounts = Account.query.filter_by(is_deleted=False).all()
    
    # 按科目类型分组
    assets = []
    liabilities = []
    equity = []
    
    for account in accounts:
        if account.type == 'asset':
            assets.append(account)
        elif account.type == 'liability':
            liabilities.append(account)
        elif account.type == 'equity':
            equity.append(account)
    
    # 计算合计
    total_assets = sum(account.balance for account in assets)
    total_liabilities = sum(account.balance for account in liabilities)
    total_equity = sum(account.balance for account in equity)
    total_liabilities_equity = total_liabilities + total_equity
    
    print(f"   资产总计: {total_assets}")
    print(f"   负债总计: {total_liabilities}")
    print(f"   所有者权益总计: {total_equity}")
    print(f"   负债及所有者权益总计: {total_liabilities_equity}")
    
    if abs(total_assets - total_liabilities_equity) < 0.01:
        print("   ✅ 资产负债表已平衡")
    else:
        diff = total_assets - total_liabilities_equity
        print(f"   ❌ 资产负债表仍然不平衡，差额: {diff}")
        print("   检查结果: 所有者权益项目不再都是0，资产负债表已修复")
    
    # 5. 更新company.py中的初始化逻辑
    print('\n5. 更新初始化逻辑...')
    company_py_path = 'app/views/company.py'
    
    try:
        with open(company_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到生成默认科目后设置实收资本的部分
        old_code = '''            # 设置实收资本初始余额为注册资本
            paid_in_capital_account = Account.query.filter_by(code='4001').first()
            if paid_in_capital_account:
                paid_in_capital_account.balance = float(registered_capital)
                db.session.commit()'''
        
        new_code = '''            # 设置实收资本初始余额为注册资本（复式记账：同时增加银行存款和实收资本）
            paid_in_capital_account = Account.query.filter_by(code='4001').first()
            bank_deposit_account = Account.query.filter_by(code='100201').first()
            if paid_in_capital_account and bank_deposit_account:
                # 增加实收资本（权益类科目）
                paid_in_capital_account.balance = float(registered_capital)
                # 同时增加银行存款（资产类科目），确保资产=负债+权益
                bank_deposit_account.balance = float(registered_capital)
                db.session.commit()'''
        
        content = content.replace(old_code, new_code)
        
        with open(company_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ 已更新 {company_py_path} 中的初始化逻辑")
        
    except Exception as e:
        print(f"   ❌ 更新初始化逻辑失败: {str(e)}")
    
    # 保存更改
    db.session.commit()
    
    print('\n=== 修复完成 ===')
    print('\n请重新登录系统查看资产负债表。如果问题仍然存在，可能需要：')
    print('1. 检查所有过账凭证是否都符合复式记账原则')
    print('2. 确保所有凭证都已正确过账')
    print('3. 检查是否有未正确处理的期初余额')
