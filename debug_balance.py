#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试资产负债表不平衡问题
"""

from app import create_app
from app.models import db, Account, Voucher

app = create_app()

with app.app_context():
    print("=== 资产负债表不平衡详细调试 ===")
    
    # 计算各类型科目的总余额
    asset_total = sum(acc.balance for acc in Account.query.filter_by(type='asset').all())
    liability_total = sum(acc.balance for acc in Account.query.filter_by(type='liability').all())
    equity_total = sum(acc.balance for acc in Account.query.filter_by(type='equity').all())
    income_total = sum(acc.balance for acc in Account.query.filter_by(type='income').all())
    expense_total = sum(acc.balance for acc in Account.query.filter_by(type='expense').all())
    cost_total = sum(acc.balance for acc in Account.query.filter_by(type='cost').all())
    
    print(f"\n1. 各类型科目总余额:")
    print(f"   资产: {asset_total}")
    print(f"   负债: {liability_total}")
    print(f"   所有者权益: {equity_total}")
    print(f"   收入: {income_total}")
    print(f"   费用: {expense_total}")
    print(f"   成本: {cost_total}")
    
    print(f"\n2. 资产负债表平衡检查:")
    print(f"   资产总计: {asset_total}")
    print(f"   负债+所有者权益: {liability_total + equity_total}")
    print(f"   差额: {abs(asset_total - (liability_total + equity_total))}")
    
    # 检查每个已过账凭证的借贷平衡
    print(f"\n3. 检查已过账凭证的借贷平衡:")
    posted_vouchers = Voucher.query.filter_by(status='posted', is_deleted=False).all()
    
    unbalanced_vouchers = []
    for i, voucher in enumerate(posted_vouchers, 1):
        total_debit = sum(entry.debit for entry in voucher.entries)
        total_credit = sum(entry.credit for entry in voucher.entries)
        
        if abs(total_debit - total_credit) > 0.01:
            unbalanced_vouchers.append((voucher, total_debit, total_credit))
            print(f"   凭证 {voucher.voucher_number} 不平衡: 借 {total_debit}, 贷 {total_credit}")
    
    if not unbalanced_vouchers:
        print(f"   所有 {len(posted_vouchers)} 张已过账凭证借贷平衡")
    
    # 检查所有科目余额的计算是否正确
    print(f"\n4. 检查特定科目余额计算:")
    
    # 选择一些关键科目进行详细检查
    key_accounts = ['1122', '2241', '5101', '4104']
    
    for acc_code in key_accounts:
        account = Account.query.filter_by(code=acc_code).first()
        if account:
            print(f"   \n科目 {acc_code} - {account.name}:")
            print(f"   当前余额: {account.balance}")
            
            # 计算所有凭证对该科目的影响
            total_effect = 0
            for voucher in posted_vouchers:
                for entry in voucher.entries:
                    if entry.account_code == acc_code:
                        if account.type in ['asset', 'expense', 'cost']:
                            effect = entry.debit - entry.credit
                        else:
                            effect = entry.credit - entry.debit
                        total_effect += effect
                        print(f"     凭证 {voucher.voucher_number}: {effect}")
            
            print(f"   累计影响: {total_effect}")
            print(f"   是否一致: {abs(account.balance - total_effect) < 0.01}")
    
    # 分析问题原因
    print(f"\n5. 问题分析:")
    
    # 检查是否有未过账的凭证但已经产生了影响
    unposted_vouchers = Voucher.query.filter(Voucher.status != 'posted', Voucher.is_deleted == False).all()
    print(f"   未过账凭证数量: {len(unposted_vouchers)}")
    
    # 检查是否有错误的科目类型
    print(f"   检查科目类型配置:")
    all_accounts = Account.query.all()
    for account in all_accounts:
        if account.type not in ['asset', 'liability', 'equity', 'income', 'expense', 'cost']:
            print(f"     科目 {account.code} - {account.name} 类型错误: {account.type}")
    
    # 检查差额与哪些科目的余额相关
    print(f"\n6. 差额分析:")
    difference = asset_total - (liability_total + equity_total)
    print(f"   差额: {difference}")
    
    # 查找余额接近差额的科目
    print(f"   余额接近差额的科目:")
    for account in Account.query.all():
        if abs(account.balance - difference) < 100:  # 允许100以内的误差
            print(f"     {account.code} - {account.name}: {account.balance}")
