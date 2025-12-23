#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有者权益科目余额脚本
"""

from app import create_app
from app.models import db, Account, Voucher, VoucherEntry

app = create_app()

with app.app_context():
    print("=== 所有者权益科目检查 ===")
    
    # 1. 检查所有所有者权益科目
    equity_accounts = Account.query.filter_by(type='equity', is_deleted=False).all()
    
    if not equity_accounts:
        print("❌ 没有找到所有者权益科目！")
    else:
        print(f"✅ 找到 {len(equity_accounts)} 个所有者权益科目：")
        for account in equity_accounts:
            print(f"   {account.code} - {account.name}: {account.balance}")
    
    # 2. 检查所有过账的凭证中涉及所有者权益科目的分录
    print("\n=== 过账凭证中所有者权益科目相关分录 ===")
    vouchers = Voucher.query.filter_by(status='posted', is_deleted=False).all()
    
    equity_entries = []
    for voucher in vouchers:
        for entry in voucher.entries:
            if entry.account and entry.account.type == 'equity':
                equity_entries.append({
                    'voucher': voucher.voucher_number,
                    'date': voucher.date,
                    'account': f"{entry.account.code} - {entry.account.name}",
                    'debit': entry.debit,
                    'credit': entry.credit
                })
    
    if not equity_entries:
        print("❌ 没有找到涉及所有者权益科目的过账凭证！")
    else:
        print(f"✅ 找到 {len(equity_entries)} 条涉及所有者权益科目的分录：")
        for entry in equity_entries:
            print(f"   凭证 {entry['voucher']} ({entry['date']}): {entry['account']} - 借: {entry['debit']}, 贷: {entry['credit']}")
    
    # 3. 检查所有科目的余额
    print("\n=== 所有科目余额总和检查 ===")
    all_accounts = Account.query.filter_by(is_deleted=False).all()
    
    total_asset = sum(a.balance for a in all_accounts if a.type == 'asset')
    total_liability = sum(a.balance for a in all_accounts if a.type == 'liability')
    total_equity = sum(a.balance for a in all_accounts if a.type == 'equity')
    total_income = sum(a.balance for a in all_accounts if a.type == 'income')
    total_expense = sum(a.balance for a in all_accounts if a.type == 'expense')
    total_cost = sum(a.balance for a in all_accounts if a.type == 'cost')
    
    print(f"总资产: {total_asset}")
    print(f"总负债: {total_liability}")
    print(f"总权益: {total_equity}")
    print(f"总利润 (收入-费用-成本): {total_income - total_expense - total_cost}")
    print(f"资产=负债+权益+利润: {total_asset} = {total_liability} + {total_equity} + ({total_income - total_expense - total_cost}) → {total_asset} = {total_liability + total_equity + total_income - total_expense - total_cost}")
    print(f"平衡状态: {'✅ 平衡' if abs(total_asset - (total_liability + total_equity + total_income - total_expense - total_cost)) < 0.01 else '❌ 不平衡'}")
