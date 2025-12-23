#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复会计科目余额的脚本
重新计算所有已过账凭证的科目余额
"""

from app import create_app
from app.models import db, Account, Voucher

app = create_app()

with app.app_context():
    print("=== 开始修复会计科目余额 ===")
    
    # 首先重置所有科目余额为0
    all_accounts = Account.query.all()
    print(f"\n1. 重置所有 {len(all_accounts)} 个科目的余额为0")
    for account in all_accounts:
        account.balance = 0
    db.session.commit()
    
    # 重新计算所有已过账凭证的科目余额
    posted_vouchers = Voucher.query.filter_by(status='posted', is_deleted=False).all()
    print(f"\n2. 重新处理 {len(posted_vouchers)} 张已过账凭证")
    
    for i, voucher in enumerate(posted_vouchers, 1):
        print(f"   处理凭证 {i}/{len(posted_vouchers)}: {voucher.voucher_number}")
        
        for entry in voucher.entries:
            account = Account.query.filter_by(code=entry.account_code).first()
            if account:
                # 根据科目类型更新余额
                if account.type in ['asset', 'expense', 'cost']:
                    account.balance += entry.debit - entry.credit
                else:  # liability, equity, income
                    account.balance += entry.credit - entry.debit
    
    db.session.commit()
    
    # 显示修复后的科目余额
    print("\n3. 修复后的科目余额")
    account_types = ['asset', 'liability', 'equity', 'income', 'expense', 'cost']
    for acc_type in account_types:
        accounts = Account.query.filter_by(type=acc_type).all()
        print(f"\n{acc_type} 类型科目 ({len(accounts)}个):")
        for acc in accounts:
            print(f"  {acc.code} - {acc.name}: {acc.balance}")
    
    # 验证资产负债表平衡
    print("\n4. 验证资产负债表平衡")
    total_assets = sum(acc.balance for acc in Account.query.filter_by(type='asset').all())
    total_liabilities = sum(acc.balance for acc in Account.query.filter_by(type='liability').all())
    total_equity = sum(acc.balance for acc in Account.query.filter_by(type='equity').all())
    
    print(f"\n总资产: {total_assets}")
    print(f"总负债: {total_liabilities}")
    print(f"所有者权益: {total_equity}")
    print(f"负债+所有者权益: {total_liabilities + total_equity}")
    
    if abs(total_assets - (total_liabilities + total_equity)) < 0.01:
        print("\n✓ 资产负债表平衡")
    else:
        print(f"\n✗ 资产负债表不平衡，差额: {abs(total_assets - (total_liabilities + total_equity))}")
    
    print("\n=== 修复完成 ===")
